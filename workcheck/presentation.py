"""Student-facing rendering only; never changes checking decisions."""
import sympy as sp
from sympy.printing.latex import LatexPrinter

from .parser import A, B, X, Expression, question_expression
from .verification import domain_of, verify


class StudentLatexPrinter(LatexPrinter):
    def _print_Mul(self, expr):
        factors = [factor for factor in expr.args if factor != sp.S.One]
        if len(factors) != len(expr.args):
            return self._print(sp.Mul(*factors, evaluate=False))
        return super()._print_Mul(expr)

    def _as_ordered_terms(self, expr, order=None):
        terms = super()._as_ordered_terms(expr, order=order)
        # A stable partition keeps the printer's usual order within each sign.
        return ([term for term in terms if not term.could_extract_minus_sign()] +
                [term for term in terms if term.could_extract_minus_sign()])


def school_latex(expression):
    # SymPy separates adjacent numeric factors with a dot, while juxtaposing
    # symbolic factors. Keep its structural printer: string deletion could turn
    # 2*3 into 23 or destroy the meaning of exponent/denominator notation.
    return StudentLatexPrinter().doprint(expression)


def feedback_markdown(text):
    """Format authored mathematical feedback; leave input-syntax hints intact."""
    return text.replace("u'·v + u·v'", r"$u'v + uv'$")


def concise_restrictions(domain):
    if domain == sp.S.Reals:
        return r"x \in \mathbb{R}"
    excluded = sp.S.Reals - domain
    if isinstance(excluded, sp.FiniteSet):
        values = sorted(excluded, key=sp.default_sort_key, reverse=True)
        return r"x \ne " + r",\; ".join(school_latex(value) for value in values)
    if isinstance(domain, sp.Interval):
        if domain.end == sp.oo:
            return "x " + ("> " if domain.left_open else r"\ge ") + school_latex(domain.start)
        if domain.start == -sp.oo:
            return "x " + ("< " if domain.right_open else r"\le ") + school_latex(domain.end)
        return (school_latex(domain.start) + (" < x " if domain.left_open else r" \le x ") +
                ("< " if domain.right_open else r"\le ") + school_latex(domain.end))
    # More complex domains retain the exact general representation.
    return r"x \in " + school_latex(domain)


def _worked_step(instruction, rows):
    return {"instruction": instruction, "math": [math for math, _ in rows],
            "explanations": [explanation for _, explanation in rows]}


def _ordered_latex(expression):
    return StudentLatexPrinter({"order": "none"}).doprint(expression)


def _equation(left, right, *, ordered=False):
    printer = _ordered_latex if ordered else school_latex
    return printer(left) + " = " + printer(right)


