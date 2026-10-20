# Actual maths coverage and limitations

Stage 5 review record, 2026-10-20. WorkCheck is a bounded proof of concept; full engineering mathematics remains a long-term goal. Passing the cases below does not validate every possible expression in these families or establish learning-outcome improvements.

## Implemented and covered by automated cases

| Area | Exercised behavior and representative inputs |
| --- | --- |
| Differentiation | Polynomials, products, integer powers and product/chain combinations: x^2(x+1), (x^2+1)^3, x^2 sin(x), exp(2x), ln(x^2+1), cos(3x), (2x+3)^4, (x^2-5x)^3. Actual input uses the supported typed grammar; powers/products render in conventional maths. |
| Step validity and completion | Original-function labels y and f(x), matching derivative labels and unevaluated D(...) working; valid unfinished and completed steps are distinct. Equivalent expanded/factored and unsimplified forms are checked symbolically. |
| First mistake and uncertainty | Product-of-derivatives misconception, first wrong coefficient equation/value, earlier unclear or incorrect line blocks dependent checks. A correct final answer cannot erase an earlier error. Unsupported notation requests clarification. |
| Partial fractions | Nonzero proper rational expressions with exact rational coefficients and two distinct rational linear factors, including nonmonic factors. Contextual A/B setup, denominator clearing, linear coefficient equations, values, partial substitution, swapped assignments, scaled/reordered equations, root substitution and completed two-term sums. |
| Domain restrictions | Logarithm inequalities, original denominator exclusions including cancelled holes, candidate extra-hole rejection and unsupported/unproved domains. Numerical agreement alone is never proof. |
| Teaching and practice | Concept notes, a distinct worked example and exactly three distinct targeted exercises. Product, powers, chain, sine/cosine, exponential, log and restricted partial-fraction template families; exact answer/step verification, reverified replacement bank, unavailable paths and individual initially hidden answers/solutions. |
| Workspace | Question/line previews, edit/add/delete/reorder, local save/restore, missing/corrupt saves, write failure, reset Cancel/confirmation, stale feedback/practice/reveal invalidation. |

The executable fixtures in tests/ are the precise coverage evidence; the validation report records actual run results. Display changes do not alter the working checker's accepted mathematics.

## Explicit boundaries

- One real variable x; first derivatives only. No implicit/parametric differentiation, higher derivatives, multivariable calculus or general engineering-curriculum coverage.
- Supported functions: sin, cos, exp, ln. No arbitrary Python, unknown functions, scientific numeric literals, arbitrary identifiers or unbounded symbolic input.
- Safe notation allows explicit * and unambiguous adjacent factors. It does not guess ambiguous 1/2x or x^2x. Function names stay whole; xsin(x) is not split.
- Partial fractions exclude repeated factors, irreducible quadratics, improper/zero source fractions, nonlinear coefficient equations and unsupported variable/coefficient denominators. Only A and B are contextual coefficients. Establish the setup before isolated coefficient equations; ambiguous reassignment asks for clarification.
- A supported name is not a promise for arbitrary nesting or domain proofs. Unknown verification gives clarification, not an invented wrong/correct verdict.
- Limits: 500 characters per field, 20 working lines, 150 syntax nodes, depth 12, 8-digit numbers, integer exponents -12 through 12 and polynomial degree at most 12. A 5-second checking deadline and separate 20-second learning deadline can return a limitation message. Limits do not truncate the draft.
- Practice uses bounded local templates. If a full verified set cannot be produced, no unchecked/incomplete filler is displayed. This unavailable case does not satisfy the exactly-three requirement.
- No automatic practice grading; answers and working reveal on request. No photo recognition, accounts, cloud sync or remote AI integration.
- Draft commits occur on Enter/blur, not each keystroke. One draft is shared across local tabs; use one editing tab. A separate 8 MiB save cap preserves data in memory and reports failure rather than truncating it.

## Runtime evidence boundaries

Windows 11 x64, Python 3.12.0, SymPy 1.14.0 and Streamlit 1.66.0 are the tested environment. Other Windows versions/devices, screen sizes, fresh Python installation and accessibility with assistive technology still require additional checks. Agent-performed automated browser checks and learner-performed physical-offline checks are distinguished in validation.md.


## Sentence interpretation refinement
Supported wording is limited to complete Differentiate/Find the derivative requests, Let/Given labelled definitions followed by a matching derivative request, and Decompose/Express/Write/Find partial-fractions requests. The interpreted expression and task require student confirmation in the UI. The parser remains bounded, offline and non-executing; no arbitrary trailing instructions are ignored. Unrecognised wording, unsafe/unsupported notation, topic mismatch and unsupported mathematics are distinct feedback categories. Complex logarithms/branches, real or imaginary component extraction and derivative/function evaluation at points remain outside verified scope; recognising words is not support for performing their mathematics.


Ordinary-notation refinement: students need no programming multiplication symbol. The shared restricted parser accepts separated products after literal powers (x^3 cos(x), 3x^2 sin(2x)), adjacent grouped factors and coefficients, and ordinary numeric multiplication signs. Keep names intact and decline ambiguous ungrouped division or exponent boundaries; clarification uses spacing/parentheses or ordinary maths operators. Questions, function labels, sentence extraction and working share this parser. Explicit legacy multiplication stays accepted; rendered maths has no programming operators. Practice attempts remain ungraded and have no dedicated input field.
