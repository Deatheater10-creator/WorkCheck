"""Authored concept explanations, selected from the parsed question."""
import sympy as sp
from .parser import X


NOTES = {
    "product": ("Product rule", "When two functions are multiplied, differentiate one at a time and add both terms. Keep the other factor unchanged in each term.", r"\frac{d}{dx}(uv)=u'v+uv'"),
    "chain": ("Chain rule", "For a function inside another function, differentiate the outside first, keeping the inside in place. Then multiply by the derivative of the inside.", r"\frac{d}{dx}f(g(x))=f'(g(x))g'(x)"),
    "power": ("Powers, constants and sums", "Bring the power down and reduce it by one. Constant multipliers stay outside; constants differentiate to zero. Differentiate sums term by term.", r"\frac{d}{dx}x^n=nx^{n-1},\qquad\frac{d}{dx}c=0"),
    "trig": ("Sine and cosine", "Sine differentiates to cosine; cosine differentiates to negative sine. Multiply by the inner derivative when the angle is a function of x.", r"\frac{d}{dx}\sin u=\cos u\,u',\qquad\frac{d}{dx}\cos u=-\sin u\,u'"),
    "exp": ("Exponential functions", "The exponential stays the same when differentiated. Multiply by the derivative of its exponent.", r"\frac{d}{dx}e^u=e^u u'"),
    "log": ("Natural logarithms", "Divide the derivative of the inside by the inside itself. The original logarithm requires its argument to be positive over the real numbers.", r"\frac{d}{dx}\ln u=\frac{u'}{u},\qquad u>0"),
    "partial": ("Partial fractions and coefficients", "Split a proper fraction into simpler fractions, one constant numerator for each distinct linear factor. Multiply by the denominator factors, expand, and compare the x coefficients and constants. Solve for the constants and substitute them back. Keep the original excluded x values.", r"\frac{N(x)}{(x+p)(x+q)}=\frac{A}{x+p}+\frac{B}{x+q},\qquad p\ne q"),
}


def concepts_for(expression, topic):
    if topic == "Partial fractions":
        return ["partial"]
    expression = expression.doit()
    nodes = list(sp.preorder_traversal(expression))
    product = any(isinstance(node, sp.Mul) and sum(f.has(X) for f in node.args) > 1 for node in nodes)
    concepts = ["product"] if product else []
    for function, concept in ((sp.log, "log"), (sp.sin, "trig"), (sp.cos, "trig"), (sp.exp, "exp")):
        if expression.has(function) and concept not in concepts:
            concepts.append(concept)
    if any((isinstance(node, sp.Pow) and node.base.has(X) and node.base != X) or
           (node.func in (sp.sin, sp.cos, sp.exp, sp.log) and node.args[0] != X) for node in nodes):
        concepts.append("chain")
    if not concepts or any(isinstance(node, sp.Pow) and node.base == X for node in nodes):
        concepts.append("power")
    return concepts


def concept_notes(concepts):
    return [{"title": NOTES[key][0], "explanation": NOTES[key][1], "formula": NOTES[key][2]} for key in concepts]
