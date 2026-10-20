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

- [x] **2. Restore saved drafts and safely start a new question**
  Becomes usable: Question, topic, and ordered lines survive restarting; confirmed reset clears the saved draft too.
  Why now: Protects student work before adding topics.
  PRD ref: `prd.md > States and Boundaries`, `Acceptance Evidence`
  Spec ref: `spec.md > Local Draft Store`, `Interface and Draft Controller`, `Approved Clarifications`
  Build: Atomic validated JSON save/restore, missing/damaged-file recovery, save-error messages, reset confirmation/cancel, and preservation of raw over-limit drafts.
  Verify (mechanical): Run storage missing/corrupt/schema/write-failure/round-trip/reset tests and UI restore/reset/cancel tests. Verify reordered and over-limit drafts restore without truncation; rerun affected maths tests.
  Learner check: Edit/reorder lines, restart and inspect restoration. Cancel New question, then confirm and restart to check the old draft stays cleared.
  Commit: `Save local drafts and recover safely`

- [x] **3. Check partial-fraction reasoning in context**
  Becomes usable: Verify setups, coefficient equations, root-substitution equations, coefficient values, and final decompositions without penalizing valid unfinished work.
  Why now: Addresses the next mathematical risk after differentiation is usable.
  PRD ref: `prd.md > Partial-Fraction Step Checking`, `Feasibility and Priority`
  Spec ref: `spec.md > Ordered Step Checker`, `Symbolic Verifier and Domain Rules`
  Build: Restricted rational-input validation, A/B denominator assignments, contextual equations, equivalent methods, completion detection, exclusions, and clarification on missing context. Request approval before any deferral if reliable support proves infeasible.
  Verify (mechanical): Run PRD coefficient example, valid incomplete and wrong equations, scaled/reordered constraints, swapped labels, root substitution, missing context, blocked dependencies, final form, and domain-hole tests. Test UI topic switching and run maths regressions.
  Learner check: Enter 1/((x+1)*(x+2)), assign A/B terms and add A+B=0; inspect valid/incomplete status. Complete it, then introduce a wrong equation and inspect first-error feedback.
  Commit: `Check contextual partial-fraction working`

- [x] **4. Learn with verified examples and revealable practice solutions**
  Becomes usable: Explanations and a worked example followed by three distinct targeted problems with initially hidden verified answers and worked solutions.
  Why now: Teaching builds on proven mathematical checks.
  PRD ref: `prd.md > Explanation and Practice`, `Acceptance Evidence`
  Spec ref: `spec.md > Explanations and Worked Examples`, `Practice Generator and Solution Verifier`
  Build: Local templates, evidence-based mistake explanations, verified examples and three-item practice batches, verified replacement bank, per-item reveals, and practice invalidation. Defer automatic practice grading as agreed.
  Verify (mechanical): Run independent hand-checked fixtures across topics; verify every solution step/answer, deliberately invalid fixture rejection, replacement/unavailable paths, three distinct relevant problems, initially hidden/reveal behavior, and edit invalidation. Run full suite.
  Learner check: Trigger a product-rule mistake, read explanation/example, inspect three practice questions and reveal each solution. Edit input and verify old practice disappears.
  Commit: `Add verified teaching and revealable practice`

- [x] **5. Verify offline use and document actual coverage**
  Becomes usable: Documented Windows launch, actual coverage/results, and honest photo recognition status.
  Why now: Validates the integrated journey before submission claims.
  PRD ref: `prd.md > Photo Input and Confirmation`, `Acceptance Evidence`
  Spec ref: `spec.md > Conditional Photo Recognition`, `Verification Plan`, `Where It Runs and How Someone Tries It`
  Build: Windows README/launch helper, tested dependency lock, validation report, and separate photo-feasibility findings. Enable recognition only if local extraction and confirmation workflow is demonstrated; otherwise explicitly document the approved typed fallback. No other feature deferral without approval.
  Verify (mechanical): Run full suite and documented launch; check core journey in a cold browser without outbound network after setup, local assets/telemetry/binding, recovery, limits, and practice reveals. Record actual results and versions. Never claim photo recognition passes without representative local evidence.
  Learner check: Follow Windows instructions and explore the whole app, including awkward inputs, restored drafts, and practice reveals. Report issues for final revision.
  Commit: `Document and verify offline WorkCheck demo`

