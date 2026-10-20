import unittest
import sympy as sp
from workcheck.parser import X, InputIssue, parse_expression, parse_step, question_expression


class ParserTests(unittest.TestCase):
    def test_ordinary_products_including_after_powers(self):
        forms = [('2x', 2*X), ('x^3 cos(x)', X**3*sp.cos(X)),
                 ('x sin(x)', X*sp.sin(X)), ('2(x+1)', 2*(X+1)),
                 ('(x+1)(x-2)', (X+1)*(X-2)),
                 ('3x^2 sin(2x)', 3*X**2*sp.sin(2*X)),
                 ('x^2(x+1)', X**2*(X+1)), ('x^2 x', X**3),
                 ('2 × 3', sp.Integer(6)), ('2 · x', 2*X)]
        for text, expected in forms:
            with self.subTest(text=text):
                self.assertEqual(sp.simplify(parse_expression(text).expr-expected), 0)
        self.assertEqual(question_expression('f(x) = x^3 cos(x)').function_label, 'f(x)')
        self.assertEqual(sp.simplify(question_expression('f(x) = x^3 cos(x)').expr-X**3*sp.cos(X)), 0)

    def test_ordinary_clarification_never_requires_programming_multiplication(self):
        for text in ['1/2x', '1/2 x', 'x^2x', 'x^2cos(x)', 'xsin(x)', '2 3']:
            with self.subTest(text=text), self.assertRaises(InputIssue) as caught:
                parse_expression(text)
            self.assertNotIn('*', str(caught.exception))
        for text, expected in [('(1/2)x', X/2), ('1/(2x)', 1/(2*X)), ('(x^2)x', X**3)]:
            self.assertEqual(sp.simplify(parse_expression(text).expr-expected), 0)
    def test_labelled_questions_with_implicit_multiplication(self):
        for text, label, expected in [
            ("f(x) = (2x + 3)^4", "f(x)", (2*X+3)**4),
            ("f(x) = (x^2 - 5x)^3", "f(x)", (X**2-5*X)**3),
            ("y = (x^2 - 5x)^3", "y", (X**2-5*X)**3),
            ("g ( x ) = 2x", "g(x)", 2*X),
            ("(x^2 - 5x)^3", None, (X**2-5*X)**3),
        ]:
            with self.subTest(text=text):
                parsed = question_expression(text)
                self.assertEqual(parsed.function_label, label)
                self.assertEqual(sp.simplify(parsed.expr - expected), 0)

    def test_function_and_derivative_working_roles(self):
        role, parsed, _ = parse_step("f(x) = (x^2-5x)^3", expected_label="f(x)")
        self.assertEqual(role, "function")
        self.assertEqual(parsed.function_label, "f(x)")
        for text in ["f'(x) = 2x", "f′(x) = 2x", "f ' ( x ) = 2x"]:
            role, parsed, _ = parse_step(text, expected_label="f(x)")
            self.assertEqual(role, "derivative")
            self.assertEqual(parsed.function_label, "f(x)")

    def test_wrong_or_unsupported_labels_request_clarification(self):
        for text in ["f(x,y)=x", "f(t)=t", "x(x)=x", "f(x)=x=2", "f'(x)=x"]:
            with self.subTest(text=text), self.assertRaises(InputIssue):
                question_expression(text)
        for text in ["g'(x)=2x", "g(x)=x^2", "f''(x)=2"]:
            with self.subTest(text=text), self.assertRaises(InputIssue):
                parse_step(text, expected_label="f(x)")

    def test_unambiguous_numeric_coefficients(self):
        for text, expected in [("2x", 2*X), ("-3x", -3*X), ("0.5x", X/2),
                               (".5x", X/2), ("2 x", 2*X), ("(2x + 3)^4", (2*X+3)**4)]:
            with self.subTest(text=text):
                self.assertEqual(sp.simplify(parse_expression(text).expr - expected), 0)

    def test_coefficients_do_not_split_names_or_guess_exponents(self):
        for text in ["2xyz", "1e2x", "x^2x", "x^ 2x", "x^-2x", "x^+2x", "1/2x", "1/-2x", "x1", "0xff"]:
            with self.subTest(text=text), self.assertRaises(InputIssue):
                parse_expression(text)

    def test_explicit_denominator_grouping_preserved(self):
        p = parse_expression("1/(2x)")
        self.assertEqual(sp.simplify(p.expr - 1/(2*X)), 0)

    def test_adjacent_factors_and_function_arguments(self):
        for text, expected in [("2(x+1)", 2*(X+1)), ("x(x+1)", X*(X+1)),
                               ("(x+1)(x-1)", (X+1)*(X-1)), ("x sin(x)", X*sp.sin(X)),
                               ("2sin(x)", 2*sp.sin(X)), ("sin(2x)", sp.sin(2*X)),
                               ("D(2x)", 2)]:
            with self.subTest(text=text):
                parsed = parse_expression(text, allow_d=True)
                self.assertEqual(sp.simplify(parsed.expr.doit()-expected), 0)

    def test_names_and_adjacent_numbers_are_not_guessed(self):
        for text in ["xsin(x)", "2abc", "2 3", "02x", "x\nx"]:
            with self.subTest(text=text), self.assertRaises(InputIssue):
                parse_expression(text)

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
