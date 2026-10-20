"""Translate a small maths grammar into SymPy objects, without eval."""
import ast
import re
import io
import tokenize
from dataclasses import dataclass, field

import sympy as sp

X = sp.Symbol("x", real=True)
A, B = sp.symbols("A B", real=True)
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
    function_label: str | None = None


def _depth(node):
    return 1 + max((_depth(c) for c in ast.iter_child_nodes(node)), default=0)


def _normalize_multiplication(source, *, allow_coefficients=False):
    """Insert products at known token boundaries, never inside identifiers.

    Python's tokenizer only identifies tokens; it does not execute the input.
    The existing restricted AST builder still checks all syntax and limits.
    """
    hint = "Use ordinary products such as 2x, 2(x+1), and x sin(x). Keep function names whole and use parentheses to clarify grouping."
    try:
        raw = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        raise InputIssue("I cannot read this notation. " + hint) from None
    tokens = [t for t in raw if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER)]
    if any(t.type == tokenize.NEWLINE and any(u.start > t.end and u.type not in
           (tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER) for u in raw) for t in raw):
        raise InputIssue("Enter one expression per field or numbered line.")
    functions = {"sin", "cos", "exp", "ln", "D"}
    symbols = {"x", "A", "B"} if allow_coefficients else {"x"}
    for token in tokens:
        if token.type == tokenize.NAME and token.string not in functions | symbols:
            raise InputIssue("Unsupported name. Use x and the listed functions; names are not split into products. " + hint)
        if token.type == tokenize.NUMBER and not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", token.string):
            raise InputIssue("Use ordinary numbers, not scientific or special literals.")
        if token.type not in (tokenize.NAME, tokenize.NUMBER, tokenize.OP) or (
            token.type == tokenize.OP and token.string not in {"+", "-", "*", "/", "**", "(", ")"}
        ):
            raise InputIssue("Unsupported notation. " + hint)
    output = []
    for i, token in enumerate(tokens):
        if i:
            previous = tokens[i-1]
            ends_factor = previous.type == tokenize.NUMBER or previous.string in symbols | {")"}
            starts_factor = token.type in (tokenize.NUMBER, tokenize.NAME) or token.string == "("
            if ends_factor and starts_factor:
                if previous.type == token.type == tokenize.NUMBER:
                    raise InputIssue("Two adjacent numbers are ambiguous. Write 2 × 3 or 2(3) to multiply numbers.")
                # Do not guess 1/2x, x^2x, or their signed variants.
                before = i-2
                if before >= 0 and tokens[before].string in {"+", "-"}:
                    before -= 1
                if before >= 0 and tokens[before].string == "/":
                    raise InputIssue("Ambiguous multiplication after division. Write 1/(2x) or (1/2)x to clarify the denominator.")
                if before >= 0 and tokens[before].string == "**":
                    separated = previous.end < token.start
                    if not separated and token.string != "(":
                        raise InputIssue("Ambiguous multiplication after a power. Write (x^2)x or x^2 x to separate the exponent from the next factor; group a full exponent in parentheses.")
                output.append((tokenize.OP, "*"))
        output.append((token.type, token.string))
    return tokenize.untokenize(output)


def parse_expression(text: str, *, allow_d: bool = False, allow_coefficients: bool = False) -> Expression:
    if len(text) > MAX_CHARS:
        raise InputIssue("The 500-character limit is exceeded. Your text has been kept.")
    source = text.strip().replace("^", "**").replace("×", "*").replace("·", "*")
    if not source:
        raise InputIssue("Enter a mathematical expression.")
    source = _normalize_multiplication(source, allow_coefficients=allow_coefficients)
    try:
        root = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        raise InputIssue("I cannot read this notation. Use products such as 2x, 2(x+1), or x sin(x), and parentheses to make the grouping clear.") from None
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
        if allow_coefficients and isinstance(node, ast.Name) and node.id in ("A", "B"):
            return Expression(A if node.id == "A" else B, degree=0)
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
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in ("sin", "cos", "exp", "ln", "D")):
            raise InputIssue("This is not a supported function call. Use products such as 2(x+1), x(x+1), or (x+1)(x-1). Separate a variable from a named function: x sin(x).")
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
        raise InputIssue("Unsupported notation. Use x, numbers, + - / ^, parentheses, ordinary products and the listed functions.")

    return build(root.body)


def function_label(text):
    """Recognize a label, not an executable function or a second variable."""
    text = re.sub(r"\s", "", text)
    if text == "y":
        return "y"
    if re.fullmatch(r"[A-Za-z]\(x\)", text) and text[0] not in ("D", "x"):
        return text
    return None


def derivative_label_latex(label):
    return label.replace("(x)", "'(x)") if label and label.endswith("(x)") else r"\frac{dy}{dx}"


def _question_expression(text):
    if len(text) > MAX_CHARS:
        raise InputIssue("The question exceeds the 500-character limit; your text is kept.")
    stripped = text.strip()
    label = None
    if "=" in stripped:
        if stripped.count("=") != 1:
            raise InputIssue("Use one function definition, for example f(x) = (2x+3)^4.")
        left, stripped = (part.strip() for part in stripped.split("=", 1))
        label = function_label(left)
        if label is None:
            raise InputIssue("Use a bare expression, y = ..., or a single-letter function label such as f(x) = ... .")
    parsed = parse_expression(stripped)
    parsed.function_label = label
    return parsed


def question_expression(text, *, topic=None):
    """Shared interpretation boundary; working-line grammar stays unchanged."""
    from .questions import interpret_question
    request = interpret_question(text, topic)
    if request.issue:
        raise InputIssue(request.issue)
    return request.parsed


def parse_step(text, *, expected_label=None):
    if len(text) > MAX_CHARS:
        raise InputIssue("This line exceeds the 500-character limit; your text is kept.")
    if text.count("=") > 1:
        raise InputIssue("Use one mathematical equality per numbered line.")
    if "=" not in text:
        return "derivative", parse_expression(text, allow_d=True), None
    left, right = (part.strip() for part in text.split("=", 1))
    rhs = parse_expression(right, allow_d=True)
    label = function_label(left)
    if label:
        if label != "y" and expected_label not in (None, "y", label):
            raise InputIssue(f"This line names {label}, but the current function is {expected_label}. Please clarify the label.")
        rhs.function_label = label
        return "function", rhs, None
    if re.sub(r"\s", "", left) == "dy/dx":
        return "derivative", rhs, None
    prime = re.fullmatch(r"([A-Za-z])\s*['′]\s*\(\s*x\s*\)", left)
    if prime and prime.group(1) not in ("D", "x"):
        label = prime.group(1) + "(x)"
        if expected_label not in (None, "y", label):
            raise InputIssue(f"This derivative names {label}, but the current function is {expected_label}. Please clarify the label.")
        rhs.function_label = label
        return "derivative", rhs, None
    lhs = parse_expression(left, allow_d=True)
    if isinstance(lhs.expr, sp.Derivative) and not lhs.expr.expr.has(sp.Derivative):
        return "derivative_equality", rhs, lhs
    raise InputIssue("Label this line y = ..., f(x) = ..., dy/dx = ..., f'(x) = ..., or D(original expression) = ... .")
