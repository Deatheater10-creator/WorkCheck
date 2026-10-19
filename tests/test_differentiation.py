import unittest
from workcheck.checking import check_differentiation as check


class DifferentiationTests(unittest.TestCase):
    def test_five_prd_examples(self):
        examples = [
            ("x^2*(x+1)", "3*x^2+2*x"),
            ("(x^2+1)^3", "6*x*(x^2+1)^2"),
            ("x^2*sin(x)", "2*x*sin(x)+x^2*cos(x)"),
            ("exp(2*x)", "2*exp(2*x)"),
            ("ln(x^2+1)", "2*x/(x^2+1)"),
        ]
        for question, answer in examples:
            with self.subTest(question=question):
                self.assertEqual(check(question, [answer]).status, "Correct final answer")

    def test_student_example_first_error(self):
        r = check("x^2*sin(x)", ["y = x^2*sin(x)", "dy/dx = (2*x)*cos(x)", "dy/dx = 2*x*cos(x)"])
        self.assertEqual(r.first_error, 2)
        self.assertIn("product rule", r.explanation)
        self.assertEqual(r.steps[0].status, "Valid intermediate step")
        self.assertEqual(r.steps[2].status, "Not checked")

    def test_unfinished_work(self):
        for line in ["y=x^2*sin(x)", "dy/dx=D(x^2*sin(x))", "dy/dx=D(x^2)*sin(x)+x^2*D(sin(x))"]:
            with self.subTest(line=line):
                r = check("x^2*sin(x)", [line])
                self.assertEqual(r.status, "Valid working — incomplete")
                self.assertFalse(r.steps[0].complete)

    def test_unfinished_chain_rule(self):
        r = check("(x^2+1)^3", ["dy/dx = 3*(x^2+1)^2*D(x^2+1)"])
        self.assertEqual(r.status, "Valid working — incomplete")

    def test_wrong_unfinished_step(self):
        r = check("x^2*sin(x)", ["dy/dx = D(x^2)*D(sin(x))"])
        self.assertEqual(r.status, "First mistake")

    def test_complete_unsimplified(self):
        self.assertEqual(check("x^2*(x+1)", ["2*x*(x+1)+x^2*1"]).status, "Correct final answer")

    def test_alternative_expanded_method(self):
        r = check("x^2*(x+1)", ["y=x^3+x^2", "dy/dx=3*x^2+2*x"])
        self.assertEqual(r.status, "Correct final answer")

    def test_valid_then_completed(self):
        r = check("x^2", ["dy/dx=D(x^2)", "dy/dx=2*x"])
        self.assertEqual(r.status, "Correct final answer")
        self.assertFalse(r.steps[0].complete)
        self.assertTrue(r.steps[1].complete)

    def test_original_copy_alone_not_completion(self):
        self.assertEqual(check("x^2", ["y=x^2"]).status, "Valid working — incomplete")

    def test_correct_final_does_not_erase_error(self):
        r = check("x^2", ["3*x", "2*x"])
        self.assertEqual(r.status, "First mistake")
        self.assertEqual(r.first_error, 1)
        self.assertEqual(r.steps[1].status, "Not checked")

    def test_unclear_earlier_line_blocks_error(self):
        r = check("x^2", ["f'(x) = 2*x", "3*x"])
        self.assertEqual(r.status, "Needs clarification")
        self.assertIsNone(r.first_error)
        self.assertEqual(r.blocked_at, 1)
        self.assertEqual(r.steps[1].status, "Not checked")

    def test_wrong_function_statement(self):
        self.assertEqual(check("x^2", ["y=x^3"]).first_error, 1)

    def test_y_line_cannot_hold_derivative(self):
        self.assertEqual(check("x^2", ["y=D(x^2)"]).status, "Needs clarification")

    def test_explicit_D_equality(self):
        self.assertEqual(check("x^2", ["D(x^2)=2*x"]).status, "Correct final answer")
        self.assertEqual(check("x^2", ["D(x^3)=3*x^2"]).status, "Needs clarification")

    def test_no_work_solves_without_verdict(self):
        r = check("x^2", [])
        self.assertEqual(r.status, "Solution")
        self.assertTrue(r.answer_latex)
        self.assertEqual(check("x^2", ["", " "]).status, "Solution")

    def test_empty_question(self):
        self.assertEqual(check("", []).status, "Needs clarification")

    def test_limits_preserve_inputs(self):
        lines = ["x"]*21
        before = lines.copy()
        self.assertEqual(check("x^2", lines).status, "Needs clarification")
        self.assertEqual(lines, before)
        text = "x"*501
        self.assertEqual(check("x^2", [text]).status, "Needs clarification")
        self.assertEqual(len(text), 501)

    def test_original_exclusions_preserved(self):
        r = check("(x^2-1)/(x-1)", ["1"])
        self.assertEqual(r.status, "Correct final answer")
        self.assertNotEqual(r.domain_latex, r"\mathbb{R}")

    def test_extra_candidate_hole_is_uncertain(self):
        r = check("x^2", ["2*x*(x-1)/(x-1)"])
        self.assertEqual(r.status, "Needs clarification")

    def test_log_valid_domain(self):
        self.assertEqual(check("ln(x)", ["1/x"]).status, "Correct final answer")

    def test_reordering_changes_first_error(self):
        self.assertEqual(check("x^2", ["2*x", "3*x"]).first_error, 2)
        self.assertEqual(check("x^2", ["3*x", "2*x"]).first_error, 1)

    def test_blank_lines_keep_visible_numbers(self):
        self.assertEqual(check("x^2", ["", "3*x"]).first_error, 2)
