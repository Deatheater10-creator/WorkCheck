"""Streamlit editor; mathematical judgments live in the checker, not widgets."""
from uuid import uuid4
from pathlib import Path
from html import escape

import streamlit as st
import sympy as sp

from .parser import LIMITS, InputIssue, parse_step, question_expression
from .worker import run_check


def invalidate():
    st.session_state.revision += 1
    st.session_state.result = None
    st.session_state.result_revision = None
    st.session_state.practice = []


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
            parsed = question_expression(text)
            st.latex(sp.latex(parsed.expr))
        else:
            role, parsed, left = parse_step(text)
            if role == "function":
                label = "y = "
            elif left is not None:
                label = sp.latex(left.expr) + " = "
            else:
                label = r"\frac{dy}{dx} = "
            st.latex(label + sp.latex(parsed.expr))
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
        st.write(result.explanation)
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
            st.code(step.text, language=None)
            st.write(step.reason)
    if result.answer_latex:
        with st.container(border=True, key="answer_panel"):
            st.subheader("Final answer")
            st.latex(r"\frac{dy}{dx} = " + result.answer_latex)
            st.caption("Retain the original real-domain restrictions:")
            st.latex(r"x \in " + result.domain_latex)


def main():
    st.set_page_config(page_title="WorkCheck", page_icon="✎", layout="centered")
    styles = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)
    defaults = {"question": "", "topic": "Differentiation", "lines": [], "revision": 0,
                "result": None, "result_revision": None, "practice": []}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
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
      <strong>Partial fractions</strong><p>Follow the decomposition and coefficient equations.</p><span class="wc-topic-badge">COMING IN A LATER BUILD STAGE</span></section>
    </div>''', unsafe_allow_html=True)
    st.caption("Stage 1 · Local differentiation checker. Draft saving, partial fractions, teaching examples and practice arrive in later stages. Photo recognition is not enabled.")
    st.selectbox("Topic", ["Differentiation"], key="topic", on_change=invalidate)
    with st.container(border=True, key="question_panel"):
        st.markdown("**01 · Start with your question**")
        st.text_input("Question · expression to differentiate", key="question", on_change=invalidate,
                      placeholder="x^2*sin(x)")
        preview(st.session_state.question, question=True)
    with st.expander("Notation and input limits"):
        st.write("Use x, numbers, + - * / ^, parentheses, sin(...), cos(...), exp(...), ln(...). Use explicit multiplication, for example x^2*sin(x).")
        st.write("Working labels: y = ..., dy/dx = ..., or D(original expression) = ... . D(...) means an unfinished derivative with respect to x.")
        st.code("dy/dx = D(x^2)*sin(x) + x^2*D(sin(x))", language=None)
        st.caption(LIMITS)
        st.caption("A preview checks notation only. It does not mean the mathematics is correct. More complex domains may require clarification.")
    st.subheader("Your working · optional")
    st.caption("One mathematical step per line. Valid unfinished working is different from a completed derivative.")
    if not st.session_state.lines:
        st.markdown('<div class="wc-empty">✎ <strong>Make your thinking visible.</strong><br>Add your first step below, or check the question on its own.</div>', unsafe_allow_html=True)
    for index, line in enumerate(st.session_state.lines):
        line_id = line["id"]
        key = "line_" + line_id
        if key not in st.session_state:
            st.session_state[key] = line["text"]
        with st.container(border=True, key="editor_" + line_id):
            st.markdown(f'<div class="wc-step-heading"><span class="wc-step-number">{index + 1}</span><span>Your next step</span></div>', unsafe_allow_html=True)
            st.text_input(f"Step {index + 1}", key=key, on_change=edit_line, args=(line_id,))
            preview(line["text"])
            up, down, delete = st.columns(3)
            up.button("Move up", key="up_" + line_id, disabled=index == 0, on_click=move_line, args=(line_id, -1))
            down.button("Move down", key="down_" + line_id, disabled=index == len(st.session_state.lines) - 1,
                        on_click=move_line, args=(line_id, 1))
            delete.button("Delete", key="delete_" + line_id, on_click=delete_line, args=(line_id,))
    st.button("Add step", on_click=add_line)
    if len(st.session_state.lines) > 20:
        st.warning("The 20-line checking limit is exceeded. Your lines remain intact; delete or combine lines to check them.")
    if st.button("Check working", type="primary"):
        revision = st.session_state.revision
        question = st.session_state.question
        lines = [line["text"] for line in st.session_state.lines]
        with st.spinner("Checking locally with exact mathematical rules…"):
            result = run_check(question, lines)
        if revision == st.session_state.revision:
            st.session_state.result = result
            st.session_state.result_revision = revision
    if st.session_state.result is not None and st.session_state.result_revision == st.session_state.revision:
        show_result(st.session_state.result)
    st.markdown('''<div class="wc-learning-panels">
      <section class="wc-learning-panel wc-example"><span class="wc-coming">Coming next · worked examples</span>
      <h3>See the method in action</h3><p>A guided worked example will connect the explanation to a fresh problem. This feature is not available in stage 1.</p></section>
      <section class="wc-learning-panel wc-practice"><span class="wc-coming">Coming next · targeted practice</span>
      <h3>Turn understanding into practice</h3><p>Three targeted questions with revealable, verified solutions are planned for a later stage. Practice is not available yet.</p></section>
    </div>''', unsafe_allow_html=True)
