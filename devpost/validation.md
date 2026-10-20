# WorkCheck Validation

## Stage 1 — Differentiation Step Checking

Status: mechanical verification and learner hands-on checks passed, including the revised appearance. Committed as 93ba8e4, `Add local differentiation step checker and editor`. No Git user identity was configured, so this checkpoint uses the explicitly labelled WorkCheck build agent <workcheck-build@localhost> author through command-scoped settings.

Appearance revision after initial learner feedback: added colourful header and topic cards, stronger step/button styling, clean white equation areas, verified/error icons and colours, blue explanation panel and labelled purple/amber upcoming learning panels. Reran the unchanged 48-test suite: **48 passed in 23.989 seconds**. Local health endpoint again returned `ok`; pip check again found no broken requirements. The learner's updated visual review remains pending; no commit was made. Maths checking modules were unchanged by this appearance revision.

Subsequent learner result: the revised appearance and stage-1 hands-on checks passed, and the checkpoint above was committed. The pending-review wording in the historical appearance entry describes the state before that confirmation.

Environment actually used: Windows, Python 3.12.0, SymPy 1.14.0, Streamlit 1.66.0. Direct versions are pinned in requirements.txt and the installed dependency set in requirements-lock.txt.

### Executed Checks

- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **48 tests passed** (22 differentiation, 12 parser, 9 exact-verification, 3 Streamlit AppTest interface, 2 spawned-worker tests).
- `.\.venv\Scripts\python.exe -m pip check`: no broken requirements found.
- `.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501`: server started on loopback.
- `http://127.0.0.1:8501/_stcore/health`: returned `ok`.
- `git diff --check`: no whitespace errors in tracked-file diffs (repository is new; files remain untracked until review/staging).
- Ignore checks confirm learner-profile.md, .env, .env.local, and .venv dependency files are excluded. No project files have been committed.

### Actual Mathematical Evidence

Hand-specified expected derivatives passed for x^2*(x+1), (x^2+1)^3, x^2*sin(x), exp(2*x), and ln(x^2+1). The learner's three-line product-rule attempt reports line 2 as the first mistake and does not check line 3.

Verified unfinished examples include the copied function, D(original function), the held product-rule sum, and a held chain-rule expression. They remain incomplete. A wrong held product of derivatives is rejected. Unsimplified but complete and expanded equivalent derivatives pass. Original-function statements are distinct from derivative claims.

Tests also passed for original-domain holes retained through cancellation, extra candidate holes requesting clarification, ln domain checks, exact decimal handling, symbolic counterexamples, and a polynomial engineered to agree at the finite sample points. Numerical agreement alone is never accepted as proof. Inconclusive domain handling requests clarification.

### Interface and Limits Evidence

Streamlit AppTest exercised entry, previews, checking, adding/deleting/reordering steps, and invalidation after edits/reordering. Over-limit question text stays intact in the editor and clears old feedback. A zero-deadline worker test verifies bounded stopping with input preserved. Unsafe/unsupported AST syntax, numeric/exponent/degree/character/node/depth limits, higher derivatives, and malformed equalities are tested.

### Not Yet Established

- Learner's visual/hands-on review is pending; automated AppTest is not a human browser review.
- Durable draft saving/recovery is stage 2. Stage 1 preserves raw edits in session memory only; closing/reloading may lose them.
- Partial-fraction checking, worked teaching examples, and verified three-item practice are later approved stages, not delivered features yet.
- Photo recognition has not been installed or benchmarked. It is not enabled.
- A cold real-browser journey with outbound network unavailable remains a stage 5 check; local architecture and AppTest do not alone establish it.
- These examples do not establish every combination in the planned function families or full curriculum correctness.

## Stage 2 — Local Autosave, Restore, and New Question

Status: 94 automated tests passed and learner explicitly confirmed all manual checks, including function notation, implicit multiplication, restoration, reordering, Cancel, and confirmed clearing. Ready to commit stage 2 and parser fixes. Historical pending-review entries below describe earlier states.

### Executed Checks

