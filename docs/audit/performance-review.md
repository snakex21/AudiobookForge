# AudiobookForge: measured performance review

Baseline: `2edbfb35c7cae5070232a054f948269d652ac76d`. Review branch: `review/performance-audit`. Local experimental changes only; no release or remote publication.

## Recommendation

Keep the Python generation pipeline for now. Go plus HTML/CSS/JS can improve portable packaging, startup, UI responsiveness, and job supervision; it does not by itself speed up Piper/ONNX inference, a remote Chatterbox server, LLM OCR/translation, network TTS, or ffmpeg. The existing pipeline already delegates its heavy work to native libraries/subprocesses/servers. There is no measured evidence that Python interpreter overhead is the dominant end-to-end cost.

First remove redundant model/document initialization. Preserve the job/chunk state contract and provider coverage; then measure an actual representative book with the user's chosen voice/model/hardware. If a web interface is desired, use a versioned job/progress API around a long-lived Python worker before considering a full port.

## Architecture and dependencies

MIT Python/tkinter desktop app. `ui/main_window.py` invokes `run_pipeline`; `ui/state.py` stores app/project state. `pipeline.py` covers PDFium/pdfplumber extraction, render+vision OCR, translation through requests, Piper/Edge/Chatterbox/OpenAI/ElevenLabs TTS, per-chunk resume state, and ffmpeg MP3 conversion/concat. ONNX Piper inference remains Python-bound; Chatterbox is an HTTP service, not a local Python model in this app. Optional torch is used for GPU discovery. `requirements.txt` omitted pypdfium2 despite direct imports and README promises; this review adds it. Dependencies remain unpinned and need a separately tested lock/constraints file before release.

## Implemented

1. Lazily load the Piper voice once per `text_to_audio` job, reuse across generated chunks, and release job references afterward. Fully resumed jobs load zero models. Separate jobs and changed voices do not share a global cache.
2. Open PDFium once per direct-extraction job; close text/page handles explicitly. Preserve pdfplumber and OCR fallbacks.
3. Do not mark nonexistent/empty provider output as completed; regenerate empty cached chunks. Generation goes to a hidden pending MP3 and atomically replaces the final chunk only after nonempty output; interrupted/stale files cannot be mistaken for fresh success, and missing keys/unknown providers fail explicitly. Pending files are excluded from the merge glob. A forced atomic-publication failure is regression-tested: no chunk becomes complete, and pending files are cleaned up.
4. Add real-PDF and isolated provider regression tests and an offline reproducible extraction benchmark.

## Measurement and tests

Run `python scripts/profile_pdf_extraction.py`; fixture is a locally generated 100-page text PDF, 7 alternating pairs, no network/model/API. `pdf-profile.json` records all timings and asserts identical output. An initial run measured 153.6 ms median reopening each page vs 24.9 ms shared (~6.18x within this extraction loop). The saved rerun is the reproducible record; timings vary on a shared machine. This small absolute saving does not establish a 6x audiobook speedup.

Piper optimization is validated structurally with a fake provider: two chunks load once, full resume loads none, changed voice starts a new job load. These are explicitly test doubles, not real synthesis, audio-quality validation, or an inference speed measurement. No model was downloaded; no paid/public TTS/OCR endpoint was called. ffmpeg is installed but actual Piper/model integration is untested.

`python -m unittest discover -s tests -v`: 18 tests, 17 pass; the same original Windows-path test fails on Linux both before and after changes (`test_recent_project_entry_uses_output_dir_name_for_generic_output_txt`). Python compilation and diff checks pass. Baseline was 11 tests, 10 pass, same one failure. Full output is `tests.txt`.

## Remaining risks and migration gates

- Cancellation is checked between pages/chunks; in-flight requests/inference/ffmpeg can still block. Use bounded subprocess timeouts and cancel-aware providers next, without claiming instantaneous cancel today.
- TTS resume signature omits some provider/model/speaker settings; changes can reuse stale chunks. Expand signature with a version and voice-sample digest before a release.
- Model/API inference timing, audio duration (real-time factor), first-audio latency, peak RSS, PDF/OCR stage time, ffmpeg time, and resume integrity must be measured on the same content/settings/hardware before comparing languages.
- PDFium microbenchmarks do not cover scans, malformed PDFs, OCR quality, or end-to-end PDF extraction including pdfplumber page discovery.
- A Go worker must preserve all five TTS providers, PDF extraction+OCR+translation, GPU/native dependencies, cancellation/resume semantics, existing projects, packaging, and 27 UI languages. A pure Go rewrite would otherwise lose important functionality or still require sidecar runtimes.

## Reproduce locally

Install the project's requirements into an isolated environment (Piper is not required for these offline tests). Then run `python -m unittest discover -s tests -v`, `python scripts/profile_pdf_extraction.py`, and `python -m compileall -q pipeline.py tests scripts`.
