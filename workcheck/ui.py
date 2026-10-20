"""Streamlit editor; mathematical judgments live in the checker, not widgets."""
from uuid import uuid4
from pathlib import Path
from html import escape

import streamlit as st

from .parser import LIMITS, InputIssue, derivative_label_latex, parse_step, question_expression
from .worker import run_check, run_learning
from .storage import DraftStore, SaveError, empty_draft
from .partial_fractions import parse_partial_line
from .presentation import school_latex, feedback_markdown
from .questions import interpret_question


@st.cache_data(show_spinner=False, max_entries=32)
def cached_learning(question, topic):
    pack = run_learning(question, topic)
    if len(pack.practice) != 3 or not pack.example:
        # Failed jobs must be retried, rather than cached as a permanent failure.
        raise ValueError(pack.message or "Verified practice is temporarily unavailable. Check again to retry.")
    return pack


def clear_learning():
    st.session_state.practice = []
    st.session_state.learning = None
    for key in list(st.session_state):
        if key.startswith("reveal_practice_"):
            del st.session_state[key]


def show_worked_steps(steps):
    for number, step in enumerate(steps, 1):
        st.markdown(f"**{number}. {step['instruction']}**")
        for index, equation in enumerate(step["math"]):
            maths, explanation = st.columns([3, 2])
            maths.latex(equation)
            if step.get("explanations"):
                explanation.write(step["explanations"][index])


def show_learning(pack):
    if pack is None:
        return
    if pack.example:
        with st.container(border=True, key="teaching_example_panel"):
            with st.expander("Worked example", expanded=True):
                st.subheader("Worked example")
                st.caption("A different question using the same main method.")
                st.latex(pack.example["question_latex"])
                show_worked_steps(pack.example["worked_solution"])
    if len(pack.practice) == 3:
        st.subheader("Your three practice problems")
        st.caption("Try each problem yourself, then reveal its answer and full working. Practice attempts are not automatically graded.")
        for index, item in enumerate(pack.practice):
            with st.container(border=True, key=f"practice_panel_{index}"):
                st.markdown(f"**Practice {index+1}**")
                st.write("Decompose into partial fractions." if st.session_state.topic == "Partial fractions" else "Differentiate with respect to x.")
                st.latex(item["question_latex"])
                st.caption("Restrictions")
                st.latex(item["restrictions_latex"])
                if st.toggle(f"Reveal answer and worked solution {index+1}", key=f"reveal_practice_{index}"):
                    st.markdown("**Answer**")
                    label = r"\frac{dy}{dx} = " if st.session_state.topic == "Differentiation" else ""
                    st.latex(label + item["answer_latex"])
                    show_worked_steps(item["worked_solution"])
    if pack.message:
        st.warning(pack.message)


def save_current():
    # Read the latest widget values before structural edits/check/reset callbacks.
    for line in st.session_state.lines:
        line["text"] = st.session_state.get("line_" + line["id"], line["text"])
    draft = {"schema_version": 1, "topic": st.session_state.topic,
             "question": st.session_state.question, "lines": st.session_state.lines,
             "revision": st.session_state.revision}
    try:
        st.session_state.draft_store.save(draft)
        st.session_state.save_message = "Saved on this device."
        st.session_state.save_failed = False
        st.session_state.recovery_warning = ""
        return True
    except SaveError as exc:
        st.session_state.save_message = str(exc) + " Your current working is kept in memory."
        st.session_state.save_failed = True
        return False


def initialize_draft():
    if st.session_state.get("draft_initialized"):
        return
    st.session_state.draft_store = DraftStore()
    loaded = st.session_state.draft_store.load()
    # Preserve live stage-1 working when this update is loaded in an existing tab.
    has_live_work = bool(st.session_state.question.strip() or st.session_state.lines)
    if not has_live_work:
        draft = loaded.draft
        st.session_state.question = draft["question"]
        st.session_state.topic = draft["topic"]
        st.session_state.lines = draft["lines"]
        st.session_state.revision = draft["revision"]
    st.session_state.save_message = loaded.message
    st.session_state.save_failed = False
    st.session_state.recovery_warning = loaded.message if loaded.warning else ""
    st.session_state.confirm_new_question = False
    st.session_state.draft_initialized = True
    if has_live_work:
        save_current()


