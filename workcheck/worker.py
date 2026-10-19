"""Run maths in a disposable local process with a hard waiting limit."""
import multiprocessing as mp
from .models import CheckResult


def _calculate(connection, question, lines):
    try:
        from .checking import check_differentiation
        connection.send(check_differentiation(question, lines))
    except Exception:
        connection.send(CheckResult("Needs clarification", "The local checker could not verify this input safely. Please simplify or clarify it."))
    finally:
        connection.close()


def run_check(question, lines, timeout=5.0):
    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_calculate, args=(child, question, lines), daemon=True)
    try:
        process.start()
        child.close()
        if parent.poll(timeout):
            try:
                return parent.recv()
            except EOFError:
                return CheckResult("Needs clarification", "The maths worker stopped without a verified result. Your input is kept.")
        return CheckResult("Needs clarification", "The local check reached its time limit. Your input is kept; simplify it and try again.")
    finally:
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
        parent.close()
        child.close()
