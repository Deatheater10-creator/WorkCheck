# WorkCheck

A local engineering-maths learning tool. **Stage 1:** differentiation step checking and an editable numbered workspace. Other approved features are not implemented yet.

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

## Supported notation and limits

Use explicit multiplication, parentheses, integer powers, `sin`, `cos`, `exp`, and `ln` in one real variable x. `exp(2*x)` means e to the power 2x. Use ordinary exact numeric literals, not scientific notation.

Limits: 500 characters per question/line, 20 working lines, 150 syntax nodes per expression, nesting depth 12, numbers up to 8 digits, integer exponents from -12 to 12, polynomial degree at most 12. Over-limit input is preserved in the editor; checking pauses. A supported function name does not guarantee every domain or expression can be proved. Unknown checks request clarification rather than guess.

All mathematical operations run locally. No API keys, paid services, or external AI calls. Stage 1 has no durable draft saving: closing/reloading may lose working until stage 2 is complete. Equation previews do not establish mathematical correctness. Feedback is cleared when working changes.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

See devpost/validation.md for actual verification results. Full offline browser verification is scheduled for the final build stage; do not infer it from architecture alone.
