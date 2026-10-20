import unittest
import sympy as sp
from workcheck.checking import check_differentiation, check_partial_fractions
from workcheck.parser import X
from workcheck.presentation import present_result, school_latex


class OrdinaryNotationTests(unittest.TestCase):
    def test_questions_working_and_rendered_derivatives(self):
        fixtures = [
            ('2x', '2', sp.Integer(2)),
            ('x^3 cos(x)', '3x^2 cos(x)-x^3 sin(x)', 3*X**2*sp.cos(X)-X**3*sp.sin(X)),
            ('x sin(x)', 'sin(x)+x cos(x)', sp.sin(X)+X*sp.cos(X)),
            ('2(x+1)', '2', sp.Integer(2)),
            ('(x+1)(x-2)', '2x-1', 2*X-1),
            ('3x^2 sin(2x)', '6x sin(2x)+6x^2 cos(2x)', 6*X*sp.sin(2*X)+6*X**2*sp.cos(2*X)),
            ('f(x) = x^3 cos(x)', "f'(x)=3x^2 cos(x)-x^3 sin(x)", 3*X**2*sp.cos(X)-X**3*sp.sin(X)),
        ]
        for question, working, expected in fixtures:
            with self.subTest(question=question):
                result = present_result(check_differentiation(question, [working]), question, 'Differentiation')
                self.assertEqual(result.status, 'Correct final answer', result.explanation)
                self.assertEqual(result.answer_latex, sp.latex(expected))
                self.assertNotIn('*', result.answer_display_latex)
                self.assertTrue(result.worked_solution)
                for step in result.worked_solution:
                    self.assertTrue(all('*' not in line for line in step['math']))

    def test_valid_unfinished_ordinary_product_rule(self):
        result = check_differentiation('x^3 cos(x)', ['D(x^3) cos(x)+x^3 D(cos(x))'])
        self.assertEqual(result.steps[0].status, 'Valid intermediate step')
        self.assertFalse(result.steps[0].complete)

    def test_ordinary_coefficient_working_in_partial_fractions(self):
        result = check_partial_fractions('1/((x+1)(x+2))',
            ['A/(x+1)+B/(x+2)', '1=A(x+2)+B(x+1)', 'A+B=0', '2A+B=1',
             'A=1', 'B=-1', '1/(x+1)-1/(x+2)'])
        self.assertEqual(result.status, 'Correct final answer')

