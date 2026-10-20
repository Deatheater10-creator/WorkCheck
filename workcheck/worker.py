"""Run maths in a disposable local process with a hard waiting limit."""
import multiprocessing as mp
import time
from .models import CheckResult


def _calculate_learning(connection, question, topic):
    from .practice import LearningPack, build_learning
    try:
        connection.send(build_learning(question, topic))
    except Exception:
        connection.send(LearningPack(message="Verified examples and practice are temporarily unavailable. Your checked working is preserved."))
    finally:
        connection.close()


def run_learning(question, topic, timeout=20.0):
    """A separate bounded job keeps teaching failures from changing verdicts."""
    from .practice import LearningPack
    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_calculate_learning, args=(child, question, topic), daemon=True)
    try:
        process.start()
        child.close()
        if parent.poll(timeout):
            try:
                return parent.recv()
            except EOFError:
                pass
        return LearningPack(message="Verified examples and practice reached their time limit or stopped. Your checked working is preserved; check again to retry.")
    finally:
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
        parent.close()
        child.close()


def _calculate(connection, question, lines, topic):
    try:
        from .checking import check_working
        result = check_working(question, lines, topic)
        # Deliver the checking outcome before optional display preparation.
        connection.send(result)
        try:
            from .presentation import present_result
            present_result(result, question, topic)
        except Exception:
            # Rendering failure must not replace a verified checking outcome.
            result.presentation_note = "The detailed display could not be prepared; the checked answer is shown below."
        connection.send(result)
    except Exception:
        connection.send(CheckResult("Needs clarification", "The local checker could not verify this input safely. Please simplify or clarify it."))
    finally:
        connection.close()


def run_check(question, lines, timeout=5.0, *, topic="Differentiation"):
    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_calculate, args=(child, question, lines, topic), daemon=True)
    try:
        process.start()
        child.close()
        deadline = time.monotonic() + timeout
        if parent.poll(timeout):
            try:
                checked_result = parent.recv()
            except EOFError:
                return CheckResult("Needs clarification", "The maths worker stopped without a verified result. Your input is kept.")
            remaining = max(0, deadline-time.monotonic())
            if parent.poll(remaining):
                try:
                    return parent.recv()
                except EOFError:
                    return checked_result
            checked_result.presentation_note = "The detailed display reached its time limit; the checked answer is shown below."
            return checked_result
        return CheckResult("Needs clarification", "The local check reached its time limit. Your input is kept; simplify it and try again.")
    finally:
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
        parent.close()
        child.close()
