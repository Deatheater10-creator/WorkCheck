# WorkCheck

A local engineering-maths learning tool. All five planned build stages are implemented: differentiation and context-aware partial-fraction step checking, an editable numbered workspace, local drafts and confirmed reset, verified teaching and three targeted practice questions, and documented offline setup. Worked solutions support progressive reveals and reduced-motion preferences.

Project guides: [readiness and submission blockers](devpost/readiness.md), [beginner code walkthrough](devpost/code-walkthrough.md), and [offline app map](devpost/app-map.html). Open the HTML map locally in your browser. These are technical guides; the learner writes their own submission.

Shipping preparation: [verified event requirements and repository status](devpost/shipping.md), [demo recording plan](devpost/demo-plan.md), and [factual evidence for learner-written answers](devpost/submission-evidence.md). The project uses the [MIT licence](LICENSE). [Public repository](https://github.com/Deatheater10-creator/WorkCheck) is published and anonymously verified. The demo video remains pending; no runtime service is needed.

## Start on Windows

WorkCheck runs on this computer in your browser. No accounts, API keys, paid services or internet are needed after setup. Python 3.12 (64-bit) and Windows 11 were used for verification. Other computers and Python versions are not yet validated.

### One-time setup (internet required)

1. Open the WorkCheck folder in VS Code. Choose **Terminal > New Terminal** and use PowerShell. The terminal must be in the folder containing `app.py` and `requirements-lock.txt`. For this installation:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\WorkCheck"
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

Run the commands one at a time and wait for each to finish. The version should say Python 3.12.x; the final check should say `No broken requirements found.` If Python 3.12 is not installed, install its 64-bit Windows version from [python.org](https://www.python.org/downloads/windows/) and reopen the terminal. If the launcher `py` is unavailable but `python --version` reports 3.12.x, use `python -m venv .venv` instead of the launcher command. Virtual-environment activation is not required.

### Launch every time (works offline after setup)

From the WorkCheck folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open **http://127.0.0.1:8501** in Edge or Chrome. Keep the terminal open. Stop the app with **Ctrl+C** in that terminal. To return, run the launch command again; do not reinstall packages. Press Enter or leave an input field and wait for `Saved on this device` before closing or refreshing.

Optional shortcut (from any folder, with the exact path adjusted if you saved the project elsewhere):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\WorkCheck\start-workcheck.ps1"
```

This execution-policy option applies only to that PowerShell process. The direct Python launch above needs no script-policy change. The helper uses its own folder and supports `-Port 8502`.

### Troubleshooting

| Symptom | What to do |
| --- | --- |
| `py` is not recognized or no Python found | Reopen PowerShell after installing Python 3.12. Check `python --version`; if it reports 3.12.x, use the fallback setup command above. |
| `.venv\Scripts\python.exe` not found | Check the current folder with `Get-Location`. Run setup from the folder containing `app.py`. |
| `No module named streamlit` or another dependency | Run `.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt` while online. Use this environment's Python, not a different installation. |
| Installation fails offline | Setup needs internet. Reconnect for installation; normal use should then work offline. Do not change pinned versions to silence an error. |
| Port 8501 already in use | Stop your earlier WorkCheck terminal with Ctrl+C, or launch with `--server.port 8502` and open http://127.0.0.1:8502. |
| Browser says the site cannot be reached | Check that the terminal is still running without errors and the browser port matches the launch command. Use `http`, not `https`. |
| Interface still shows old code | Stop with Ctrl+C, relaunch from this folder, refresh the browser, and check the question again. |
| Unexpected rational-polynomial restriction | Check the **Topic** selector. Sine, cosine and differentiation questions require **Differentiation**, not **Partial fractions**. |
| Draft not restored | Commit field edits with Enter or blur first. Check for save warnings; the normal save is in `%LOCALAPPDATA%\WorkCheck`. Test drafts are separate. |
| Save warning or damaged file | Keep the tab open and use **Retry saving**. Damaged files are preserved; see Local drafts below. Do not delete the only copy of your working. |
| Maths checking or practice times out | Your input stays intact. Try checking again with fewer applications running, or simplify the expression. A timeout is not a wrong-answer verdict. |

## Try differentiation

Worked solutions start fully visible. Choose **Step by step** to restart with one mathematical transformation, **Next step** to continue, or **Show all** to restore the full solution immediately. The current solution, worked example and each revealed practice solution keep separate progress. Practice answers remain hidden until their own reveal switch is enabled. Editing the question or working clears old results and reveal progress; Cancel on New question preserves them.

Reveals use a short fade, buttons give gentle visual feedback, and the first mistaken result line briefly highlights once per check. Equations do not slide or resize. All effects run locally and are disabled when your device requests reduced motion (on Windows 11, turn off **Settings > Accessibility > Visual effects > Animation effects**). Automatic practice grading remains deferred.

Question: `x^2 sin(x)`

Add these working lines:

```text
y = x^2 sin(x)
dy/dx = 2x cos(x)
dy/dx = 2x cos(x)
```

The second line is the first mistake: the product rule requires the sum of two terms, not multiplication of the derivatives. Later dependent lines are not checked.

Valid unfinished working:

```text
dy/dx = D(x^2) sin(x) + x^2 D(sin(x))
```

`D(...)` means an unevaluated derivative with respect to x. This line is valid but incomplete. A completed derivative can remain unsimplified:

```text
dy/dx = 2x sin(x) + x^2 cos(x)
```

Original-function lines use `y = ...`; derivative lines use `dy/dx = ...`, a plain derivative expression, or `D(original expression) = ...`. Unsupported notation asks for clarification. An original-function restatement alone is unfinished, not wrong.

Questions can also use a single-letter function definition such as `f(x) = (2x + 3)^4` or `f(x) = (x^2 - 5x)^3`; `y = (x^2 - 5x)^3` and bare expressions remain supported. The left side is a label, not part of the expression being differentiated. For an `f(x)` question, the preview retains `f(x)` and the final answer uses `f'(x)`. Matching `f(x) = ...` working is an original-function statement, while `f'(x) = ...` (or `f′(x) = ...`) claims a derivative. Held `D(...)` steps can use that derivative label and remain unfinished until evaluated. A different named function in the working asks for clarification rather than being silently treated as the current function. Labels such as `g(x)` also work; multiple variables and higher derivatives remain unsupported.

## Questions written as sentences

A small offline wording grammar recognises complete requests such as:

- `Differentiate y = x^2 sin(x).`
- `Find the derivative of (2x+3)^4 with respect to x.`
- `Let f(x) = ln(x^2+1). Find the derivative.`
- `Given f(x) = (2x+3)^4; find f'(x).`
- `Decompose 1/((x+1)(x+2)) into partial fractions.`
- `Express 1/((x+1)(x+2)) as partial fractions.`

For recognised sentences, WorkCheck shows **Interpreted question** with rendered maths and a task description. Tick **I confirm the interpreted expression and task** to enable checking. Changing the question or topic clears confirmation, results and practice. Editing working preserves the question confirmation but still clears stale results/practice. Restored sentences need confirmation again. Original typed text is saved unchanged. Bare expressions/function definitions continue to work directly.

Optional leading Please, the phrase the function, and Given that are accepted in the documented forms. The wording must match a documented template; this is not general language understanding. Unrecognised wording asks you to clarify the complete request. A topic mismatch asks you to select the requested topic. Notation still goes through the same restricted safe parser. Extra instructions are not discarded to manufacture a supported question.

**Unsupported mathematics** is separate from wording. For example, `Let f(x) = ln(x)/ln(-x). Find the imaginary coefficient of f'(1).` requests complex-valued/component mathematics and derivative evaluation. Complex logarithms need branch choices; neither branch-sensitive complex calculations nor evaluation of derivatives at a point are verified by this version. WorkCheck displays the recognised definition when possible, explains the limitation, and provides no answer or practice for that request. It does not assume a branch or reinterpret it as ordinary real differentiation. Integrals and higher derivatives likewise remain outside scope.

## Supported notation and limits

Use parentheses, integer powers, `sin`, `cos`, `exp`, and `ln` in one real variable x. Numeric coefficients and adjacent factors such as `2x`, `-3x`, `0.5x`, `2(x+1)`, `x(x+1)`, `(x+1)(x-1)`, and `x sin(x)` are accepted by the same parser in previews, questions, and working. Function names stay whole: `xsin(x)` is not silently split. `(2x + 3)^4` has derivative `8(2x+3)^3`; `(x^2 - 5x)^3` has derivative `3(x^2-5x)^2(2x-5)`. Explicit `*` continues to work. Ambiguous forms such as `1/2x` or `x^2x` request clarification; write `1/(2x)` or `(1/2)x`, and `(x^2)x`, as intended. `exp(2x)` means e to the power 2x. Use ordinary exact numeric literals, not scientific notation.

After updating the Python source, stop and restart the local Streamlit server to ensure the running app loads the new code. Start it from this project folder, or use its absolute app.py path. Refresh the browser after restarting. This does not delete the local saved draft.

Limits: 500 characters per question/line, 20 working lines, 150 syntax nodes per expression, nesting depth 12, numbers up to 8 digits, integer exponents from -12 to 12, polynomial degree at most 12. Over-limit input is preserved in the editor; checking pauses. A supported function name does not guarantee every domain or expression can be proved. Unknown checks request clarification rather than guess.

All mathematical operations run locally. No API keys, paid services, or external AI calls. Equation previews do not establish mathematical correctness. Feedback is cleared when working changes.

## Try partial fractions

Select **Partial fractions** and enter `1/((x+1)(x+2))` as the question. Add one step per line:

```text
A/(x+1)+B/(x+2)
1=A(x+2)+B(x+1)
A+B=0
2A+B=1
A=1
B=-1
1/(x+1)-1/(x+2)
```

The setup assigns A and B to specific denominator terms. Setup, identities, coefficient equations, coefficient values, and partial substitutions such as `1/(x+1)+B/(x+2)` are valid intermediate working, not finished answers. The resolved sum completes the decomposition. A copied original fraction alone is also unfinished. Equivalent equation order/scaling and swapped A/B denominator assignments are supported.

Results use school-style formatting, preferring positive terms first. This example displays `1/(x+1) - 1/(x+2)` and `x ≠ -1, -2`, followed by the coefficient method: write the two-term setup, multiply through, compare coefficients, solve A/B, and substitute. Each displayed method is verified locally. Finite excluded values are compact; interval bounds such as `x > 0` are retained where relevant. Presentation does not change answer equivalence or step verdicts.

Try checking only the first and third lines: the result should be valid but incomplete. Change `A+B=0` to `A+B=1`: it should be the first mistake. Without a setup, a coefficient equation asks for clarification. An unresolved or incorrect line blocks dependent checking; a later correct answer does not erase it.

For the root-substitution method, after the setup use `x=-1: 1=A` and `x=-2: 1=-B`. Alternatively, select a root with `x=-1` on its own line, then write the denominator-cleared identity. This means substitution into a polynomial identity, not substituting into the original fraction at a point where it is undefined.

Scope: nonzero proper rational expressions with exact rational coefficients and two distinct rational linear denominator factors. Preserve original exclusions (here x != -1, -2). Repeated/quadratic factors, nonlinear coefficient equations, unknown coefficient names beyond A/B, and ambiguous changes of coefficient assignments request clarification rather than a guessed verdict. Solving and checking remain local; numerical agreement is not proof.

## Local drafts and New question

Your current question, topic, and numbered working are saved automatically when you press Enter or leave an edited field. **Before refreshing or closing, finish editing and look for “Saved on this device.”** Text still actively being typed may not yet have reached the local app. Restore happens when you return, including after restarting the server. Feedback and practice results are not restored; recheck the saved working.

The normal Windows save is `%LOCALAPPDATA%\WorkCheck\draft.json`. It contains one current draft; use one editing tab at a time. There are no accounts or cloud sync. The file is outside the Git repository. Tests use isolated temporary files via `WORKCHECK_DRAFT_PATH` and do not touch your real draft.

**New question** asks before clearing a nonempty question or working. **Cancel** keeps the draft. **Clear question and working** saves an empty draft before clearing the screen; old working will not return on refresh. If that save fails, the visible working stays intact and an error is shown. Empty drafts can reset without a confirmation prompt.

A missing save starts normally. A damaged or incompatible save is preserved as `draft.damaged-<id>.json` beside the save, with a recovery message and fresh editor. Save failures keep the working in memory and offer **Retry saving**. Do not close until saving succeeds if you need the current edits to survive. Computational input limits never truncate stored text. An 8 MiB save-file safety limit reports a save failure for an oversized draft rather than truncating it.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

See [validation](devpost/validation.md) for actual verification results, [coverage](devpost/coverage.md) for tested maths and limitations, and [photo feasibility](devpost/photo-feasibility.md) for the separate OCR decision. Stage 5 and the ordinary-notation parser fixes passed learner review, including learner-performed offline checks.


Worked-solution refinement: render actual mathematical equations with a short explanation beside every transformation. Partial fractions include expansion, collection, coefficient comparison, elimination, back-substitution, and the original-to-final equality using the question's actual coefficients. Differentiation shows explicit derivative transformations for the supported sum, product, integer power, chain, sine, cosine, exponential, and logarithm rules. Verify generated transformations symbolically before display; never change the working checker's acceptance rules. Stage 3 was accepted by the learner after review.


## Learn and practise

Check a supported question, with or without an attempt. Read the first-error or method feedback, then **Understand the concept** before the worked solutions and the separate **Worked example**. Three distinct practice problems follow, selected for the main method (product, chain, powers, sine/cosine, exponential, logarithm, or restricted partial fractions). Supporting rules used by the example are explained too.

Each practice problem has its own **Reveal answer and worked solution** toggle, initially off. Revealing one does not reveal the others. Answers and complete worked transformations use rendered maths and retain each problem's real-domain restrictions. There is no automatic grading of practice attempts.

All generation and verification run locally in a separate bounded job. Only complete verified sets are displayed: one example plus exactly three distinct practice problems, different from the current question. Small generated candidates fall back to a reverified hand-checked bank; if a full set cannot be verified, an explicit unavailable message preserves your checked answer. Check again to retry. Verified content can be cached in local app memory; failures are not cached. No API keys or external requests are used.

Changing the question, topic, or working (including adding, deleting or reordering lines), rechecking, or confirming New question clears previous practice and reveals. Cancelling New question preserves them. Draft restoration restores your input, not previous answers or reveals.


## Verification status and final review

On Windows 11 x64 / Python 3.12.0, a clean installation from all 37 pinned wheels passed dependency checks. The full **163-test suite passed with nonlocal backend connections blocked**. A fresh headless Edge profile passed cold offline maths rendering (including locally served KaTeX fonts), both topic flows, explanations, individual practice reveals, refresh/server-restart restoration and confirmed reset. The PowerShell launch helper passed from another folder, including loopback-only binding and Ctrl+C stop.

These automated checks were agent-run. The learner subsequently confirmed the offline checks and ordinary-notation review passed. The walkthrough below is retained for repeat checks or another device. A fresh Python installer and another Windows machine have not been tested. Stage 5 passed learner review and offline checks. Final readiness sign-off and the code tour/app map remain before submission preparation.

1. Finish any field edit and wait for **Saved on this device**. Stop the app, disconnect internet, then use the launch command above. Open a new InPrivate/private browser window at the local address.
2. Confirm the saved question, topic and ordered working return. Check the differentiation example above: inspect the first mistake, readable maths, closable concept/example panels and three initially hidden practice solutions. Reveal them individually.
3. Switch to Partial fractions and try the example above; inspect the two denominator exclusions, feedback and practice. Use the correct Topic selector for each task.
4. Change a question or working line: previous results/practice must disappear. Try ambiguous input `1/2x`: it should ask for clarification and preserve your input. Cancel **New question** and confirm preservation; only confirm clearing when ready to discard that draft.
5. Restart once more and check draft restoration (or the empty draft after confirmed clearing). Reconnect internet and report anything confusing or broken before approval.

Developer-only reproducible offline checks use existing dependencies and installed Edge; they create isolated drafts/profiles under ignored `.workcheck/`:

```powershell
.\.venv\Scripts\python.exe scripts/offline_browser_check.py --tests-only
.\.venv\Scripts\python.exe scripts/offline_browser_check.py
```

Run these separately, with ports 8503 and 9231 free. The browser check opens a temporary headless profile, not your normal browser. It blocks nonlocal page/backend traffic without disabling your computer's adapter; see the validation report for exact scope and limitations. Initial setup/package downloads and the separate OCR documentation research are online activities, not runtime requirements.


## Ordinary multiplication is the default

Type `2x`, `x^3 cos(x)`, `x sin(x)`, `2(x+1)`, `(x+1)(x-2)`, `3x^2 sin(2x)`, or `f(x) = x^3 cos(x)`. The same safe parser handles question expressions, function definitions, numbered working and questions copied from practice. There is no separate practice-attempt input or automatic practice grading in this version.

After a power, put a space before a named function or another variable factor: `x^3 cos(x)` or `x^2 x`. Adjacent parentheses such as `x^2(x+1)` are also accepted. Function names are never split: use `x sin(x)`, not `xsin(x)`. For ambiguous division use `1/(2x)` or `(1/2)x`; for an unclear exponent boundary use `(x^2)x`. Multiply two numbers using grouping (`2(3)`) or the ordinary multiplication symbols × and ·. Existing explicit programming-style multiplication remains accepted for compatibility, but students do not need it. Rendered maths remains conventional, including stacked fractions and clear numeric multiplication.
