---
doc: spec
status: approved
---

# WorkCheck — Technical Specification

## How This Works, In Plain Language
Streamlit supplies the screen: question field, numbered working lines, equation previews, and results below. Python runs on the student's computer. SymPy manipulates mathematical expressions; WorkCheck adds explicit rules to decide what a line means, whether it is valid, whether it finishes the task, or whether clarification is needed. There is no external AI call.

For example, for x^2*sin(x), the app recognizes a copied function separately from a claimed derivative. It verifies derivative expressions mathematically and identifies the student's multiplication of derivatives as the first error. A differently written but equivalent correct derivative is accepted.

The app saves the current draft to a local file. Practice uses local mathematical templates, with answers and worked steps verified before a problem is displayed. Each problem's solution starts hidden and can be revealed. After setup, these features work without internet. Photo recognition is a separate, unverified possibility, not a prerequisite for the typed version.

## The Core Journey Through the System
Implements `prd.md > The Core Journey`, `Typed Input`, and `Checking and Feedback`.
1. Load the last valid saved draft, or start empty with an appropriate recovery message.
2. Student selects the task, types the question, and edits numbered lines. Stable line IDs preserve the association between text and controls when lines move.
3. Commit each field edit to local storage; parse supported text to create equation previews. Preview never implies correctness.
4. On Check, send a snapshot to the local maths worker. Classify each line and verify it in order, retaining original domain restrictions and coefficient context.
5. Return explicit step statuses, completion information, first-error location if established, and clarification messages where needed.
6. Show results below the input in PRD order. Generate and verify a relevant worked example and exactly three practice items. Show hidden solution controls only for verified items.
7. Any question/topic/line edit invalidates previous results and revealed practice content. Recheck before showing results for the new snapshot.

