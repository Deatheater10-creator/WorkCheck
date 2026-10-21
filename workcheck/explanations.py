"""Authored concept explanations, selected from the parsed question."""
import sympy as sp
from .parser import X


NOTES = {
    "product": ("Product rule", "Use this rule when two expressions containing x are multiplied together. Call the two parts u and v.\n\n1. Differentiate the first part and leave the second part unchanged.\n2. Leave the first part unchanged and differentiate the second part.\n3. Add the two results.\n\nThe prime mark in the formula below means 'the derivative of'. Do not just multiply the two derivatives.", r"\frac{d}{dx}(uv)=u'v+uv'"),
    "chain": ("Chain rule", "Use this rule when one expression is inside another, such as a bracket raised to a power. The bracket is the inside; the power is the outside.\n\n1. Differentiate the outside while keeping the inside unchanged.\n2. Multiply by the derivative of the inside.\n\nIn the formula below, g(x) is the inside expression. This extra multiplication is easy to miss.", r"\frac{d}{dx}f(g(x))=f'(g(x))g'(x)"),
    "power": ("Powers, constants and sums", "For a power of x, multiply by the old power, then reduce the power by 1. A number multiplied by an expression stays as a multiplier. A number on its own has derivative zero because it does not change as x changes.\n\nFor an expression joined by plus or minus signs, differentiate each term and keep its sign.", r"\frac{d}{dx}x^n=nx^{n-1},\qquad\frac{d}{dx}c=0"),
    "trig": ("Sine and cosine", "The derivative of sine is cosine. The derivative of cosine is negative sine: keep that minus sign. These rules use angles in radians.\n\nIf the angle is an expression such as 2x, also multiply by its derivative. This is the chain rule. In the formula, u is the angle expression and u' is its derivative.", r"\frac{d}{dx}\sin u=\cos u\,u',\qquad\frac{d}{dx}\cos u=-\sin u\,u'"),
    "exp": ("Exponential functions", "The derivative of e raised to x is itself. If its power is a longer expression, keep the whole exponential unchanged and multiply by the derivative of that power.\n\nIn the formula, u is the expression in the power and u' is its derivative.", r"\frac{d}{dx}e^u=e^u u'"),
    "log": ("Natural logarithms", "For ln of an expression, first differentiate the expression inside the brackets. Divide that derivative by the original inside expression.\n\nIn the formula, u is the inside expression and u' is its derivative. For real-number questions, the inside must be greater than zero. Keep this restriction in your answer.", r"\frac{d}{dx}\ln u=\frac{u'}{u},\qquad u>0"),
    "partial": ("Partial fractions and coefficients", "The aim is to rewrite one fraction as two simpler fractions with the same value. A and B stand for the two numbers we need to find.\n\n1. Put A and B above the two separate denominator factors.\n2. Multiply both sides by the full denominator to remove the fractions.\n3. Open the brackets. Match the x terms and the number terms on both sides. A coefficient is the number or expression multiplying x.\n4. Solve the two equations for A and B, then put their values back into the fractions.\n\nValues of x that made the original denominator zero are still not allowed.", r"\frac{N(x)}{(x+p)(x+q)}=\frac{A}{x+p}+\frac{B}{x+q},\qquad p\ne q"),
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
