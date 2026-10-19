import unittest
from workcheck.worker import run_check


class WorkerTests(unittest.TestCase):
    def test_actual_spawned_check(self):
        r = run_check("x^2", ["2*x"], timeout=10)
        self.assertEqual(r.status, "Correct final answer")

    def test_hard_deadline_preserves_input(self):
        lines = ["2*x"]
        r = run_check("x^2", lines, timeout=0)
        self.assertEqual(r.status, "Needs clarification")
        self.assertIn("time limit", r.explanation)
        self.assertEqual(lines, ["2*x"])
