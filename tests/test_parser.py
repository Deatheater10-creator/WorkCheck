import unittest
import sympy as sp
from workcheck.parser import X, InputIssue, parse_expression, parse_step, question_expression


class ParserTests(unittest.TestCase):
    def test_exact_decimal(self):
        self.assertEqual(parse_expression("0.1").expr, sp.Rational(1, 10))

    def test_held_derivative(self):
        p = parse_expression("D(x^2)", allow_d=True)
        self.assertTrue(p.held)
        self.assertIsInstance(p.expr, sp.Derivative)
        self.assertEqual(p.expr.doit(), 2*X)

    def test_hold_survives_zero_multiplier(self):
        self.assertTrue(parse_expression("0*D(x^2)", allow_d=True).held)

    def test_labels(self):
        self.assertEqual(parse_step("y = x^2")[0], "function")
        self.assertEqual(parse_step("dy / dx = 2*x")[0], "derivative")
        self.assertEqual(parse_step("D(x^2) = 2*x")[0], "derivative_equality")
        self.assertEqual(sp.simplify(question_expression("y = x^2").expr-X**2), 0)

    def test_restrictions_survive_cancellation(self):
        p = parse_expression("(x-1)/(x-1)")
        self.assertTrue(p.restrictions)

    def test_denominator_and_log_restrictions(self):
        self.assertEqual(len(parse_expression("ln(x)/x").restrictions), 2)

    def test_negative_exponent(self):
        self.assertTrue(parse_expression("x^-2").restrictions)

    def test_unsafe_and_unsupported_syntax(self):
        for text in ["__import__('os')", "x.__class__", "x[0]", "[x for x in []]", "True",
                     "sin(x, x)", "sin(x=1)", "lambda: x", "D(x)", "tan(x)", "A+x", "1e3", "0xff"]:
            with self.subTest(text=text), self.assertRaises(InputIssue):
                parse_expression(text)

    def test_limits(self):
        for text in ["x"*501, "123456789", "x^13", "x^0.5", "x^x", "(x^12)^12", "("*1000 + "x" + ")"*1000]:
            with self.subTest(text=text[:40]), self.assertRaises(InputIssue):
                parse_expression(text)

    def test_node_and_depth_limits(self):
        for text in ["+".join(["x"]*80), "sin("*14+"x"+")"*14]:
            with self.assertRaises(InputIssue):
                parse_expression(text)

    def test_nested_derivative_and_equality_chain(self):
        with self.assertRaises(InputIssue):
            parse_expression("D(D(x))", allow_d=True)
        with self.assertRaises(InputIssue):
            parse_step("y=x=1")

    def test_zero_denominator(self):
        with self.assertRaises(InputIssue):
            parse_expression("1/0")
