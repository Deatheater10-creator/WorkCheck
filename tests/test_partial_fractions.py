import unittest
import sympy as sp
from workcheck.parser import A, B, X, InputIssue, parse_expression
from workcheck.partial_fractions import check_partial_fractions as check, parse_partial_line

QUESTION = "1/((x+1)*(x+2))"
SETUP = "A/(x+1)+B/(x+2)"
FINAL = "1/(x+1)-1/(x+2)"


class PartialFractionTests(unittest.TestCase):
    def test_partial_coefficient_substitution_remains_intermediate(self):
        result = check(QUESTION, [SETUP, "A=1", "1/(x+1)+B/(x+2)"])
        self.assertEqual(result.status, "Valid working — incomplete")
        self.assertFalse(result.steps[-1].complete)
        self.assertEqual(check(QUESTION, [SETUP, "2/(x+1)+B/(x+2)"]).first_error, 2)
        self.assertEqual(check(QUESTION, [SETUP, "1/(x+1)+B/(x+2)", FINAL]).status, "Correct final answer")
    def test_full_prd_example(self):
        lines = [SETUP, "1=A*(x+2)+B*(x+1)", "A+B=0", "2*A+B=1", "A=1", "B=-1", FINAL]
        result = check(QUESTION, lines)
        self.assertEqual(result.status, "Correct final answer")
        self.assertEqual([step.complete for step in result.steps], [False]*6+[True])
        self.assertEqual(result.derivative_label_latex, "")

    def test_valid_unfinished_equations_and_values(self):
        for extra in [[], ["A+B=0"], ["A=1"], ["A=1", "B=-1"]]:
            with self.subTest(extra=extra):
                result = check(QUESTION, [SETUP]+extra)
                self.assertEqual(result.status, "Valid working — incomplete")
                self.assertTrue(all(s.status == "Valid intermediate step" for s in result.steps))

    def test_wrong_coefficient_is_first_error(self):
        result = check(QUESTION, [SETUP, "A+B=1", FINAL])
        self.assertEqual(result.first_error, 2)
        self.assertEqual(result.steps[-1].status, "Not checked")

    def test_wrong_value_is_first_error(self):
        self.assertEqual(check(QUESTION, [SETUP, "A=-1", "B=-1"]).first_error, 2)

    def test_wrong_cleared_identity(self):
        self.assertEqual(check(QUESTION, [SETUP, "1=A*(x+1)+B*(x+2)"]).first_error, 2)

    def test_missing_context_blocks_later_error(self):
        result = check(QUESTION, ["A+B=0", "A+B=1"])
        self.assertEqual(result.status, "Needs clarification")
        self.assertEqual(result.blocked_at, 1)
        self.assertIsNone(result.first_error)
        self.assertEqual(result.steps[1].status, "Not checked")

    def test_equivalent_scaled_and_reordered_constraints(self):
        result = check(QUESTION, [SETUP, "-4*A-2*B=-2", "2*A+2*B=0", "1=2*A+B", FINAL])
        self.assertEqual(result.status, "Correct final answer")

    def test_coefficient_order_matches_student_assignments(self):
        result = check(QUESTION, ["B/(x+1)+A/(x+2)", "A+B=0", "A+2*B=1", "B=1", "A=-1", FINAL])
        self.assertEqual(result.status, "Correct final answer")
        self.assertEqual(check(QUESTION, ["B/(x+1)+A/(x+2)", "A=1"]).first_error, 2)

    def test_setup_can_be_equated_to_original_in_either_order(self):
        for line in [QUESTION+"="+SETUP, SETUP+"="+QUESTION]:
            with self.subTest(line=line):
                self.assertEqual(check(QUESTION, [line, "A+B=0"]).status, "Valid working — incomplete")

    def test_root_substitution_prefixes(self):
        result = check(QUESTION, [SETUP, "x=-1: 1=A", "x=-2: 1=-B", FINAL])
        self.assertEqual(result.status, "Correct final answer")
        self.assertEqual(check(QUESTION, [SETUP, "x=-1: 1=-A"]).first_error, 2)

    def test_separate_root_selection_and_specialization(self):
        result = check(QUESTION, [SETUP, "x=-1", "1=A*(x+2)+B*(x+1)", "A=1",
                                  "x=-2", "1=A*(x+2)+B*(x+1)", "B=-1", FINAL])
        self.assertEqual(result.status, "Correct final answer")

    def test_root_requires_setup_and_supported_root(self):
        self.assertEqual(check(QUESTION, ["x=-1: 1=A"]).status, "Needs clarification")
        self.assertEqual(check(QUESTION, [SETUP, "x=5: 1=A"]).status, "Needs clarification")

    def test_nonlinear_coefficient_equation_is_unsupported_not_wrong(self):
        result = check(QUESTION, [SETUP, "A*B=-1", FINAL])
        self.assertEqual(result.status, "Needs clarification")
        self.assertEqual(result.blocked_at, 2)
        self.assertIsNone(result.first_error)

    def test_coefficient_denominators_request_clarification(self):
        self.assertEqual(check(QUESTION, [SETUP, "A/A=1"]).status, "Needs clarification")
        self.assertEqual(check(QUESTION, [SETUP, "x=-1: 1/(x+1)=A"]).status, "Needs clarification")

    def test_changed_assignments_need_clarification(self):
        self.assertEqual(check(QUESTION, [SETUP, "B/(x+1)+A/(x+2)"]).status, "Needs clarification")

    def test_wrong_setup_factors_are_mathematical_error(self):
        self.assertEqual(check(QUESTION, ["A/(x+1)+B/(x+3)"]).first_error, 1)

    def test_incomplete_or_nonlinear_setup_needs_clarification(self):
        for line in ["A/(x+1)", "A/(x+1)+A/(x+2)", "A*B/(x+1)+B/(x+2)"]:
            with self.subTest(line=line):
                self.assertEqual(check(QUESTION, [line]).status, "Needs clarification")

    def test_unfinished_source_copy_is_valid(self):
        self.assertEqual(check(QUESTION, [QUESTION]).status, "Valid working — incomplete")

    def test_numeric_final_without_setup(self):
        self.assertEqual(check(QUESTION, [FINAL]).status, "Correct final answer")
        self.assertEqual(check(QUESTION, ["-1/(x+1)+1/(x+2)"]).first_error, 1)

    def test_final_equality_after_context_either_direction(self):
        for final in [QUESTION+"="+FINAL, FINAL+"="+QUESTION]:
            with self.subTest(final=final):
                self.assertEqual(check(QUESTION, [SETUP, "A=1", "B=-1", final]).status, "Correct final answer")

    def test_correct_final_does_not_erase_earlier_error(self):
        self.assertEqual(check(QUESTION, [SETUP, "A=2", FINAL]).first_error, 2)

    def test_final_cannot_introduce_domain_holes(self):
        result = check(QUESTION, ["(x-3)/((x-3)*(x+1))-1/(x+2)"])
        self.assertEqual(result.status, "Needs clarification")

    def test_setup_cannot_introduce_domain_holes(self):
        result = check(QUESTION, ["A*(x-3)/((x-3)*(x+1))+B/(x+2)"])
        self.assertEqual(result.status, "Needs clarification")

    def test_original_domain_holes_are_retained(self):
        source = "(x-3)/((x-3)*(x+1)*(x+2))"
        result = check(source, [FINAL])
        self.assertEqual(result.status, "Correct final answer")
        self.assertIn("3", result.domain_latex)

    def test_linear_numerator_and_nonmonic_factors(self):
        source = "(2x+3)/((2x+1)*(x+2))"
        lines = ["A/(2x+1)+B/(x+2)", "A+2B=2", "2A+B=3", "A=4/3", "B=1/3",
                 "(4/3)/(2x+1)+(1/3)/(x+2)"]
        self.assertEqual(check(source, lines).status, "Correct final answer")
        original = (2*X+3)/((2*X+1)*(X+2))
        expected = sp.Rational(4, 3)/(2*X+1)+sp.Rational(1, 3)/(X+2)
        self.assertEqual(sp.cancel(original-expected), 0)

    def test_scaled_setup_denominators(self):
        result = check(QUESTION, ["A/(2x+2)+B/(3x+6)", "A=2", "B=-3", FINAL])
        self.assertEqual(result.status, "Correct final answer")

    def test_unattempted_question_solves(self):
        result = check(QUESTION, [])
        self.assertEqual(result.status, "Solution")
        self.assertTrue(result.answer_latex)
        self.assertEqual(result.derivative_label_latex, "")

    def test_unsupported_questions_are_not_student_errors(self):
        for question in ["x^2", "0", "(x^2+1)/(x+1)", "1/(x+1)^2", "1/(x^2+1)",
                         "1/((x+1)*(x+2)*(x+3))", "1/(x^2-2)", "sin(x)"]:
            with self.subTest(question=question):
                self.assertEqual(check(question, []).status, "Needs clarification")

    def test_shared_limits_and_unsafe_syntax(self):
        for lines in [[SETUP]*21, ["x"*501], ["__import__('os')"], ["A.__class__=1"]]:
            with self.subTest(lines=str(lines)[:30]):
                self.assertEqual(check(QUESTION, lines).status, "Needs clarification")
        with self.assertRaises(InputIssue):
            parse_expression("A+B")
        self.assertEqual(parse_expression("2A+B", allow_coefficients=True).expr.doit(), 2*A+B)

    def test_blank_lines_keep_visible_error_number(self):
        self.assertEqual(check(QUESTION, [SETUP, "", "A+B=1"]).first_error, 3)

    def test_parse_root_notation_and_invalid_prefix(self):
        self.assertEqual(parse_partial_line("x=-1: 1=A").root, -1)
        with self.assertRaises(InputIssue):
            parse_partial_line("substitute: 1=A")
