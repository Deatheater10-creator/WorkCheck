"""Bounded local templates and exact verification before educational display."""
from dataclasses import dataclass, field
import sympy as sp
from .parser import X, Expression, question_expression, parse_expression, InputIssue
from .checking import check_working
from .verification import domain_of, verify
from .presentation import school_latex, concise_restrictions, derivative_solution, coefficient_solution
from .explanations import concepts_for, concept_notes


@dataclass(frozen=True)
class Candidate:
    question: str
    answer: str
    working: tuple[str, ...] = ()


@dataclass
class LearningPack:
    concepts: list = field(default_factory=list)
    example: dict | None = None
    practice: list = field(default_factory=list)
    message: str = ""


def generated_candidates(concept):
    """Six small candidates, with independently constructed answer formulas."""
    for a in range(2, 8):
        n = 2 + a % 3
        if concept == "partial":
            p, q, A, B = a, a+2, a-1, -a
            question = f"({A+B}*x+{A*q+B*p})/((x+{p})*(x+{q}))"
            answer = f"{A}/(x+{p})+({B})/(x+{q})"
        elif concept == "product":
            question = f"x^{n}*sin({a}*x)"
            answer = f"{n}*x^{n-1}*sin({a}*x)+{a}*x^{n}*cos({a}*x)"
        elif concept == "log":
            question = f"ln({a}*x+1)"
            answer = f"{a}/({a}*x+1)"
        elif concept == "exp":
            question = f"exp({a}*x+1)"
            answer = f"{a}*exp({a}*x+1)"
        elif concept == "trig":
            question = f"cos({a}*x+1)" if a % 2 else f"sin({a}*x+1)"
            answer = f"-{a}*sin({a}*x+1)" if a % 2 else f"{a}*cos({a}*x+1)"
        elif concept == "chain":
            question = f"({a}*x+1)^{n}"
            answer = f"{a*n}*({a}*x+1)^{n-1}"
        else:
            question = f"{a}*x^{n}+x"
            answer = f"{a*n}*x^{n-1}+1"
        yield Candidate(question, answer)


# Hand-checked answers, reverified on every use rather than trusted as text.
FALLBACK = {
    "product": [("x*sin(x)", "sin(x)+x*cos(x)"), ("x*cos(x)", "cos(x)-x*sin(x)"), ("x*exp(x)", "exp(x)+x*exp(x)"), ("x^2*sin(x)", "2*x*sin(x)+x^2*cos(x)"), ("x^2*cos(x)", "2*x*cos(x)-x^2*sin(x)")],
    "chain": [("(2*x+3)^2", "4*(2*x+3)"), ("(3*x+1)^3", "9*(3*x+1)^2"), ("(x^2+1)^2", "4*x*(x^2+1)"), ("(x^2+2)^3", "6*x*(x^2+2)^2"), ("(4*x+1)^2", "8*(4*x+1)")],
    "power": [("x^2", "2*x"), ("x^3", "3*x^2"), ("2*x^2+1", "4*x"), ("3*x^3+x", "9*x^2+1"), ("x^4", "4*x^3")],
    "trig": [("sin(x)", "cos(x)"), ("cos(x)", "-sin(x)"), ("sin(2*x)", "2*cos(2*x)"), ("cos(3*x)", "-3*sin(3*x)"), ("sin(x^2)", "2*x*cos(x^2)")],
    "exp": [("exp(x)", "exp(x)"), ("exp(2*x)", "2*exp(2*x)"), ("exp(3*x)", "3*exp(3*x)"), ("exp(x^2)", "2*x*exp(x^2)"), ("exp(4*x)", "4*exp(4*x)")],
    "log": [("ln(x)", "1/x"), ("ln(2*x)", "1/x"), ("ln(x+1)", "1/(x+1)"), ("ln(x^2+1)", "2*x/(x^2+1)"), ("ln(3*x+2)", "3/(3*x+2)")],
    "partial": [("1/((x+1)*(x+2))", "1/(x+1)-1/(x+2)"), ("2/((x+1)*(x+3))", "1/(x+1)-1/(x+3)"), ("3/((x+2)*(x+5))", "1/(x+2)-1/(x+5)"), ("1/(x*(x+1))", "1/x-1/(x+1)"), ("4/((x+1)*(x+5))", "1/(x+1)-1/(x+5)")],
}


def verify_candidate(candidate, topic):
    """Answer and any supplied working must pass before generating display rows.

    Detailed solution builders also verify every derivative rule replacement,
    polynomial expansion, coefficient equation and elimination symbolically.
    An unavailable or unproved transformation rejects the whole candidate.
    """
    try:
        source = question_expression(candidate.question)
        checked = check_working(candidate.question, list(candidate.working), topic)
        if not checked.answer_latex or checked.status not in ("Solution", "Correct final answer"):
            return None
        domain = domain_of(source)
        answer = parse_expression(candidate.answer)
        expected = sp.apart(sp.cancel(source.expr), X) if topic == "Partial fractions" else sp.diff(source.expr.doit(), X)
        if topic != "Partial fractions":
            domain = domain.intersect(domain_of(Expression(expected)))
        if verify(answer, expected, domain).status != "proved":
            return None
        if topic == "Partial fractions" and check_working(candidate.question, [candidate.answer], topic).status != "Correct final answer":
            return None
        steps = coefficient_solution(source.expr, domain) if topic == "Partial fractions" else derivative_solution(source.expr, domain, r"\frac{dy}{dx}")
        if not steps or any(not step["math"] or len(step["math"]) != len(step["explanations"]) for step in steps):
            return None
        return {"question": candidate.question, "question_latex": school_latex(source.expr),
                "answer_latex": school_latex(answer.expr.doit()), "restrictions_latex": concise_restrictions(domain),
                "worked_solution": steps, "verified": True}
    except (InputIssue, ValueError, TypeError, NotImplementedError):
        return None


def build_learning(question, topic):
    if not check_working(question, [], topic).answer_latex:
        return LearningPack(message="Practice needs a supported question first. Clarify the question and check again.")
    source = question_expression(question, topic=topic)
    concepts = concepts_for(source.expr, topic)
    pack = LearningPack(concepts=concept_notes(concepts))
    concept = concepts[0]
    selected, seen = [], []
    # Candidate and fallback lists are bounded. Exactly four verified distinct
    # items are required: one teaching example followed by three exercises.
    pools = (generated_candidates(concept), (Candidate(q, a) for q, a in FALLBACK[concept]))
    for pool in pools:
        for candidate in pool:
            try:
                expression = question_expression(candidate.question).expr.doit()
            except InputIssue:
                continue
            if sp.simplify(expression-source.expr.doit()) == 0 or any(sp.simplify(expression-old) == 0 for old in seen):
                continue
            item = verify_candidate(candidate, topic)
            if item is None:
                continue
            seen.append(expression)
            selected.append(item)
            if len(selected) == 4:
                # Teach supporting rules used by the example/exercises too.
                for selected_item in selected:
                    for supporting in concepts_for(question_expression(selected_item["question"]).expr, topic):
                        if supporting not in concepts:
                            concepts.append(supporting)
                pack.concepts = concept_notes(concepts)
                pack.example, pack.practice = selected[0], selected[1:]
                return pack
    pack.message = "Three distinct verified practice problems are temporarily unavailable. Your checked working is preserved."
    return pack
