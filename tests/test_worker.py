import unittest
from unittest.mock import MagicMock, patch
import copy
from pathlib import Path
import subprocess
import sys
from workcheck.worker import run_check
from workcheck.models import CheckResult


class WorkerTests(unittest.TestCase):
    def test_spawn_entrypoint_does_not_import_the_interface(self):
        root = Path(__file__).resolve().parents[1]
        probe = subprocess.run([sys.executable, "-c",
            "import runpy, sys; runpy.run_path('app.py', run_name='__mp_main__'); "
            "assert 'workcheck.ui' not in sys.modules; assert 'streamlit' not in sys.modules"],
            cwd=root, capture_output=True, text=True, timeout=15)
        self.assertEqual(probe.returncode, 0, probe.stderr)

    def test_learning_in_real_bounded_worker(self):
        from workcheck.worker import run_learning
        pack = run_learning("x^2*sin(x)", "Differentiation")
        self.assertEqual(len(pack.practice), 3)
        self.assertTrue(pack.example["verified"])

    def test_learning_timeout_has_no_unverified_content(self):
        from workcheck.worker import run_learning
        pack = run_learning("x^2*sin(x)", "Differentiation", timeout=0.001)
        self.assertEqual(pack.practice, [])
        self.assertIsNone(pack.example)
        self.assertTrue(pack.message)

    def test_display_failure_keeps_checking_result(self):
        from workcheck.worker import _calculate
        class Connection:
            def __init__(self):
                self.results = []
            def send(self, result):
                self.results.append(copy.deepcopy(result))
            def close(self):
                pass
        connection = Connection()
        with patch("workcheck.presentation.present_result", side_effect=ValueError("display only")):
            _calculate(connection, "x^2", ["2*x"], "Differentiation")
        self.assertEqual(len(connection.results), 2)
        self.assertEqual(connection.results[0].status, "Correct final answer")
        self.assertEqual(connection.results[1].status, "Correct final answer")
        self.assertTrue(connection.results[1].presentation_note)

    def test_display_deadline_keeps_already_checked_result(self):
        context, parent, child, process = (MagicMock() for _ in range(4))
        context.Pipe.return_value = (parent, child)
        context.Process.return_value = process
        process.pid = 123
        process.is_alive.return_value = False
        parent.poll.side_effect = [True, False]
        parent.recv.return_value = CheckResult("Correct final answer", "Verified", answer_latex="2 x")
        with patch("workcheck.worker.mp.get_context", return_value=context):
            result = run_check("x^2", ["2*x"])
        self.assertEqual(result.status, "Correct final answer")
        self.assertEqual(result.answer_latex, "2 x")
        self.assertIn("display reached its time limit", result.presentation_note)
    def test_partial_topic_dispatch_and_unknown_topic(self):
        result = run_check("1/((x+1)*(x+2))", ["A/(x+1)+B/(x+2)", "A+B=0"],
                           timeout=10, topic="Partial fractions")
        self.assertEqual(result.status, "Valid working — incomplete")
        self.assertEqual(result.derivative_label_latex, "")
        self.assertEqual(run_check("x^2", [], timeout=10, topic="Unknown").status, "Needs clarification")

    def test_partial_full_working_in_real_worker(self):
        lines = ["A/(x+1)+B/(x+2)", "1=A*(x+2)+B*(x+1)", "A+B=0", "2*A+B=1",
                 "A=1", "B=-1", "1/(x+1)-1/(x+2)"]
        result = run_check("1/((x+1)*(x+2))", lines, topic="Partial fractions")
        self.assertEqual(result.status, "Correct final answer", result.explanation)
        self.assertEqual(len(result.steps), 7)
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
