import threading
from pathlib import Path
import json
import locale
import sys
import time


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_resource_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
    return Path(__file__).resolve().parent.parent


PROJECT_DIR = get_base_dir()
RESOURCE_DIR = get_resource_dir()
CONFIG_PATH = PROJECT_DIR / "config.json"
DEFAULT_OUTPUT_DIR = str(PROJECT_DIR / "audiobook_output")
DEFAULT_PDF_PATH = ""
DEFAULT_SPEAKER_WAV = ""
RECENT_PROJECT_LIMIT = 8
RECENT_PROJECT_CONFIG_KEYS = [
    "mode",
    "pdf_path",
    "txt_path",
    "project_source_file",
    "output_dir",
    "speaker_wav",
    "copy_source_to_project",
    "pdf_language",
    "target_language",
    "extraction_mode",
    "llm_provider",
    "llm_url",
    "llm_model",
    "tts_provider",
    "piper_voice",
    "piper_download_preset",
    "edge_voice",
    "export_pdf",
]


def normalize_path_value(path_value: str) -> str:
    if not path_value:
        return ""
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = PROJECT_DIR / candidate
    return str(candidate.resolve())


def build_recent_project_entry(config: dict, status: str | None = None) -> dict | None:
    output_dir = normalize_path_value(config.get("output_dir", ""))
    source_path = normalize_path_value(config.get("txt_path") or config.get("pdf_path") or "")
    has_saved_job = bool(output_dir) and (Path(output_dir) / "job_state.json").exists()
    if not source_path and not has_saved_job:
        return None

    snapshot = {}
    for key in RECENT_PROJECT_CONFIG_KEYS:
        value = config.get(key, "")
        if key in {"pdf_path", "txt_path", "output_dir", "speaker_wav"}:
            value = normalize_path_value(value)
        snapshot[key] = value

    source_name = Path(source_path).name if source_path else Path(output_dir or "project").name
    if source_name.lower() == "output.txt" and output_dir:
        source_name = Path(output_dir).name or source_name
    return {
        "name": source_name or "project",
        "source_path": source_path,
        "output_dir": output_dir,
        "mode": snapshot.get("mode", "pdf_to_audio"),
        "status": status or "configured",
        "last_opened_at": int(time.time()),
        "config": snapshot,
    }


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
        if lowered.startswith("sk"):
            return "slk"
        if lowered.startswith("sl"):
            return "slv"
        if lowered.startswith("hr"):
            return "hrv"
        if lowered.startswith("ro"):
            return "ro"
        if lowered.startswith("hu"):
            return "hu"
        if lowered.startswith("de"):
            return "de"
        if lowered.startswith("fr"):
            return "fr"
        if lowered.startswith("ca"):
            return "cat"
        if lowered.startswith("af"):
            return "af"
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
        if lowered.startswith("et"):
            return "est"
        if lowered.startswith("lv"):
            return "lav"
        if lowered.startswith("lt"):
            return "lit"
        if lowered.startswith("sv"):
            return "sv"
        if lowered.startswith("fi"):
            return "fi"
        if lowered.startswith("da"):
            return "da"
        if lowered.startswith("no") or lowered.startswith("nb"):
            return "no"
    return "en"


class AppState:
    def __init__(self):
        self.config = {
            "pdf_path": DEFAULT_PDF_PATH,
            "output_dir": DEFAULT_OUTPUT_DIR,
            "speaker_wav": DEFAULT_SPEAKER_WAV,
            "project_source_file": "",
            "copy_source_to_project": True,
            "app_language": detect_system_language(),
            "tts_provider": "piper",
            "piper_voice": "",
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
            "recent_projects": [],
            "ui_sections": {
                "work_mode": True,
                "source_files": True,
                "recent_projects": True,
                "pdf_settings": True,
                "text_extraction": True,
                "tts": True,
                "llm": True,
            },
        }
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.running = False
        self.logs = []

    def reset_events(self):
        self.pause_event.clear()
        self.stop_event.clear()

    def save(self):
        self.config["recent_projects"] = self._normalize_recent_projects(self.config.get("recent_projects", []))
        serializable_config = {k: v for k, v in self.config.items() if not k.startswith("_")}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(serializable_config, f, indent=2)

    def load(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.config.update(json.load(f))
        self.config.setdefault("recent_projects", [])
        self.config.setdefault("ui_sections", {})
        self.config["ui_sections"].setdefault("recent_projects", True)
        self.config["recent_projects"] = self._normalize_recent_projects(self.config.get("recent_projects", []))

    def _normalize_recent_projects(self, projects: list) -> list:
        normalized = []
        seen_output_dirs = set()
        for project in projects:
            if not isinstance(project, dict):
                continue
            config_snapshot = project.get("config")
            if not isinstance(config_snapshot, dict):
                config_snapshot = {}
            merged_config = {**config_snapshot}
            for key in RECENT_PROJECT_CONFIG_KEYS:
                if key in project and key not in merged_config:
                    merged_config[key] = project.get(key)
            normalized_project = build_recent_project_entry(
                merged_config,
                status=project.get("status", "configured"),
            )
            if not normalized_project:
                continue
            normalized_project["name"] = str(project.get("name") or normalized_project["name"])
            normalized_project["last_opened_at"] = int(project.get("last_opened_at", normalized_project["last_opened_at"]))
            output_dir = normalized_project.get("output_dir", "")
            if output_dir and output_dir in seen_output_dirs:
                continue
            if output_dir:
                seen_output_dirs.add(output_dir)
            normalized.append(normalized_project)
        normalized.sort(key=lambda item: item.get("last_opened_at", 0), reverse=True)
        return normalized[:RECENT_PROJECT_LIMIT]

    def remember_recent_project(self, config: dict | None = None, status: str | None = None):
        project = build_recent_project_entry(config or self.config, status=status)
        if not project:
            return
        existing_projects = self._normalize_recent_projects(self.config.get("recent_projects", []))
        existing_projects = [
            item for item in existing_projects
            if item.get("output_dir") != project.get("output_dir")
        ]
        self.config["recent_projects"] = [project, *existing_projects][:RECENT_PROJECT_LIMIT]


state = AppState()
state.load()