def coefficient_solution(source, domain):
    """Verify setup, expansion, collection, elimination and back-substitution."""
    fraction = sp.cancel(source)
    _, denominator = sp.fraction(fraction)
    _, factors = sp.factor_list(denominator, X)
    if len(factors) != 2 or any(power != 1 or sp.degree(factor, X) != 1 for factor, power in factors):
        return []
    factors = sorted((factor for factor, _ in factors),
                     key=lambda factor: -sp.Poly(factor, X).nth(0)/sp.Poly(factor, X).nth(1), reverse=True)
    first, second = factors
    setup = A/first + B/second
    left = sp.cancel(fraction*first*second)
    right = sp.Add(A*second, B*first, evaluate=False)
    # Multiplying the ansatz by the factors gives the displayed right side.
    if sp.cancel(setup*first*second-right) != 0:
        return []
    left_poly, right_poly = sp.Poly(left, X), sp.Poly(right, X)
    equations = [sp.Eq(right_poly.nth(power), left_poly.nth(power), evaluate=False)
                 for power in (1, 0)]
    residuals = [equation.lhs-equation.rhs for equation in equations]
    matrix, values = sp.linear_eq_to_matrix(residuals, [A, B])
    solutions = sp.linsolve((matrix, values), [A, B])
    if not isinstance(solutions, sp.FiniteSet) or len(solutions) != 1:
        return []
    coefficients = next(iter(solutions))
    if any(value.free_symbols for value in coefficients):
        return []
    substitutions = dict(zip([A, B], coefficients))
    final = setup.subs(substitutions)
    # Check the solved system, cleared identity, and final rational identity.
    if any(sp.simplify(residual.subs(substitutions)) != 0 for residual in residuals):
        return []
    if sp.expand(right.subs(substitutions)-left) != 0:
        return []
    if verify(Expression(final), fraction, domain).status != "proved":
        return []
    expanded_terms = []
    for symbol, factor in ((A, second), (B, first)):
        poly = sp.Poly(factor, X)
        expanded_terms.extend([symbol*poly.nth(1)*X, symbol*poly.nth(0)])
    expanded = sp.Add(*expanded_terms, evaluate=False)
    collected = sp.Add(sp.Mul(right_poly.nth(1), X, evaluate=False), right_poly.nth(0), evaluate=False)
    if sp.expand(expanded-right) != 0 or sp.expand(collected-right) != 0:
        return []
    # Eliminate B using an exact linear combination of the coefficient equations.
    p, q = matrix[0, 0], matrix[0, 1]
    r, s = matrix[1, 0], matrix[1, 1]
    u, v = values[0], values[1]
    solve_rows = []
    if q != 0 and s != 0:
        def scaled(value, expression):
            return expression if value == 1 else school_latex(value) + r"\left(" + expression + r"\right)"
        lhs_text = (scaled(q, school_latex(equations[1].lhs)) + " - " +
                    scaled(s, school_latex(equations[0].lhs)))
        # Parentheses preserve the subtraction of each complete equation.
        if q == 1:
            lhs_text = r"\left(" + school_latex(equations[1].lhs) + r"\right) - " + scaled(s, school_latex(equations[0].lhs))
        if s == 1:
            lhs_text = lhs_text.rsplit(" - ", 1)[0] + r" - \left(" + school_latex(equations[0].lhs) + r"\right)"
        rhs_text = scaled(q, school_latex(v)) + " - " + scaled(s, school_latex(u))
        elim_left, elim_right = sp.expand(q*equations[1].lhs-s*equations[0].lhs), q*v-s*u
        if sp.expand((elim_left-elim_right)-(q*residuals[1]-s*residuals[0])) != 0:
            return []
        solve_rows.append((lhs_text + " = " + rhs_text, "Make the B terms equal by multiplying each whole equation if needed. Subtract one equation from the other: the B terms disappear."))
        if sp.simplify(elim_left-A) != 0 or sp.simplify(elim_right-substitutions[A]) != 0:
            solve_rows.append((_equation(elim_left, elim_right), "Combine the A terms on the left and work out the numbers on the right."))
    else:
        index = 0 if q == 0 else 1
        solve_rows.append((school_latex(equations[index]), "Only A is unknown in this equation. Rearrange it to find A."))
    solve_rows.append((_equation(A, substitutions[A]), "Divide both sides by the number multiplying A, if needed. This gives the value of A."))
    # Substitute into an equation whose B coefficient is nonzero.
    index = 0 if q != 0 else 1
    row = matrix.row(index)
    substituted_left = sp.Add(row[0]*substitutions[A], row[1]*B, evaluate=False)
    substituted_right = values[index]
    if sp.expand(substituted_left-substituted_right-residuals[index].subs(A, substitutions[A])) != 0:
        return []
    solve_rows.append((_equation(substituted_left, substituted_right, ordered=True),
                       "Put the value you found for A into an equation that still contains B."))
    reduced_left = row[1]*B
    reduced_right = sp.simplify(substituted_right-row[0]*substitutions[A])
    if sp.simplify(reduced_left-B) != 0:
        solve_rows.append((_equation(reduced_left, reduced_right), "Subtract the known number from both sides to leave only the B term on the left."))
    if sp.simplify(reduced_left.subs(substitutions)-reduced_right) != 0:
        return []
    solve_rows.append((_equation(B, substitutions[B]), "Rearrange to leave B on its own. Now both unknown numbers are known."))
    return [
        _worked_step("Set up", [(_equation(source, setup), "Split the denominator into its two factors. Put an unknown number, A or B, above each one; we will find these numbers next.")]),
        _worked_step("Multiply both sides by $" + school_latex(first*second) + "$", [
            (_equation(left, right), "Multiply every term on both sides by the same full denominator. The matching factors cancel, leaving an equation without fractions.")]),
        _worked_step("Expand and collect", [
            (_equation(left, expanded, ordered=True), "Open each bracket: multiply the number or letter outside by every term inside."),
            (school_latex(left) + r" = \left(" + school_latex(right_poly.nth(1)) + r"\right)x + \left(" + school_latex(right_poly.nth(0)) + r"\right)", "Put the terms containing x together. Put the terms without x together.")]),
        _worked_step("Compare coefficients", [
            (school_latex(equations[0]), "The expression multiplying x must be the same on both sides. If a side has no x term, its x coefficient is zero."),
            (school_latex(equations[1]), "The terms without x must also match on both sides. This gives the second equation.")]),
        _worked_step("Solve the simultaneous equations", solve_rows),
        _worked_step("Substitute", [
            (_equation(source, final), "Put the values of A and B back into the two fractions. This is the final answer."),
            (concise_restrictions(domain), "These x values made the original denominator zero, so they are still not allowed.")]),
    ]