def request_new_question():
    if st.session_state.question.strip() or any(line["text"].strip() for line in st.session_state.lines):
        st.session_state.confirm_new_question = True
    else:
        confirm_new_question()


def cancel_new_question():
    st.session_state.confirm_new_question = False


def confirm_new_question():
    draft = empty_draft()
    draft["revision"] = st.session_state.revision + 1
    try:
        # Save first. If this fails, preserve the visible working and old saved draft.
        st.session_state.draft_store.save(draft)
    except SaveError as exc:
        st.session_state.save_message = f"Could not start a new question: {exc} Your working has not been cleared."
        st.session_state.save_failed = True
        return
    for line in st.session_state.lines:
        st.session_state.pop("line_" + line["id"], None)
    st.session_state.question = draft["question"]
    st.session_state.topic = draft["topic"]
    st.session_state.lines = []
    st.session_state.revision = draft["revision"]
    st.session_state.result = None
    st.session_state.result_revision = None
    clear_learning()
    st.session_state.confirm_new_question = False
    st.session_state.recovery_warning = ""
    st.session_state.save_message = "New question started. The previous saved working has been cleared."
    st.session_state.save_failed = False


def invalidate():
    st.session_state.revision += 1
    st.session_state.result = None
    st.session_state.result_revision = None
    clear_learning()
    if st.session_state.get("draft_initialized"):
        save_current()


def edit_line(line_id):
    for line in st.session_state.lines:
        if line["id"] == line_id:
            line["text"] = st.session_state["line_" + line_id]
    invalidate()


def add_line():
    st.session_state.lines.append({"id": uuid4().hex, "text": ""})
    invalidate()


def move_line(line_id, offset):
    lines = st.session_state.lines
    index = next(i for i, line in enumerate(lines) if line["id"] == line_id)
    target = index + offset
    if 0 <= target < len(lines):
        lines[index], lines[target] = lines[target], lines[index]
        invalidate()


def delete_line(line_id):
    st.session_state.lines = [line for line in st.session_state.lines if line["id"] != line_id]
    invalidate()


def preview(text, *, question=False):
    if not text.strip():
        return
    try:
        if question:
            parsed = question_expression(text, topic=st.session_state.topic)
            label = parsed.function_label + " = " if parsed.function_label else ""
            st.latex(label + school_latex(parsed.expr))
        else:
            if st.session_state.topic == "Partial fractions":
                line = parse_partial_line(text)
                label = school_latex(line.left.expr) + " = " if line.left is not None else ""
                prefix = f"x = {school_latex(line.root)}:\\quad " if line.root is not None and not line.root_marker else ""
                st.latex(prefix + label + school_latex(line.right.expr))
                return
            source_label = None
            try:
                source_label = question_expression(st.session_state.question).function_label
            except InputIssue:
                pass
            role, parsed, left = parse_step(text, expected_label=source_label)
            if role == "function":
                label = parsed.function_label + " = "
            elif left is not None:
                label = school_latex(left.expr) + " = "
            else:
                label = derivative_label_latex(parsed.function_label or source_label) + " = "
            st.latex(label + school_latex(parsed.expr))
    except InputIssue as exc:
        st.caption(f"Preview unavailable: {exc}")


