---
doc: prd
status: approved
---

# WorkCheck — Product Requirements

A local maths learning tool for engineering students, with no paid services or AI integration.
Sources: `scope.md > The Unique Kernel`, `The Core Loop`, and `The POC Boundary`. The learner approved the revised scope, input notation, checking boundary, and full PRD, with verified revealable practice solutions required.

## The Core Journey
1. Enter a question by typing or uploading a photo; optionally include attempted solution steps.
2. For photos, inspect the recognized question and every recognized solution step. Correct errors and explicitly confirm the text before solving or checking.
3. Submit the confirmed question and any attempted working.
4. With attempted working, see the verdict first, then an explanation identifying the first incorrect supported step, then the final answer. For correct working, explain why it is valid. If a step cannot be verified, request clarification instead of calling it wrong.
5. Without an attempt, receive the solution and explanation; do not label a nonexistent attempt right or wrong.
6. Read a worked example, then receive exactly three targeted practice problems and guidance on relevant concepts to learn.

## Screens and Layout
Keep the original question in its own field, with numbered editable working lines and formatted equation previews. Results appear below the question and working. If photo recognition is available, show the photo beside the editable transcription and require confirmation before checking. Result order: verdict, explanation beginning with what the student got wrong, final answer, worked example, and practice. For correct working or no attempt, explain the applicable method without inventing a mistake.

Stage-3 presentation refinement requested by the learner: use familiar school-style equations, preferring positive terms before negative terms where practical. When a real domain excludes only finitely many values, show concise restrictions such as x != -1, -2 rather than an interval union. Preserve inequalities and other genuine domain bounds. For the reference partial-fraction example, show 1/(x+1) - 1/(x+2) and the six-part coefficient method: full setup equality; multiply through; expand and collect; compare coefficients; eliminate and back-substitute with actual equations; substitute the final sum and retain restrictions. This changes presentation, not which mathematical answers or methods are accepted.

## Look and Feel
- Warm white background `#F8FAFC`, deep navy headings/navigation `#14213D`, deep teal main buttons/highlights `#0F766E`.
- Correct steps green `#15803D`; first incorrect step red `#B91C1C`; hints and unclear input amber `#92400E`.
- White cards, generous spacing, large readable equations. Pair feedback colours with icons and labels such as “Correct,” “First mistake,” and “Needs clarification.”
- Teal is the main accent; reserve red and green for checking results. No font family has been chosen.
- Stage-1 learner feedback expands the visual direction: retain navy/teal and add blue, purple, and soft amber accents; use a colourful header, distinct topic cards, prominent buttons and numbered steps, and lightly tinted explanation/example/practice panels. Keep equation areas clean with strong contrast. Red is reserved for errors and green for verified correct steps, with labels/icons. Appearance changes must preserve working behavior; unavailable topics and learning features remain clearly labelled until built.

## Features and Behavior

### Typed Input
Source: `scope.md > The POC Boundary`.
Accept function-definition labels such as f(x) = ... and y = ... in the question, retaining bare-expression support. Treat the left side as a label and differentiate the right side. Preview f(x) definitions with their label and display their derivative as f'(x). Apply the same distinction to original-function and derivative working lines; preserve valid unfinished D(...) steps and request clarification for mismatched or unsupported labels.
Learner-requested notation repair: accept unambiguous numeric coefficients such as 2x in both question and working, preserving the original draft text. Explain explicit * notation beside entry fields and in errors for unsupported or ambiguous multiplication. (2x + 3)^4 remains within approved chain-rule coverage; its derivative is 8*(2*x+3)^3.
Accept a typed question in its own field and optional ordered solution steps, one mathematical step per numbered editable line. Students can add, edit, delete, and reorder lines. Reordering updates their numbers and checking order. Show a formatted equation preview so students can inspect their input; a preview is not a correctness verdict. Manual typing must always remain available. Clearly show accepted notation and supported topics.

Approved notation: select the task (differentiate or decompose into partial fractions) and enter its expression using x, numeric constants, parentheses, explicit multiplication `*`, division `/`, and powers `^`. Use `sin(...)`, `cos(...)`, `exp(...)`, and `ln(...)` for supported functions. Display examples beside entry fields. Accept the labelled working and coefficient equations defined under Checking and Feedback. Other notation must receive actionable clarification, not a mathematical-error verdict. Exact formatting shortcuts and input-size limits are technical-spec decisions; unsupported complexity must produce an honest limitation message.

