import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from workcheck.storage import SessionDraftStore, empty_draft


class HostedTests(unittest.TestCase):
    def test_drafts_are_separate_and_copied(self):
        first, second = SessionDraftStore(), SessionDraftStore()
        draft = empty_draft()
        draft['question'] = 'x^2'
        first.save(draft)
        draft['question'] = 'changed'
        self.assertEqual(first.load().draft['question'], 'x^2')
        self.assertEqual(second.load().draft['question'], '')
        loaded = first.load().draft
        loaded['question'] = 'also changed'
        self.assertEqual(first.load().draft['question'], 'x^2')

    def test_hosted_ui_isolation(self):
        entry = str(Path(__file__).resolve().parents[1] / 'cloud_app.py')
        app = AppTest.from_file(entry, default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertIsInstance(app.session_state.draft_store, SessionDraftStore)
        app.text_input(key='question').set_value('x^2').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.draft_store.load().draft['question'], 'x^2')
        other = AppTest.from_file(entry, default_timeout=20).run()
        self.assertEqual(other.session_state.question, '')


if __name__ == '__main__':
    unittest.main()
