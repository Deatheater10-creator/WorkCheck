import unittest
from unittest.mock import patch
import sympy as sp
from workcheck.parser import X, question_expression
from workcheck.practice import Candidate, FALLBACK, build_learning, verify_candidate
from workcheck.explanations import concepts_for


class PracticeTests(unittest.TestCase):
    def test_independent_hand_calculated_answers_and_domains(self):
        fixtures = [
            ("x^2*sin(x)", "2*x*sin(x)+x^2*cos(x)", sp.S.Reals),
            ("(2*x+3)^4", "8*(2*x+3)^3", sp.S.Reals),
            ("cos(3*x)", "-3*sin(3*x)", sp.S.Reals),
            ("exp(2*x)", "2*exp(2*x)", sp.S.Reals),
            ("ln(2*x+1)", "2/(2*x+1)", sp.Interval.open(-sp.Rational(1, 2), sp.oo)),
        ]
        from workcheck.presentation import concise_restrictions
        for question, answer, domain in fixtures:
            with self.subTest(question=question):
                item = verify_candidate(Candidate(question, answer), "Differentiation")
                self.assertIsNotNone(item)
                self.assertEqual(item["restrictions_latex"], concise_restrictions(domain))
                self.assertGreater(len(item["worked_solution"][1]["math"]), 1)
        item = verify_candidate(Candidate("1/((x+1)*(x+2))", "1/(x+1)-1/(x+2)"), "Partial fractions")
        self.assertEqual(item["restrictions_latex"], r"x \ne -1,\; -2")
        self.assertEqual(item["worked_solution"][3]["math"], ["A + B = 0", "2 A + B = 1"])
        self.assertEqual(item["worked_solution"][4]["math"][-1], "B = -1")

    def test_every_hand_checked_replacement_is_reverified(self):
        for concept, fixtures in FALLBACK.items():
            topic = "Partial fractions" if concept == "partial" else "Differentiation"
            for question, answer in fixtures:
                with self.subTest(concept=concept, question=question):
                    self.assertIsNotNone(verify_candidate(Candidate(question, answer), topic))

    def test_three_distinct_targeted_problems_and_separate_example(self):
        for question, concept in [("x^2*sin(x)", "product"), ("(2*x+3)^4", "chain"),
                                  ("x^3+1", "power"), ("cos(2*x)", "trig"),
                                  ("ln(x+1)", "log"), ("exp(3*x)", "exp"),
                                  ("1/((x+1)*(x+2))", "partial")]:
            topic = "Partial fractions" if concept == "partial" else "Differentiation"
            with self.subTest(concept=concept):
                pack = build_learning(question, topic)
                self.assertEqual(len(pack.practice), 3)
                self.assertFalse(pack.message)
                self.assertTrue(pack.concepts)
                items = [pack.example]+pack.practice
                self.assertEqual(len({item["question"] for item in items}), 4)
                for item in items:
                    self.assertTrue(item["verified"])
                    self.assertTrue(item["restrictions_latex"])
                    expression = question_expression(item["question"]).expr.doit()
                    self.assertEqual(concepts_for(expression, topic)[0], concept)
                    self.assertNotEqual(sp.simplify(expression-question_expression(question).expr.doit()), 0)
                    for step in item["worked_solution"]:
                        self.assertEqual(len(step["math"]), len(step["explanations"]))
                        self.assertTrue(all("*" not in row for row in step["math"]))

    def test_bad_answer_bad_intermediate_and_extra_hole_are_rejected(self):
        cases = [Candidate("x^2", "2*x+1/1000000"),
                 Candidate("x^2", "(2*x*(x-1))/(x-1)"),
                 Candidate("x^2", "2*x", ("3*x", "2*x"))]
        for candidate in cases:
            self.assertIsNone(verify_candidate(candidate, "Differentiation"))
        self.assertIsNone(verify_candidate(Candidate("1/((x+1)*(x+2))", "1/(x+1)-1/(x+2)",
                                                    ("A/(x+1)+B/(x+2)", "A+B=1", "1/(x+1)-1/(x+2)")), "Partial fractions"))

    def test_wrong_generated_derivative_transformation_is_rejected(self):
        with patch("workcheck.presentation._derivative_rule", return_value=(sp.S.Zero, "Bad rule")):
            self.assertIsNone(verify_candidate(Candidate("x^2", "2*x"), "Differentiation"))

    def test_bad_generated_candidates_use_reverified_replacements(self):
        with patch("workcheck.practice.generated_candidates", return_value=iter([Candidate("bad()", "0"), Candidate("x^2", "99")])):
            pack = build_learning("x^3+7", "Differentiation")
        self.assertEqual(len(pack.practice), 3)
        self.assertEqual(pack.example["question"], FALLBACK["power"][0][0])

    def test_cancelled_original_exclusions_are_retained(self):
        item = verify_candidate(Candidate("(x-3)/((x-3)*(x+1)*(x+2))", "1/(x+1)-1/(x+2)"), "Partial fractions")
        self.assertIsNotNone(item)
        self.assertEqual(item["restrictions_latex"], r"x \ne 3,\; -1,\; -2")

    def test_partial_fraction_answer_must_be_complete_not_only_equivalent(self):
        self.assertIsNone(verify_candidate(Candidate("1/((x+1)*(x+2))", "1/((x+1)*(x+2))"), "Partial fractions"))

    def test_duplicate_or_inadequate_set_is_not_displayed(self):
        duplicates = [Candidate("x*x", "2*x"), Candidate("x^2", "2*x")]*3
        with patch("workcheck.practice.generated_candidates", return_value=iter(duplicates)), patch.dict("workcheck.practice.FALLBACK", {"power": []}):
            pack = build_learning("x^3", "Differentiation")
        self.assertEqual(pack.practice, [])
        self.assertIsNone(pack.example)
        self.assertIn("unavailable", pack.message)

    def test_unsupported_question_does_not_generate_practice(self):
        pack = build_learning("1/(x+1)^2", "Partial fractions")
        self.assertFalse(pack.practice)
        self.assertIn("supported question", pack.message)