### Photo Input and Confirmation
Source: `scope.md > The POC Boundary` (reopened).
Extract both question and optional attempted steps locally. Present editable recognized text, preserving step order. Require student confirmation before using it. An image preview alone is not photo recognition. If recognition fails or a symbol is unclear, request correction or typed input rather than guess and judge the work.
Local handwritten-maths recognition has not been demonstrated. Include it only after a successful local feasibility check. The learner explicitly accepts a fully working typed-input submission if recognition is not feasible; clearly defer photo recognition in that case. Manual typing always remains available.

### Supported Mathematics
Source: `scope.md > The POC Boundary` and requested PRD expansion.
- First derivatives in one variable: polynomials, products, powers, sin(x), cos(x), exp(x), and ln(x), including product-rule and chain-rule combinations.
- Representative requested examples: x^2*(x+1), (x^2+1)^3, x^2*sin(x), exp(2*x), ln(x^2+1).
- Partial fractions: proper rational expressions with two distinct linear factors. Repeated factors and irreducible quadratic factors are excluded.
- Function families are planned coverage, not a promise to handle arbitrary nesting or every combination. The technical specification must document practical expression limits and testable combinations, preserving the representative examples and agreed step types. Expressions beyond those limits receive a limitation message rather than a guessed verdict.
- Real-valued domain restrictions must be retained where relevant; an undefined expression cannot receive an unconditional correctness verdict.

### Checking and Feedback
Source: `scope.md > The Unique Kernel`.
Finding the first incorrect step is the core feature. Check numbered lines in order, using the original question, each line's mathematical role, and previously verified steps. Step validity and solution completion are separate judgments: unfinished valid working is not wrong. Do not require a student to follow the displayed worked solution's method or wording.

#### Step Outcomes
The learner explicitly approved this checking boundary during PRD review and requires these distinctions in implementation and tests. Approval of this section is separate from approval of the entire PRD.

| Outcome | Meaning and feedback |
| --- | --- |
| Valid intermediate step | A verified statement or transformation that advances or correctly restates the working. Label it valid; if the attempt ends here, say it is incomplete, not incorrect. |
| Correct final answer | A verified expression that completes the requested task, including relevant domain restrictions. Label completion separately from the validity of preceding steps. |
| First incorrect step | The earliest verified mathematical error, with all preceding steps verified. Identify its line and explain the error before showing the final answer. |
| Unclear or unsupported step | The app cannot read, interpret, or verify the line within its supported checks. Explain the specific limitation and request clarification; do not guess or mark it wrong. |

A correct final answer does not erase an earlier error. If an earlier line is unresolved, do not claim a later error is the first; state that checking is blocked at the unresolved line. Subsequent dependent working must not be validated by assuming an incorrect or unresolved premise is true.

#### Differentiation Step Checking
Check complete derivative expressions on each numbered line, including unsimplified product-rule and chain-rule results and equivalent simplifications. Recognize original-function lines labelled `y = ...` separately from derivative claims labelled `dy/dx = ...`. Accept mathematically equivalent expressions and valid alternative methods within the supported checks; do not match only a model answer's text or sequence. Unsupported notation or a step whose role cannot be established requests clarification. This does not promise interpretation of arbitrary prose or every possible derivative notation.

#### Partial-Fraction Step Checking
For the agreed proper rational expressions with two distinct linear factors, support the decomposition setup, denominator-clearing identity, coefficient equations, coefficient values, and final decomposition. Interpret symbols such as A and B using their assigned denominator terms in the current question and previous verified working; never interpret an isolated coefficient equation without that context. Accept valid alternative methods, including coefficient comparison and substitution at denominator roots, where their steps can be verified. Equivalent forms and legitimate reorderings of coefficient names must not be rejected solely for differing from a preferred method.

Acceptance example: for `1/((x+1)*(x+2))`, after the student assigns `A/(x+1) + B/(x+2)`, verify `1 = A*(x+2) + B*(x+1)`, then `A+B = 0` and `2*A+B = 1` as valid intermediate steps. The first coefficient equation alone is incomplete, not wrong. `A = 1` and `B = -1` are valid coefficient values; `1/(x+1) - 1/(x+2)` is a correct final decomposition, retaining exclusions x != -1, -2. At the same coefficient-comparison stage, `A+B = 1` is an incorrect coefficient equation. If denominator assignments are missing or ambiguous, ask the student to establish them before judging coefficient equations.

