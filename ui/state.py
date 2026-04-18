import threading
from pathlib import Path
import json
import locale


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config.json"
DEFAULT_OUTPUT_DIR = str(PROJECT_DIR / "audiobook_output")
DEFAULT_PDF_PATH = str(PROJECT_DIR / "book.pdf")
DEFAULT_SPEAKER_WAV = str(PROJECT_DIR / "speaker.wav")


def detect_system_language() -> str:
    candidates = []
    try:
        default_locale = locale.getdefaultlocale()[0]
        if default_locale:
            candidates.append(default_locale)
    except Exception:
        pass
    try:
        current_locale = locale.getlocale()[0]
        if current_locale:
            candidates.append(current_locale)
    except Exception:
        pass

    for lang in candidates:
        lowered = lang.lower()
        if lowered.startswith("pl"):
            return "pl"
        if lowered.startswith("cs") or lowered.startswith("cz"):
            return "cs"
        if lowered.startswith("de"):
            return "de"
        if lowered.startswith("fr"):
            return "fr"
        if lowered.startswith("es"):
            return "es"
        if lowered.startswith("it"):
            return "it"
        if lowered.startswith("ru"):
            return "ru"
        if lowered.startswith("uk"):
            return "uk"
        if lowered.startswith("tr"):
            return "tr"
        if lowered.startswith("pt"):
            return "pt"
        if lowered.startswith("nl"):
            return "nl"
        if lowered.startswith("sv"):
            return "sv"
    return "en"


class AppState:
    def __init__(self):
        self.config = {
            "pdf_path": DEFAULT_PDF_PATH,
            "output_dir": DEFAULT_OUTPUT_DIR,
            "speaker_wav": DEFAULT_SPEAKER_WAV,
            "app_language": detect_system_language(),
            "tts_provider": "piper",
            "piper_voice": "pl_PL-gosia-medium",
            "piper_download_preset": "pl_PL-gosia-medium",
            "edge_voice": "pl-PL-ZofiaNeural",
            "llm_provider": "lmstudio",
            "llm_url": "http://localhost:1234/v1",
            "llm_api_key": "",
            "llm_model": "",
            "mode": "pdf_to_audio",
            "pdf_language": "pol",
            "target_language": "pol",
            "extraction_mode": "pypdfium",
            "export_pdf": False,
        }
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.running = False
        self.logs = []

    def reset_events(self):
        self.pause_event.clear()
        self.stop_event.clear()

    def save(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def load(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.config.update(json.load(f))


state = AppState()
state.load()
