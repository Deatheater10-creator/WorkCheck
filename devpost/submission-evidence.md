# WorkCheck factual evidence for learner-written answers

These are technical reference notes, not paste-ready submission answers. The complete signed-in form has not been inspected. Do not assume generic Devpost field names or character limits; the learner should provide the actual prompts. Personal reflections, motivations, claims about learning and the exit survey remain the learner's own writing.

## Facts that have evidence

| Topic | Project facts to consult | Evidence |
| --- | --- | --- |
| Working kernel | Typed question plus numbered working; first incorrect supported step, explanation, worked learning and three targeted practice problems. | `devpost/prd.md`, `tests/test_differentiation.py`, `tests/test_partial_fractions.py`, `tests/test_ui.py` |
| Actual maths scope | Tested first real differentiation/product/chain combinations and restricted two-distinct-linear-factor partial fractions. | `devpost/coverage.md`, executable maths fixtures |
| Inputs | Ordinary multiplication, supported function labels and bounded common sentence forms; confirmation before checking sentence interpretations. | `workcheck/parser.py`, `workcheck/questions.py`, parser/questions/ordinary-notation tests |
| Verification | Exact symbolic checks plus explicit validity/completion/uncertainty rules. No numerical-agreement proof. Context matters for A/B equations. | `workcheck/verification.py`, topic checkers, verification tests |
| Teaching | Locally authored concepts and worked steps, a separate example and exactly three distinct problems; answers/steps verified before display. | `workcheck/practice.py`, `workcheck/presentation.py`, practice tests |
| Local use | Python, SymPy and Streamlit; no runtime external AI requests, paid service, account or cloud sync. Initial dependencies require installation. | `requirements-lock.txt`, README, offline guard/browser reports |
| Drafts and interface | Save/restore, reset confirmation/Cancel, stale-result clearing, individual practice reveals, progressive working and reduced-motion effects. | Storage/UI tests and final offline Edge flow |
| Skill Pack process | Approved scope, PRD and spec; ordered build slices and recorded learner reviews; readiness report, walkthrough/map; 6-ship preparation started after explicit readiness confirmation. | `devpost/scope.md`, `prd.md`, `spec.md`, `checklist.md`, Git history |
| Test evidence | Last full guarded run: 181 tests passed in 142.493 seconds; complete cold offline Edge flow passed. Shipping entry reran 3 maths cases and 2 relevant UI cases successfully. | `devpost/validation.md`, `devpost/shipping.md` |

The development used an AI coding assistant, but WorkCheck's runtime uses local mathematical rules and SymPy. These are separate facts; do not claim runtime AI or handwriting recognition. The actual hardware/OS exercised was Windows 11 x64 with Python 3.12.0, SymPy 1.14.0 and Streamlit 1.66.0. Do not claim other operating systems or every expression in a topic has been validated.

## Facts that are not established

- Full engineering-mathematics curriculum support.
- Reliable photo recognition; it remains deferred under the approved typed-only fallback.
- Automatic grading of practice attempts; it remains deferred.
- Measured improvements in student outcomes, market demand, user numbers, or comparisons proving superiority over other products.
- A public repository or public demo-video URL; neither has been confirmed.
- The learner's personal lessons, motivations, eligibility declarations or survey answers.
- Eligibility of any other project; WorkCheck's audit does not inspect another app's development history.

## How writing support will work

1. The learner supplies the actual field prompt and any length limit, then writes an answer in their own words.
2. The agent can identify factual gaps, unsupported claims and mismatches with implemented coverage. It can point to the evidence above.
3. The agent can correct spelling and grammar in learner-written text. It will not transform notes into submission prose, draft narration, polish tone or supply personal reflections.

The first factual writing question, when the learner is ready: **In your own words, what does WorkCheck do and who is it for?** No answer is supplied here. For the required Skill Pack usage field, consult the process evidence row, then describe your own experience; do not copy an agent-generated paragraph.
