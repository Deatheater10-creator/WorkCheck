import unittest
from unittest.mock import patch
import sympy as sp
from workcheck.questions import interpret_question
from workcheck.parser import X, InputIssue, question_expression
from workcheck.checking import check_working
from workcheck.practice import build_learning


COMPLEX = "Let f(x) = ln(x)/ln(-x). Find the imaginary coefficient of f'(1)."


class SentenceQuestionTests(unittest.TestCase):
    def test_supported_differentiation_forms_and_actual_derivatives(self):
        forms = [
            ("Differentiate y = x^2*sin(x).", 2*X*sp.sin(X)+X**2*sp.cos(X), 'y'),
            ("Find the derivative of (2x+3)^4 with respect to x.", 8*(2*X+3)**3, None),
            ("Calculate the first derivative of f(x) = 2.5x.", sp.Rational(5, 2), 'f(x)'),
            ("Let f(x) = (x^2-5x)^3. Find f'(x).", 3*(X**2-5*X)**2*(2*X-5), 'f(x)'),
            ("Given g(x)=ln(x^2+1); determine the derivative of g(x).", 2*X/(X**2+1), 'g(x)'),
            ("Let y = exp(2x), find dy/dx.", 2*sp.exp(2*X), 'y'),
            ("Please differentiate the function f(x)=x^2.", 2*X, 'f(x)'),
            ("Given that f(x)=x^3, find f'(x).", 3*X**2, 'f(x)'),
        ]
        for text, expected, label in forms:
            with self.subTest(text=text):
                request = interpret_question(text, 'Differentiation')
                self.assertFalse(request.issue)
                self.assertTrue(request.sentence)
                self.assertEqual(request.parsed.function_label, label)
                self.assertEqual(sp.simplify(sp.diff(request.parsed.expr.doit(), X)-expected), 0)
                self.assertEqual(check_working(text, [], 'Differentiation').status, 'Solution')

    def test_supported_partial_fraction_sentence_forms(self):
        for wording in ['Decompose {} into partial fractions.', 'Express {} as partial fractions.',
                        'Write {} in partial fractions.', 'Find the partial fractions of {}.']:
            text = wording.format('1/((x+1)*(x+2))')
            request = interpret_question(text, 'Partial fractions')
            self.assertFalse(request.issue)
            result = check_working(text, ['A/(x+1)+B/(x+2)', 'A+B=0'], 'Partial fractions')
            self.assertIsNone(result.first_error)
            self.assertEqual(result.steps[1].status, 'Valid intermediate step')

    def test_exact_complex_request_never_becomes_real_differentiation(self):
        request = interpret_question(COMPLEX, 'Differentiation')
        self.assertEqual(request.category, 'Unsupported mathematics')
        self.assertIsNotNone(request.parsed)
        for word in ['branch', 'Complex', 'evaluation']:
            self.assertIn(word, request.issue)
        with patch('workcheck.differentiation.sp.diff', side_effect=AssertionError('Must not differentiate')):
            result = check_working(COMPLEX, [], 'Differentiation')
        self.assertEqual(result.status, 'Needs clarification')
        self.assertEqual(result.answer_latex, '')
        self.assertFalse(build_learning(COMPLEX, 'Differentiation').practice)

    def test_wording_notation_math_and_topic_are_separate(self):
        fixtures = [
            ('Please work out whatever is needed for x^2.', 'Unrecognised wording'),
            ("Let f(x)=x^2. Find g'(x).", 'Unrecognised wording'),
            ("Let f(x)=x^2. Find F'(x).", 'Unrecognised wording'),
            ('Differentiate x.__class__.', 'Unsupported notation'),
            ("Let f(x)=x^2. Find f'(1).", 'Unsupported mathematics'),
            ('Find the second derivative of x^3.', 'Unsupported mathematics'),
            ('Differentiate x^2 at x=1.', 'Unsupported mathematics'),
            ('Decompose 1/((x+1)*(x+2)) into partial fractions.', 'Topic mismatch'),
        ]
        for text, category in fixtures:
            with self.subTest(text=text):
                request = interpret_question(text, 'Differentiation')
                self.assertEqual(request.category, category)
                self.assertTrue(request.issue)
                with self.assertRaises(InputIssue):
                    question_expression(text, topic='Differentiation')

    def test_additional_requests_are_never_discarded(self):
        for text in ["Let f(x)=x^2. Find f'(x) and integrate it.",
                     "Let f(x)=x^2. Find f'(x). Also find a minimum.",
                     'Differentiate x^2; then explain its inverse.']:
            self.assertTrue(interpret_question(text, 'Differentiation').issue)

    def test_safe_parser_and_whole_question_limits_still_apply(self):
        for text in ['Differentiate __import__("os").system("echo unsafe").',
                     'Differentiate (lambda: 1)().', 'Differentiate x^100.',
                     'Differentiate '+(' '*490)+'x^2.']:
            self.assertTrue(interpret_question(text, 'Differentiation').issue)
        self.assertEqual(interpret_question('f(x)=(2x+3)^4', 'Differentiation').sentence, False)
        self.assertFalse(interpret_question("Let f(x)=x^2. Find f'(x).", 'Differentiation').issue)