def _derivative_rule(expression):
    D = lambda value: sp.Derivative(value, X, evaluate=False)
    if not expression.has(X):
        return sp.S.Zero, "This part is a fixed number. It does not change as x changes, so its derivative is zero."
    if expression == X:
        return sp.S.One, "The derivative of x is 1: when x increases by one, x itself also increases by one."
    if isinstance(expression, sp.Add):
        return sp.Add(*(D(term) for term in expression.args)), "Differentiate each term separately. Keep the plus or minus sign belonging to each term."
    if isinstance(expression, sp.Mul):
        constants = [factor for factor in expression.args if not factor.has(X)]
        variables = [factor for factor in expression.args if factor.has(X)]
        if constants:
            return sp.Mul(*constants)*D(sp.Mul(*variables)), "Keep the number multiplying this part unchanged. Differentiate only the expression containing x."
        return sp.Add(*(D(factor)*sp.Mul(*(other for j, other in enumerate(expression.args) if j != i))
                        for i, factor in enumerate(expression.args))), "Use the product rule. Make one term for each part: differentiate that part and leave the other parts unchanged. Add these terms."
    if isinstance(expression, sp.Pow) and expression.exp.is_Integer:
        base, power = expression.args
        explanation = (f"Power rule: bring the power {power} in front and lower the power by 1. "
                       "Keep what is inside the power unchanged for now, then multiply by its derivative.")
        return power*base**(power-1)*D(base), explanation
    argument = expression.args[0] if expression.args else None
    if expression.func == sp.sin:
        return sp.cos(argument)*D(argument), "Change sine to cosine and keep the same angle expression. Then multiply by the derivative of that angle expression."
    if expression.func == sp.cos:
        return -sp.sin(argument)*D(argument), "Change cosine to negative sine: do not lose the minus sign. Keep the same angle expression and multiply by its derivative."
    if expression.func == sp.exp:
        return sp.exp(argument)*D(argument), "Keep the exponential exactly as it is. Multiply it by the derivative of the expression in its power."
    if expression.func == sp.log:
        return D(argument)/argument, "Differentiate the expression inside ln. Put that derivative on top of a fraction, with the original inside expression underneath."
    return None, ""


def derivative_solution(source, domain, label):
    expression = source.doit()
    expected = sp.diff(expression, X)
    derivative_label = label + " = "
    current = sp.Derivative(expression, X, evaluate=False)
    rows = [(derivative_label + school_latex(current), "The d/dx symbol means 'differentiate with respect to x'. It shows a derivative we still need to work out.")]
    for _ in range(80):
        held = next((node for node in sp.preorder_traversal(current) if isinstance(node, sp.Derivative)), None)
        if held is None:
            break
        replacement, explanation = _derivative_rule(held.expr)
        if replacement is None:
            return []
        updated = current.xreplace({held: replacement})
        if updated == current or verify(Expression(updated), expected, domain).status != "proved":
            return []
        rows.append((derivative_label + school_latex(updated), "Focus on $" + school_latex(held.expr) + "$ in this line. " + explanation))
        current = updated
    if current.has(sp.Derivative) or verify(Expression(current), expected, domain).status != "proved":
        return []
    return [
        _worked_step("Start with the function", [(school_latex(source), "Start with the expression in the question. We want to find how it changes as x changes.")]),
        _worked_step("Differentiate step by step", rows),
        _worked_step("Write the final answer", [
            (derivative_label + school_latex(expected), "All the derivatives are now worked out. Combine terms if helpful; a different-looking answer is accepted when it has the same mathematical value."),
            (concise_restrictions(domain), "These are the x values for which this answer applies. Keep any limits from the original question and the derivative.")]),
    ]


def present_result(result, question, topic):
    """Attach display metadata, preserving raw answers and all checked statuses."""
    if not result.answer_latex:
        return result
    parsed = question_expression(question, topic=topic)
    domain = domain_of(parsed)
    if topic == "Partial fractions":
        answer = sp.apart(sp.cancel(parsed.expr), X)
    else:
        answer = sp.diff(parsed.expr.doit(), X)
        derivative_domain = domain_of(Expression(answer))
        if domain is not None and derivative_domain is not None:
            domain = domain.intersect(derivative_domain)
    # Only replace rendering of the very answer/domain already returned by the
    # checker. Never infer mathematical data by parsing the LaTeX strings.
    if sp.latex(answer) == result.answer_latex:
        result.answer_display_latex = school_latex(answer)
    if domain is not None and sp.latex(domain) == result.domain_latex:
        result.restrictions_display_latex = concise_restrictions(domain)
    if topic == "Partial fractions":
        result.worked_solution = coefficient_solution(parsed.expr, domain)
        result.worked_solution_title = "Worked solution · coefficient method"
        if not result.worked_solution:
            result.presentation_note = "A verified coefficient-method explanation is unavailable for this input."
    else:
        result.worked_solution = derivative_solution(parsed.expr, domain, result.derivative_label_latex)
        result.worked_solution_title = "Worked solution · differentiation"
        if not result.worked_solution:
            result.presentation_note = "A verified step-by-step explanation is unavailable for this input."
    return result
