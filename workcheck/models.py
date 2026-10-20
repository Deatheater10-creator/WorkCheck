from dataclasses import dataclass, field


@dataclass
class StepResult:
    number: int
    text: str
    status: str
    reason: str
    complete: bool = False


@dataclass
class CheckResult:
    status: str
    explanation: str
    steps: list[StepResult] = field(default_factory=list)
    answer_latex: str = ""
    domain_latex: str = ""
    first_error: int | None = None
    blocked_at: int | None = None
    derivative_label_latex: str = r"\frac{dy}{dx}"
    answer_display_latex: str = ""
    restrictions_display_latex: str = ""
    worked_solution: list = field(default_factory=list)
    worked_solution_title: str = "Worked solution"
    presentation_note: str = ""


@dataclass
class Proof:
    status: str  # proved, disproved, unknown
    reason: str
