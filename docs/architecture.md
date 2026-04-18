# Architecture

## Overview

AudiobookForge is a local-first desktop application built with Python and `tkinter`.

Primary flow:

1. The UI collects mode, paths, language, OCR, LLM, and TTS settings.
2. `run_pipeline()` selects the execution path.
3. PDF pages are extracted directly or rendered for OCR.
4. Text is optionally translated through an LLM endpoint.
5. Text is split into chunks for TTS generation.
6. Audio chunks are merged into the final audiobook file.

## Main Modules

### `app.py`

- Application entry point.
- Starts the Tkinter UI.

### `ui/state.py`

- Stores application state and configuration.
- Loads and saves `config.json`.
- Detects the initial UI language from the operating system.
- Exposes pause and stop threading events.

### `ui/main_window.py`

- Builds the desktop UI.
- Handles dynamic form visibility by selected mode.
- Manages user-facing runtime logs.
- Handles Piper model download, scanning, and TTS/LLM selectors.
- Runs the pipeline in a background thread.

### `pipeline.py`

- Contains the main conversion pipeline.
- Handles PDF extraction, OCR, translation, TTS, and audio merging.

## Processing Modes

### `pdf_to_audio`

- Extract text from PDF.
- Use OCR fallback if direct extraction is weak.
- Generate audio and merge chunks.

### `translate_to_audio`

- Render PDF pages.
- Translate page content with an LLM.
- Generate audio from translated text.

### `translate_to_txt`

- Translate PDF content and save the result to `output.txt`.

### `txt_to_audio`

- Skip PDF and OCR.
- Read an existing `.txt` file.
- Generate and merge audio only.

## OCR Strategy

Primary path:

- direct extraction through `pypdfium2`

Fallback path:

- render page to image
- send image to Vision-capable LLM
- retry on empty OCR response

Additional handling:

- correction of malformed characters from some legacy PDFs

## TTS Strategy

### Piper

- local `.onnx` models
- offline generation
- voice selection based on downloaded models

### Edge TTS

- Microsoft neural voices
- language-specific voice selection

### Other Providers

- Chatterbox
- ElevenLabs
- OpenAI TTS

## Output Files

- `output.txt`
- `chunks/chunk_001.mp3`, `chunk_002.mp3`, ...
- `filelist.txt`
- `audiobook_final.mp3`

## Packaging Notes

- preferred packaging mode: `PyInstaller --onedir`
- `--onefile` may be unreliable with `piper-tts` and `pypdfium2`
- `ffmpeg` must exist in `PATH` or be bundled separately