## Hands-on Checkpoints

Current status: All five build slices are complete. The learner approved the ordinary-notation parser fixes, confirmed their offline checks passed, and authorized the Stage 5 commit. Latest guarded suite: 177 tests passed; fresh offline browser flows passed. Final readiness sign-off and the code tour/app map remain unfinished before 6-ship. Earlier entries below are the review history.


Stage 1 complete: 48 automated checks passed, revised appearance passed learner hands-on review, and commit 93ba8e4 records the checkpoint. Stage 2 is in progress. Details: devpost/validation.md.

Stage 2 complete: learner confirmed function notation, implicit multiplication, restoration, reordering, Cancel, and confirmed clearing. All 94 tests passed. Commit a744ae7 records local drafts and parser repairs. Stage 3 is in progress.

Stage 3 mechanical verification: 129 tests passed, including the full coefficient-method example in an actual spawned worker, root substitution, swapped labels, partial coefficient substitution, domain restrictions, and topic-aware UI checks. App restarted for learner review. Await hands-on feedback before checking or committing stage 3. Optional Discord project-thread suggestion has been offered once.

Stage-3 presentation revision: 143 tests now pass, including positive-first answers, compact exclusions, verified five-step coefficient-method display, equivalent-answer acceptance, and unchanged checking results if presentation fails. Restarted app for review; stage-3 checkbox and commit remain pending as requested.

- [x] Early usable behavior explored — learner confirmed stage 1 passed hands-on checks after the appearance revision
- [x] Final kick-the-tires exploration and feedback completed — after slice 5

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

- Learner requested school-style positive-first answers, concise isolated domain exclusions, and the explicit five-step coefficient-method explanation during stage-3 review. Implemented these in a separate display layer; underlying checker modules and acceptance rules are unchanged. Added presentation/equivalence/worker fallback/UI tests. This brings the requested coefficient-method explanation forward; general worked examples and verified practice remain stage 4. Stage 3 stays uncommitted pending review.

- Stage 3 implements the approved partial-fraction context rather than comparing only final answers. Added coefficient-scoped parsing, exact linear-system implication checks, explicit root-substitution notation, partial coefficient substitutions, domain preservation, and topic-aware UI/worker dispatch. An initial final-equality completion bug was repaired; equivalent correct decompositions on either side are recognized. Stage-3 learner check and commit remain pending.

- Learner reported continued rejection of ordinary implicit products. Fresh direct tests accepted both examples before this follow-up, so a live-session cause was not conclusively established. Replaced the coefficient-only regex with token-based normalization for recognized adjacent factors, added both bare-input UI/worker regressions, and restarted the app from its absolute workspace path. Preserve all pending stage-2 changes. Restoration/reset hands-on checks remain explicitly unconfirmed; stage 2 stays unchecked and uncommitted. Stage 3 has not started.

- Learner requested f(x) definitions alongside y and bare expressions, including implicit coefficients. Added shared label parsing, matching prime-labelled derivative working, labelled previews/results, mismatch clarification, and regression tests. Stage-2 learner review is still pending; no mathematical topic or approved feature was deferred.

- Learner reported rejection of (2x + 3)^4 during stage-2 review. Added restricted implicit numeric-coefficient multiplication for x, visible * guidance, ambiguity rejection, and parser/maths/UI regression coverage. This repairs input handling within approved chain-rule coverage; stage-2 hands-on review remains pending.

- Stage-1 hands-on feedback requested a more colourful interface. Added local-only header/topic/step/button styles and tinted learning panels while preserving checking behavior. Updated PRD/spec visual direction. Examples/practice remain labelled as upcoming until their approved implementation stage. Await a second learner visual review before the stage-1 commit.

- Learner requested complete equations beside concise explanations. Expanded presentation to six coefficient-method sections, including elimination and back-substitution, and explicit transformations for supported differentiation questions. Stage 3 remains unchecked and uncommitted for review.

