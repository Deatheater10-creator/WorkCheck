from dataclasses import asdict
import unittest
import sympy as sp

from workcheck.checking import check_partial_fractions, check_differentiation
from workcheck.parser import X, parse_expression
from workcheck.presentation import school_latex, concise_restrictions, present_result, coefficient_solution

QUESTION = "1/((x+1)*(x+2))"
DISPLAY = r"\frac{1}{x + 1} - \frac{1}{x + 2}"


class PresentationTests(unittest.TestCase):
    def test_structural_school_notation_and_numeric_multiplication(self):
        examples = {
            "2*x": "2 x",
            "A*(x+2)": r"A \left(x + 2\right)",
            "3*(x+1)^2": r"3 \left(x + 1\right)^{2}",
            "x**2": "x^{2}",
            "1/(x+1)": r"\frac{1}{x + 1}",
            "2*3": r"2 \cdot 3",
            "2*(3*x)": r"2 \cdot 3 x",
        }
        for raw, expected in examples.items():
            with self.subTest(raw=raw):
                parsed = parse_expression(raw, allow_coefficients=True)
                before = sp.srepr(parsed.expr)
                self.assertEqual(school_latex(parsed.expr), expected)
                self.assertEqual(sp.srepr(parsed.expr), before)

    def test_preview_omits_redundant_unit_multiplier_without_evaluating_D(self):
        raw = parse_expression("1/((x+1)*(x+2))")
        self.assertEqual(school_latex(raw.expr), r"\frac{1}{\left(x + 1\right) \left(x + 2\right)}")
        held = parse_expression("1*D(x^2)", allow_d=True)
        self.assertIn(r"\frac{d}{d x}", school_latex(held.expr))
        self.assertTrue(held.held)
    def test_positive_fraction_before_negative(self):
        expression = -1/(X+2) + 1/(X+1)
        self.assertEqual(school_latex(expression), DISPLAY)
        self.assertEqual(sp.cancel(expression-1/((X+1)*(X+2))), 0)

    def test_negative_source_still_positive_first(self):
        expression = 1/(X+2)-1/(X+1)
        self.assertEqual(school_latex(expression), r"\frac{1}{x + 2} - \frac{1}{x + 1}")

    def test_isolated_exclusions_are_compact_and_exact(self):
        domain = sp.S.Reals-sp.FiniteSet(-1, -2)
        self.assertEqual(concise_restrictions(domain), r"x \ne -1,\; -2")
        self.assertEqual(concise_restrictions(sp.S.Reals), r"x \in \mathbb{R}")
        self.assertIn("3", concise_restrictions(domain-sp.FiniteSet(3)))

    def test_inequalities_not_replaced_by_exclusions(self):
        self.assertEqual(concise_restrictions(sp.Interval.open(0, sp.oo)), "x > 0")
        self.assertEqual(concise_restrictions(sp.Interval(-sp.oo, 2)), r"x \le 2")
        self.assertEqual(concise_restrictions(sp.Interval.Lopen(0, 2)), r"0 < x \le 2")
        complex_domain = sp.Union(sp.Interval(-sp.oo, -1), sp.Interval(1, sp.oo))
        self.assertTrue(concise_restrictions(complex_domain).startswith(r"x \in "))

    def test_requested_six_step_coefficient_method(self):
        result = present_result(check_partial_fractions(QUESTION, []), QUESTION, "Partial fractions")
        self.assertEqual(result.answer_display_latex, DISPLAY)
        self.assertEqual(result.restrictions_display_latex, r"x \ne -1,\; -2")
        self.assertEqual(len(result.worked_solution), 6)
        steps = result.worked_solution
        self.assertIn(" = ", steps[0]["math"][0])
        self.assertEqual(steps[1]["math"], [r"1 = A \left(x + 2\right) + B \left(x + 1\right)"])
        self.assertEqual(steps[2]["math"], [r"1 = A x + 2 A + B x + B", r"1 = \left(A + B\right)x + \left(2 A + B\right)"])
        self.assertEqual(steps[3]["math"], ["A + B = 0", "2 A + B = 1"])
        self.assertEqual(steps[4]["math"], [r"\left(2 A + B\right) - \left(A + B\right) = 1 - 0", "A = 1", "1 + B = 0", "B = -1"])
        self.assertTrue(steps[5]["math"][0].endswith(DISPLAY))
        for step in steps:
            self.assertEqual(len(step["math"]), len(step["explanations"]))
            self.assertTrue(all(step["explanations"]))

    def test_equivalent_answers_remain_accepted_and_checking_data_unchanged(self):
        alternatives = ["1/(x+1)-1/(x+2)", "-1/(x+2)+1/(x+1)",
                        "(2/2)/(x+1)-(3/3)/(x+2)"]
        for answer in alternatives:
            with self.subTest(answer=answer):
                result = check_partial_fractions(QUESTION, [answer])
                before = asdict(result)
                present_result(result, QUESTION, "Partial fractions")
                after = asdict(result)
                for key in ("status", "explanation", "steps", "answer_latex", "domain_latex", "first_error", "blocked_at"):
                    self.assertEqual(after[key], before[key])
                self.assertEqual(result.status, "Correct final answer")
                self.assertEqual(result.answer_display_latex, DISPLAY)

    def test_error_and_uncertainty_statuses_unchanged(self):
        for lines, status in [(["A/(x+1)+B/(x+2)", "A+B=1"], "First mistake"),
                              (["A+B=0"], "Needs clarification")]:
            result = present_result(check_partial_fractions(QUESTION, lines), QUESTION, "Partial fractions")
            self.assertEqual(result.status, status)
            self.assertEqual(len(result.worked_solution), 6)

    def test_original_cancelled_hole_preserved_in_display(self):
        question = "(x-3)/((x-3)*(x+1)*(x+2))"
        result = present_result(check_partial_fractions(question, []), question, "Partial fractions")
        self.assertEqual(result.restrictions_display_latex, r"x \ne 3,\; -1,\; -2")

    def test_general_coefficient_examples_are_verified_before_display(self):
        for question in ["(2x+3)/((2x+1)*(x+2))", "1/(4*(x+1)*(x+2))", "-1/((x+1)*(x+2))"]:
            with self.subTest(question=question):
                result = present_result(check_partial_fractions(question, []), question, "Partial fractions")
                self.assertEqual(len(result.worked_solution), 6)
        self.assertEqual(coefficient_solution(1/(X+1)**2, sp.S.Reals-sp.FiniteSet(-1)), [])

    def test_derivative_label_and_log_domain_preserved(self):
        result = present_result(check_differentiation("f(x)=ln(x)", []), "f(x)=ln(x)", "Differentiation")
        self.assertEqual(result.derivative_label_latex, "f'(x)")
        self.assertEqual(result.restrictions_display_latex, "x > 0")
        self.assertEqual(len(result.worked_solution), 3)

    def test_actual_differentiation_work_for_supported_rules(self):
        for question in ["x^2*(x+1)", "(x^2+1)^3", "x^2*sin(x)", "exp(2x)", "ln(x^2+1)", "cos(3x)", "7", "(2x+3)^4", "(x^2-5x)^3"]:
            with self.subTest(question=question):
                result = present_result(check_differentiation(question, []), question, "Differentiation")
                self.assertEqual(len(result.worked_solution), 3)
                working = result.worked_solution[1]
                self.assertGreaterEqual(len(working["math"]), 2)
                self.assertEqual(len(working["math"]), len(working["explanations"]))
                self.assertTrue(all(working["explanations"]))

    def test_partial_fraction_actual_coefficients_and_zero_root(self):
        for question in ["(3x+7)/((x+2)*(x+5))", "1/(x*(2x+3))", "(x+1)/((2x-1)*(3x+2))"]:
            with self.subTest(question=question):
                result = present_result(check_partial_fractions(question, []), question, "Partial fractions")
                self.assertEqual(len(result.worked_solution), 6)
                self.assertIn(" = ", result.worked_solution[2]["math"][0])
                self.assertGreaterEqual(len(result.worked_solution[4]["math"]), 4)
