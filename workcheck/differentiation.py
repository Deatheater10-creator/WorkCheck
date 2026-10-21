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
            return ("This line multiplies the two derivatives. For a product, you need to keep one part unchanged each time, then add two terms.\n\n"
                    "**How to fix it — use the product rule**\n\n"
                    f"1. Differentiate ${sp.latex(u)}$ and keep ${sp.latex(v)}$ unchanged.\n"
                    f"2. Keep ${sp.latex(u)}$ unchanged and differentiate ${sp.latex(v)}$.\n"
                    "3. Add these two terms.\n\n"
                    "The rule is $u'v + uv'$, where u and v are the two parts and the prime mark means 'the derivative of'. Follow the worked solution below to see each change.")
    return ("This derivative is not correct. Compare this line with the worked solution below, one change at a time. "
            "Check the signs and powers, and remember the derivative of any expression inside brackets. "
            "This line alone does not show exactly which smaller change caused the mistake.")


def check_differentiation(question: str, lines: list[str]) -> CheckResult:
    try:
        source = question_expression(question, topic="Differentiation")
    except InputIssue as exc:
        return CheckResult("Needs clarification", str(exc))
    if len(lines) > MAX_STEPS:
        return CheckResult("Needs clarification", "The 20-working-line limit is exceeded. Your working is kept; remove or combine lines to check it.")
    domain = domain_of(source)
    if domain is None or domain is sp.S.EmptySet:
        return CheckResult("Needs clarification", "I cannot work out which real values of x are allowed for this question. This is a limit of the checker; it does not mean your question is wrong.")
    answer = sp.diff(source.expr.doit(), X)
    expected_domain = domain_of(type(source)(answer))
    if expected_domain is None:
        return CheckResult("Needs clarification", "I cannot check which values of x are allowed in this derivative. This version cannot verify the question safely.")
    domain = domain.intersect(expected_domain)
    result = CheckResult("Solution", "You have not entered any working to check. Read the method below, then try the practice questions.",
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
            result.steps.append(StepResult(number, text, "Not checked", "Fix or clarify the earlier line, then check again. A later line may depend on that earlier mistake."))
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
            result.steps.append(StepResult(number, text, "First mistake", reason))
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
            reason = ("This is a correct final derivative. You do not need to simplify it further." if complete
                      else "This step is correct so far. You still need to work out the remaining derivatives." if role != "function"
                      else "You have copied the original function correctly. Next, start differentiating it.")
            result.steps.append(StepResult(number, text, label, reason, complete))
    if supplied and not blocked:
        result.status = "Correct final answer" if completed else "Valid working — incomplete"
        result.explanation = ("Your working is correct and you have reached the final derivative." if completed
                              else "Your working is correct so far, but the derivative is not finished. Work out any derivatives still shown in the line; an unfinished step is not a mistake.")
    return result