- Presentation review: use structural SymPy LaTeX rendering for submitted lines in feedback cards and notation examples, as well as question/step previews, generated working and answers. Symbolic factors use juxtaposition; adjacent numeric factors retain a multiplication dot. Render authored product-rule feedback as inline maths. Keep raw editable input, input-syntax instructions, stored drafts, parser and checking rules unchanged. Unsupported notation receives a preview-unavailable message rather than a guessed rendering. Stage 3 remains uncommitted.

- Stage 3 accepted: learner approved worked steps and maths formatting and requested the completed stage be committed. Stage 4 remains unstarted pending the requested scope and acceptance-check report. No approved feature was deferred.

- Stage 4 authorized: implement concept-first teaching, a separate verified example and exactly three distinct verified practice problems with individual hidden answer/solution toggles. Use separate bounded local generation, a reverified fallback bank and honest unavailable path. Clear stale practice and reveal state on edits/recheck/reset. Preserve automatic-grading deferral. Stage 4 stays unchecked and uncommitted until hands-on review.

- Stage 4 ready for review: full suite passed 163 tests in 171.086 seconds; dependency consistency and whitespace checks passed. Loopback server restarted and health returned ok. Verified concept-first teaching, separate example, three distinct exercises, per-item hidden solutions, exact maths/domain checks, invalid-content rejection and fallback/unavailable paths, and edit/reorder/topic/reset invalidation. Await learner feedback before committing or checking the Stage 4 box.

- Stage 4 review refinement: the concept explanation and separate worked example now have independent expand/collapse controls. Both start open, preserving explanation-before-example-before-practice order. Practice answer reveals remain independent and initially hidden. Stage 4 stays uncommitted pending learner review.

- Stage 4 accepted: learner confirmed that the final version works correctly and passes review, and authorized the commit. Automatic practice grading remains deferred. Stage 5 remains unstarted while its scope and acceptance checks are reported.

- Stage 5 authorized: verify offline setup/runtime, document actual supported maths and limits, and investigate photo recognition separately. Added exact beginner Windows commands and a folder-independent launch helper. Retain approved typed-only fallback because local handwriting recognition is not demonstrated. Automatic practice grading remains deferred. Await final mechanical evidence and learner offline review before committing.

- Stage 5 ready for review: 163 tests passed in 197.585 seconds under a self-tested nonlocal socket guard, with no suite network attempts. Clean pinned installation and dependency consistency passed. The fresh Edge browser flow passed for maths rendering/local assets, both topic routes, learning/reveals, refresh/server-restart restoration and reset. Windows helper launch/loopback binding/stop passed. Documented actual supported forms, resource limits, initial failed verification attempts and remaining physical-offline/personal-browser checks. Photo recognition retains the approved typed fallback; no other feature was deferred. Stage 5 remains unchecked and uncommitted.

- During pending Stage 5 review, learner requested safe common-sentence interpretation. Added explicit task/expression extraction and student confirmation for supported forms; kept complex/branch-sensitive maths and point evaluation unsupported. New parser, mathematics-boundary and UI-flow regressions are being verified under the offline guard. Existing Stage 5 docs, launch helper, coverage/photo findings and verification tooling remain intact; all changes remain uncommitted.

- Sentence refinement verified: 171 guarded tests passed and the fresh offline browser sentence/confirmation/unsupported-complex flow passed. Preserved all pending Stage 5 changes and the typed-only photo fallback. Await learner review; Stage 5 remains unchecked and uncommitted.

- Learner requested ordinary multiplication as default throughout WorkCheck. Fixed clear factor boundaries after powers, updated student guidance/default examples, and retained ambiguity/name/safety checks and explicit-input compatibility. Added parser, hand-calculated derivative/working and UI learning regressions. Stage 5 and its existing pending changes remain uncommitted for review.

- Ordinary-notation refinement ready for review: 177 guarded tests passed and the fresh offline Edge ordinary-question/working flow passed. Existing Stage 5 changes are preserved; no commit made.

- Stage 5 accepted: learner confirmed ordinary mathematical notation passes review and their offline checks passed, and requested committing Stage 5 plus the reviewed parser fixes. Record those manual checks as learner-performed; do not treat them as agent-performed or imply a new-machine installation was tested. Final Review readiness sign-off and Code Tour and App Map remain pending. Report the remaining 5-build workflow before starting it. Photo recognition retains the approved typed fallback; automatic practice grading remains deferred.