- Full command `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **75 tests passed in 32.214 seconds**, including the original mathematical regression cases and new storage/UI coverage.
- Live local server restarted with permission for the normal Windows AppData save path. Loopback health endpoint returned `ok`.
- `git diff --check`: passed. No stage-2 files have been staged or committed.

### Actual Storage and Interface Evidence

Fresh AppTest sessions restore question, topic, and reordered working from the same isolated file, simulating refresh and return after closure. Over-limit raw question/line text survives restoration without truncation. Cancellation leaves visible fields and saved bytes unchanged; confirmation saves an empty draft and a fresh session restores empty fields. Nonempty working requires confirmation even with an empty question; empty drafts reset without a prompt. Confirmed reset clears old feedback as well.

Tests cover missing files, truncated JSON, invalid encoding, excessive JSON numeric literals, incompatible schemas/types, duplicate line IDs, oversized files, unreadable files, failed atomic replacement, failed archival, failed reset, failed autosave and retry. Damaged originals are preserved under distinct recovery filenames. A failed reset leaves both current working and old save intact. Partial-fractions topic restoration does not invoke the differentiation checker; its checking remains disabled until stage 3.

Tests use temporary file overrides, not the student's real draft. The final real-browser refresh/close-and-return check is for the learner to perform next. A fresh automated app session is evidence for restoration logic, not proof of every browser close timing. Edits still actively being typed are not durable until Streamlit commits the field (Enter or leaving it); UI and README explicitly instruct waiting for the saved status.

No approved mathematical/teaching feature was deferred. Later slices remain pending. Full offline cold-browser verification remains scheduled for stage 5.

### Implicit-Coefficient Regression Repair

Learner reported that (2x + 3)^4 was rejected despite being in approved chain-rule coverage. The restricted parser now normalizes unambiguous numeric coefficients of x, in question/preview/working, without changing the saved raw text. Other products require explicit *. Ambiguous denominator/exponent adjacency requests clarification with examples; identifiers and scientific literals are not silently split.

Final full suite after this repair: **81 tests passed in 37.239 seconds**. New parser tests cover coefficients, decimal coefficients, explicit denominator grouping, ambiguity, and unsafe/unsupported identifiers. The maths regression establishes symbolically that d/dx[(2x+3)^4] = 8*(2*x+3)^3, accepts that answer, rejects an omitted inner factor, and accepts the held chain-rule step as valid but unfinished. AppTest verifies the user's exact input produces an equation preview and correct-final-answer feedback. Existing saving/restoration/reset tests continue to pass. Loopback health returned ok; diff whitespace check passed. Stage-2 hands-on review is still pending; no additional commit was made.

### Function-Definition Label Regression

Added requested f(x) question definitions and matching f'(x)/f′(x) working. The left side is metadata; only the right side enters the mathematical expression parser. y and bare-expression behavior remains supported. Single-letter named labels such as g(x) are supported; mismatched names, different independent variables, and higher derivatives request clarification. Valid named original-function and held derivative working remain intermediate, distinct from completion.

Final full suite: **90 tests passed in 46.922 seconds**. Tests combine function labels with implicit multiplication in all three requested inputs; verify exact derivatives against hand-specified mathematical expressions; check label display, valid unfinished/completed/incorrect named steps, earlier uncertainty blocking, bare expressions, and persistence of the raw labelled question. AppTest confirms question previews retain f(x), solver output displays f'(x), and labelled working previews/checks work. An initial test incorrectly demanded identical factoring in LaTeX; it was corrected to distinguish exact mathematical verification from display-label checks, accepting equivalent valid answer forms. All prior mathematical, autosave, restore, and reset checks pass. Server health returned ok and diff whitespace check passed. Stage 2 remains uncommitted pending learner hands-on approval.

### Follow-up Implicit Multiplication Repair

The learner continued to see rejection of (2x + 3)^4 and (x^2 - 5x)^3. Direct fresh-process parser/maths checks accepted the exact examples before this follow-up, so the discrepancy in the learner's browser was not conclusively reproduced. The running local server was inspected and restarted using the absolute WorkCheck app.py path to load the current files.

Coefficient-only regex normalization was replaced by token-based insertion of multiplication between recognized adjacent factors. Numeric coefficients, parenthesized factors, and spaced function products now share this normalization in question previews, solver questions, and working steps. Explicit multiplication and function-label support remain. Unknown names are not split; unsupported syntax and ambiguous adjacency are rejected before the existing restricted AST builder. No evaluation-based parser was added.

Full executed suite: **94 tests passed in 43.571 seconds**. Added checks for both bare expressions matching explicit-product inputs; expected derivatives 8*(2*x+3)^3 and 3*(x^2-5*x)^2*(2*x-5); valid original-function and held-derivative working; both inputs in actual fresh spawned maths workers; and both through the editor/preview/check path in AppTest. Existing safety, label, mathematical, autosave, restoration, and reset regression tests continue to pass.

These are automated results only. The learner has explicitly not confirmed stage-2 restoration or reset behavior. Those hands-on checks remain pending; stage 2 is unchecked and uncommitted, and stage 3 has not begun. All pending stage-2 files remain in the working tree. Restarting the app did not clear or replace the student's saved draft.
