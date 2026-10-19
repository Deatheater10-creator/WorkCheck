"""Conservative exact proofs; numerical agreement is never proof."""
import sympy as sp
from sympy.calculus.util import continuous_domain
from .models import Proof
from .parser import X, Expression


def domain_of(parsed: Expression):
    try:
        evaluated = parsed.expr.doit()
        domain = continuous_domain(evaluated, X, sp.S.Reals)
        for kind, expression in parsed.restrictions:
            expression = expression.doit()
            if kind == "nonzero":
                zeros = sp.solveset(expression, X, domain=sp.S.Reals)
                if zeros.has(sp.ConditionSet):
                    return None
                domain = domain - zeros
            else:
                permitted = sp.solve_univariate_inequality(expression > 0, X, relational=False)
                domain = domain.intersect(permitted)
        if domain.has(sp.ConditionSet):
            return None
        return domain
    except (NotImplementedError, ValueError, TypeError, RecursionError):
        return None


def verify(candidate: Expression, expected, required_domain):
    candidate_domain = domain_of(candidate)
    if required_domain is None or candidate_domain is None:
        return Proof("unknown", "I cannot establish the real-valued domain for this step.")
    if required_domain is sp.S.EmptySet:
        return Proof("unknown", "The original expression has no supported real-valued domain.")
    try:
        contained = required_domain.is_subset(candidate_domain)
    except (NotImplementedError, TypeError):
        contained = None
    if contained is not True:
        return Proof("unknown", "This step may change the domain. Please clarify the restrictions before checking.")
    actual = candidate.expr.doit()
    if actual.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        return Proof("unknown", "This expression contains an undefined or infinite value.")
    difference = sp.trigsimp(sp.cancel(sp.together(actual - expected)))
    difference = sp.simplify(difference)
    if difference == 0:
        return Proof("proved", "Verified by exact symbolic equality on the original domain.")
    if difference.is_rational_function(X) and required_domain.is_finite_set is False:
        numerator, _ = sp.fraction(sp.cancel(difference))
        if sp.Poly(numerator, X).is_zero is False:
            return Proof("disproved", "The exact rational difference is nonzero on the original domain.")
    # A disproved exact value is a counterexample. Floating samples are never used.
    for point in (sp.Integer(0), sp.Integer(1), sp.Integer(-1), sp.Integer(2), sp.Integer(-2), sp.Rational(1, 2)):
        if required_domain.contains(point) is sp.S.true:
            value = sp.simplify(difference.subs(X, point))
            if not value.has(sp.zoo, sp.nan, sp.oo, -sp.oo) and value.is_zero is False:
                return Proof("disproved", f"The expressions differ at x = {point} (exact symbolic counterexample).")
    return Proof("unknown", "I could not prove or disprove this expression with the supported exact rules.")
