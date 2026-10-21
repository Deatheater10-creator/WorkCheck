"""Context-aware exact checks for proper fractions with two linear factors."""
from dataclasses import dataclass
import re
import sympy as sp
from sympy.solvers.solveset import NonlinearError

from .models import CheckResult, StepResult
from .parser import A, B, X, Expression, InputIssue, MAX_CHARS, MAX_STEPS, parse_expression, question_expression
from .verification import domain_of, verify

COEFFICIENTS = {A, B}


class InvalidStep(ValueError):
    """A supported, unambiguously false mathematical step."""


@dataclass
class PartialLine:
    left: Expression | None
    right: Expression
    root: sp.Expr | None = None
    root_marker: bool = False


@dataclass
class Context:
    setup: sp.Expr
    equations: list
    augmented: sp.Matrix
    solution: dict
    root: sp.Expr | None = None


def parse_partial_line(text):
    if len(text) > MAX_CHARS:
        raise InputIssue("This line exceeds the 500-character limit; your text is kept.")
    root = None
    if ":" in text:
        prefix, text = text.split(":", 1)
        if not re.match(r"^\s*x\s*=", prefix):
            raise InputIssue("For root substitution, use x=-1: 1=A, or a separate x=-1 line after the setup.")
        root = parse_expression(prefix.split("=", 1)[1]).expr.doit()
        if root.is_Rational is not True:
            raise InputIssue("Use an exact rational denominator root in a substitution.")
    if text.count("=") > 1:
        raise InputIssue("Use one equation per line; root substitutions may use x=-1: 1=A.")
    if "=" not in text:
        if root is not None:
            raise InputIssue("Put an equation after the root-substitution colon.")
        return PartialLine(None, parse_expression(text, allow_coefficients=True))
    lhs, rhs = text.split("=", 1)
    left = parse_expression(lhs, allow_coefficients=True)
    right = parse_expression(rhs, allow_coefficients=True)
    if lhs.strip() == "x" and root is None and right.expr.doit().is_Rational is True:
        return PartialLine(left, right, right.expr.doit(), True)
    return PartialLine(left, right, root)


def _rational_polynomials(expression):
    try:
        numerator, denominator = sp.fraction(sp.cancel(expression))
        return sp.Poly(numerator, X, domain=sp.QQ), sp.Poly(denominator, X, domain=sp.QQ)
    except (sp.PolynomialError, ValueError, TypeError, sp.polys.polyerrors.CoercionFailed):
        raise InputIssue("This topic accepts fractions built from powers of x with whole-number or fraction coefficients. For sine, cosine, exponential or logarithm questions, choose Differentiation instead.") from None


def _roots(expression):
    numerator, denominator = _rational_polynomials(expression)
    if numerator.is_zero or numerator.degree() >= denominator.degree():
        raise InputIssue("Use a fraction whose top is not zero and whose highest power of x is smaller on top than underneath. Fractions that need division first are not supported yet.")
    _, factors = sp.factor_list(denominator.as_expr(), X)
    if len(factors) != 2 or any(power != 1 or sp.degree(factor, X) != 1 for factor, power in factors):
        raise InputIssue("The denominator must split into two different factors of the form ax+b, such as x+1 and 2x+3. Repeated factors and factors containing x squared are not supported yet.")
    return {sp.cancel(-sp.Poly(factor, X).nth(0)/sp.Poly(factor, X).nth(1)) for factor, _ in factors}


def _simple_root(expression):
    numerator, denominator = _rational_polynomials(expression)
    if numerator.is_zero or numerator.degree() > 0 or denominator.degree() != 1:
        raise InputIssue("Each decomposition term must have a constant numerator and one linear denominator.")
    return sp.cancel(-denominator.nth(0)/denominator.nth(1))


