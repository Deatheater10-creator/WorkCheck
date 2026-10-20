---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn. Concise explanations before each hands-on check; wait for learner feedback before committing and continuing.

## Slices

- [x] **1. Check differentiation working and find the first mistake**
  Becomes usable: A local editor with numbered steps, equation previews, and valid-intermediate/completed/incorrect/uncertain feedback.
  Why now: Delivers the core feature first, including setup rather than separate scaffolding.
  PRD ref: `prd.md > Typed Input`, `Differentiation Step Checking`, `Step Outcomes`
  Spec ref: `spec.md > Restricted Maths Parser`, `Symbolic Verifier and Domain Rules`, `Ordered Step Checker`, `Approved Clarifications`, `Look and Feel`
  Build: Install and pin dependencies, configure local-only Streamlit, implement restricted parser and bounded worker, differentiation checks including held D(...) notation, numbered add/edit/delete/reorder controls, previews, results below input, clear nondestructive limits, and stale-result invalidation. Mark practice/persistence as not yet implemented until their slices land.
  Verify (mechanical): Run unittest cases for all five PRD expressions, held valid/unfinished vs completed derivatives, the learner's product-rule mistake, equivalent methods, domain uncertainty, timeout, correct-final-after-error, unresolved-earlier blocking, and limits preserving raw input. Use Streamlit AppTest for check/editor/reorder/stale feedback; launch server and check readiness.
  Learner check: Check x^2*sin(x) with the original mistaken working, then valid unfinished D(...) working and a completed derivative. Edit a line and inspect cleared results; report confusing or incorrect behavior.
  Commit: `Add local differentiation step checker and editor`

- [ ] **2. Restore saved drafts and safely start a new question**
  Becomes usable: Question, topic, and ordered lines survive restarting; confirmed reset clears the saved draft too.
  Why now: Protects student work before adding topics.
  PRD ref: `prd.md > States and Boundaries`, `Acceptance Evidence`
  Spec ref: `spec.md > Local Draft Store`, `Interface and Draft Controller`, `Approved Clarifications`
  Build: Atomic validated JSON save/restore, missing/damaged-file recovery, save-error messages, reset confirmation/cancel, and preservation of raw over-limit drafts.
  Verify (mechanical): Run storage missing/corrupt/schema/write-failure/round-trip/reset tests and UI restore/reset/cancel tests. Verify reordered and over-limit drafts restore without truncation; rerun affected maths tests.
  Learner check: Edit/reorder lines, restart and inspect restoration. Cancel New question, then confirm and restart to check the old draft stays cleared.
  Commit: `Save local drafts and recover safely`

- [ ] **3. Check partial-fraction reasoning in context**
  Becomes usable: Verify setups, coefficient equations, root-substitution equations, coefficient values, and final decompositions without penalizing valid unfinished work.
  Why now: Addresses the next mathematical risk after differentiation is usable.
  PRD ref: `prd.md > Partial-Fraction Step Checking`, `Feasibility and Priority`
  Spec ref: `spec.md > Ordered Step Checker`, `Symbolic Verifier and Domain Rules`
  Build: Restricted rational-input validation, A/B denominator assignments, contextual equations, equivalent methods, completion detection, exclusions, and clarification on missing context. Request approval before any deferral if reliable support proves infeasible.
  Verify (mechanical): Run PRD coefficient example, valid incomplete and wrong equations, scaled/reordered constraints, swapped labels, root substitution, missing context, blocked dependencies, final form, and domain-hole tests. Test UI topic switching and run maths regressions.
  Learner check: Enter 1/((x+1)*(x+2)), assign A/B terms and add A+B=0; inspect valid/incomplete status. Complete it, then introduce a wrong equation and inspect first-error feedback.
  Commit: `Check contextual partial-fraction working`

