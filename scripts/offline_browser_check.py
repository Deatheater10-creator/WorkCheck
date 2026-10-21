"""Development-only cold Edge check. Uses installed websockets, no new packages.

Creates an isolated draft/profile under ignored .workcheck/. All page HTTP
requests outside the test app are refused. A refusing browser proxy, disabled
QUIC and a backend socket guard additionally prevent external HTTP/socket use.
This does not disable the user's network adapter or change browser settings.
"""
import base64
import http.server
import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request
from urllib.parse import urlparse
from uuid import uuid4
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.workcheck' / ('offline-' + uuid4().hex[:8])
RUN.mkdir(parents=True)
EDGE = Path(os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)')) / 'Microsoft/Edge/Application/msedge.exe'
APP_PORT, DEBUG_PORT = 8503, 9231
FLAGS = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
GUARD = '''import socket, ipaddress, os
from pathlib import Path
original_connect = socket.socket.connect
original_connect_ex = socket.socket.connect_ex
def allowed(address):
    if not isinstance(address, tuple):
        return True
    host = str(address[0])
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == 'localhost'
def reject(address):
    with open(os.environ['WORKCHECK_NETWORK_LOG'], 'a', encoding='utf-8') as log:
        log.write(repr(address) + '\\n')
    raise OSError('Offline verification blocks non-loopback connections')
def connect(self, address):
    if not allowed(address): reject(address)
    return original_connect(self, address)
def connect_ex(self, address):
    if not allowed(address): reject(address)
    return original_connect_ex(self, address)
socket.socket.connect = connect
socket.socket.connect_ex = connect_ex
'''


def wait_for(fn, timeout=35):
    deadline = time.monotonic()+timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = fn()
            if value:
                return value
        except (OSError, ValueError) as exc:
            last = exc
        time.sleep(0.1)
    raise AssertionError(f'Condition did not become true: {last}')


class RefusingProxy(http.server.BaseHTTPRequestHandler):
    requests = []
    def do_CONNECT(self):
        self.requests.append(self.path)
        try:
            self.send_error(503, 'Offline test: external access refused')
        except OSError:
            pass  # Browser background services may close a refused connection.
    do_GET = do_CONNECT
    do_POST = do_CONNECT
    def log_message(self, *_):
        pass


class Browser:
    def __init__(self, ws):
        self.ws, self.counter = ws, 0
        self.responses, self.external, self.requests, self.errors = {}, [], [], []
    def call(self, method, params=None):
        self.counter += 1
        ident = self.counter
        self.ws.send(json.dumps({'id': ident, 'method': method, 'params': params or {}}))
        while ident not in self.responses:
            event = json.loads(self.ws.recv(timeout=45))
            if 'id' in event:
                self.responses[event['id']] = event
            elif event.get('method') == 'Fetch.requestPaused':
                request = event['params']
                url = request['request']['url']
                parsed = urlparse(url)
                local = parsed.hostname in ('127.0.0.1', 'localhost') and parsed.port == APP_PORT
                permitted = local or parsed.scheme in ('data', 'blob')
                if not permitted:
                    self.external.append(url)
                self.counter += 1
                self.ws.send(json.dumps({'id': self.counter,
                    'method': 'Fetch.continueRequest' if permitted else 'Fetch.failRequest',
                    'params': {'requestId': request['requestId'], **({} if permitted else {'errorReason': 'InternetDisconnected'})}}))
            elif event.get('method') == 'Network.requestWillBeSent':
                self.requests.append(event['params']['request']['url'])
            elif event.get('method') == 'Runtime.exceptionThrown':
                self.errors.append(event['params']['exceptionDetails'])
        response = self.responses.pop(ident)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response.get('result', {})
    def js(self, expression):
        result = self.call('Runtime.evaluate', {'expression': expression, 'returnByValue': True, 'awaitPromise': True})
        if 'exceptionDetails' in result:
            raise AssertionError(result['exceptionDetails'])
        return result.get('result', {}).get('value')
    def text(self):
        return self.js("document.body ? document.body.innerText : ''") or ''
    def wait_text(self, text):
        return wait_for(lambda: text in self.text())
    def button(self, label):
        found = self.js("(() => {const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==="+json.dumps(label)+"); if(!b)return false;b.click();return true})()")
        assert found, f'Missing button: {label}'
        time.sleep(0.4)
    def fill(self, index, value):
        wait_for(lambda: self.js("document.querySelectorAll('[data-testid=stTextInput] input').length") > index)
        found = self.js("(() => {const e=document.querySelectorAll('[data-testid=stTextInput] input')["+str(index)+"];if(!e)return false;e.focus();e.select();return true})()")
        assert found, f'Missing input: {index}'
        self.call('Input.insertText', {'text': value})
        self.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
        self.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
        def saved():
            try:
                draft = json.loads((RUN/'draft.json').read_text(encoding='utf-8'))
                return (draft['question'] if index == 0 else draft['lines'][index-1]['text']) == value
            except (FileNotFoundError, ValueError, IndexError):
                return False
        wait_for(saved)
    def screenshot(self, name):
        data = self.call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})['data']
        (RUN/name).write_bytes(base64.b64decode(data))


