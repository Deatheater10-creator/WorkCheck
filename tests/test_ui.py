import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class UITests(unittest.TestCase):
    def test_feedback_uses_rendered_submitted_maths_in_both_topics(self):
        app = self.app()
        for topic, question, working in [
            ("Differentiation", "x**2*sin(x)", "dy/dx=2*x*cos(x)"),
            ("Partial fractions", "1/((x+1)*(x+2))", "A/(x+1)+B/(x+2)"),
        ]:
            with self.subTest(topic=topic):
                app.selectbox(key="topic").select(topic).run()
                app.text_input(key="question").set_value(question).run()
                if not app.session_state["lines"]:
                    self.click(app, "Add step")
                app.text_input[1].set_value(working).run()
                self.click(app, "Check working")
                self.assertEqual(len(app.code), 0)
                self.assertTrue(all("*" not in item.value for item in app.latex))
                self.assertTrue(any(r"\frac" in item.value for item in app.latex))
                self.assertEqual(app.text_input[1].value, working)
                self.assertEqual(app.session_state["result"].steps[0].text, working)
                self.assertEqual(len(app.exception), 0)

    def test_numeric_multiplication_preview_keeps_visible_separator(self):
        app = self.app()
        app.text_input(key="question").set_value("2*3*x").run()
        self.assertTrue(any(r"2 \cdot 3 x" in item.value for item in app.latex))
        self.assertEqual(app.text_input(key="question").value, "2*3*x")

    def test_school_style_partial_answer_and_six_worked_steps(self):
        app = self.app()
        app.selectbox(key="topic").select("Partial fractions").run()
        app.text_input(key="question").set_value("1/((x+1)*(x+2))").run()
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Solution")
        equations = [item.value for item in app.latex]
        self.assertTrue(any(r"\frac{1}{x + 1} - \frac{1}{x + 2}" in equation for equation in equations))
        self.assertTrue(any(r"x \ne -1,\; -2" in equation for equation in equations))
        self.assertFalse(any(r"\cup" in equation for equation in equations))
        self.assertEqual(len(app.session_state["result"].worked_solution), 6)
        self.assertTrue(any("Compare coefficients" in item.value for item in app.markdown))
        app.text_input(key="question").set_value("2/((x+1)*(x+2))").run()
        self.assertIsNone(app.session_state["result"])
        self.assertFalse(any("Compare coefficients" in item.value for item in app.markdown))
        self.assertEqual(len(app.exception), 0)
    def test_both_reported_bare_inputs_through_live_editor_path(self):
        app = self.app()
        self.click(app, "Add step")
        for question, answer in [("(2x + 3)^4", "8*(2x+3)^3"),
                                 ("(x^2 - 5x)^3", "3*(x^2-5x)^2*(2x-5)")]:
            with self.subTest(question=question):
                app.text_input(key="question").set_value(question).run()
                self.assertIsNone(app.session_state["result"])
                self.assertGreater(len(app.latex), 0)
                app.text_input[1].set_value("dy/dx=" + answer).run()
                self.click(app, "Check working")
                self.assertEqual(app.session_state["result"].status, "Correct final answer")
                self.assertEqual(len(app.exception), 0)
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.draft_path = Path(self.temp.name) / "draft.json"
        override = patch.dict("os.environ", {"WORKCHECK_DRAFT_PATH": str(self.draft_path)})
        override.start()
        self.addCleanup(override.stop)

    def app(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        return app

    @staticmethod
    def click(app, label):
        next(button for button in app.button if button.label == label).click().run()

    def test_check_and_invalidate(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2*sin(x)").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("dy/dx = 2*x*cos(x)").run()
        self.click(app, "Check working")
        self.assertEqual(len(app.exception), 0)
        self.assertIn("First mistake", app.error[0].value)
        app.text_input[1].set_value("dy/dx = D(x^2)*sin(x)+x^2*D(sin(x))").run()
        self.assertIsNone(app.session_state["result"])
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Valid working — incomplete")
        app.text_input(key="question").set_value("x^3").run()
        self.assertIsNone(app.session_state["result"])

    def test_add_reorder_delete_and_preview(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("y=x^2").run()
        self.click(app, "Add step")
        app.text_input[2].set_value("2*x").run()
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Correct final answer")
        first_id = app.session_state["lines"][0]["id"]
        app.button(key="down_"+first_id).click().run()
        self.assertEqual([line["text"] for line in app.session_state["lines"]], ["2*x", "y=x^2"])
        self.assertIsNone(app.session_state["result"])
        self.assertGreater(len(app.latex), 0)
        app.button(key="delete_"+first_id).click().run()
        self.assertEqual(len(app.session_state["lines"]), 1)
        self.assertEqual(len(app.exception), 0)

    def test_overlimit_edit_is_kept_and_clears_feedback(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2").run()
        self.click(app, "Check working")
        text = "x"*501
        app.text_input(key="question").set_value(text).run()
        self.assertIsNone(app.session_state["result"])
        self.assertEqual(app.text_input(key="question").value, text)
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Needs clarification")
        self.assertEqual(app.text_input(key="question").value, text)
        self.assertEqual(len(app.exception), 0)

    def test_restore_after_new_session_and_refresh(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2*sin(x)").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("y=x^2*sin(x)").run()
        self.click(app, "Add step")
        app.text_input[2].set_value("D(x^2*sin(x))").run()
        first_id = app.session_state["lines"][0]["id"]
        app.button(key="down_"+first_id).click().run()
        restored = self.app()  # A fresh session simulates refresh/close-and-return.
        self.assertEqual(restored.text_input(key="question").value, "x^2*sin(x)")
        self.assertEqual([line["text"] for line in restored.session_state["lines"]],
                         ["D(x^2*sin(x))", "y=x^2*sin(x)"])
        self.assertEqual(restored.session_state["topic"], "Differentiation")
        self.assertIsNone(restored.session_state["result"])

    def test_reset_cancel_preserves_visible_and_saved_work(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("2*x").run()
        original = self.draft_path.read_bytes()
        self.click(app, "New question")
        self.assertTrue(app.session_state["confirm_new_question"])
        self.click(app, "Cancel")
        self.assertEqual(app.text_input(key="question").value, "x^2")
        self.assertEqual(app.text_input[1].value, "2*x")
        self.assertEqual(self.draft_path.read_bytes(), original)

    def test_confirm_reset_does_not_restore_old_work(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("2*x").run()
        self.click(app, "Check working")
        self.click(app, "New question")
        self.click(app, "Clear question and working")
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.text_input(key="question").value, "")
        self.assertEqual(app.session_state["lines"], [])
        self.assertIsNone(app.session_state["result"])
        restored = self.app()
        self.assertEqual(restored.text_input(key="question").value, "")
        self.assertEqual(restored.session_state["lines"], [])

    def test_failed_reset_keeps_visible_and_saved_work(self):
        app = self.app()
        app.text_input(key="question").set_value("x^2").run()
        original = self.draft_path.read_bytes()
        self.click(app, "New question")
        from workcheck.storage import SaveError
        with patch("workcheck.storage.DraftStore.save", side_effect=SaveError("test write failure")):
            self.click(app, "Clear question and working")
        self.assertEqual(app.text_input(key="question").value, "x^2")
        self.assertEqual(self.draft_path.read_bytes(), original)
        self.assertTrue(app.session_state["save_failed"])
        self.assertTrue(any("not been cleared" in warning.value for warning in app.warning))

    def test_overlimit_draft_survives_restart(self):
        app = self.app()
        text = "x"*501
        app.text_input(key="question").set_value(text).run()
        self.click(app, "Add step")
        app.text_input[1].set_value(text).run()
        restored = self.app()
        self.assertEqual(restored.text_input(key="question").value, text)
        self.assertEqual(restored.text_input[1].value, text)

    def test_topic_restores_and_runs_its_own_checker(self):
        app = self.app()
        app.selectbox(key="topic").select("Partial fractions").run()
        restored = self.app()
        self.assertEqual(restored.selectbox(key="topic").value, "Partial fractions")
        self.assertFalse(next(b for b in restored.button if b.label == "Check working").disabled)
        restored.text_input(key="question").set_value("1/((x+1)*(x+2))").run()
        self.click(restored, "Check working")
        self.assertEqual(restored.session_state["result"].status, "Solution")
        self.assertEqual(restored.session_state["result"].derivative_label_latex, "")

    def test_partial_equations_first_error_and_edit_invalidation(self):
        app = self.app()
        app.selectbox(key="topic").select("Partial fractions").run()
        app.text_input(key="question").set_value("1/((x+1)*(x+2))").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("A/(x+1)+B/(x+2)").run()
        self.click(app, "Add step")
        app.text_input[2].set_value("A+B=0").run()
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Valid working — incomplete")
        app.text_input[2].set_value("A+B=1").run()
        self.assertIsNone(app.session_state["result"])
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].first_error, 2)
        app.selectbox(key="topic").select("Differentiation").run()
        self.assertIsNone(app.session_state["result"])
        self.assertEqual(len(app.exception), 0)

    def test_damaged_file_warning_and_fresh_save(self):
        self.draft_path.write_bytes(b"broken save")
        app = self.app()
        self.assertTrue(app.session_state["recovery_warning"])
        self.assertTrue(list(self.draft_path.parent.glob("draft.damaged-*.json")))
        app.text_input(key="question").set_value("x^2").run()
        self.assertEqual(self.app().text_input(key="question").value, "x^2")

    def test_failed_autosave_retry(self):
        app = self.app()
        from workcheck.storage import SaveError
        with patch("workcheck.storage.DraftStore.save", side_effect=SaveError("test disk full")):
            app.text_input(key="question").set_value("x^2").run()
        self.assertEqual(app.text_input(key="question").value, "x^2")
        self.assertTrue(app.session_state["save_failed"])
        self.click(app, "Retry saving")
        self.assertFalse(app.session_state["save_failed"])
        self.assertEqual(self.app().text_input(key="question").value, "x^2")

    def test_working_only_still_requires_reset_confirmation(self):
        app = self.app()
        self.click(app, "Add step")
        app.text_input[1].set_value("D(x^2)").run()
        self.click(app, "New question")
        self.assertTrue(app.session_state["confirm_new_question"])
        self.click(app, "Cancel")
        self.assertEqual(self.app().text_input[1].value, "D(x^2)")

    def test_empty_reset_needs_no_confirmation(self):
        app = self.app()
        self.click(app, "New question")
        self.assertFalse(app.session_state["confirm_new_question"])
        self.assertEqual(app.text_input(key="question").value, "")
        self.assertEqual(self.app().session_state["lines"], [])

    def test_implicit_chain_rule_input_and_preview(self):
        app = self.app()
        app.text_input(key="question").set_value("(2x + 3)^4").run()
        self.assertGreater(len(app.latex), 0)
        self.click(app, "Add step")
        app.text_input[1].set_value("dy/dx=8*(2*x+3)^3").run()
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Correct final answer")
        self.assertEqual(len(app.exception), 0)

    def test_named_question_preview_solver_and_restore(self):
        app = self.app()
        question = "f(x) = (x^2 - 5x)^3"
        app.text_input(key="question").set_value(question).run()
        self.assertTrue(any("f(x) =" in equation.value for equation in app.latex))
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].derivative_label_latex, "f'(x)")
        self.assertTrue(any("f'(x) =" in equation.value for equation in app.latex))
        self.assertEqual(self.app().text_input(key="question").value, question)
        self.assertEqual(len(app.exception), 0)

    def test_named_working_previews_and_checking(self):
        app = self.app()
        app.text_input(key="question").set_value("f(x)=(2x+3)^4").run()
        self.click(app, "Add step")
        app.text_input[1].set_value("f(x)=(2x+3)^4").run()
        self.click(app, "Add step")
        app.text_input[2].set_value("f'(x)=8*(2x+3)^3").run()
        self.assertTrue(any("f'(x) =" in equation.value for equation in app.latex))
        self.click(app, "Check working")
        self.assertEqual(app.session_state["result"].status, "Correct final answer")
        self.assertEqual(app.session_state["result"].steps[0].status, "Valid intermediate step")
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