def show_result(result):
    st.divider()
    st.subheader("Results")
    if result.status == "First mistake":
        st.error("✗ First mistake — line " + str(result.first_error))
    elif result.status == "Correct final answer":
        st.success("✓ Correct final answer")
    elif result.status == "Needs clarification":
        st.warning("? Needs clarification")
    else:
        st.info(result.status)
    with st.container(border=True, key="explanation_panel"):
        st.markdown("**Explanation · understand your working**")
        st.markdown(feedback_markdown(result.explanation))
        pack = st.session_state.get("learning")
        if pack and pack.concepts:
            with st.expander("Understand the concept", expanded=True):
                st.subheader("Understand the concept")
                for concept in pack.concepts:
                    st.markdown("**" + concept["title"] + "**")
                    st.write(concept["explanation"])
                    st.latex(concept["formula"])
    for step in result.steps:
        with st.container(border=True):
            if step.status in ("Correct final answer", "Valid intermediate step"):
                status_class, icon = "wc-verified", "✓"
            elif step.status == "First mistake":
                status_class, icon = "wc-error", "✗"
            elif step.status == "Needs clarification":
                status_class, icon = "wc-unclear", "?"
            else:
                status_class, icon = "wc-unchecked", "—"
            st.markdown(
                f'<div class="wc-step-heading"><span class="wc-step-number">{step.number}</span>'
                f'<span class="{status_class}">{icon} {escape(step.status)}</span></div>',
                unsafe_allow_html=True,
            )
            # Render the original submitted line, including incorrect working.
            # Parsing here formats notation only; it never regrades the step.
            preview(step.text)
            st.markdown(feedback_markdown(step.reason))
    if result.answer_latex:
        with st.container(border=True, key="answer_panel"):
            st.subheader("Final answer")
            label = result.derivative_label_latex + " = " if result.derivative_label_latex else ""
            st.latex(label + (result.answer_display_latex or result.answer_latex))
            st.caption("Restrictions")
            st.latex(result.restrictions_display_latex or (r"x \in " + result.domain_latex))
    if result.worked_solution:
        with st.container(border=True, key="worked_solution_panel"):
            with st.expander(result.worked_solution_title, expanded=True):
                st.subheader(result.worked_solution_title)
                show_worked_steps(result.worked_solution)
    if result.presentation_note:
        st.caption(result.presentation_note)
    show_learning(st.session_state.get("learning"))