def main():
    ordinary_mode = '--ordinary' in sys.argv
    sentence_mode = '--sentences' in sys.argv or ordinary_mode
    differentiation_question = ('Differentiate f(x) = x^3 cos(x).' if ordinary_mode else
                                'Differentiate y = x^2*sin(x).' if sentence_mode else 'x^2*sin(x)')
    differentiation_working = "f'(x)=-3x^2 sin(x)" if ordinary_mode else 'dy/dx=2*x*cos(x)'
    guard_dir = RUN/'guard'
    guard_dir.mkdir()
    (guard_dir/'sitecustomize.py').write_text(GUARD, encoding='utf-8')
    env = dict(os.environ, WORKCHECK_DRAFT_PATH=str(RUN/'draft.json'),
               WORKCHECK_NETWORK_LOG=str(RUN/'backend-blocked.txt'),
               PYTHONPATH=os.pathsep.join([str(guard_dir), str(ROOT)]))
    server_log = (RUN/'server.log').open('w', encoding='utf-8')
    server = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', str(ROOT/'app.py'),
        '--server.address', '127.0.0.1', '--server.port', str(APP_PORT), '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'], cwd=ROOT, env=env, stdout=server_log, stderr=subprocess.STDOUT, creationflags=FLAGS)
    proxy = socketserver.ThreadingTCPServer(('127.0.0.1', 0), RefusingProxy)
    proxy.daemon_threads = True
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    browser_process, browser = None, None
    report = {'run_directory': str(RUN), 'checks': [], 'isolation': 'Fresh Edge profile; refusing HTTP proxy and CDP nonlocal request blocking; backend nonloopback socket guard'}
    try:
        wait_for(lambda: urllib.request.urlopen(f'http://127.0.0.1:{APP_PORT}/_stcore/health').status == 200)
        browser_process = subprocess.Popen([str(EDGE), '--headless=new', '--disable-gpu', '--no-first-run',
            '--no-default-browser-check', '--disable-background-networking', '--disable-component-update',
            '--disable-sync', '--disable-quic', '--metrics-recording-only',
            f'--remote-debugging-port={DEBUG_PORT}', '--remote-allow-origins=*',
            '--user-data-dir='+str(RUN/'browser-profile'),
            '--proxy-server=http://127.0.0.1:'+str(proxy.server_address[1]),
            '--proxy-bypass-list=127.0.0.1;localhost', 'about:blank'], creationflags=FLAGS,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        targets = wait_for(lambda: json.load(urllib.request.urlopen(f'http://127.0.0.1:{DEBUG_PORT}/json')))
        target = next(target for target in targets if target['type'] == 'page')
        ws = connect(target['webSocketDebuggerUrl'], max_size=16*1024*1024, legacy=True)
        browser = Browser(ws)
        browser.call('Page.enable')
        browser.call('Network.enable')
        browser.call('Network.setCacheDisabled', {'cacheDisabled': True})
        browser.call('Runtime.enable')
        browser.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'no-preference'}]})
        browser.call('Fetch.enable', {'patterns': [{'urlPattern': '*'}]})
        browser.call('Page.navigate', {'url': f'http://127.0.0.1:{APP_PORT}'})
        browser.wait_text('Your working')
        report['checks'].append('Cold browser load with empty profile and cache disabled')
        browser.fill(0, differentiation_question)
        browser.button('Add step')
        browser.fill(1, differentiation_working)
        if sentence_mode:
            assert browser.js("[...document.querySelectorAll('button')].find(e=>e.innerText==='Check working').disabled")
            browser.js("[...document.querySelectorAll('input[type=checkbox]')].find(e=>e.getAttribute('role')!=='switch').click()")
            wait_for(lambda: browser.js("![...document.querySelectorAll('button')].find(e=>e.innerText==='Check working').disabled"))
            report['checks'].append('Sentence expression/task preview and required student confirmation')
        browser.button('Check working')
        browser.wait_text('Your three practice problems')
        assert 'First mistake' in browser.text(), browser.text()
        assert 'multiplies the two derivatives' in browser.text()
        report['checks'].append('Exact product-rule acceptance example: first mistake, concept, worked example, three exercises')
        assert browser.js("document.querySelectorAll('.katex').length") > 10
        assert browser.js("document.querySelectorAll('.katex-error').length") == 0
        assert browser.js("[...document.querySelectorAll('.katex-html')].filter(e=>e.getBoundingClientRect().height>0).length") > 10
        assert browser.js("[...document.querySelectorAll('.katex-display')].every(e=>!e.innerText.includes('*'))")
        report['checks'].append('KaTeX maths rendered in browser, no parse errors or programming multiplication')
        browser.js("document.querySelector('.st-key-explanation_panel').scrollIntoView({block:'start',behavior:'instant'})")
        browser.screenshot('student-explanation.png')
        # Real CSS and progressive controls: equations fade without changing geometry.
        panel = '.st-key-worked_solution_panel'
        click_in_panel = lambda label: browser.js(
            f"[...document.querySelectorAll('{panel} button')].find(e=>e.innerText.trim()==={json.dumps(label)}).click()")
        rows = "document.querySelectorAll('.st-key-worked_solution_panel [class*=st-key-solution_reveal_]')"
        full_rows = browser.js(rows + '.length')
        assert full_rows > 2
        assert browser.js("getComputedStyle(document.querySelector('[class*=st-key-mistake_highlight_]')).animationName") == 'wc-mistake'
        click_in_panel('Step by step')
        wait_for(lambda: browser.js(rows + '.length') == 1)
        wait_for(lambda: browser.js("document.querySelectorAll('[class*=st-key-mistake_highlight_]').length") == 0)
        maths_ready = "Boolean(" + rows + "[0]?.querySelector('.katex-display .katex'))"
        wait_for(lambda: browser.js(maths_ready))
        geometry = "(()=>{const e=" + rows + "[0].querySelector('.katex-display');const r=e.getBoundingClientRect();return [r.width,r.height,getComputedStyle(e).transform]})()"
        before = browser.js(geometry)
        assert browser.js("getComputedStyle(" + rows + "[0]).animationName") == 'wc-reveal'
        click_in_panel('Next step')
        wait_for(lambda: browser.js(rows + '.length') == 2)
        wait_for(lambda: browser.js(maths_ready))
        assert browser.js(geometry) == before
        browser.js("document.querySelector('.st-key-worked_solution_panel').scrollIntoView({block:'start',behavior:'instant'})")
        browser.screenshot('progressive.png')
        browser.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        assert browser.js("matchMedia('(prefers-reduced-motion: reduce)').matches")
        assert browser.js("getComputedStyle(" + rows + "[0]).animationName") == 'none'
        assert browser.js("getComputedStyle(document.querySelector('button')).transitionDuration") == '0s'
        click_in_panel('Show all')
        wait_for(lambda: browser.js(rows + '.length') == full_rows)
        browser.call('Emulation.setEmulatedMedia', {'features': []})
        report['checks'].append('Progressive transformations, show all, stable equation dimensions and reduced-motion CSS verified in Edge')
        browser.screenshot('differentiation.png')
        # Inspect actual browser controls before interacting (Streamlit uses switches).
        (RUN/'controls.json').write_text(json.dumps(browser.js("[...document.querySelectorAll('input, [role=switch]')].map(e=>({tag:e.tagName,type:e.type,role:e.getAttribute('role'),'aria-label':e.getAttribute('aria-label')}))"), indent=2), encoding='utf-8')
        wait_for(lambda: browser.js("document.querySelectorAll('input[role=switch]').length") == 3)
        toggles = browser.js("document.querySelectorAll('input[role=switch]').length")
        assert toggles == 3, f'Expected 3 practice toggles, got {toggles}'
        assert browser.js("[...document.querySelectorAll('input[role=switch]')].every(e=>!e.checked)")
        assert browser.js("[...document.querySelectorAll('strong')].filter(e=>e.innerText==='Answer').length") == 0
        for index in range(3):
            browser.js(f"document.querySelectorAll('input[role=switch]')[{index}].click()")
            wait_for(lambda: browser.js("[...document.querySelectorAll('strong')].filter(e=>e.innerText==='Answer').length") == index+1)
        report['checks'].append('Three initially hidden solutions reveal individually with full maths')
        browser.screenshot('revealed.png')
        browser.call('Page.reload', {'ignoreCache': True})
        browser.wait_text('Your working')
        wait_for(lambda: browser.js("document.querySelectorAll('[data-testid=stTextInput] input').length") == 2)
        assert browser.js("[...document.querySelectorAll('[data-testid=stTextInput] input')].map(e=>e.value)") == [differentiation_question, differentiation_working]
        assert 'Your three practice problems' not in browser.text()
        report['checks'].append('Draft restored after refresh; old practice and reveals not restored')
        server.terminate()
        server.wait(timeout=15)
        server = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', str(ROOT/'app.py'),
            '--server.address', '127.0.0.1', '--server.port', str(APP_PORT), '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'], cwd=ROOT, env=env, stdout=server_log, stderr=subprocess.STDOUT, creationflags=FLAGS)
        wait_for(lambda: urllib.request.urlopen(f'http://127.0.0.1:{APP_PORT}/_stcore/health').status == 200)
        browser.call('Page.reload', {'ignoreCache': True})
        wait_for(lambda: browser.js("document.querySelectorAll('[data-testid=stTextInput] input').length") == 2)
        assert browser.js("[...document.querySelectorAll('[data-testid=stTextInput] input')].map(e=>e.value)") == [differentiation_question, differentiation_working]
        report['checks'].append('Draft restored after stopping and restarting the local server')
        browser.button('New question')
        browser.button('Cancel')
        assert browser.js("document.querySelector('[data-testid=stTextInput] input').value") == differentiation_question
        browser.button('New question')
        browser.button('Clear question and working')
        wait_for(lambda: browser.js("document.querySelector('[data-testid=stTextInput] input').value") == '')
        browser.call('Page.reload', {'ignoreCache': True})
        browser.wait_text('Your working')
        wait_for(lambda: browser.js("document.querySelectorAll('[data-testid=stTextInput] input').length") == 1)
        assert browser.js("document.querySelector('[data-testid=stTextInput] input').value") == ''
        report['checks'].append('Cancel preserves draft; confirmed reset clears durable and visible draft')
        # Open the accessible menu with a real key event. Typing immediately
        # after a rerender can target an input React is about to replace.
        wait_for(lambda: browser.js("Boolean(document.querySelector('input[role=combobox]:not(:disabled)'))"))
        browser.js("document.querySelector('input[role=combobox]').focus()")
        browser.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'ArrowDown', 'code': 'ArrowDown', 'windowsVirtualKeyCode': 40})
        browser.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'ArrowDown', 'code': 'ArrowDown', 'windowsVirtualKeyCode': 40})
        wait_for(lambda: browser.js("[...document.querySelectorAll('[role=option]')].some(e=>e.innerText.trim().includes('Partial fractions'))"))
        browser.js("[...document.querySelectorAll('[role=option]')].find(e=>e.innerText.trim().includes('Partial fractions')).click()")
        wait_for(lambda: json.loads((RUN/'draft.json').read_text(encoding='utf-8'))['topic'] == 'Partial fractions')
        browser.fill(0, '1/((x+1)(x+2))')
        browser.button('Add step')
        browser.fill(1, 'A/(x+1)+B/(x+2)')
        browser.button('Add step')
        browser.fill(2, 'A+B=1')
        browser.button('Check working')
        browser.wait_text('Your three practice problems')
        assert 'First mistake' in browser.text()
        wait_for(lambda: browser.js("document.querySelectorAll('input[role=switch]').length") == 3)
        assert browser.js("[...document.querySelectorAll('.katex')].some(e=>e.textContent.includes('−1')&&e.textContent.includes('−2'))")
        browser.js("document.querySelector('input[role=switch]').click()")
        wait_for(lambda: browser.js("[...document.querySelectorAll('strong')].filter(e=>e.innerText==='Answer').length") == 1)
        browser.screenshot('partial-fractions.png')
        report['checks'].append('Partial-fraction first coefficient mistake, learning, domain exclusions and individual practice reveal')
        if sentence_mode:
            browser.fill(0, "Let f(x) = ln(x)/ln(-x). Find the imaginary coefficient of f'(1).")
            browser.wait_text('Unsupported mathematics')
            wait_for(lambda: browser.js("document.querySelectorAll('input[role=switch]').length") == 0)
            assert 'No complex branch is assumed' in browser.text()
            assert 'Your three practice problems' not in browser.text()
            assert browser.js("[...document.querySelectorAll('button')].find(e=>e.innerText==='Check working').disabled")
            report['checks'].append('Complex-log branch/component and derivative-evaluation request rejected without answer/practice')
        report['browser_external_requests_blocked'] = browser.external
        report['browser_requests'] = sorted(set(browser.requests))
        report['javascript_exceptions'] = browser.errors
        assert not browser.external, f'Page attempted external requests: {browser.external}'
        assert not browser.errors, browser.errors
        report['passed'] = True
    except Exception as exc:
        report['passed'] = False
        report['failure'] = repr(exc)
        if browser:
            try:
                (RUN/'failure-body.txt').write_text(browser.text(), encoding='utf-8')
                (RUN/'failure-dom.html').write_text(browser.js('document.body.outerHTML'), encoding='utf-8')
                browser.screenshot('failure.png')
            except Exception:
                pass
        raise
    finally:
        report['proxy_requests_refused'] = RefusingProxy.requests
        network_log = RUN/'backend-blocked.txt'
        report['backend_external_attempts'] = network_log.read_text(encoding='utf-8').splitlines() if network_log.exists() else []
        (RUN/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({'passed': report.get('passed'), 'report': str(RUN/'report.json'), 'checks': report['checks'], 'failure': report.get('failure')}, indent=2), flush=True)
        if browser:
            browser.ws.close()
        if browser_process:
            browser_process.terminate()
            browser_process.wait(timeout=15)
        server.terminate()
        server.wait(timeout=15)
        server_log.close()
        proxy.shutdown()


