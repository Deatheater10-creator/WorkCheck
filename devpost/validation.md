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

Status: 94 automated tests passed and learner explicitly confirmed all manual checks, including function notation, implicit multiplication, restoration, reordering, Cancel, and confirmed clearing. Committed as a744ae7, `Save local drafts and fix mathematical input notation`. Historical pending-review entries below describe earlier states.

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

Subsequent result: learner explicitly confirmed all stage-2 manual checks and authorized commit and progression. Commit a744ae7 records stage 2 and these parser repairs. The paragraph above records the earlier pending state, not current progress.

## Stage 3 — Context-Aware Partial-Fraction Checking

Status: mechanical verification passed; learner hands-on review pending. Stage 3 is uncommitted and its checklist box remains unchecked.

Executed `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **129 tests passed in 64.450 seconds**. This includes 32 focused partial-fraction tests, full regression coverage from earlier stages, topic-aware Streamlit AppTest interactions, and the complete seven-line PRD coefficient example in an actual fresh worker using the normal five-second deadline. Dependency consistency and diff whitespace checks passed. App restarted from the absolute workspace path; loopback health returned ok.

Actual mathematical coverage: valid setup, denominator clearing, exact coefficient constraints, coefficient values, valid unfinished systems, partial substitution, final sum, final equality in either direction, equivalent equation scaling/order, swapped A/B assignments, nonmonic/scaled denominators, root-substitution prefixes and separate root markers, and original-domain exclusions. An initial test caught a correct reversed final equality being classified incomplete; this was fixed before the final passing run.

Error/uncertainty cases: wrong coefficient relation, wrong value, wrong identity, and unambiguously wrong supported denominator factors identify the first error. Missing setup, unsupported nonlinear or rational coefficient equations, ambiguous changes of assignments, unsupported questions, and new domain holes request clarification without guessing. An earlier error or unknown blocks later dependent steps; a correct final answer does not erase an earlier error. A and B remain disallowed in differentiation inputs.

The interface now dispatches to the selected topic's local checker, previews coefficient equations, and displays decomposition answers without a derivative label. All stage-2 save/restore/reset tests remain passing. No feature was deferred and no external service or dependency was introduced. Worked teaching examples and revealable practice remain pending stage 4. Full offline cold-browser verification remains stage 5 work.

### Student-Facing Answer Presentation

Learner requested a display refinement during stage-3 review: positive fraction before negative, compact isolated exclusions, and the five-step coefficient method. Implemented a separate display module and display-only result fields; mathematical checker modules and verification decisions are unchanged. Raw answer/domain strings and step/status data remain available and are explicitly compared before/after presentation in tests. Previews omit redundant unit multipliers while preserving held derivative notation.

The reference result now displays 1/(x+1) - 1/(x+2), with x != -1, -2. The method shows A/(x+1)+B/(x+2); 1=A(x+2)+B(x+1); A+B=0 and 2A+B=1; A=1 and B=-1; and the final decomposition. The generated coefficient system, solved values, cleared identity, final identity, and relevant domain are verified exactly before displaying the method. Finite exclusions are compact; non-isolated restrictions retain inequalities or the full exact domain representation rather than dropping conditions.

Final full command: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **143 tests passed in 95.358 seconds**. Coverage includes positive/negative source ordering, isolated and cancelled domain holes, simple inequalities and complex domains, all five reference display steps, equivalent submitted answer orders, unchanged error/uncertainty/step outcomes, preview and result labels, visible worked solution, edit invalidation, and display failure/deadline fallback. An initial UI assertion was corrected to account for Streamlit's LaTeX wrappers; the final full suite passes. The worker delivers the original checked result before optional formatting, so a presentation failure or timeout cannot replace a completed mathematical verdict.

App restarted using the absolute workspace path and health endpoint returned ok. All stage-3 changes remain uncommitted and its learner review is pending. The requested coefficient-method explanation was brought forward; broader fresh examples and revealable practice remain stage-4 work.


## Detailed mathematical working revision

Implemented actual equations and an adjacent explanation for every transformation. The reference partial-fraction solution now includes all six requested sections, expansion and collection, both coefficient equations, explicit subtraction to eliminate B, back-substitution, the original-to-final equality, and compact restrictions. Generated coefficients and transformations use the actual question and are symbolically verified before display. Supported differentiation rules also show intermediate derivative transformations with reasons. The working checker and acceptance rules are preserved.

Executed `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **145 tests passed in 76.778 seconds**. Includes exact reference working, different/nonmonic/rational coefficients, a zero root, all supported derivative rule families, equivalent-answer acceptance, unchanged checking data, UI rendering and invalidation, autosave/reset, and worker failure/deadline regression coverage. `git diff --check` passed. Stage 3 remains uncommitted for learner review; no new manual review is claimed.


## School-style maths across student outputs

