# WorkCheck

A local engineering-maths learning tool. **Stages 1-4:** differentiation and context-aware partial-fraction step checking, an editable numbered workspace, local draft saving/restoration, and confirmed reset. Verified working for the current question, concept explanations, a separate worked example and three targeted practice questions are available. Stage 4 passed learner hands-on review.

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

## Try partial fractions

Select **Partial fractions** and enter `1/((x+1)*(x+2))` as the question. Add one step per line:

```text
A/(x+1)+B/(x+2)
1=A*(x+2)+B*(x+1)
A+B=0
2*A+B=1
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

See devpost/validation.md for actual verification results. Full offline browser verification is scheduled for the final build stage; do not infer it from architecture alone.


Worked-solution refinement: render actual mathematical equations with a short explanation beside every transformation. Partial fractions include expansion, collection, coefficient comparison, elimination, back-substitution, and the original-to-final equality using the question's actual coefficients. Differentiation shows explicit derivative transformations for the supported sum, product, integer power, chain, sine, cosine, exponential, and logarithm rules. Verify generated transformations symbolically before display; never change the working checker's acceptance rules. Stage 3 was accepted by the learner after review.


## Learn and practise

Check a supported question, with or without an attempt. Read the first-error or method feedback, then **Understand the concept** before the worked solutions and the separate **Worked example**. Three distinct practice problems follow, selected for the main method (product, chain, powers, sine/cosine, exponential, logarithm, or restricted partial fractions). Supporting rules used by the example are explained too.

Each practice problem has its own **Reveal answer and worked solution** toggle, initially off. Revealing one does not reveal the others. Answers and complete worked transformations use rendered maths and retain each problem's real-domain restrictions. There is no automatic grading of practice attempts.

All generation and verification run locally in a separate bounded job. Only complete verified sets are displayed: one example plus exactly three distinct practice problems, different from the current question. Small generated candidates fall back to a reverified hand-checked bank; if a full set cannot be verified, an explicit unavailable message preserves your checked answer. Check again to retry. Verified content can be cached in local app memory; failures are not cached. No API keys or external requests are used.

Changing the question, topic, or working (including adding, deleting or reordering lines), rechecking, or confirming New question clears previous practice and reveals. Cancelling New question preserves them. Draft restoration restores your input, not previous answers or reveals.
