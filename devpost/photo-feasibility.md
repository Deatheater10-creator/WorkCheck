# Local photo-recognition feasibility

Reviewed 2026-10-20. **Submission decision: retain the approved typed-only fallback.** Photo recognition is not enabled. This is a finding that reliable recognition has not been demonstrated, not a claim that local recognition is impossible.

## Evidence obtained

The baseline environment has no torch, pix2tex, texify or surya package installed. No OCR weights were installed or downloaded during this stage. The project has no representative learner-provided handwritten question-plus-ordered-working test set. Browser-test screenshots are not handwriting examples and do not establish recognition quality.

| Candidate | Current official-source findings | Missing WorkCheck evidence |
| --- | --- | --- |
| pix2tex / LaTeX-OCR | Formula-image-to-LaTeX tool; README describes PyTorch installation, automatic checkpoint downloads, and the need to double-check predictions. Repository code is MIT licensed. | Windows CPU setup and timing, model-weight licence/size audit, multi-line handwriting accuracy, question-versus-working separation, preserved line order and conversion to our restricted input grammar. |
| Texify | Official repository marks it deprecated and points users to Surya. | No installation or benchmark here; selecting a deprecated tool would not establish our complete workflow. |
| Surya | Current documentation describes a 650M-parameter OCR/layout model. CPU inference needs a llama.cpp server; GPU inference uses vLLM. Code is Apache-2.0, while weights have separate modified Open Rail-M terms. The project states it targets document OCR rather than natural-scene photos. | Version-specific CPU/Windows feasibility, precise checkpoint sizes/licence terms, local-only operation after setup and our handwritten-maths acceptance benchmark have not been verified. |

Sources inspected: [pix2tex official repository](https://github.com/lukas-blecher/LaTeX-OCR), [Texify official repository](https://github.com/VikParuchuri/texify), [Surya official repository](https://github.com/datalab-to/surya). Documentation findings are not local performance results.

## Required evidence before future enablement

1. Choose an exact package/model version; audit code and weight licences, disk/memory needs, checkpoint sources and CPU-only Windows compatibility in an optional isolated environment.
2. Obtain explicit setup-download consent before installing large optional models. Keep OCR outside the required typed-input environment; never fetch models silently at runtime.
3. Benchmark representative handwritten differentiation and partial-fraction questions plus numbered working. Record exact transcription errors, ambiguous symbols, ordering, latency and failures on this device.
4. Demonstrate cold offline inference after setup, conversion into the safe parser grammar, editable transcription beside the photo and student confirmation before checking.
5. Reject uncertain recognition rather than inventing an error verdict. Keep typing available.

Until these checks pass, WorkCheck accepts typed questions and working only. No photo-upload UI or automatic-recognition claim is included. No paid service or external AI API is proposed. Automatic practice grading remains deferred independently of photo recognition.
