---
doc: scope
status: approved
---

# WorkCheck

A zero-additional-budget maths learning tool for engineering students that solves supported questions and helps students understand mistakes in optional solution steps. Typed input is required; photo input has been requested and needs a local feasibility check.

## The Unique Kernel
Go beyond an answer: identify the first incorrect step in a supported attempt, explain the relevant concept, show a worked example, and provide three targeted practice problems. Without an attempt, provide a solution and learning guidance.

## Who It's For
An engineering student studying differentiation or partial fractions who needs accessible help understanding a solution or where their own working went wrong. The learner sees too few free, easy tools focused on these students.

## The Core Loop
Open WorkCheck, type a question and optionally the attempted solution steps, then receive a solution or mistake feedback. Read the explanation and worked example before trying three related practice problems; use the feedback to guide further study.

## Inspiration & Identity
Supportive and educational, with explanations and worked examples before exercises. Visual direction has not been established; define it in the PRD.

## Why This Matters to the Learner
“I hope to help students have better learning conditions.” The learner also wants to understand how to use AI to build software and understand coding frameworks.

## What "Working" Looks Like
In a short on-screen demonstration, a student types a supported question, optionally adds solution steps, and receives mathematically checked results, an explanation, a worked example, and three relevant practice problems. A deliberately incorrect supported attempt demonstrates locating the first wrong step rather than only showing the final answer.

The build must verify the agreed problem types against worked solutions before describing them as validated. Proposed checks include a question without an attempt, correct working, and an attempt containing a known error across the supported topic families. Exact supported forms and checks will be defined in PRD and spec; this draft makes no accuracy claims.

The submission workflow includes a short demo video and public GitHub repository. Deployment is optional. Keep the experiment sized to the curriculum's roughly 2–4 hours of active work; reduce supported forms if implementation proves too large, with learner agreement.

## The POC Boundary
- Required: typed questions and optional typed solution steps, in a separate question field and numbered editable lines with equation previews. Photo recognition is conditional on a successful local feasibility check: extract both question and working, show editable text beside the photo, and require confirmation before checking. The learner explicitly accepts a typed-only submission if local recognition is not feasible. A photo preview alone does not count as recognizing maths.
- Differentiation: polynomials, products, powers, sin(x), cos(x), exp(x), and ln(x), including product-rule and chain-rule combinations. Requested examples include x^2*(x+1), (x^2+1)^3, x^2*sin(x), exp(2*x), and ln(x^2+1). Exact supported complexity and step forms remain to be settled in the PRD; implicit differentiation, parametric equations, and higher derivatives are deferred.
- Partial fractions: proper rational expressions with two distinct linear factors; repeated factors and irreducible quadratic factors are excluded from this demo.
- Solve supported questions; check supported attempts for the first incorrect step; explain the concept, show a worked example, and provide exactly three targeted practice problems. Each problem has a hidden, revealable answer and worked solution, mathematically verified locally before display. Automatic grading of practice attempts is deferred.
- All solving and checking must run locally on the user's device, with no external service requests. Explanations, worked examples, and practice generation must also work locally. Use mathematical rules and a free symbolic maths library if appropriate, with authored explanation and practice templates. No AI integration, paid services, or runtime cloud dependency. Library and framework choices belong in the spec; installing free dependencies during setup may require internet access.
- State unsupported inputs clearly rather than claim general curriculum coverage. Exact input and step formats belong in the PRD.
- Automatically save and restore the current question, selected topic, and ordered working locally on the same device. Include “New question” with confirmation before clearing nonempty working. No accounts or cloud sync.

## Planned Coverage Versus Validated Coverage
Full engineering mathematics curriculum coverage is the long-term ambition. The submission targets only the agreed product-rule, chain-rule, and restricted partial-fractions forms. Even these remain planned until tested: publish the actual tested forms and outcomes, without implying curriculum-wide correctness or improved learning outcomes have been established.

## Later
- Other differentiation rules and broader partial-fractions cases.
- Wider engineering mathematics curriculum.
- Broader handwriting support beyond whatever photo cases can actually be recognized and validated locally.

## Explicitly Cut
- AI integration in the submitted proof of concept: the learner wants the app to perform supported maths itself without AI service charges.
- Unreliable photo recognition: learner approved deferral if local recognition is not feasible. Manual typing always remains available.
- Claims to solve or validate the full engineering maths curriculum: the small demo cannot establish that coverage.

## Open Decisions for the PRD
The learner approved the revised scope and PRD, including conditional photo input, expanded differentiation forms, the first-error checking boundary, input notation, and verified revealable practice solutions. Typed-only fallback is accepted if local recognition is infeasible. Partial-fraction deferral requires a proposal and learner agreement.

Exact expression and step formats, supported differentiation forms, and how to handle ambiguous or unsupported steps need definition before building. First-error checking must be limited to forms the implementation can actually verify.
