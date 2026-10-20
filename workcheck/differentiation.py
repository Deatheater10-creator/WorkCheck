import sympy as sp
from .models import CheckResult, StepResult
from .parser import X, MAX_STEPS, InputIssue, derivative_label_latex, parse_step, question_expression
from .verification import domain_of, verify


def _mistake_explanation(source, candidate):
    expression = source.expr.doit()
    if isinstance(expression, sp.Mul) and len(expression.args) == 2:
        u, v = expression.args
        wrong_product = sp.diff(u, X) * sp.diff(v, X)
        if sp.simplify(candidate.expr.doit() - wrong_product) == 0:
            return ("This line multiplies the two derivatives. The product rule requires "
                    "u'·v + u·v': differentiate one factor at a time and add the two terms.")
    return "This expression is not the requested derivative on the original domain. Recheck the differentiation and algebra in this line."


def check_differentiation(question: str, lines: list[str]) -> CheckResult:
    try:
        source = question_expression(question)
    except InputIssue as exc:
        return CheckResult("Needs clarification", str(exc))
    if len(lines) > MAX_STEPS:
        return CheckResult("Needs clarification", "The 20-working-line limit is exceeded. Your working is kept; remove or combine lines to check it.")
    domain = domain_of(source)
    if domain is None or domain is sp.S.EmptySet:
        return CheckResult("Needs clarification", "I cannot establish a nonempty supported real domain for this question.")
    answer = sp.diff(source.expr.doit(), X)
    expected_domain = domain_of(type(source)(answer))
    if expected_domain is None:
        return CheckResult("Needs clarification", "I cannot verify this derivative's domain within the supported rules.")
    domain = domain.intersect(expected_domain)
    result = CheckResult("Solution", "No attempted working was supplied. Here is the derivative.",
                         answer_latex=sp.latex(answer), domain_latex=sp.latex(domain),
                         derivative_label_latex=derivative_label_latex(source.function_label))
    active_label = source.function_label
    completed = False
    supplied = False
    blocked = False
    for number, text in enumerate(lines, 1):
        if not text.strip():
            continue
        supplied = True
        if blocked:
            result.steps.append(StepResult(number, text, "Not checked", "Resolve the earlier incorrect or unclear line first."))
            continue
        try:
            role, candidate, left = parse_step(text, expected_label=active_label)
            if role == "derivative_equality":
                # The equality must refer to the original derivative, not an unrelated subproblem.
                from .parser import Expression
                left_proof = verify(Expression(left.expr.expr, left.restrictions), source.expr.doit(), domain)
                if left_proof.status != "proved":
                    raise InputIssue("The D(...) on the left must refer to the original function. Clarify the line's role.")
                candidate.restrictions += left.restrictions
            if role == "function" and candidate.held:
                raise InputIssue("A function-definition line should state the original function, not its derivative. Use dy/dx = or the matching f'(x) = label for derivative working.")
            proof = verify(candidate, source.expr.doit() if role == "function" else answer, domain)
            if proof.status == "unknown":
                raise InputIssue(proof.reason)
        except InputIssue as exc:
            result.steps.append(StepResult(number, text, "Needs clarification", str(exc)))
            result.status = "Needs clarification"
            result.explanation = f"Line {number}: {exc} Later lines have not been checked."
            result.blocked_at = number
            blocked = True
            continue
        if proof.status == "disproved":
            reason = ("This line does not match the original function." if role == "function"
                      else _mistake_explanation(source, candidate))
            result.steps.append(StepResult(number, text, "First mistake", reason + " " + proof.reason))
            result.status = "First mistake"
            result.first_error = number
            result.explanation = f"Line {number}: {reason}"
            blocked = True
        else:
            if candidate.function_label and candidate.function_label != "y" and active_label in (None, "y"):
                active_label = candidate.function_label
            complete = role != "function" and not candidate.held
            completed = completed or complete
            label = "Correct final answer" if complete else "Valid intermediate step"
            reason = ("The derivative is complete; no further simplification is required." if complete
                      else "This is valid working, but it does not yet complete the derivative.")
            result.steps.append(StepResult(number, text, label, reason, complete))
    if supplied and not blocked:
        result.status = "Correct final answer" if completed else "Valid working — incomplete"
        result.explanation = ("All supplied steps are valid and the derivative is complete." if completed
                              else "The supplied working is valid so far. Evaluate the remaining derivatives to finish; unfinished is not wrong.")
    return result