- [ ] **4. Learn with verified examples and revealable practice solutions**
  Becomes usable: Explanations and a worked example followed by three distinct targeted problems with initially hidden verified answers and worked solutions.
  Why now: Teaching builds on proven mathematical checks.
  PRD ref: `prd.md > Explanation and Practice`, `Acceptance Evidence`
  Spec ref: `spec.md > Explanations and Worked Examples`, `Practice Generator and Solution Verifier`
  Build: Local templates, evidence-based mistake explanations, verified examples and three-item practice batches, verified replacement bank, per-item reveals, and practice invalidation. Defer automatic practice grading as agreed.
  Verify (mechanical): Run independent hand-checked fixtures across topics; verify every solution step/answer, deliberately invalid fixture rejection, replacement/unavailable paths, three distinct relevant problems, initially hidden/reveal behavior, and edit invalidation. Run full suite.
  Learner check: Trigger a product-rule mistake, read explanation/example, inspect three practice questions and reveal each solution. Edit input and verify old practice disappears.
  Commit: `Add verified teaching and revealable practice`

- [ ] **5. Verify offline use and document actual coverage**
  Becomes usable: Documented Windows launch, actual coverage/results, and honest photo recognition status.
  Why now: Validates the integrated journey before submission claims.
  PRD ref: `prd.md > Photo Input and Confirmation`, `Acceptance Evidence`
  Spec ref: `spec.md > Conditional Photo Recognition`, `Verification Plan`, `Where It Runs and How Someone Tries It`
  Build: Windows README/launch helper, tested dependency lock, validation report, and separate photo-feasibility findings. Enable recognition only if local extraction and confirmation workflow is demonstrated; otherwise explicitly document the approved typed fallback. No other feature deferral without approval.
  Verify (mechanical): Run full suite and documented launch; check core journey in a cold browser without outbound network after setup, local assets/telemetry/binding, recovery, limits, and practice reveals. Record actual results and versions. Never claim photo recognition passes without representative local evidence.
  Learner check: Follow Windows instructions and explore the whole app, including awkward inputs, restored drafts, and practice reveals. Report issues for final revision.
  Commit: `Document and verify offline WorkCheck demo`

## Hands-on Checkpoints

Stage 1 complete: 48 automated checks passed, revised appearance passed learner hands-on review, and commit 93ba8e4 records the checkpoint. Stage 2 is in progress. Details: devpost/validation.md.

Stage 2 learner review passed: learner explicitly confirmed function notation, implicit multiplication, restoration, reordering, Cancel, and confirmed clearing. Mechanical verification: 94 passing tests. Ready for the stage-2 checkpoint including parser repairs.

- [x] Early usable behavior explored — learner confirmed stage 1 passed hands-on checks after the appearance revision
- [ ] Final kick-the-tires exploration and feedback completed — after slice 5

Learn mode includes each slice's learner check. Fast mode pauses at these planned checkpoints and at consequential plan changes.

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — trace a check through interface, checker, and verifier
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: not yet performed.
Route and stops: identify actual code locations after final revisions.
Edit outcome: not yet offered.
Reflection: not yet offered; personal responses belong in ignored profile.
Activity mode: planned live app and editor.

## Revisions

- Learner reported continued rejection of ordinary implicit products. Fresh direct tests accepted both examples before this follow-up, so a live-session cause was not conclusively established. Replaced the coefficient-only regex with token-based normalization for recognized adjacent factors, added both bare-input UI/worker regressions, and restarted the app from its absolute workspace path. Preserve all pending stage-2 changes. Restoration/reset hands-on checks remain explicitly unconfirmed; stage 2 stays unchecked and uncommitted. Stage 3 has not started.

- Learner requested f(x) definitions alongside y and bare expressions, including implicit coefficients. Added shared label parsing, matching prime-labelled derivative working, labelled previews/results, mismatch clarification, and regression tests. Stage-2 learner review is still pending; no mathematical topic or approved feature was deferred.

- Learner reported rejection of (2x + 3)^4 during stage-2 review. Added restricted implicit numeric-coefficient multiplication for x, visible * guidance, ambiguity rejection, and parser/maths/UI regression coverage. This repairs input handling within approved chain-rule coverage; stage-2 hands-on review remains pending.

- Stage-1 hands-on feedback requested a more colourful interface. Added local-only header/topic/step/button styles and tinted learning panels while preserving checking behavior. Updated PRD/spec visual direction. Examples/practice remain labelled as upcoming until their approved implementation stage. Await a second learner visual review before the stage-1 commit.