def main():
    st.set_page_config(page_title="WorkCheck", page_icon="✎", layout="centered")
    styles = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)
    defaults = {"question": "", "topic": "Differentiation", "lines": [], "revision": 0,
                "result": None, "result_revision": None, "practice": [], "learning": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    initialize_draft()
    st.markdown('''<header class="wc-hero">
      <div class="wc-eyebrow">YOUR MATHS STUDY WORKSPACE</div>
      <h1>WorkCheck</h1><p>Understand your working.<br>Build confidence, one step at a time.</p>
      <div class="wc-hero-math" aria-hidden="true">ƒ′(x)</div>
      <div class="wc-hero-chips"><span>Step-by-step checking</span><span>Clear explanations</span><span>Runs locally</span></div>
    </header>
    <div class="wc-topics" aria-label="Topic coverage">
      <section class="wc-topic wc-topic-blue"><span class="wc-topic-symbol" aria-hidden="true">u′v + uv′</span>
      <strong>Product rule</strong><p>Keep track of both terms when differentiating a product.</p><span class="wc-topic-badge">AVAILABLE · DIFFERENTIATION</span></section>
      <section class="wc-topic wc-topic-purple"><span class="wc-topic-symbol" aria-hidden="true">f′(g(x)) · g′(x)</span>
      <strong>Chain rule</strong><p>Connect the outer derivative to the inner function.</p><span class="wc-topic-badge">AVAILABLE · DIFFERENTIATION</span></section>
      <section class="wc-topic wc-topic-amber"><span class="wc-topic-symbol" aria-hidden="true">A / (x+a)</span>
      <strong>Partial fractions</strong><p>Follow the decomposition and coefficient equations.</p><span class="wc-topic-badge">AVAILABLE · TWO LINEAR FACTORS</span></section>
    </div>''', unsafe_allow_html=True)
    st.caption("Local maths checking and verified practice · Your draft stays on this device. Photo recognition is not enabled.")
    if st.session_state.recovery_warning:
        st.warning(st.session_state.recovery_warning)
    st.button("New question", on_click=request_new_question)
    if st.session_state.confirm_new_question:
        with st.container(border=True):
            st.warning("Start a new question? This will clear the current question and working from this screen and the saved draft.")
            confirm, cancel = st.columns(2)
            confirm.button("Clear question and working", on_click=confirm_new_question)
            cancel.button("Cancel", on_click=cancel_new_question)
    st.selectbox("Topic", ["Differentiation", "Partial fractions"], key="topic", on_change=invalidate)
    is_partial = st.session_state.topic == "Partial fractions"
    with st.container(border=True, key="question_panel"):
        st.markdown("**01 · Start with your question**")
        st.text_input("Question · fraction to decompose" if is_partial else "Question · expression to differentiate", key="question", on_change=invalidate,
                      placeholder="1/((x+1)(x+2))" if is_partial else "x^3 cos(x)")
        request = interpret_question(st.session_state.question, st.session_state.topic)
        signature = (st.session_state.question, st.session_state.topic)
        if st.session_state.get("interpretation_signature") != signature:
            st.session_state.interpretation_signature = signature
            st.session_state.question_confirmed = False
        if request.sentence:
            st.markdown("**Interpreted question**")
            if request.parsed:
                label = request.parsed.function_label + " = " if request.parsed.function_label else ""
                st.latex(label + school_latex(request.parsed.expr))
            st.write("Task: " + request.task)
            if request.issue:
                st.warning(request.category + ": " + request.issue.removeprefix(request.category + ": "))
            else:
                st.caption("Confirm the expression and task before checking. This confirms the interpretation, not mathematical correctness or domain support.")
                st.checkbox("I confirm the interpreted expression and task", key="question_confirmed", on_change=invalidate)
        elif st.session_state.question.strip():
            st.caption("Task: " + request.task)
        st.caption("Use ordinary maths: 2x, x^3 cos(x), 2(x+1), and (x+1)(x-2). Use parentheses to clarify grouping; multiplication symbols are optional.")
        if not is_partial:
            st.caption("Enter an expression, y = ..., or f(x) = ..., for example f(x) = (x^2 - 5x)^3. For f(x), the derivative is shown as f'(x).")
        else:
            st.caption("Use a proper rational fraction with two distinct linear factors. Original denominator exclusions are retained in the answer.")
        preview(st.session_state.question, question=True)
    with st.expander("Notation and input limits"):
        if is_partial:
            st.write("Use a proper fraction with two distinct rational linear factors. Set up A/(x+1)+B/(x+2) first, then enter one identity, coefficient equation, or value per line. A and B are available in this topic's working only.")
            for example in ("A/(x+1)+B/(x+2)", "1=A(x+2)+B(x+1)", "A+B=0", "2A+B=1", "A=1", "B=-1", "1/(x+1)-1/(x+2)"):
                preview(example)
            st.write("Alternative method: after the setup, use x=-1: 1=A or put x=-1 on its own line before a denominator-cleared equation. Root substitution is for polynomial identities, not the original undefined fraction.")
        st.write("Use x, numbers, + - / ^, parentheses, sin(...), cos(...), exp(...), ln(...). Ordinary products such as 2x, x^3 cos(x), 3x^2 sin(2x), and (x+1)(x-2) are accepted. Keep function names whole: write x sin(x), not xsin(x). Use parentheses for ambiguous division or powers. Between numbers, use parentheses or the maths symbols × and ·.")
        if not is_partial:
            st.write("Working labels: y = ... or f(x) = ... for the original function; dy/dx = ... or matching f'(x) = ... for the derivative. Single-letter labels such as g(x) also work. D(...) means an unfinished derivative with respect to x; D(original expression) = ... is supported too.")
            preview("dy/dx = D(x^2) sin(x) + x^2 D(sin(x))")
        st.caption(LIMITS)
        st.caption("A preview checks notation only. It does not mean the mathematics is correct. More complex domains may require clarification.")
    st.subheader("Your working · optional")
    st.caption("One mathematical step per line. Valid unfinished working is different from a completed decomposition." if is_partial
               else "One mathematical step per line. Valid unfinished working is different from a completed derivative.")
    if not st.session_state.lines:
        st.markdown('<div class="wc-empty">✎ <strong>Make your thinking visible.</strong><br>Add your first step below, or check the question on its own.</div>', unsafe_allow_html=True)
    for index, line in enumerate(st.session_state.lines):
        line_id = line["id"]
        key = "line_" + line_id
        if key not in st.session_state:
            st.session_state[key] = line["text"]
        with st.container(border=True, key="editor_" + line_id):
            st.markdown(f'<div class="wc-step-heading"><span class="wc-step-number">{index + 1}</span><span>Your next step</span></div>', unsafe_allow_html=True)
            st.text_input(f"Step {index + 1}", key=key, on_change=edit_line, args=(line_id,),
                          help="Start with A/(x+1)+B/(x+2), then one equation such as A+B=0 per line. See notation help for root substitutions." if is_partial else
                          "Use ordinary products: 2x, x^3 cos(x), 3x^2 sin(2x), or 8(2x+3)^3. Clarify ambiguous grouping with parentheses.")
            preview(line["text"])
            up, down, delete = st.columns(3)
            up.button("Move up", key="up_" + line_id, disabled=index == 0, on_click=move_line, args=(line_id, -1))
            down.button("Move down", key="down_" + line_id, disabled=index == len(st.session_state.lines) - 1,
                        on_click=move_line, args=(line_id, 1))
            delete.button("Delete", key="delete_" + line_id, on_click=delete_line, args=(line_id,))
    st.button("Add step", on_click=add_line)
    if st.session_state.save_failed:
        st.warning(st.session_state.save_message)
        st.button("Retry saving", on_click=save_current)
    else:
        st.caption(st.session_state.save_message)
    st.caption("Edits are saved when you press Enter or leave a field. Before closing or refreshing, finish editing and look for ‘Saved on this device.’ One current draft is shared by local tabs; use one editing tab at a time.")
    if len(st.session_state.lines) > 20:
        st.warning("The 20-line checking limit is exceeded. Your lines remain intact; delete or combine lines to check them.")
    needs_confirmation = request.sentence and (bool(request.issue) or not st.session_state.get("question_confirmed", False))
    if st.button("Check working", type="primary", disabled=needs_confirmation):
        clear_learning()
        save_current()
        revision = st.session_state.revision
        question = st.session_state.question
        lines = [line["text"] for line in st.session_state.lines]
        with st.spinner("Checking locally with exact mathematical rules…"):
            result = run_check(question, lines, topic=st.session_state.topic)
        learning = None
        if result.answer_latex:
            with st.spinner("Verifying your worked example and three practice solutions locally…"):
                try:
                    learning = cached_learning(question, st.session_state.topic)
                except ValueError as exc:
                    from .practice import LearningPack
                    learning = LearningPack(message=str(exc))
        if revision == st.session_state.revision:
            st.session_state.result = result
            st.session_state.result_revision = revision
            st.session_state.learning = learning
            st.session_state.practice = learning.practice if learning else []
    if st.session_state.result is not None and st.session_state.result_revision == st.session_state.revision:
        show_result(st.session_state.result)
    st.markdown('''<div class="wc-learning-panels">
      <section class="wc-learning-panel wc-example"><span class="wc-coming">Understand the method</span>
      <h3>See the method in action</h3><p>Check a supported question to see the concept explained before a fully worked example.</p></section>
      <section class="wc-learning-panel wc-practice"><span class="wc-coming">Verified targeted practice</span>
      <h3>Turn understanding into practice</h3><p>Three distinct questions follow the example. Reveal each answer and full worked solution when you are ready.</p></section>
    </div>''', unsafe_allow_html=True)
