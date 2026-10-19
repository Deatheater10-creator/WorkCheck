"""Translate a small maths grammar into SymPy objects, without eval."""
import ast
import re
from dataclasses import dataclass, field

import sympy as sp

X = sp.Symbol("x", real=True)
MAX_CHARS = 500
MAX_STEPS = 20
MAX_NODES = 150
MAX_DEPTH = 12
LIMITS = (
    "Limits: 500 characters per question/line; 20 working lines; "
    "150 syntax nodes; nesting depth 12; numbers up to 8 digits; "
    "integer powers from -12 to 12; polynomial degree at most 12. "
    "Over-limit input stays in the editor; checking pauses until you shorten it."
)


class InputIssue(ValueError):
    """A limitation or syntax problem, never a mathematical wrong verdict."""


@dataclass
class Expression:
    expr: sp.Expr
    restrictions: list[tuple[str, sp.Expr]] = field(default_factory=list)
    held: bool = False
    degree: int | None = None


def _depth(node):
    return 1 + max((_depth(c) for c in ast.iter_child_nodes(node)), default=0)


def parse_expression(text: str, *, allow_d: bool = False) -> Expression:
    if len(text) > MAX_CHARS:
        raise InputIssue("The 500-character limit is exceeded. Your text has been kept.")
    source = text.strip().replace("^", "**")
    if not source:
        raise InputIssue("Enter a mathematical expression.")
    try:
        root = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        raise InputIssue("I cannot read this notation. Use explicit * and parentheses.") from None
    if sum(1 for _ in ast.walk(root)) > MAX_NODES:
        raise InputIssue("The 150-node expression limit is exceeded. Simplify the input.")
    if _depth(root) > MAX_DEPTH:
        raise InputIssue("The nesting depth limit of 12 is exceeded.")

    def build(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            literal = ast.get_source_segment(source, node)
            if not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", literal or ""):
                raise InputIssue("Use ordinary numbers, not scientific or special literals.")
            if sum(c.isdigit() for c in literal) > 8:
                raise InputIssue("Numeric literals may have at most 8 digits.")
            return Expression(sp.Rational(literal), degree=0)
        if isinstance(node, ast.Name) and node.id == "x":
            return Expression(X, degree=1)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            a = build(node.operand)
            if isinstance(node.op, ast.USub):
                a.expr = sp.Mul(-1, a.expr, evaluate=False)
            return a
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            a = build(node.left)
            if isinstance(node.op, ast.Pow):
                n = node.right
                sign = 1
                if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
                    sign = -1 if isinstance(n.op, ast.USub) else 1
                    n = n.operand
                if not isinstance(n, ast.Constant) or type(n.value) is not int or abs(n.value) > 12:
                    raise InputIssue("Only literal integer powers from -12 to 12 are supported.")
                exponent = sign * n.value
                restrictions = a.restrictions + ([("nonzero", a.expr)] if exponent < 0 else [])
                degree = a.degree * exponent if a.degree is not None and exponent >= 0 else None
                result = Expression(sp.Pow(a.expr, exponent, evaluate=False), restrictions, a.held, degree)
            else:
                b = build(node.right)
                restrictions = a.restrictions + b.restrictions
                degree = None
                if isinstance(node.op, (ast.Add, ast.Sub)):
                    rhs = b.expr if isinstance(node.op, ast.Add) else sp.Mul(-1, b.expr, evaluate=False)
                    expr = sp.Add(a.expr, rhs, evaluate=False)
                    if a.degree is not None and b.degree is not None:
                        degree = max(a.degree, b.degree)
                elif isinstance(node.op, ast.Mult):
                    expr = sp.Mul(a.expr, b.expr, evaluate=False)
                    if a.degree is not None and b.degree is not None:
                        degree = a.degree + b.degree
                else:
                    if b.expr.is_zero is True:
                        raise InputIssue("Division by zero is undefined. Please correct the expression.")
                    expr = sp.Mul(a.expr, sp.Pow(b.expr, -1, evaluate=False), evaluate=False)
                    restrictions.append(("nonzero", b.expr))
                    if b.degree == 0:
                        degree = a.degree
                result = Expression(expr, restrictions, a.held or b.held, degree)
            if result.degree is not None and result.degree > 12:
                raise InputIssue("The supported polynomial degree limit is 12.")
            return result
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
            name = node.func.id
            functions = {"sin": sp.sin, "cos": sp.cos, "exp": sp.exp, "ln": sp.log}
            if name not in functions and not (name == "D" and allow_d):
                raise InputIssue("Use sin, cos, exp, ln; D(...) is available in working only.")
            a = build(node.args[0])
            if name == "D":
                if a.held:
                    raise InputIssue("Nested D(...) means higher derivatives, which are not supported yet.")
                return Expression(sp.Derivative(a.expr, X, evaluate=False), a.restrictions, True)
            restrictions = a.restrictions + ([("positive", a.expr)] if name == "ln" else [])
            return Expression(functions[name](a.expr, evaluate=False), restrictions, a.held)
        raise InputIssue("Unsupported notation. Use x, numbers, + - * / ^, parentheses, and the listed functions.")

    return build(root.body)


def question_expression(text):
    if len(text) > MAX_CHARS:
        raise InputIssue("The question exceeds the 500-character limit; your text is kept.")
    stripped = text.strip()
    if re.match(r"^y\s*=", stripped):
        stripped = stripped.split("=", 1)[1]
    return parse_expression(stripped)


def parse_step(text):
    if len(text) > MAX_CHARS:
        raise InputIssue("This line exceeds the 500-character limit; your text is kept.")
    if text.count("=") > 1:
        raise InputIssue("Use one mathematical equality per numbered line.")
    if "=" not in text:
        return "derivative", parse_expression(text, allow_d=True), None
    left, right = (part.strip() for part in text.split("=", 1))
    rhs = parse_expression(right, allow_d=True)
    if left == "y":
        return "function", rhs, None
    if re.sub(r"\s", "", left) == "dy/dx":
        return "derivative", rhs, None
    lhs = parse_expression(left, allow_d=True)
    if isinstance(lhs.expr, sp.Derivative) and not lhs.expr.expr.has(sp.Derivative):
        return "derivative_equality", rhs, lhs
    raise InputIssue("Label this line y = ..., dy/dx = ..., or D(original expression) = ... .")
