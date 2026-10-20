# WorkCheck

A local engineering-maths learning tool. **Stages 1–2:** differentiation step checking, an editable numbered workspace, local draft saving/restoration, and confirmed reset. Other approved features are not implemented yet.

## Start on Windows

Open this folder in VS Code and open a PowerShell terminal. Python 3.12 is required.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The first two commands are setup; installation needs internet. On later visits, only run the third command. Open http://127.0.0.1:8501 and keep the terminal running. Stop with Ctrl+C. No environment activation or execution-policy changes are needed.

If Python is missing, install Python 3.12 from python.org. If port 8501 is occupied, append `--server.port 8502` and open the matching address. If a dependency is missing, run the install command with this environment's Python.

## Try differentiation

Question: `x^2*sin(x)`

Add these working lines:

```text
y = x^2*sin(x)
dy/dx = (2*x)*cos(x)
dy/dx = 2*x*cos(x)
```

The second line is the first mistake: the product rule requires the sum of two terms, not multiplication of the derivatives. Later dependent lines are not checked.

Valid unfinished working:

```text
dy/dx = D(x^2)*sin(x) + x^2*D(sin(x))
```

`D(...)` means an unevaluated derivative with respect to x. This line is valid but incomplete. A completed derivative can remain unsimplified:

```text
dy/dx = 2*x*sin(x) + x^2*cos(x)
```

Original-function lines use `y = ...`; derivative lines use `dy/dx = ...`, a plain derivative expression, or `D(original expression) = ...`. Unsupported notation asks for clarification. An original-function restatement alone is unfinished, not wrong.

Questions can also use a single-letter function definition such as `f(x) = (2x + 3)^4` or `f(x) = (x^2 - 5x)^3`; `y = (x^2 - 5x)^3` and bare expressions remain supported. The left side is a label, not part of the expression being differentiated. For an `f(x)` question, the preview retains `f(x)` and the final answer uses `f'(x)`. Matching `f(x) = ...` working is an original-function statement, while `f'(x) = ...` (or `f′(x) = ...`) claims a derivative. Held `D(...)` steps can use that derivative label and remain unfinished until evaluated. A different named function in the working asks for clarification rather than being silently treated as the current function. Labels such as `g(x)` also work; multiple variables and higher derivatives remain unsupported.

## Supported notation and limits

Use parentheses, integer powers, `sin`, `cos`, `exp`, and `ln` in one real variable x. Numeric coefficients and adjacent factors such as `2x`, `-3x`, `0.5x`, `2(x+1)`, `x(x+1)`, `(x+1)(x-1)`, and `x sin(x)` are accepted by the same parser in previews, questions, and working. Function names stay whole: `xsin(x)` is not silently split. `(2x + 3)^4` has derivative `8*(2*x+3)^3`; `(x^2 - 5x)^3` has derivative `3*(x^2-5*x)^2*(2*x-5)`. Explicit `*` continues to work. Ambiguous forms such as `1/2x` or `x^2x` request clarification; write `1/(2*x)` or `(1/2)*x`, and `(x^2)*x`, as intended. `exp(2*x)` means e to the power 2x. Use ordinary exact numeric literals, not scientific notation.

After updating the Python source, stop and restart the local Streamlit server to ensure the running app loads the new code. Start it from this project folder, or use its absolute app.py path. Refresh the browser after restarting. This does not delete the local saved draft.

Limits: 500 characters per question/line, 20 working lines, 150 syntax nodes per expression, nesting depth 12, numbers up to 8 digits, integer exponents from -12 to 12, polynomial degree at most 12. Over-limit input is preserved in the editor; checking pauses. A supported function name does not guarantee every domain or expression can be proved. Unknown checks request clarification rather than guess.

All mathematical operations run locally. No API keys, paid services, or external AI calls. Equation previews do not establish mathematical correctness. Feedback is cleared when working changes.

## Local drafts and New question

Your current question, topic, and numbered working are saved automatically when you press Enter or leave an edited field. **Before refreshing or closing, finish editing and look for “Saved on this device.”** Text still actively being typed may not yet have reached the local app. Restore happens when you return, including after restarting the server. Feedback and practice results are not restored; recheck the saved working.

The normal Windows save is `%LOCALAPPDATA%\WorkCheck\draft.json`. It contains one current draft; use one editing tab at a time. There are no accounts or cloud sync. The file is outside the Git repository. Tests use isolated temporary files via `WORKCHECK_DRAFT_PATH` and do not touch your real draft.

**New question** asks before clearing a nonempty question or working. **Cancel** keeps the draft. **Clear question and working** saves an empty draft before clearing the screen; old working will not return on refresh. If that save fails, the visible working stays intact and an error is shown. Empty drafts can reset without a confirmation prompt.

A missing save starts normally. A damaged or incompatible save is preserved as `draft.damaged-<id>.json` beside the save, with a recovery message and fresh editor. Save failures keep the working in memory and offer **Retry saving**. Do not close until saving succeeds if you need the current edits to survive. Computational input limits never truncate stored text. An 8 MiB save-file safety limit reports a save failure for an oversized draft rather than truncating it.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

See devpost/validation.md for actual verification results. Full offline browser verification is scheduled for the final build stage; do not infer it from architecture alone.
