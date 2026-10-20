import unittest
from workcheck.worker import run_check


class WorkerTests(unittest.TestCase):
    def test_both_reported_inputs_in_actual_spawned_solver(self):
        for question, answer in [("(2x + 3)^4", "8*(2*x+3)^3"),
                                 ("(x^2 - 5x)^3", "3*(x^2-5*x)^2*(2*x-5)")]:
            with self.subTest(question=question):
                self.assertEqual(run_check(question, [answer], timeout=10).status, "Correct final answer")
    def test_actual_spawned_check(self):
        r = run_check("x^2", ["2*x"], timeout=10)
        self.assertEqual(r.status, "Correct final answer")

    def test_hard_deadline_preserves_input(self):
        lines = ["2*x"]
        r = run_check("x^2", lines, timeout=0)
        self.assertEqual(r.status, "Needs clarification")
        self.assertIn("time limit", r.explanation)
        self.assertEqual(lines, ["2*x"])
