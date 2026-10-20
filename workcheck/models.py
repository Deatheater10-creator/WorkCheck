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


@dataclass
class Proof:
    status: str  # proved, disproved, unknown
    reason: str
