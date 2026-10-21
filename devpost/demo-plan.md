# WorkCheck demo recording plan

This is a technical screen-action plan, not a narration script or personal reflection. The learner chooses what to say and can change the emphasis. The proposed focus is the approved kernel: first incorrect step → clear correction → worked learning → verified practice. The public video constraint and upload destination are recorded in [shipping.md](shipping.md); aim for about **2 minutes 40 seconds** to leave a buffer.

## Before recording

Launch from the WorkCheck folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8501. Make equations readable at the recording size. Use fictional mathematical examples only; keep account pages, personal drafts, notifications and unrelated windows outside the recording area. Do not clear valued working just for a demo: use the isolated demo-draft option below if needed.

For Windows 11, open Snipping Tool, choose **Record → New**, select the browser region, then Start/Stop and save the file. The shortcut **Windows+Shift+R** opens video capture on supported current versions. These are Microsoft-documented mechanics, not a claim the learner's recorder was tested: [Microsoft support](https://support.microsoft.com/en-au/windows/apps/use-snipping-tool-to-capture-screenshots). No paid recorder or editor is required by this plan. Choose your own spoken explanation or captions; none is drafted here.

Optional isolated demo instance, in a separate PowerShell terminal, leaving the usual device draft alone:

```powershell
$env:WORKCHECK_DRAFT_PATH = Join-Path $PWD '.workcheck\demo-draft.json'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8502 for that instance. Its demo draft is local and ignored by Git. Edits are committed when you press Enter or leave the field; check the saved indicator before refreshing. Stop the instance with Ctrl+C when done. Keep the recording under `.workcheck/` until you deliberately upload it; do not add personal recordings to the repository.

## Suggested screen sequence

Times are optional editing/pacing targets, not another hackathon requirement.

| Approximate time | On-screen action | Evidence to make visible |
| --- | --- | --- |
| 0:00–0:15 | Show WorkCheck and Differentiation mode. | The real local application and its typed-input scope. |
| 0:15–0:50 | Enter the question and mistaken working below, then Check working. | First mistake at line 1; readable product-rule correction and actual final derivative. |
| 0:50–1:15 | Read the concept, open the worked example; choose Step by step, Next step, then Show all. | Actual equations and short explanations, with useful progressive controls. |
| 1:15–1:35 | Show all three practice questions and reveal one answer/solution. | Exactly three targeted problems, answers initially hidden and independently revealable. |
| 1:35–2:15 | Use New question and its confirmation; choose Partial fractions. Enter the setup and correct coefficient equation below and check. Then change the coefficient equation to the wrong one and check again. | Correct but unfinished working is accepted; the wrong equation becomes the first mistake. |
| 2:15–2:30 | Finish editing, confirm saved status, then refresh. | Question, topic and numbered working return. Old computed results are cleared. |
| 2:30–2:40 | End on the app or the factual coverage page. | Typed-only PoC; photo recognition and automatic practice grading remain deferred. |

Do not replace the demonstration with slides. If the live check takes time, allow it to finish; do not edit the recording to imply unsupported mathematics was verified. No copyrighted soundtrack or unrelated branding is needed. Review the saved recording for readable equations and the actual verdict before uploading.

## Exact differentiation input

Question:

```text
f(x) = x^2 sin(x)
```

Working line 1:

```text
f'(x) = 2x cos(x)
```

Expected: First mistake, line 1. This multiplies the two derivatives instead of adding the two product-rule terms. The final answer shown by WorkCheck is 2x sin(x) + x² cos(x). Optional extra, only if time allows: edit the original mistaken line to `f'(x) = 2x sin(x) + x^2 cos(x)` and check again; do not merely append a correct answer beneath an earlier wrong step.

## Exact partial-fraction input

Question:

```text
1/((x+1)(x+2))
```

Working, one equation/expression per numbered line:

```text
A/(x+1)+B/(x+2)
A+B=0
```

Expected: valid working, incomplete. Change only line 2 to `A+B=1`, then check again. Expected: first mistake at line 2; the earlier setup remains valid. Final decomposition: 1/(x+1) − 1/(x+2), with x ≠ −1, −2. No photograph or automatic practice-grading flow should be demonstrated or claimed.

## After recording

Keep a local copy. Upload using the public video destination specified in shipping.md. Check the final URL in a signed-out/private window, with the video visible and playable without requesting access, and provide that URL for verification. A proposed recording plan is not a completed video; no video has been recorded or uploaded by the agent.
