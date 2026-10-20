"""Public checking boundary; later topics plug in here."""
from .differentiation import check_differentiation
from .partial_fractions import check_partial_fractions
from .models import CheckResult

def check_working(question, lines, topic="Differentiation"):
    if topic == "Differentiation":
        return check_differentiation(question, lines)
    if topic == "Partial fractions":
        return check_partial_fractions(question, lines)
    return CheckResult("Needs clarification", "Choose a supported topic before checking.")


__all__ = ["check_differentiation", "check_partial_fractions", "check_working"]