def _setup(parsed, source, roots, domain):
    expression = parsed.expr.doit()
    terms = sp.Add.make_args(expression)
    if len(terms) != 2:
        raise InputIssue("Start with two terms assigning A and B to the linear denominators, e.g. A/(x+1)+B/(x+2).")
    used, assigned_roots = set(), set()
    for term in terms:
        symbols = term.free_symbols & COEFFICIENTS
        if len(symbols) != 1:
            raise InputIssue("Assign exactly one coefficient, A or B, to each denominator term.")
        symbol = next(iter(symbols))
        if symbol in used:
            raise InputIssue("Use A and B once each in the decomposition setup.")
        coefficient = sp.cancel(sp.diff(term, symbol))
        if sp.cancel(term-symbol*coefficient) != 0 or coefficient.free_symbols & COEFFICIENTS:
            raise InputIssue("The setup must be linear in A and B.")
        used.add(symbol)
        assigned_roots.add(_simple_root(coefficient))
    if used != COEFFICIENTS:
        raise InputIssue("Assign A and B to the two denominator terms.")
    if assigned_roots != roots:
        raise InvalidStep("These denominators do not match the question's two distinct factors, so the setup cannot represent the original fraction.")
    numerator = sp.fraction(sp.cancel(expression-source))[0]
    equations = sp.Poly(numerator, X).all_coeffs()
    matrix, values = sp.linear_eq_to_matrix(equations, [A, B])
    if matrix.rank() != 2 or matrix.row_join(values).rank() != 2:
        raise InputIssue("I cannot find one definite pair of values for A and B from this setup. Check that you have one fraction for each denominator factor.")
    solution = next(iter(sp.linsolve((matrix, values), [A, B])))
    substitution = dict(zip([A, B], solution))
    # Retain restrictions from the raw setup, including holes cancelled by algebra.
    substituted = Expression(parsed.expr.subs(substitution),
                             [(kind, expr.subs(substitution)) for kind, expr in parsed.restrictions])
    proof = verify(substituted, source, domain)
    if proof.status != "proved":
        raise InputIssue("I cannot confirm this setup for all the x values allowed in the question. " + proof.reason)
    return Context(expression, equations, matrix.row_join(values), substitution)


def _partly_resolved(parsed, context, source, roots, domain):
    terms = sp.Add.make_args(parsed.expr.doit())
    if len(terms) != 2:
        raise InputIssue("For this intermediate step, enter the full two-term fraction sum or a complete coefficient equation.")
    found = set()
    try:
        for term in terms:
            numerator, denominator = sp.fraction(sp.cancel(term))
            poly = sp.Poly(numerator, A, B)
            if poly.total_degree() > 1 or X in numerator.free_symbols:
                raise InputIssue("Use constant numerators linear in A and B for this intermediate sum.")
            found.add(_simple_root(1/denominator))
    except sp.PolynomialError:
        raise InputIssue("I cannot interpret this coefficient numerator as supported linear working.") from None
    if found != roots:
        raise InputIssue("Clarify how this intermediate sum uses the original two denominator factors.")
    substituted = Expression(parsed.expr.subs(context.solution),
                             [(kind, expr.subs(context.solution)) for kind, expr in parsed.restrictions])
    return verify(substituted, source, domain)


def _is_final(expression, roots):
    terms = sp.Add.make_args(expression.doit())
    if len(terms) != 2 or expression.free_symbols & COEFFICIENTS:
        return False
    try:
        return {_simple_root(term) for term in terms} == roots
    except InputIssue:
        return False


