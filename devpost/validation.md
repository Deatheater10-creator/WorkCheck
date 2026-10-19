# WorkCheck Validation

## Stage 1 — Differentiation Step Checking

Status: mechanical verification passed and learner explicitly confirmed stage 1 passed hands-on checks, including the revised appearance. Ready for the stage-1 commit.

Appearance revision after initial learner feedback: added colourful header and topic cards, stronger step/button styling, clean white equation areas, verified/error icons and colours, blue explanation panel and labelled purple/amber upcoming learning panels. Reran the unchanged 48-test suite: **48 passed in 23.989 seconds**. Local health endpoint again returned `ok`; pip check again found no broken requirements. The learner's updated visual review remains pending; no commit was made. Maths checking modules were unchanged by this appearance revision.

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
