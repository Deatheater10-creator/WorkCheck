import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class UITests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