#### Feasibility and Priority
Proper differentiation step checking takes priority over adding topics. Investigate local context-aware partial-fraction checking during spec. If it cannot be implemented reliably within the first-build boundary, propose deferring partial fractions and seek learner agreement on that change. Do not silently replace intermediate-step checking with final-answer comparison or ship a partial-fractions checker that labels valid unfinished working wrong. This fallback is a requested proposal path, not approval to defer the topic now.

Learner-supplied acceptance example: question “Differentiate y = x^2*sin(x)” with steps `y = x^2*sin(x)`, `dy/dx = (2*x)*cos(x)`, and `dy/dx = 2*x*cos(x)`. The first line correctly copies the original function. Flag line 2 as the first mistake, explain that multiplying the derivatives is not the product rule and that u'v + uv' is required, then show `2*x*sin(x) + x^2*cos(x)`. Do not identify line 3 as the first error. Support labels such as `y = ...` and `dy/dx = ...`; distinguish the original-function statement from a claimed derivative.

### Explanation and Practice
Source: `scope.md > The Core Loop`.
Explain the relevant concept before exercises, show a worked example, then provide exactly three related practice problems. With an identified mistake, target its concept; without an attempt, target the question's method. Each practice problem must have an answer and worked solution, hidden initially and revealable on demand. Verify each problem's answer and every mathematical step of its worked solution locally before displaying that problem or allowing its solution to be revealed. Verification must establish mathematical validity, not merely match template text. Retain relevant domain restrictions. If verification fails or is inconclusive, do not display the unverified content; use a verified replacement or explain that practice is temporarily unavailable. Never claim that an unavailable set fulfills the exactly-three requirement. All content, generation, and verification run locally. Automatic grading of practice attempts remains deferred.

## States and Boundaries
- Unfinished differentiation: D(expression) denotes an unevaluated derivative with respect to x. Verified steps retaining this notation are valid intermediate working, not a completed derivative; mathematically incorrect held expressions remain incorrect. See spec.md > Approved Clarifications for examples and checking rules.
- Clearly explain input limits. Preserve and save raw question/working when limits are exceeded; never truncate the draft to make it fit. Explain which limit prevents checking.
- Any question/topic/working change clears or visibly invalidates prior feedback and practice, including reveals; stale asynchronous results must not appear current.
- Automatically save the current question, selected topic, and numbered working lines locally on the same device; restore them when the student returns. Preserve line order through edits and reordering. No accounts or cloud sync.
- Provide a clearly labelled “New question” button. Confirm before clearing nonempty working; cancellation preserves the draft. Confirmed reset clears the saved draft as well as the visible working so old content cannot return on restart.
- Empty question: ask for a question; do not solve.
- Photo awaiting confirmation: show editable question and steps; do not check automatically.
- Unreadable or ambiguous input: identify what needs clarification and permit edits.
- Unsupported question or step: state the limitation without marking the student wrong.
- Valid unfinished attempt: label verified lines as valid and state that the solution is incomplete; do not mark it wrong or complete.
- Correct completed attempt: show a correct-final-answer label, with preceding step validity assessed separately, and explanation before the final answer.
- Incorrect attempt: show the first verifiable mistake and explain it before the final answer.
- No attempt: solve and explain without a right/wrong verdict about the student.
- Revised input: previous feedback must not appear to apply to changed working.
- All solving, checking, recognition, explanations, examples, and practice run locally, without external service requests. Free setup downloads may require internet.

## Product Decisions
- During technical planning, learner required local autosave/restore of question, topic, and numbered lines, plus confirmed clearing of nonempty working via “New question.” No accounts or cloud sync are needed.
- Typed input and photos are both requested; photos must extract question and working for student confirmation and correction.
- Learner specified a separate question field, numbered editable steps with add/edit/delete/reorder controls, equation previews, and the photo beside its transcription if recognition becomes available. Manual typing always remains available.
- Results belong below the question and working. Following the verdict, the explanation starts with what went wrong before showing the final answer.
- Each of the three practice problems requires a hidden, revealable answer and worked solution, mathematically verified locally before display. Automatic grading of practice attempts remains deferred. This supersedes the earlier decision that answers were unnecessary.
- Uncertain input requires clarification, not an incorrect verdict.
- First-error checking must preserve valid intermediate work, distinguish completion from validity, and recognize equivalent expressions and supported alternative methods. Include context-aware partial-fraction coefficient equations; if infeasible, propose deferring that topic rather than weakening differentiation step checking.
- Result ordering and the navy/teal/warm-white palette were supplied by the learner.
- Include common functions with product/chain-rule combinations; defer implicit differentiation, parametric equations, and higher derivatives.
- No AI service integration or paid services; all checking local.