Replaced raw code echoes in feedback cards and worked notation examples with the same restricted-parser-to-LaTeX path used by previews. This displays the actual submitted equation (including mistaken working) without changing its checker status or saved text. Formatted the authored product-rule formula as inline maths. All supported expression rendering remains structural, not deletion of multiplication characters; numeric factors retain a visible dot. Typing fields and explicit input-syntax help retain the accepted syntax.

Full command `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **148 tests passed in 107.251 seconds**. Added exact formatting regressions for all requested expression forms and numeric multiplication, checks that rendering leaves internal expressions intact, and UI tests for both topics preserving raw draft/step data without code displays. Existing equivalent-answer, first-error, uncertainty, storage and worker tests pass. Diff whitespace checks pass. Restarted the loopback server; health returned ok. Stage 3 remains uncommitted; hands-on review pending.


## Stage 3 accepted

Learner confirmed that the worked steps and mathematical formatting are clear and acceptable, and explicitly requested committing the completed Stage 3 changes. Most recent executable verification remains 148 passing tests in 107.251 seconds; only documentation/progress records changed since that run. Stage 3 is complete. Stage 4 remains unstarted while its planned scope and acceptance checks are reported.


## Stage 4 - verified teaching and revealable practice (review pending)

Implemented authored concept explanations before mathematical working, a separate verified worked example, and exactly three distinct targeted exercises. Supported template families: product, integer powers/polynomials, chain, sine/cosine, exponential, natural logarithm, and restricted partial fractions. Include supporting concepts used by the example/exercises. Every displayed solution retains actual transformations and short reasons in school-style LaTeX with real-domain restrictions. Answer and full working are both hidden initially behind an individual toggle per exercise. Automatic practice grading is still deferred.

Verification checks candidate questions, optional supplied working, exact symbolic answers and domains. Partial-fraction answers must also be completed decompositions. Existing solution builders explicitly verify each derivative rule replacement and coefficient-method transformation. Invalid or unsupported candidates are rejected; distinctness is checked symbolically against the current question and other selected items. Six generated candidates per family and the five-entry hand-checked replacement bank are bounded. Reverify replacements; publish no incomplete practice set. Separate spawned learning jobs are limited to 20 seconds and preserve the checker verdict on failure. Verified packs may be cached in app memory; failures are not cached, so retry is possible. No new dependencies, external requests or paid services were added.

Executed `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **163 tests passed in 171.086 seconds**. Independent hand-calculated cases cover product/chain/trig/exponential/log derivatives and coefficient-method equations. All replacement fixtures are reverified. Tests reject a near-but-wrong answer, an answer with an additional hole, an incorrect intermediate despite a correct final answer, a deliberately corrupted derivative rule and an equivalent but unfinished partial-fraction answer. Tests cover replacement selection, duplicate/inadequate sets, unsupported questions, logarithm restrictions, original cancelled holes, three distinct targeted exercises and a different example, concept order, hidden/individual reveals, edits/structural changes/topic/reset invalidation, Cancel preservation, unavailable content preserving the verdict, and real worker/timeout paths. Earlier differentiation, partial-fraction, parser, autosave and reset regressions pass. The first UI-only run exposed a test selector calling startswith on an unkeyed button; the selector was corrected before the successful full run.

`pip check`: no broken requirements. `git diff --check`: passed. Restarted Streamlit at 127.0.0.1:8501; health returned ok. No claim of a manual visual review or final cold-browser offline verification is made; the latter remains Stage 5. Stage 4 remains unchecked and uncommitted for learner hands-on review.


### Stage 4 review - collapsible teaching panels
Concept explanation and the separate worked example now use independent Streamlit expanders, initially open. The relevant differentiation teaching-order/reveal/invalidation UI regression passed (1 test, 12.968 seconds); the partial-fraction presentation UI regression also passed. Diff whitespace checks pass. This is a presentation-only refinement; mathematical generation and checking are unchanged. Stage 4 remains uncommitted for hands-on review. Opening/closing the native browser expander remains part of the learner visual check.

Learner reported no visible change. Restarted the existing local server from the absolute app path to load updated modules; health returned ok. Also made the current-question Worked solution collapsible, alongside the concept explanation and separate Worked example. The teaching-order/reveal/invalidation UI test now asserts all three expanders are initially open and passed (1 test in 20.056 seconds). Learner should refresh and recheck to regenerate results. Stage 4 remains uncommitted.


## Stage 4 accepted

Learner confirmed Stage 4 now works correctly and passes hands-on review, and authorized committing it. Latest full suite: 163 tests passed in 171.086 seconds. After presentation-only collapsible-panel refinements, relevant differentiation and partial-fraction UI checks passed; the last differentiation teaching/reveal/invalidation run passed in 20.056 seconds. Server restart and loopback health were verified. No mathematical generation/checking changes followed the full suite. Stage 4 is complete. Automatic practice grading remains deferred. Stage 5 has not started; the next action is to report its saved scope and acceptance checks.