def _coefficient_equation(line, context):
    if context is None:
        raise InputIssue("First assign A and B to denominator terms, e.g. A/(x+1)+B/(x+2), before checking coefficient equations.")
    residual = line.left.expr - line.right.expr
    if any(expr.free_symbols for parsed in (line.left, line.right) for _, expr in parsed.restrictions):
        raise InputIssue("Clear variable or coefficient denominators before comparing coefficients or substituting a root.")
    # Polynomial identities and linear coefficient equations only. A rational
    # equation could introduce exclusions or division by an unknown coefficient.
    try:
        sp.Poly(residual, X, A, B)
    except sp.PolynomialError:
        raise InputIssue("Multiply through by the denominators first to remove the fractions. Then enter the equation after opening the brackets, or an equation in A and B.") from None
    root = line.root if line.root is not None else context.root
    if root is not None:
        residual = residual.subs(X, root)
    try:
        relations = sp.Poly(sp.expand(residual), X).all_coeffs()
        matrix, values = sp.linear_eq_to_matrix(relations, [A, B])
    except (sp.PolynomialError, NonlinearError, ValueError):
        raise InputIssue("I can check equations with A and B to the first power here. Powers or products of A and B are not supported in this step; please clarify your working.") from None
    target = matrix.row_join(values)
    return context.augmented.col_join(target).rank() == context.augmented.rank()