def test_suite():
    """Run the ordinary suite with a self-tested nonlocal socket guard."""
    guard_dir = RUN/'guard'
    guard_dir.mkdir()
    (guard_dir/'sitecustomize.py').write_text(GUARD, encoding='utf-8')
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(guard_dir), str(ROOT)]),
               WORKCHECK_NETWORK_LOG=str(RUN/'guard-self-test.log'))
    probe = subprocess.run([sys.executable, '-c',
        "import socket; socket.create_connection(('203.0.113.1',443),timeout=1)"], env=env, capture_output=True, text=True)
    assert probe.returncode != 0 and 'Offline verification blocks' in probe.stderr
    env['WORKCHECK_NETWORK_LOG'] = str(RUN/'suite-network-attempts.log')
    with (RUN/'tests.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    tail = (RUN/'tests.log').read_text(encoding='utf-8').splitlines()[-12:]
    report = {'passed': result.returncode == 0, 'guard_self_test': True, 'summary': tail,
              'network_attempts': (RUN/'suite-network-attempts.log').read_text(encoding='utf-8').splitlines()
              if (RUN/'suite-network-attempts.log').exists() else []}
    (RUN/'suite-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(RUN/'suite-report.json'), **report}, indent=2), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    test_suite() if '--tests-only' in sys.argv else main()
