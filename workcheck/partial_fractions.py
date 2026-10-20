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
        raise InputIssue("This version supports rational polynomials with exact rational coefficients.") from None


def _roots(expression):
    numerator, denominator = _rational_polynomials(expression)
    if numerator.is_zero or numerator.degree() >= denominator.degree():
        raise InputIssue("Use a nonzero proper fraction: its numerator degree must be smaller than its denominator degree.")
    _, factors = sp.factor_list(denominator.as_expr(), X)
    if len(factors) != 2 or any(power != 1 or sp.degree(factor, X) != 1 for factor, power in factors):
        raise InputIssue("Supported partial fractions need two distinct rational linear factors; repeated or quadratic factors are not supported yet.")
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
        raise InputIssue("I cannot establish a unique coefficient context for this setup.")
    solution = next(iter(sp.linsolve((matrix, values), [A, B])))
    substitution = dict(zip([A, B], solution))
    # Retain restrictions from the raw setup, including holes cancelled by algebra.
    substituted = Expression(parsed.expr.subs(substitution),
                             [(kind, expr.subs(substitution)) for kind, expr in parsed.restrictions])
    proof = verify(substituted, source, domain)
    if proof.status != "proved":
        raise InputIssue("I cannot verify this setup on the original domain. " + proof.reason)
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
        raise InputIssue("Clear denominators first; this checker supports polynomial identities and linear coefficient equations.") from None
    root = line.root if line.root is not None else context.root
    if root is not None:
        residual = residual.subs(X, root)
    try:
        relations = sp.Poly(sp.expand(residual), X).all_coeffs()
        matrix, values = sp.linear_eq_to_matrix(relations, [A, B])
    except (sp.PolynomialError, NonlinearError, ValueError):
        raise InputIssue("I can verify linear equations in A and B here; please clarify this nonlinear step.") from None
    target = matrix.row_join(values)
    return context.augmented.col_join(target).rank() == context.augmented.rank()


def check_partial_fractions(question, lines):
    try:
        parsed_source = question_expression(question)
        source = sp.cancel(parsed_source.expr)
        roots = _roots(source)
        domain = domain_of(parsed_source)
        if domain is None or domain is sp.S.EmptySet:
            raise InputIssue("I cannot verify the original real domain for this question.")
        if len(lines) > MAX_STEPS:
            raise InputIssue("The 20-working-line limit is exceeded. Your working is kept.")
    except InputIssue as exc:
        return CheckResult("Needs clarification", str(exc), derivative_label_latex="")
    result = CheckResult("Solution", "No attempted working was supplied. Here is the partial-fraction decomposition.",
                         answer_latex=sp.latex(sp.apart(source, X)), domain_latex=sp.latex(domain), derivative_label_latex="")
    context = None
    completed, supplied, blocked = False, False, False
    for number, text in enumerate(lines, 1):
        if not text.strip():
            continue
        supplied = True
        if blocked:
            result.steps.append(StepResult(number, text, "Not checked", "Resolve the earlier incorrect or unclear line first."))
            continue
        complete, valid, reason = False, True, ""
        try:
            line = parse_partial_line(text)
            if line.root is not None:
                if context is None:
                    raise InputIssue("Establish the A/B decomposition setup before selecting a denominator root.")
                if line.root not in roots:
                    raise InputIssue("This version supports substitution at the question's denominator roots. Please clarify this substitution.")
            if line.root_marker:
                context.root = line.root
                reason = f"Selected x={line.root} for substitution in the denominator-cleared identity. This is not a final answer."
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
                        reason = ("This partial substitution agrees exactly with the original coefficient system. A coefficient remains unresolved in the written expression, so this is valid but incomplete."
                                  if valid else "This partial substitution is not equivalent to the original fraction with your established coefficient assignments.")
                    else:
                        new_context = _setup(setup, source, roots, domain)
                        if context is not None and sp.cancel(context.setup-new_context.setup) != 0:
                            raise InputIssue("These A/B assignments differ from the earlier setup. Start a new attempt or clarify the change.")
                        context = new_context
                        reason = "Valid decomposition setup. A and B are assigned to these denominator terms; their values and the final decomposition remain to be found."
                elif candidates or (context is not None and line.left is not None and not numeric_equation):
                    if line.left is None:
                        raise InputIssue("Enter a complete equation for this coefficient step.")
                    valid = _coefficient_equation(line, context)
                    reason = ("This equation follows exactly from the original question and the assigned coefficient system. It is valid intermediate working, not a completed decomposition."
                              if valid else "This equation does not follow from the original question with your A/B denominator assignments. Recheck coefficient comparison or root substitution.")
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
                    reason = ("The equivalent sum of resolved simple fractions completes the decomposition." if complete
                              else "This expression is equivalent to the original fraction, but it is not yet a resolved partial-fraction sum." if valid
                              else "This expression is not equivalent to the original fraction on its domain.")
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
        result.explanation = ("All supplied steps are valid and the partial-fraction decomposition is complete." if completed
                              else "Your working is valid so far. Coefficient equations and values are intermediate steps; finish with the resolved partial-fraction sum.")
    return result
