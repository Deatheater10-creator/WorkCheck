# WorkCheck code walkthrough

This is a source-based walkthrough of a tested action. It is a reference you can follow in VS Code; it does not claim that you have performed a new hands-on exercise or learned the code already. The companion [app map](app-map.html) works offline.

## The pieces in plain language

**Python** is the language the instructions are written in. A **function** is a named set of instructions; a **module** is a Python file containing related instructions.

**Streamlit** is the interface framework: it creates fields, buttons and equation displays in your browser. Clicking a control reruns the interface code, while session state remembers the current screen's data. **SymPy** is the symbolic maths library: it manipulates expressions exactly. WorkCheck adds its own rules for checking steps; SymPy alone does not decide that unfinished work is wrong.

A **worker** is a separate Python process used for bounded calculations. **JSON** is the plain-text format used for the saved draft. **CSS** controls colours and animations. None of these needs an AI service at runtime.

## One familiar action, three stops

Use Differentiation, question `f(x) = x^2 sin(x)`, and one working line `f'(x) = 2x cos(x)`. Click **Check working**. The expected result is **First mistake, line 1**. The correct derivative is the sum of two terms: 2x sin(x) + x² cos(x).

### 1. Read the input and protect the draft

Open [workcheck/ui.py](../workcheck/ui.py) and search for `def main` and `if st.button("Check working"`. The interface reads the question, topic and ordered lines, clears old teaching results, and calls:

```python
result = run_check(question, lines, topic=st.session_state.topic)
```

`questions.py::interpret_question` recognises the supported sentence forms; sentence interpretations need confirmation. `parser.py::question_expression` and `parse_step` turn supported notation into expressions using a restricted syntax tree, without evaluating arbitrary Python. The question and working use the same notation rules. A preview checks notation, not mathematical correctness.

Also find `invalidate` and `save_current` in `ui.py`. Edits increase a revision number and clear old feedback, practice and reveal progress. `storage.py::DraftStore` saves only the question, topic and ordered raw working in `%LOCALAPPDATA%\WorkCheck\draft.json`. It does not save verdicts or practice answers. Restoration therefore brings back your attempt and requires a fresh check.

### 2. Decide what the working means and check it

Open [workcheck/differentiation.py](../workcheck/differentiation.py) and search for `check_differentiation`. The route is `worker.py::run_check` → `checking.py::check_working` → the selected topic checker. The separate worker bounds the calculation; it does not call a remote service.

The differentiation checker compares a derivative line with the required derivative and an original-function line with the original function. It checks the allowed x values as well. `verification.py::verify` tries exact algebraic equality. One exact counterexample can disprove equality; agreement at a few numbers cannot prove it.

For this example, the line is mathematically wrong, and `_mistake_explanation` recognises the specific product-of-derivatives result. The correction names the actual parts, x² and sin(x), and says to differentiate one while keeping the other unchanged, then add the two terms.

The status rules are separate from the calculation. A valid line still containing `D(...)` is unfinished; an equivalent completed derivative can be a final answer. The first incorrect or unclear line blocks dependent later lines. If proof is unavailable, the result asks for clarification rather than guessing.

For partial fractions, the corresponding file is `partial_fractions.py`. `_setup` establishes which fraction uses A or B; `_coefficient_equation` checks subsequent equations in that context. This is why A+B=0 needs the original question and an earlier A/B setup, and why swapped labels can still be valid.

### 3. Teach, verify and display

Return to [workcheck/ui.py](../workcheck/ui.py) and search for `show_result` and `show_learning`. They display the verdict, correction, concept, final answer, working, separate example and three practice problems. `show_worked_steps` controls progressive reveals; it never changes an equation or a verdict.

The teaching data comes from `worker.py::run_learning` and `practice.py::build_learning`. Authored templates propose examples and exercises. `verify_candidate` checks the answers, and the solution builders in `presentation.py` verify the mathematical transformations before the item is displayed. A full set needs one distinct example and exactly three distinct practice problems. If that cannot be verified, the app reports it instead of showing unchecked filler.

`explanations.py::NOTES` holds concept wording. `presentation.py::school_latex` formats actual expressions as readable maths. `styles.css` handles local fades, button feedback and reduced-motion preferences. Practice answers stay hidden behind independent controls; there is no automatic grading of practice attempts.

## Where to start when changing something

| Desired change | Start here | What establishes it still works |
| --- | --- | --- |
| Concept wording | `workcheck/explanations.py::NOTES` | Teaching/presentation tests; inspect the actual rendered lesson |
| Explanation beside a mathematical change | `workcheck/presentation.py::_derivative_rule` or `coefficient_solution` | Exact worked-equation fixtures in `tests/test_presentation.py` |
| Fields, labels or reveal controls | `workcheck/ui.py::main`, `show_worked_steps`, `clear_learning` | `tests/test_ui.py`, then a browser check |
| First-error decisions | `differentiation.py` or `partial_fractions.py` | Topic tests, equivalent answers, unfinished steps and uncertainty cases |
| Local restoration/reset | `ui.py::invalidate` and `storage.py::DraftStore` | Storage/UI restoration, Cancel and confirmed-reset tests |
| Ordinary multiplication | `parser.py::_normalize_multiplication` | Parser safety tests and `tests/test_ordinary_notation.py` |

An optional small edit is to change only the explanatory sentence under a concept in `NOTES`, leaving its formula unchanged. Refresh and check again to see it. This is offered, not performed; no edit or response is required. A kept edit should be checked and committed separately.

## A practice to reuse

Turn a requirement into a concrete input and expected result before asking an agent to change code. WorkCheck's ordinary-notation fixtures cover `3x^2 sin(2x)` and function labels, while the original product-rule mistake checks first-error feedback. See `tests/test_ordinary_notation.py`, `tests/test_differentiation.py` and the approved PRD's Checking and Feedback section. On another project, the same habit helps distinguish a real fix from a convincing explanation.

The Windows worker-startup repair is another example: move the UI import inside `app.py`'s `if __name__ == "__main__"` guard. A spawned maths process reimports the entry file under another name, so it now avoids loading Streamlit. `tests/test_worker.py::test_spawn_entrypoint_does_not_import_the_interface` checks that boundary without extending the maths deadline.

Optional reflection: what would you do differently next time you start a project with an AI coding assistant? No answer is needed to use this guide, and this guide does not supply a personal reflection or submission answer.

## Run again

From the WorkCheck folder in PowerShell, after installing the pinned dependencies:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8501. Keep the terminal open; Ctrl+C stops the app. See [README.md](../README.md) for the exact first-time setup and troubleshooting. This walkthrough is a snapshot; the app map records the source commit.