## Stack
Learner approved Python, SymPy, and Streamlit. Routine details below are proposed implementation choices for review, not additional learner decisions.
- Python 3.12: installed interpreter observed at planning time (3.12.0). Use a supported patched 3.12 release for distribution. [Python virtual environments](https://docs.python.org/3.12/library/venv.html).
- SymPy: symbolic differentiation, polynomial algebra, rational normalization, coefficient equations, and equation rendering. Documentation currently identifies 1.14.0. [Calculus](https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html), [simplification and partial fractions](https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html).
- Streamlit: local browser interface and interaction controls. [Installation](https://docs.streamlit.io/get-started/installation/command-line), [session memory](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [equation display](https://docs.streamlit.io/develop/api-reference/text/st.latex), [expanders](https://docs.streamlit.io/develop/api-reference/layout/st.expander).
- Python standard library: restricted syntax parsing, JSON drafts, atomic file replacement, bounded worker processes, and unittest tests. No database or additional service.
- Resolve and pin exact compatible dependency versions during the first build setup; record direct versions in requirements.txt and the tested full environment in requirements-lock.txt. No dependency installation or application runtime compatibility test has occurred during this planning step.

## Where It Runs and How Someone Tries It
Local Windows process, browser at http://127.0.0.1:8501. Bind only to 127.0.0.1. No API keys, accounts, cloud database, hosting, or paid services. Loopback browser traffic stays on the same device.

Beginner Windows instructions to include in README (planned commands; files are created during build):
1. Install Python 3.12 if needed. Open this folder in VS Code and open a PowerShell terminal.
2. Create an isolated dependency folder:
   `py -3.12 -m venv .venv`
3. Install the tested dependencies while online:
   `.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt`
4. Start the app:
   `.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`
5. Open http://127.0.0.1:8501 if the browser does not open. Keep the terminal running. Stop with Ctrl+C. Repeat step 4 on later visits; do not reinstall each time.
6. Run tests with `.\.venv\Scripts\python.exe -m unittest discover -s tests`.

Using the explicit Python path avoids PowerShell activation-policy changes. Explain missing Python/launcher, dependency errors, and occupied port in README; if 8501 is occupied, use 8502 and open the matching address. Optional start.ps1 runs the same launch command; README command remains available.

Record the required short demo locally and provide the public GitHub repository; deployment remains optional. Demonstrate the student's product-rule mistake, a valid unfinished partial-fraction attempt, and a verified practice solution reveal. Prove offline operation after installation before submission. These are instructions to implement and verify, not claims that setup already works.

## Look and Feel
Implements `prd.md > Look and Feel` and `Screens and Layout`.
Use Streamlit theme configuration plus small local styles: background #F8FAFC, text/headings #14213D, primary accent #0F766E, white cards. Correct #15803D, first mistake #B91C1C, clarification #92400E, always accompanied by text and icons. Use installed/system font fallbacks, large equation displays, visible labels, and generous spacing. No remote fonts, CDN scripts, or images.

Keep question and ordered editable lines above results. Use Add step, Delete, Move up, and Move down controls; disable moves at boundaries. Use separate collapsed expanders labelled “Reveal answer and worked solution” for the three verified practice problems. Collapsed is a learning convenience, not a secrecy guarantee.

Stage-1 appearance revision requested by the learner: local styles in workcheck/styles.css add a navy/teal/blue header with a purple accent, blue product-rule and purple chain-rule topic cards, soft amber partial-fractions card, prominent gradient numbered badges and action buttons, blue-tinted explanation panels, and purple/amber worked-example/practice panels. Keep equation surfaces white with navy text and retain focus outlines. Red/green labels and icons indicate errors/verified steps only. Upcoming features are clearly labelled placeholders, not simulated behavior. All styling assets remain local.

## Components

### Interface and Draft Controller
Implements `prd.md > Typed Input`, `Screens and Layout`, and `States and Boundaries`.
Streamlit widgets edit a single canonical draft in session memory, initialized from disk once per session. Persist widget callbacks and structural edits immediately; show saved/error status truthfully. Text widgets commit on their normal blur/Enter event: explain that text still actively being typed is not durable until committed, and verify this interaction during build. Capture pending field edits before Check or New question. Each edit increments a revision; only show results whose revision matches.

“New question” asks for confirmation when the question or any working line contains non-whitespace text. Cancel preserves everything. Confirm atomically saves an empty draft and resets widgets, results, coefficient context, and practice reveal state. If reset cannot be saved, report the failure rather than imply the old draft cannot return. First build is one local draft for one app instance, not independent drafts per tab; document that concurrent editing in multiple tabs is unsupported.

### Restricted Maths Parser
Implements `prd.md > Typed Input` and `Supported Mathematics`.
Normalize ^ to exponentiation and recognize optional y= and dy/dx= prefixes before parsing. Split a single equality outside parentheses into two expressions for coefficient/identity lines. Parse Python expression syntax with ast.parse and recursively construct only approved SymPy objects. No eval, exec, direct sympify of student text, or parse_expr on untrusted strings. Reject attributes, indexing, arbitrary calls, comprehensions, unknown names, multiple equality chains, and malformed input with clarification.

Allow numeric constants as exact integers/rationals (convert finite decimal strings exactly), x, the four approved function names, + - * / powers, and parentheses. A and B exist only in partial-fraction working context; y and dy/dx are labels, not independent variables. exp(x) is the input notation for e^x. Retain both source structure and normalized expressions so cancellation cannot erase original exclusions.

Proposed practical bounds: 500 characters per line, 20 working lines, 150 syntax nodes per expression, nesting depth 12, numeric literals at most 8 digits, and integer power magnitude at most 12. Polynomial degree at most 12 in supported differentiation forms. Noninteger and variable exponents request clarification in this first grammar. Products and compositions of the agreed functions are allowed within these bounds; every stated example must pass. These are explicit proposed first-build limits, not mathematical invalidity judgments. Unsupported domain analysis also returns uncertainty rather than a wrong verdict.

### Symbolic Verifier and Domain Rules
Implements `prd.md > Checking and Feedback` and `Supported Mathematics`.
Represent verification as proved, disproved, or unknown, with reason and domain. Try exact polynomial/rational identities, then bounded algebraic/trigonometric transformations for supported expressions. Zero exact residual can establish equality only with compatible domain conditions; an unevaluated residual alone does not establish inequality. Establish false claims using exact nonzero polynomial/rational reasoning or a validated exact counterexample in the original domain. Numerical samples may help debugging, but numerical agreement is never proof and inconclusive numerical evidence cannot drive a verdict.

Retain denominator exclusions and require ln arguments > 0 in real-valued tasks. Do not introduce added restrictions or use log identities without proving their conditions. Candidate and source must agree on the relevant original domain. If preservation cannot be established by supported rules, return unknown and explain it. Use a local spawned worker with a bounded job duration (proposed 5 seconds per check or practice batch); terminate on timeout and return a limitation message without freezing the UI. No worker network calls.

### Ordered Step Checker
Implements `prd.md > Step Outcomes`, `Differentiation Step Checking`, and `Partial-Fraction Step Checking`.
Return each line's role, mathematical validity, completion flag, reason, and dependencies. Keep overall attempt status separate from a final expression's validity. Stop dependent checking at the first disproved or unresolved line; subsequent lines are “Not checked” with the blocking reason. This prevents claiming a later error is first. If an independently recognized final answer is inspected after a block, any statement about it must explicitly leave the preceding error/block intact; simpler first implementation stops at the block.

Differentiation: verify y= lines against the source function; derivative-labelled or unambiguously derivative-role expression lines against the exact derivative. Preserve unsimplified source to show the student's structure. A correct complete derivative is complete even if unsimplified; an original-function restatement is valid intermediate working, not completion. Accept equivalent forms and supported alternative methods. Support unfinished derivatives as specified under Approved Clarifications below; other unsupported notation requests clarification.

Partial fractions: validate proper rational input whose denominator has exactly two distinct rational linear factors after retaining exclusions. Bind A and B to the denominator terms from the student's decomposition setup; a setup introduces unknowns, it does not falsely assert equality for arbitrary A,B. Derive the exact coefficient constraints from the source and assigned terms. Check denominator clearing symbolically; compare coefficient constraints using exact linear algebra and check root-substitution equations under the corresponding substitution. Admit equivalent nonzero scaling, different equation order, and swapped A/B assignments. A relevant valid consequence of the constraints is intermediate, not necessarily enough to complete the problem. Missing setup/context requests clarification. Isolated values are not a final decomposition; a verified sum of resolved simple fractions is completion. A mere copy of the source fraction is not completion. Reject false constraints using the established exact system, without assuming the student's earlier false equations. Keep the x exclusions in output.

Feasibility evidence still needed: during build, run the PRD's complete coefficient example, swapped labels, root substitution, valid incomplete working, wrong constraint, and unresolved context before claiming this checker works. If those cannot be supported reliably, bring a concrete partial-fraction deferral proposal to the learner; no automatic scope reduction.

### Explanations and Worked Examples
Implements `prd.md > Explanation and Practice`.
Use authored, local rule explanations and structured worked-example templates, parameterized by parsed expressions. Recognize a misconception only when a rule supports it (for example, a claimed derivative equal to u'*v' instead of u'*v+u*v'). Otherwise explain the verified mismatch without inventing the student's reasoning. Begin with the first mistake when present. For valid unfinished work, explain what remains; for uncertainty explain the limitation first. Verify displayed mathematical transformations, not just final expressions.

### Practice Generator and Solution Verifier
Implements `prd.md > Explanation and Practice` and `Acceptance Evidence`.
Local bounded templates cover product rule, chain rule/common functions, and restricted partial fractions. Select three distinct, relevant problems using small exact coefficients. Each carries its question, concept, answer, structured worked steps, domain restrictions, and verification record.

Verify mathematical claims in every worked step and final answer using explicit rule checks plus symbolic verification, rather than trusting the generator or only comparing its final output. A derivative-rule step has a rule application to verify; coefficient steps use the same explicit context rules as student working. Test against independent, hand-checked expected cases so using shared verification code does not become the only evidence.

Verify the full three-item set before displaying it; solutions start collapsed. Retry a bounded number of candidates and fall back to stored, hand-checked templates that are reverified locally. If three verified items cannot be produced, show an honest practice-unavailable message, not unchecked or duplicated filler. Such a failure does not meet the exactly-three acceptance requirement. Reveal answer and worked solution per item; no automatic practice grading. Regenerated practice resets reveals and verification records.

### Local Draft Store
Implements `prd.md > States and Boundaries`.
Proposed path: %LOCALAPPDATA%\WorkCheck\draft.json, falling back to the user's home AppData/Local path if needed. Store schema version, topic, question string, ordered line IDs/text, and revision. JSON only; no serialized Python objects. No photos, computed verdicts, practice answers, or reveal state need persistence.

Write UTF-8 to a temporary sibling file, flush, then replace atomically. A missing file is normal first use. Validate schema/types/size on load. For damaged or incompatible files, retain a recoverable copy when possible, show a readable warning, and open a fresh in-memory draft; do not crash or silently overwrite the only damaged original. Permission/disk errors leave current working usable in memory and clearly warn that it is not saved; offer retry. New question must clear the durable draft on confirmed reset. No accounts, cloud sync, shared history, or transmission of draft text.

### Conditional Photo Recognition
Implements `prd.md > Photo Input and Confirmation` and `Feasibility and Priority`.
Documentation investigation: [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) converts formula images to LaTeX and downloads checkpoints; its docs caution that output needs checking. This does not demonstrate reliable extraction of a handwritten question plus ordered working. [Texify](https://github.com/VikParuchuri/texify) supports mathematical text but its repository now marks it deprecated and points to Surya. No candidate has been installed, benchmarked on this device, or verified for the PRD's photo workflow.

Keep OCR dependencies out of the required environment and no enabled recognition UI in the typed baseline. A separate optional investigation must verify Windows/CPU compatibility, checkpoint licence and size, local-only inference after an explicit setup download, representative handwritten question-plus-working images, preserved line order, expression conversion into the restricted grammar, and editable confirmation before checking. Log actual transcription errors and limitations. Do not use external AI APIs or silently fetch model files at runtime. If not demonstrated practical, record photo recognition as deferred under the already approved typed-only fallback. Never label a photo preview or manual transcription as automatic recognition.

## Data Model
- Draft: schema_version, topic, question, lines[{id,text}], revision. Disk plus active session copy; edits persist and restore on next launch.
- CheckResult: source_revision, overall_status, steps[{id,role,validity,completion,reason}], first_error_id, blocked_at, answer, domain, explanation. Memory only; discard on edit/restart.
- PracticeItem: problem, concept, answer, worked_steps, domain, verified; memory only, tied to the result revision. Reveal state per item is temporary.
- Coefficient context: source rational expression, original exclusions, A/B denominator assignments, exact constraints, verified prior steps. Memory within a check; rebuild after changes, never reuse stale assignments.
- Optional image/transcription: memory only; any edit clears confirmation. No image persistence promised.

## File Structure
```text
WorkCheck/
  app.py                      # Streamlit composition and local entry point
  workcheck/
    __init__.py
    ui.py                     # editor, feedback, reveals, confirmation
    models.py                 # draft, line, verdict and practice records
    parser.py                 # restricted grammar and role labels
    verification.py           # exact identities and domain checks
    checking.py               # ordered outcomes and blocking rules
    differentiation.py        # derivative role checks and rule forms
    partial_fractions.py      # coefficient context and step checks
    explanations.py           # local concept text and worked examples
    practice.py               # three verified items and fallback bank
    storage.py                # validated JSON load/save/recovery
    worker.py                 # bounded local maths jobs
  tests/
    test_parser.py
    test_verification.py
    test_differentiation.py
    test_partial_fractions.py
    test_checking.py
    test_practice.py
    test_storage.py
  .streamlit/config.toml      # local bind, no telemetry, palette
  requirements.txt           # pinned direct runtime dependencies
  requirements-lock.txt      # tested complete dependency set
  start.ps1                  # optional Windows launch helper
  README.md                  # Windows setup/run/test and supported notation
  devpost/
    learner-profile.md       # ignored personal learning context
    scope.md
    prd.md
    spec.md
    validation.md            # actual results, created during build
    photo-feasibility.md     # research and optional benchmark outcomes
```
No optional OCR module is required until a candidate passes feasibility. Keep generated environments, local drafts, and downloaded checkpoints out of commits.

## External Services and Dependencies
No runtime external services, endpoints, auth keys, rate limits, or paid usage. Dependency installation uses package downloads during setup only. Serve browser assets locally; disable Streamlit usage telemetry with browser.gatherUsageStats=false and remote font sources. [Configuration reference](https://docs.streamlit.io/develop/api-reference/configuration/config.toml). Verify offline behavior instead of assuming that a local Python process alone guarantees it.

## Verification Plan
Implements `prd.md > Acceptance Evidence`; tests are necessary for the mathematical core.
- Exact expected derivative cases cover all five PRD examples, equivalent expanded/factored and unsimplified answers, and the learner's first-error example.
- Test all four outcome distinctions; correct final after earlier error cannot clear it; earlier unresolved line blocks a later first-error claim; reordering changes checking order and invalidates results.
- Partial-fraction tests cover contextual setups, clearing denominators, coefficient equations, assigned values, final form, alternative label assignment and root substitution, incomplete valid work, and incorrect/unsupported steps.
- Domain tests retain original holes after cancellation, reject unproved log/domain transformations, and return unknown where proof is unavailable. Numerical near-equality alone never passes.
- Practice tests verify three distinct items, every worked step and answer, rejection of deliberately wrong answers/steps, verified replacement, failure message, and hidden/reveal interactions.
- Persistence tests cover missing/truncated/wrong-schema files, write failure, round-trip ordered lines, restart restoration, and confirmed reset. UI walkthrough checks editing, preview, add/delete/reorder, reset cancel/confirm, stale-result clearing, and committed-field saving.
- Runtime check with outbound network unavailable: cold browser load, equation rendering, draft restore, maths check, examples, and practice reveal. No runtime dependency or checkpoint download. Confirm loopback-only binding and telemetry disabled.
- Run tests after relevant build steps and record actual outcomes and exact tested versions/forms in devpost/validation.md. Manual screen checks supplement tests; planning-time claims do not count as validation.

## Important Failure Modes
- Invalid, ambiguous, unsupported, or overly complex maths: explain the specific limitation and request clarification. Preserve the student's draft.
- Inconclusive symbolic proof/domain or worker timeout: report unknown, never guess correctness or continue a dependent first-error claim.
- Missing/corrupt/unwritable draft: first-use or recovery message with usable in-memory editor; never falsely claim autosave succeeded.
- Failed practice verification: verified replacement or clear unavailability, never expose unverified solutions.
- OCR absent/unreliable: use the approved typed path and clearly state photo recognition is deferred.

## What Was Simplified and Why
One current local draft instead of accounts or cloud sync; explicit numbered expressions instead of arbitrary prose interpretation; locally authored teaching templates instead of AI output; conditional OCR instead of a runtime dependency on unproven handwriting recognition. None replaces real mathematical verification or first-error checking. Automatic practice grading remains deferred; verified revealable solutions are required.

## Decisions and Open Issues
- Learner chose Python/SymPy/Streamlit and offline operation after setup, local draft recovery, explicit validity/completion/uncertainty rules, and no numerical-agreement proof.
- Learner wants to understand frameworks. Concrete division: Streamlit builds the interactive screen; SymPy performs algebra; WorkCheck's Python rules supply educational judgments. No additional framework is needed.
- A genuine uncertainty was whether handwritten question-plus-working extraction can work locally. Documentation research did not establish feasibility; optional testing above defines the evidence required. Typed fallback is already authorized.
- Partial-fraction context checks are designed but not executed. Preserve topic coverage unless evidence requires a learner-approved deferral proposal.
- Proposed practical grammar/resource limits, one-instance draft semantics, and local save location need review as part of this spec. Exact dependency pins and offline asset behavior need verification at setup/build, not invented version claims.
- This is larger than a trivial 2–4-hour calculator: ordered checking, domains, coefficient context, verified teaching content, and recovery all add work. Prioritize a complete differentiation slice and required verification; report any schedule pressure and seek agreement before cutting agreed behavior.
- Learner approved this specification with the clarifications below. Stage 1 subsequently installed SymPy 1.14.0 and Streamlit 1.66.0 on Python 3.12.0 and ran 48 passing tests; see devpost/validation.md for actual evidence and remaining gaps. No OCR benchmark has been run.

## Approved Clarifications

### Unfinished Derivative Notation
`D(expression)` denotes the unevaluated derivative with respect to x. The restricted parser constructs held SymPy Derivative objects, never arbitrary calls. For y=x^2*sin(x), `dy/dx = D(x^2*sin(x))` and `dy/dx = D(x^2)*sin(x) + x^2*D(sin(x))` are valid unfinished lines; `dy/dx = 2*x*sin(x) + x^2*cos(x)` is complete. Also support `D(source) = expression` as a derivative-role equality when its left side refers to the requested derivative. Evaluate held derivatives only for mathematical verification, retaining the raw structure for completion detection. Remaining D nodes mean unfinished; they do not by themselves establish validity. A mathematically false unfinished line is incorrect. Unsupported notation asks for clarification. Add tests for these distinctions and incorrect held product-rule expressions.

### Feedback Invalidation
On question, topic, or working edits, clear or visibly invalidate all prior feedback, final answers, examples, practice questions, and reveals. Increment the draft revision and discard late worker responses for old revisions. Invalid and over-limit edits must invalidate results too. Test both editing and reordering.

### Nondestructive Input Limits
Show the configured limits in plain language beside the input/help controls. If exceeded, retain and locally save raw input without truncation, identify the exceeded limit, and suspend affected checking/previews until corrected. Computational limits must not be destructive storage or edit limits. Test over-limit draft round trips, clear feedback, and resumption after correction. Handle oversized/damaged save files with a recovery message and preserve recoverable originals.