def check_partial_fractions(question, lines):
    try:
        parsed_source = question_expression(question, topic="Partial fractions")
        source = sp.cancel(parsed_source.expr)
        roots = _roots(source)
        domain = domain_of(parsed_source)
        if domain is None or domain is sp.S.EmptySet:
            raise InputIssue("I cannot check which real values of x are allowed in the original fraction. This is a limit of the checker, not a wrong-answer verdict.")
        if len(lines) > MAX_STEPS:
            raise InputIssue("The 20-working-line limit is exceeded. Your working is kept.")
    except InputIssue as exc:
        return CheckResult("Needs clarification", str(exc), derivative_label_latex="")
    result = CheckResult("Solution", "You have not entered any working to check. Follow the method below to see how to split this fraction into simpler fractions.",
                         answer_latex=sp.latex(sp.apart(source, X)), domain_latex=sp.latex(domain), derivative_label_latex="")
    context = None
    completed, supplied, blocked = False, False, False
    for number, text in enumerate(lines, 1):
        if not text.strip():
            continue
        supplied = True
        if blocked:
            result.steps.append(StepResult(number, text, "Not checked", "Fix or clarify the earlier line, then check again. A later line may depend on that earlier mistake."))
            continue
        complete, valid, reason = False, True, ""
        try:
            line = parse_partial_line(text)
            if line.root is not None:
                if context is None:
                    raise InputIssue("First show which fraction uses A and which uses B. Then choose a value of x that makes one denominator factor zero.")
                if line.root not in roots:
                    raise InputIssue("This version supports substitution at the question's denominator roots. Please clarify this substitution.")
            if line.root_marker:
                context.root = line.root
                reason = f"You have chosen $x={sp.latex(line.root)}$. Put this value into the equation after removing the fractions, not into the original fraction. This is a useful step, but the answer is not finished."
            else:
                candidates = [p for p in (line.left, line.right) if p is not None and p.expr.free_symbols & COEFFICIENTS]
                numeric_equation = (not candidates and line.left is not None and
                                    (verify(line.left, source, domain).status == "proved" or
                                     verify(line.right, source, domain).status == "proved"))
                # A coefficient-bearing expression is a setup only when it is a
                # standalone expression, or equated directly to the source.
                setup = None
                if line.left is None and candidates:
                    setup = line.right
                elif line.left is not None:
                    for candidate, other in [(line.left, line.right), (line.right, line.left)]:
                        if candidate.expr.free_symbols & COEFFICIENTS and not other.expr.free_symbols & COEFFICIENTS:
                            if verify(other, source, domain).status == "proved":
                                setup = candidate
                if setup is not None:
                    if context is not None and setup.expr.free_symbols & COEFFICIENTS != COEFFICIENTS:
                        proof = _partly_resolved(setup, context, source, roots, domain)
                        if proof.status == "unknown":
                            raise InputIssue(proof.reason)
                        valid = proof.status == "proved"
                        reason = ("The value you have put in is correct. There is still an A or B in your fractions: find its value and put that in too."
                                  if valid else "The value you have put into these fractions does not give the original fraction. Keep A and B with the same denominators as in your setup, and check the value you substituted.")
                    else:
                        new_context = _setup(setup, source, roots, domain)
                        if context is not None and sp.cancel(context.setup-new_context.setup) != 0:
                            raise InputIssue("These A/B assignments differ from the earlier setup. Start a new attempt or clarify the change.")
                        context = new_context
                        reason = "This setup is correct. A and B stand for the numbers we need to find. Next, multiply both sides by the full denominator to remove the fractions."
                elif candidates or (context is not None and line.left is not None and not numeric_equation):
                    if line.left is None:
                        raise InputIssue("Enter a complete equation for this coefficient step.")
                    valid = _coefficient_equation(line, context)
                    reason = ("This equation is correct for your A and B setup. Keep going: find both numbers, then put them back into the fractions."
                              if valid else _coefficient_correction(context))
                else:
                    if line.root is not None:
                        raise InputIssue("Root substitution needs a denominator-cleared coefficient equation.")
                    candidate = line.right
                    if line.left is not None:
                        left_proof = verify(line.left, source, domain)
                        if left_proof.status == "proved" and _is_final(line.left.expr, roots) and verify(line.right, source, domain).status == "proved":
                            candidate = line.left
                        elif left_proof.status != "proved":
                            if verify(line.right, source, domain).status == "proved":
                                candidate = line.left
                            else:
                                raise InputIssue("For a final decomposition equality, one side must match the original fraction.")
                    proof = verify(candidate, source, domain)
                    if proof.status == "unknown":
                        raise InputIssue(proof.reason)
                    valid = proof.status == "proved"
                    complete = valid and _is_final(candidate.expr, roots)
                    reason = ("These simpler fractions add up to the original fraction. This is a correct final answer." if complete
                              else "This has the same value as the original fraction, so the step is correct. To finish, write the two simpler fractions with numbers in place of A and B." if valid
                              else "These fractions do not add up to the original fraction. Put them over a common denominator and check the numerator, including any minus signs.")
        except InvalidStep as exc:
            valid, reason = False, str(exc)
        except InputIssue as exc:
            result.steps.append(StepResult(number, text, "Needs clarification", str(exc)))
            result.status, result.blocked_at = "Needs clarification", number
            result.explanation = f"Line {number}: {exc} Later steps have not been checked."
            blocked = True
            continue
        if not valid:
            result.steps.append(StepResult(number, text, "First mistake", reason))
            result.status, result.first_error = "First mistake", number
            result.explanation = f"Line {number}: {reason}"
            blocked = True
        else:
            completed = completed or complete
            result.steps.append(StepResult(number, text, "Correct final answer" if complete else "Valid intermediate step", reason, complete))
    if supplied and not blocked:
        result.status = "Correct final answer" if completed else "Valid working — incomplete"
        result.explanation = ("Your working is correct and your final fractions add up to the original fraction." if completed
                              else "Your working is correct so far. To finish, find A and B and put their values back into the two fractions. An unfinished step is not a mistake.")
    return result


def _coefficient_correction(context):
    """Explain the already-established equations; no new validity decision."""
    equations = []
    for row in range(context.augmented.rows):
        lhs = context.augmented[row, 0]*A + context.augmented[row, 1]*B
        rhs = context.augmented[row, 2]
        equations.append("$" + sp.latex(sp.Eq(lhs, rhs, evaluate=False)) + "$")
    return ("This equation does not agree with the question using your A and B setup.\n\n"
            "**How to check it**\n\n"
            "After removing the fractions and opening the brackets, match the terms containing x on both sides. "
            "Then match the terms without x. If a side has no x term, its x coefficient is zero.\n\n"
            "Your setup gives these two equations: " + "; ".join(equations) + ". "
            "Use them to check your line. The worked solution below shows how to get the equations; you may also use a valid substitution method.")
