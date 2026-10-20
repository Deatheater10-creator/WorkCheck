"""Bounded sentence templates; never discard an unrecognised request clause."""
from dataclasses import dataclass
import re
from .parser import MAX_CHARS, InputIssue, Expression, _question_expression


@dataclass
class QuestionRequest:
    expression_text: str = ""
    parsed: Expression | None = None
    topic: str | None = None
    task: str = ""
    sentence: bool = False
    category: str = ""
    issue: str = ""


def _task(topic):
    return "Decompose into partial fractions" if topic == "Partial fractions" else "Find the first derivative with respect to x over the real domain"


def _unsupported(text):
    if re.search(r"\b(imaginary|complex|branch|principal|real part|modulus|argument of)\b", text, re.I):
        return ("Complex-valued or component request", "Complex logarithms require branch choices, and imaginary/real components of complex derivatives are not verified here. Derivative evaluation at a point is also outside the current scope. No complex branch is assumed.")
    if re.search(r"\b(second|third|higher)\s+derivative|['′]{2,}", text, re.I):
        return "Higher derivative", "Only first-derivative expressions are supported; higher derivatives are not verified."
    point_derivative = any(match.group(1).strip() != "x" for match in re.finditer(r"\b[A-Za-z]\s*['′]\s*\(([^)]*)\)", text))
    if point_derivative or re.search(r"\b(evaluate|evaluating)\b|\b(?:at|when)\s+x\s*=|\bat\s+(?:the point|[-+]?\d)", text, re.I):
        return "Evaluate a derivative or function at a point", "Derivative/function evaluation at a point is not supported. WorkCheck currently verifies derivative expressions on their real domains."
    if re.search(r"\b(integrate|integral|limit|matrix|implicit|parametric|partial derivative)\b", text, re.I):
        return "Operation outside the supported topics", "Only first real differentiation and restricted partial-fraction decomposition are currently verified."
    return None


def interpret_question(text, topic=None):
    request = QuestionRequest(topic=topic, task=_task(topic))
    if len(text) > MAX_CHARS:
        request.category, request.issue = "Input limit", "The question exceeds the 500-character limit; your text is kept."
        return request
    source = text.strip()
    if len(source) >= 2 and (source[0], source[-1]) in (("“", "”"), ('"', '"')):
        source = source[1:-1].strip()
    source = re.sub(r"^Please\s+(?=(?:differentiate|find|calculate|determine|decompose|express|write)\b)", "", source, flags=re.I)
    unsupported = _unsupported(source)
    expression, operation = None, None
    # A leading function definition plus a separate, complete request clause.
    definition = re.fullmatch(r"(?:Let|Given)\s+(?:that\s+)?((?:[A-Za-z]\s*\(\s*x\s*\)|y)\s*=\s*.+?)(?:\.\s+|;\s*|,\s*)(.+?)[.?!]?", source, re.I | re.S)
    if definition:
        expression, wording = definition.groups()
        try:
            label = _question_expression(expression).function_label
        except InputIssue as exc:
            request.category, request.issue = "Unsupported notation", str(exc)
            return request
        escaped = re.escape(label)
        prime = re.escape(label.replace('(x)', "'(x)")) if label != 'y' else r"dy\s*/\s*dx"
        valid = (r"(?:find|calculate|determine)\s+(?:the\s+)?(?:first\s+)?derivative(?:\s+of\s+"+escaped+r")?(?:\s+with\s+respect\s+to\s+x)?"+
                 r"|differentiate(?:\s+"+escaped+r")?(?:\s+with\s+respect\s+to\s+x)?"+
                 r"|(?:find|calculate|determine)\s+"+prime)
        references = re.findall(r"\b([A-Za-z])\s*['′]?\s*\(\s*([A-Za-z])\s*\)", wording)
        labels_match = all(name == label[0] and variable == "x" for name, variable in references)
        if labels_match and re.fullmatch(valid + r"[.?!]?", wording.strip(), re.I):
            operation = "Differentiation"
    else:
        templates = [
            (r"Differentiate\s+(?:the\s+function\s+)?(.+?)(?:\s+with\s+respect\s+to\s+x)?[.?!]?", "Differentiation"),
            (r"(?:Find|Calculate|Determine)\s+(?:the\s+)?(?:first\s+)?derivative\s+of\s+(?:the\s+function\s+)?(.+?)(?:\s+with\s+respect\s+to\s+x)?[.?!]?", "Differentiation"),
            (r"Decompose\s+(.+?)\s+into\s+partial\s+fractions[.?!]?", "Partial fractions"),
            (r"(?:Express|Write)\s+(.+?)\s+(?:as|in)\s+partial\s+fractions[.?!]?", "Partial fractions"),
            (r"Find\s+(?:the\s+)?partial\s+fractions\s+(?:of|for)\s+(.+?)[.?!]?", "Partial fractions"),
        ]
        for pattern, inferred in templates:
            match = re.fullmatch(pattern, source, re.I | re.S)
            if match:
                expression, operation = match.group(1), inferred
                break
    if unsupported:
        request.sentence = True
        request.task, explanation = unsupported
        request.category = "Unsupported mathematics"
        request.issue = "Unsupported mathematics: " + explanation
        if expression:
            request.expression_text = expression
            try:
                request.parsed = _question_expression(expression)
            except InputIssue:
                pass
        return request
    if operation:
        request.expression_text, request.topic = expression, operation
        request.task, request.sentence = _task(operation), True
        if re.search(r"\b(and|then|using|find|show|please)\b", expression, re.I):
            request.category = "Unrecognised wording"
            request.issue = "Unrecognised question wording: additional instructions in this request need clarification. They have not been discarded."
            return request
    elif definition or re.match(r"[A-Za-z]{3,}\s+", source) and not re.match(r"(?:sin|cos|exp|ln)\s*\(", source):
        request.expression_text = expression or ""
        if expression:
            try:
                request.parsed = _question_expression(expression)
            except InputIssue:
                pass
        request.sentence, request.category = True, "Unrecognised wording"
        request.task = "Request not interpreted"
        request.issue = "Unrecognised question wording: I cannot establish the complete requested task. Use 'Differentiate f(x) = ...', 'Let f(x) = ... . Find the derivative.', or 'Decompose ... into partial fractions'. Additional instructions must be clarified; they are not ignored."
        return request
    else:
        request.expression_text = source
    try:
        request.parsed = _question_expression(request.expression_text)
    except InputIssue as exc:
        request.category, request.issue = "Unsupported notation", str(exc)
        return request
    if operation and topic is not None and operation != topic:
        request.category = "Topic mismatch"
        request.issue = f"Topic mismatch: this wording requests {operation}. Select that topic before confirming and checking."
    return request
