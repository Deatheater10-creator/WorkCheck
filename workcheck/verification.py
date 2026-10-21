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
        return Proof("unknown", "I cannot check which real values of x are allowed in this step. I have not marked it wrong; please clarify the expression or its restrictions.")
    if required_domain is sp.S.EmptySet:
        return Proof("unknown", "I cannot find any allowed real values of x for the original expression using this version's rules.")
    try:
        contained = required_domain.is_subset(candidate_domain)
    except (NotImplementedError, TypeError):
        contained = None
    if contained is not True:
        return Proof("unknown", "This step may rule out x values that the original question allows. Check for a new denominator or logarithm and explain any extra restrictions. I cannot verify this step yet.")
    actual = candidate.expr.doit()
    if actual.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        return Proof("unknown", "This expression contains an undefined or infinite value.")
    difference = sp.trigsimp(sp.cancel(sp.together(actual - expected)))
    difference = sp.simplify(difference)
    if difference == 0:
        return Proof("proved", "The expressions have the same value for all x values allowed in the question.")
    if difference.is_rational_function(X) and required_domain.is_finite_set is False:
        numerator, _ = sp.fraction(sp.cancel(difference))
        if sp.Poly(numerator, X).is_zero is False:
            return Proof("disproved", "The expressions do not have the same value for all x values allowed in the question.")
    # A disproved exact value is a counterexample. Floating samples are never used.
    for point in (sp.Integer(0), sp.Integer(1), sp.Integer(-1), sp.Integer(2), sp.Integer(-2), sp.Rational(1, 2)):
        if required_domain.contains(point) is sp.S.true:
            value = sp.simplify(difference.subs(X, point))
            if not value.has(sp.zoo, sp.nan, sp.oo, -sp.oo) and value.is_zero is False:
                return Proof("disproved", f"The expressions give different values when $x = {sp.latex(point)}$. That shows they are not the same expression.")
    return Proof("unknown", "I cannot confirm whether these expressions are equal using this version's rules. This is a checking limit, not a wrong-answer verdict.")