## What We're Building
The supported solve/check/teach loop using typed input, local execution, explicit uncertainty handling, and three targeted practice problems. Photo recognition is conditional on demonstrated local feasibility; the learner accepts typed-only delivery if it is not feasible. A manual-only photo preview cannot be presented as recognition.

## Acceptance Evidence
Source: `scope.md > What "Working" Looks Like` and `Planned Coverage Versus Validated Coverage`.
- Demonstrate a supported question without an attempt and one with correct working.
- Use known incorrect attempts to verify first-error feedback, explanation order, final answer, worked example, and exactly three relevant problems.
- Verify equivalent valid forms are not rejected solely for formatting.
- Verify valid unfinished attempts receive an incomplete status without an incorrect verdict, and correct final answers are distinguished from intermediate steps.
- Verify unsimplified derivative expressions, equivalent simplifications, and supported alternative methods; retain the learner's x^2*sin(x) first-error example.
- Verify the partial-fraction setup and coefficient-equation example above, including a valid unfinished system, an incorrect coefficient equation, and missing context requiring clarification.
- Verify a correct final answer following an earlier incorrect step does not clear that error, and an unresolved earlier step prevents a later first-error claim.
- Demonstrate unclear and unsupported inputs yield clarification or a limitation message.
- For all three practice problems, verify the answers and every worked-solution step mathematically, including domain restrictions. Confirm solutions are hidden initially and revealable per problem; failed or inconclusive verification must not expose unverified content. Include a deliberately invalid practice fixture to test rejection and a verified replacement path.
- For photo support, demonstrate actual local extraction of question and steps, a correction, and confirmation before checking.
- Demonstrate the core flow with network access unavailable after setup.
- Edit and reorder working, close and reopen the app, and verify that question, topic, and ordered lines are restored. Verify cancelling “New question” preserves working and confirming clears both visible and saved drafts.
- Record actual tested forms and results across differentiation and partial fractions; do not claim full curriculum validation or proven learning improvement.

## Deferred From the POC
Implicit differentiation, parametric equations, higher derivatives, repeated/quadratic partial-fraction factors, and the wider engineering maths curriculum. These expand the mathematical and validation burden beyond the small experiment.

## Non-Goals
AI integration, paid services, runtime cloud dependencies, or claims of general handwriting recognition and curriculum-wide correctness.

## Open Questions
No product approval is outstanding. The learner approved the full PRD and revised scope, including notation and verified revealable practice solutions. The checking boundary must not be weakened during implementation.

During spec: document practical expression limits and investigate local photo recognition feasibility. The typed-only fallback is approved. Investigate context-aware partial-fraction checking; if infeasible, propose topic deferral for learner agreement. These investigations cannot silently reduce the agreed first-error checking behavior.
Review format: Markdown, explicitly selected by the learner.


Worked-solution refinement: render actual mathematical equations with a short explanation beside every transformation. Partial fractions include expansion, collection, coefficient comparison, elimination, back-substitution, and the original-to-final equality using the question's actual coefficients. Differentiation shows explicit derivative transformations for the supported sum, product, integer power, chain, sine, cosine, exponential, and logarithm rules. Verify generated transformations symbolically before display; never change the working checker's acceptance rules. Stage 3 was accepted by the learner after review.


### Learner-authorized sentence interpretation refinement
Accept a bounded set of common question wordings for the existing differentiation and partial-fraction tasks. Show the safely parsed function/expression and full interpreted task; require confirmation for sentences before checking. Reset confirmation on question/topic changes and restoration. Keep original drafts, working grammar, domain rules and offline operation intact. Distinguish unrecognised complete wording from unsupported notation, mismatched selected topic and mathematics outside scope. Reject unsupported complex logarithm/branch/component requests and derivative evaluation before any differentiation. The example requesting the imaginary coefficient of the derivative at 1 receives a limitation, not a real-differentiation answer. Additional or mismatched instructions require clarification rather than silent stripping.


Ordinary-notation refinement: students need no programming multiplication symbol. The shared restricted parser accepts separated products after literal powers (x^3 cos(x), 3x^2 sin(2x)), adjacent grouped factors and coefficients, and ordinary numeric multiplication signs. Keep names intact and decline ambiguous ungrouped division or exponent boundaries; clarification uses spacing/parentheses or ordinary maths operators. Questions, function labels, sentence extraction and working share this parser. Explicit legacy multiplication stays accepted; rendered maths has no programming operators. Practice attempts remain ungraded and have no dedicated input field.
