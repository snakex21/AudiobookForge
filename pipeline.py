import os
import json
import time
import base64
import hashlib
import threading
import subprocess
import shutil
import requests
import sys
import re
from pathlib import Path
from typing import Optional, Callable, Literal, List
from PIL import Image
import io

try:
    import torch
except Exception:
    torch = None

PDF_PATH = "book.pdf"
OUTPUT_DIR = "audiobook_output"
SPEAKER_WAV = "speaker.wav"


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


PROJECT_DIR = get_base_dir()

LLM_PROVIDER = "lmstudio"
LLM_URLS = {
    "lmstudio": "http://localhost:1234/v1",
    "ollama": "http://localhost:11434/v1",
    "openai_compatible": "http://localhost:8080/v1",
    "chatterbox": "http://localhost:8004/v1",
}
LLM_MODEL = None

CLOUD_PROVIDERS = ["openrouter", "anthropic", "openai", "nvidia", "groq", "mistral", "together"]
TTS_PROVIDERS = ["chatterbox", "piper", "elevenlabs", "edge_tts", "openai_tts", "custom"]
MODES = ["pdf_to_audio", "translate_to_audio", "translate_to_txt"]
AUDIO_LANGUAGE_SETTINGS = {
    "pol": {"language_code": "pl", "edge_voice": "pl-PL-AgnieszkaNeural"},
    "eng": {"language_code": "en", "edge_voice": "en-US-AriaNeural"},
    "deu": {"language_code": "de", "edge_voice": "de-DE-KatjaNeural"},
    "rus": {"language_code": "ru", "edge_voice": "ru-RU-SvetlanaNeural"},
    "ces": {"language_code": "cs", "edge_voice": "cs-CZ-VlastaNeural"},
    "fra": {"language_code": "fr", "edge_voice": "fr-FR-DeniseNeural"},
    "ukr": {"language_code": "uk", "edge_voice": "uk-UA-PolinaNeural"},
    "spa": {"language_code": "es", "edge_voice": "es-ES-ElviraNeural"},
    "ita": {"language_code": "it", "edge_voice": "it-IT-ElsaNeural"},
}
LANGUAGE_NAMES = {
    "pol": "polski",
    "eng": "angielski",
    "deu": "niemiecki",
    "rus": "rosyjski",
    "fra": "francuski",
    "ces": "czeski",
    "ukr": "ukraiński",
    "spa": "hiszpański",
    "ita": "włoski",
}

LANGUAGE_PROMPT_NAMES = {
    "pol": "Polish",
    "eng": "English",
    "deu": "German",
    "rus": "Russian",
    "fra": "French",
    "ces": "Czech",
    "ukr": "Ukrainian",
    "spa": "Spanish",
    "ita": "Italian",
    "por": "Portuguese",
    "nld": "Dutch",
    "swe": "Swedish",
    "tur": "Turkish",
}

LANGUAGE_STOPWORDS = {
    "pol": {"i", "w", "z", "na", "się", "sie", "że", "to", "nie", "jest", "do", "dla", "oraz", "ale", "jak", "które", "ktore", "przez"},
    "eng": {"the", "and", "to", "of", "in", "is", "for", "that", "with", "on", "as", "are", "be", "this", "by", "from"},
    "deu": {"der", "die", "das", "und", "ist", "nicht", "mit", "von", "zu", "ein", "eine", "den", "dem", "des", "auf", "für", "fur", "als", "auch", "im", "in"},
    "rus": {"и", "в", "не", "на", "что", "это", "с", "по", "для", "как", "из", "к", "но", "она", "он", "бы"},
    "fra": {"le", "la", "les", "de", "des", "et", "en", "un", "une", "pour", "dans", "est", "sur", "avec", "par", "que"},
    "ces": {"a", "v", "z", "na", "je", "se", "to", "že", "pro", "s", "do", "jako", "které", "ktere", "ale", "by"},
    "ukr": {"і", "в", "не", "на", "що", "це", "з", "до", "для", "як", "але", "по", "та", "у", "які", "yaki"},
    "spa": {"el", "la", "los", "las", "de", "del", "y", "en", "para", "con", "que", "por", "una", "un", "como", "es"},
    "ita": {"il", "lo", "la", "gli", "le", "di", "del", "e", "in", "per", "con", "che", "una", "un", "come", "è", "e"},
    "por": {"o", "a", "os", "as", "de", "do", "da", "e", "em", "para", "com", "que", "uma", "um", "como", "é"},
    "nld": {"de", "het", "een", "en", "van", "in", "op", "voor", "met", "dat", "als", "is", "te", "door", "uit", "niet"},
    "swe": {"och", "det", "att", "i", "en", "som", "på", "för", "med", "är", "av", "till", "den", "detta", "inte", "från"},
    "tur": {"ve", "bir", "bu", "için", "ile", "da", "de", "olan", "olarak", "çok", "gibi", "ama", "daha", "mi", "ne", "ya"},
}


def detect_gpu() -> str:
    try:
        if torch and torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            is_amd = any(x in name.upper() for x in ["AMD", "RADEON", "RX"])
            return name + (" (ROCm)" if is_amd else " (CUDA)")
    except:
        pass
    try:
        rocminfo_paths = [
            "rocminfo",
            r"C:\Program Files\AMD\ROCm\bin\rocminfo.exe",
            r"C:\Program Files\AMD\ROCm\5.7\bin\rocminfo.exe",
            r"C:\Program Files\AMD\ROCm\6.2\bin\rocminfo.exe",
        ]
        for rocminfo in rocminfo_paths:
            try:
                result = subprocess.run([rocminfo], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "Marketing Name" in line:
                            return line.split(":")[-1].strip() + " (ROCm)"
            except FileNotFoundError:
                continue
    except:
        pass
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name"],
            capture_output=True, text=True, timeout=5
        )
        cards = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line == "Name":
                continue
            skip = ["Virtual", "Microsoft", "Meta", "Remote", "Basic", "Display"]
            if any(s in line for s in skip):
                continue
            cards.append(line)
        if cards:
            return cards[0] + " (bez CUDA/ROCm)"
    except:
        pass
    return "CPU (brak GPU)"


def resolve_project_path(path_value: str, default: str = OUTPUT_DIR) -> Path:
    candidate = Path(path_value or default)
    return candidate if candidate.is_absolute() else PROJECT_DIR / candidate


def get_audio_language_settings(language_code: str) -> dict:
    return AUDIO_LANGUAGE_SETTINGS.get(language_code, AUDIO_LANGUAGE_SETTINGS["pol"])


def format_duration(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def estimate_tokens(text: str) -> int:
    return max(0, len(text.strip()) // 4)


def chunk_sort_key(path: Path) -> int:
    match = re.search(r"chunk_(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def page_sort_key(path: Path) -> int:
    match = re.search(r"page_(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def build_job_signature(config: dict) -> dict:
    return {
        "mode": config.get("mode", "translate_to_audio"),
        "pdf_path": str(Path(config.get("pdf_path", "book.pdf")).resolve()) if config.get("pdf_path") else "",
        "txt_path": str(Path(config.get("txt_path", "")).resolve()) if config.get("txt_path") else "",
        "speaker_wav": str(Path(config.get("speaker_wav", "")).resolve()) if config.get("speaker_wav") else "",
        "pdf_language": config.get("pdf_language", "pol"),
        "target_language": config.get("target_language", "pol"),
        "extraction_mode": config.get("extraction_mode", "pypdfium"),
        "llm_provider": config.get("llm_provider", "lmstudio"),
        "llm_url": config.get("llm_url", ""),
        "llm_model": config.get("llm_model", ""),
        "tts_provider": config.get("tts_provider", "piper"),
        "piper_voice": config.get("piper_voice", ""),
        "edge_voice": config.get("edge_voice", ""),
        "export_pdf": config.get("export_pdf", False),
    }


def clear_previous_job_output(output_dir: Path) -> None:
    for stale_file in [
        output_dir / "output.txt",
        output_dir / "output_przetlumaczony.pdf",
        output_dir / "audiobook_final.mp3",
        output_dir / "filelist.txt",
        output_dir / "translation_state.json",
        output_dir / "tts_state.json",
        output_dir / "pipeline_stats.json",
    ]:
        stale_file.unlink(missing_ok=True)

    for stale_dir in [output_dir / "pages", output_dir / "chunks"]:
        if stale_dir.exists():
            shutil.rmtree(stale_dir, ignore_errors=True)


def prepare_output_dir_for_job(config: dict, output_dir: Path, log_callback: Callable[[str], None]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    state_file = output_dir / "job_state.json"
    current_state = build_job_signature(config)
    previous_state = None
    start_action = config.get("_job_start_action", "resume")

    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as handle:
                previous_state = json.load(handle)
        except Exception:
            previous_state = None

    if previous_state and start_action == "overwrite":
        clear_previous_job_output(output_dir)
        log_callback("Start od nowa - czyszcze stare pliki wyjsciowe.")
    elif previous_state and previous_state != current_state:
        raise Exception("Folder wyjsciowy zawiera inne zadanie. Wybierz wznowienie albo nowy folder.")
    elif previous_state == current_state:
        log_callback("Wykryto poprzedni stan zadania - wznowienie jest mozliwe.")

    with open(state_file, "w", encoding="utf-8") as handle:
        json.dump(current_state, handle, indent=2)


def read_output_text(output_dir: Path) -> str:
    output_file = output_dir / "output.txt"
    return output_file.read_text(encoding="utf-8") if output_file.exists() else ""


def count_output_pages(text_content: str) -> int:
    return text_content.count("=== Strona")


def stages_for_mode(mode: str) -> list[str]:
    if mode == "txt_to_audio":
        return ["audio", "merge"]
    if mode == "pdf_to_audio":
        return ["extraction", "audio", "merge"]
    if mode == "translate_to_txt":
        return ["extraction", "translation"]
    return ["extraction", "translation", "audio", "merge"]


def collect_pipeline_stats(
    output_dir: Path,
    start_time: float,
    mode: str = "translate_to_audio",
    stage_timings: Optional[dict] = None,
    current_stage: Optional[str] = None,
    completed: bool = False,
) -> dict:
    stage_timings = stage_timings or {}
    output_file = output_dir / "output.txt"
    pages_dir = output_dir / "pages"
    chunks_dir = output_dir / "chunks"
    text_content = read_output_text(output_dir)
    page_count = count_output_pages(text_content)
    rendered_page_count = len(list(pages_dir.glob("page_*.jpg"))) if pages_dir.exists() else 0
    chunk_count = len(list(chunks_dir.glob("chunk_*.mp3"))) if chunks_dir.exists() else 0
    enabled_stages = stages_for_mode(mode)

    stages = {}
    for stage_name in ["extraction", "translation", "audio", "merge"]:
        if stage_name not in enabled_stages:
            status = "skipped"
        elif stage_name in stage_timings:
            status = "completed"
        elif completed:
            status = "pending"
        elif current_stage == stage_name:
            status = "running"
        else:
            status = "pending"

        stage_stats = {
            "status": status,
            "elapsed_seconds": round(stage_timings.get(stage_name, 0), 2),
        }
        if stage_name == "extraction":
            stage_stats["page_count"] = rendered_page_count if mode in {"translate_to_audio", "translate_to_txt"} else page_count
        elif stage_name == "translation":
            stage_stats["page_count"] = page_count
            stage_stats["estimated_tokens"] = estimate_tokens(text_content)
        elif stage_name == "audio":
            stage_stats["chunk_count"] = chunk_count
        elif stage_name == "merge":
            stage_stats["final_audio_exists"] = (output_dir / "audiobook_final.mp3").exists()
        stages[stage_name] = stage_stats

    stats = {
        "elapsed_seconds": round(time.time() - start_time, 2),
        "mode": mode,
        "current_stage": None if completed else current_stage,
        "completed": completed,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "character_count": len(text_content),
        "estimated_tokens": estimate_tokens(text_content),
        "stages": stages,
    }
    with open(output_dir / "pipeline_stats.json", "w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2)
    return stats


def load_json_file(path: Path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def save_json_file(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def extract_translation_state_from_output(output_file: Path) -> dict:
    if not output_file.exists():
        return {"pages": {}}

    content = output_file.read_text(encoding="utf-8")
    pages = {}
    pattern = re.compile(r"(?:^|\n)=== Strona (\d+) ===\n(.*?)(?=(?:\n=== Strona \d+ ===\n)|\Z)", re.S)
    for match in pattern.finditer(content):
        page_num = match.group(1)
        page_text = match.group(2).strip()
        error_match = re.fullmatch(r"\[BŁĄD STRONY \d+: (.*)\]", page_text, re.S)
        if error_match:
            pages[page_num] = {"status": "failed", "error": error_match.group(1).strip()}
        else:
            pages[page_num] = {"status": "completed", "text": page_text}
    return {"pages": pages}


def save_translation_output(output_file: Path, translation_state: dict) -> None:
    lines = []
    for page_num in sorted((int(key) for key in translation_state.get("pages", {})), key=int):
        page_state = translation_state["pages"][str(page_num)]
        text = page_state.get("text", "") if page_state.get("status") == "completed" else f"[BŁĄD STRONY {page_num}: {page_state.get('error', 'nieznany błąd')}]"
        lines.append(f"=== Strona {page_num} ===\n{text}".strip())

    output_text = "\n\n".join(lines)
    if output_text:
        output_text += "\n"
    output_file.write_text(output_text, encoding="utf-8")


def should_skip_tts_chunk(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True

    compact = re.sub(r"\s+", "", stripped)
    if re.fullmatch(r"[\W_]+", compact, re.UNICODE):
        return True

    if re.fullmatch(r"(?i)[\[(]?(?:strona|page|p\.?)[\s:\-]*\d+[\])]?$", stripped):
        return True

    if re.fullmatch(r"(?i)[\[(]?(?:\d+|[ivxlcdm]+)(?:[\./\-:]\d+)?[\])]?$", compact):
        return True

    word_tokens = re.findall(r"[A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻżЀ-ӿ]{2,}", stripped)
    if word_tokens:
        return False

    letters = len(re.findall(r"[A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻżЀ-ӿ]", stripped))
    digits = len(re.findall(r"\d", stripped))
    symbols = len(re.findall(r"[^\w\s]", stripped, re.UNICODE))
    return letters <= 3 and digits + symbols >= max(3, letters)


def resolve_ffmpeg_path() -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path and not ffmpeg_path.lower().endswith("python313\\scripts\\ffmpeg.exe"):
        return ffmpeg_path

    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Replay" / "resources" / "bin" / "ffmpeg.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python313" / "Lib" / "site-packages" / "panda3d_tools" / "ffmpeg.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise Exception("Nie znaleziono działającego ffmpeg.exe")


def list_llm_models(url: str, api_key: Optional[str] = None, log_callback: Optional[Callable[[str], None]] = None) -> List[str]:
    models = []
    endpoints = [f"{url}/models", f"{url.rstrip('/v1')}/api/v0/models"]

    log = log_callback or print

    for endpoint in endpoints:
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            resp = requests.get(endpoint, headers=headers, timeout=15)
            log(f"DEBUG {endpoint}: {resp.status_code} {resp.text[:200]}")
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data:
                    models = [m["id"] for m in data["data"] if "id" in m]
                elif "models" in data:
                    models = [m.get("id") or m.get("name") for m in data["models"]]
                if models:
                    break
        except Exception as e:
            log(f"DEBUG error {endpoint}: {e}")

    return [m for m in models if m]


def detect_llm_model(url: str, api_key: Optional[str] = None) -> Optional[str]:
    models = list_llm_models(url, api_key)
    return models[0] if models else None


def pdf_to_images(pdf_path: Path, output_dir: Path, log_callback: Callable[[str], None], progress_callback: Callable[[str, int, int], None], start_page: int = 1):
    import pypdfium2 as pdfium

    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        total = len(pdf)

        for i in range(start_page - 1, len(pdf)):
            page_num = i + 1
            page_path = pages_dir / f"page_{page_num:03d}.jpg"
            if page_path.exists():
                progress_callback("translation", page_num, total)
                continue
            page = pdf[i]
            bitmap = page.render(scale=200 / 72, rotation=0)
            pil_image = bitmap.to_pil()
            pil_image.save(str(page_path), "JPEG")
            progress_callback("translation", page_num, total)
            log_callback(f"Zapisano stronę {page_num}")
    finally:
        pdf.close()

    return total


def extract_language_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻżЀ-ӿ']+", text.lower())


def get_language_score(text: str, lang_code: str) -> int:
    stopwords = LANGUAGE_STOPWORDS.get(lang_code)
    if not stopwords:
        return 0
    tokens = extract_language_tokens(text)
    return sum(1 for token in tokens if token in stopwords)


def looks_like_untranslated_page(text: str, source_lang: str, target_lang: str) -> bool:
    if source_lang == target_lang:
        return False

    if source_lang not in LANGUAGE_STOPWORDS or target_lang not in LANGUAGE_STOPWORDS:
        return False

    tokens = extract_language_tokens(text)
    if len(tokens) < 25:
        return False

    source_score = get_language_score(text, source_lang)
    target_score = get_language_score(text, target_lang)
    source_ratio = source_score / max(1, len(tokens))

    return source_score >= 4 and source_ratio >= 0.06 and source_score > max(2, target_score * 2)


def build_translation_prompt(source_lang: str, target_lang: str, stricter: bool = False) -> str:
    source_name = LANGUAGE_PROMPT_NAMES.get(source_lang, source_lang)
    target_name = LANGUAGE_PROMPT_NAMES.get(target_lang, target_lang)
    prompt = (
        f"Read the page and translate all meaningful prose from {source_name} into {target_name}. "
        f"Return only the translated page text in {target_name}. "
        "Preserve proper names, book titles in original script, ISBN numbers, e-mail addresses, URLs, publisher names, and other metadata when appropriate. "
        "Do not keep full sentences or paragraphs in the source language unless they are explicit quotations or titles that should remain in the original form. "
        "If the page contains only page numbers, isolated punctuation, or meaningless OCR garbage, return an empty string."
    )
    if stricter:
        prompt += (
            f" IMPORTANT: the previous answer kept too much {source_name}. "
            f"This retry must output prose predominantly in {target_name}. "
            f"Do not leave body paragraphs in {source_name}."
        )
    return prompt


def translate_page(image_path: Path, llm_url: str, model: str, api_key: Optional[str] = None,
                   source_lang: str = "pol", target_lang: str = "pol",
                   log_callback: Optional[Callable[[str], None]] = None) -> str:
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    last_text = ""
    for attempt in range(2):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": build_translation_prompt(source_lang, target_lang, stricter=attempt > 0)},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
                ]}
            ],
            "max_tokens": 4096
        }

        try:
            resp = requests.post(f"{llm_url}/chat/completions", json=payload, headers=headers, timeout=120)
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
            last_text = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"API error: {e}")

        if not looks_like_untranslated_page(last_text, source_lang, target_lang):
            return last_text

        if log_callback:
            log_callback("Wynik tłumaczenia wygląda na pozostawiony w języku źródłowym - ponawiam stronę z ostrzejszym promptem.")

    raise Exception("Model zwrócił tekst wyglądający na nieprzetłumaczony po ponowieniu próby")


def ocr_page_with_vision(image_path: Path, llm_url: str, model: str, api_key: Optional[str] = None) -> str:
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Przeczytaj i przepisz dokładnie cały tekst widoczny na obrazku. Zachowaj oryginalną treść bez tłumaczenia. Zwróć TYLKO tekst, bez komentarzy.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
                ],
            },
        ],
        "max_tokens": 4096,
    }

    resp = requests.post(f"{llm_url}/chat/completions", json=payload, headers=headers, timeout=120)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    raise Exception(f"HTTP {resp.status_code}: {resp.text}")


def translate_pdf(pdf_path: Path, output_dir: Path, llm_url: str, model: str, api_key: Optional[str],
                  source_lang: str, target_lang: str,
                  log_callback: Callable[[str], None], progress_callback: Callable[[str, int, int], None], pause_event: threading.Event, stop_event: threading.Event):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "output.txt"
    translation_state_file = output_dir / "translation_state.json"
    translation_state = load_json_file(translation_state_file, {"pages": {}})
    if not translation_state.get("pages"):
        translation_state = extract_translation_state_from_output(output_file)

    completed_pages = sorted(
        int(page_num)
        for page_num, page_state in translation_state.get("pages", {}).items()
        if page_state.get("status") == "completed"
    )
    if completed_pages:
        log_callback(f"Wznowienie tłumaczenia - gotowe strony: {len(completed_pages)}")

    pages_dir = output_dir / "pages"
    page_files = sorted(pages_dir.glob("page_*.jpg"), key=page_sort_key)
    total_pages = len(page_files)

    for i, page_file in enumerate(page_files):
        if stop_event.is_set():
            break

        page_num = i + 1
        page_state = translation_state.setdefault("pages", {}).get(str(page_num), {})
        if page_state.get("status") == "completed":
            progress_callback("translation", page_num, total_pages)
            continue

        while pause_event.is_set():
            time.sleep(0.5)
            if stop_event.is_set():
                break

        if stop_event.is_set():
            break

        try:
            text = translate_page(page_file, llm_url, model, api_key, source_lang=source_lang, target_lang=target_lang, log_callback=log_callback)
            translation_state["pages"][str(page_num)] = {"status": "completed", "text": text}
            log_callback(f"Przetłumaczono stronę {page_num}")
        except Exception as e:
            translation_state["pages"][str(page_num)] = {"status": "failed", "error": str(e)}
            log_callback(f"Błąd strony {page_num}: {e}")

        save_translation_output(output_file, translation_state)
        save_json_file(translation_state_file, translation_state)
        progress_callback("translation", page_num, total_pages)

    failed_pages = sorted(
        int(page_num)
        for page_num, page_state in translation_state.get("pages", {}).items()
        if page_state.get("status") == "failed"
    )
    if failed_pages and not stop_event.is_set():
        raise Exception(f"Nie udalo sie przetlumaczyc stron: {', '.join(map(str, failed_pages[:20]))}")

    log_callback("Tłumaczenie zakończone")


def generate_audio_with_edge_tts(text: str, output_path: Path, voice: str = "pl-PL-AgnieszkaNeural",
                                 log_callback: Optional[Callable[[str], None]] = None, retries: int = 4):
    import edge_tts

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            output_path.unlink(missing_ok=True)
            communicate = edge_tts.Communicate(text, voice)
            communicate.save_sync(str(output_path))
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("Edge TTS wygenerowal pusty plik")
            return
        except Exception as exc:
            output_path.unlink(missing_ok=True)
            last_error = exc
            error_text = f"{type(exc).__name__}: {exc}"
            transient_error = any(token in error_text for token in [
                "503",
                "WSServerHandshakeError",
                "Invalid response status",
                "ServerDisconnectedError",
                "TimeoutError",
                "ClientConnectorError",
                "NoAudioReceived",
                "No audio was received",
            ])
            if transient_error and attempt < retries:
                if log_callback:
                    log_callback(f"Edge TTS retry {attempt}/{retries - 1} po bledzie: {exc}")
                time.sleep(min(2 * attempt, 8))
                continue
            raise last_error


def generate_audio_with_elevenlabs(text: str, output_path: Path, api_key: str, voice_id: str = "rachel"):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", 
                         json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
                         headers=headers, timeout=60)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)


def generate_audio_with_openai_tts(text: str, output_path: Path, api_key: str, model: str = "tts-1", voice: str = "alloy"):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post("https://api.openai.com/v1/audio/speech", 
                         json={"model": model, "input": text, "voice": voice},
                         headers=headers, timeout=60)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)


def generate_audio_with_chatterbox(text: str, output_path: Path,
                                   speaker_wav: Optional[Path] = None,
                                   url: str = "http://localhost:8004/v1"):
    headers = {"Content-Type": "application/json"}

    if speaker_wav and speaker_wav.exists():
        with open(speaker_wav, "rb") as f:
            wav_data = base64.b64encode(f.read()).decode()
        payload = {
            "model": "chatterbox",
            "input": text,
            "voice": "clone",
            "voice_sample": wav_data,
        }
    else:
        payload = {
            "model": "chatterbox",
            "input": text,
            "voice": "default",
        }

    resp = requests.post(f"{url}/audio/speech", json=payload, headers=headers, timeout=120)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
    else:
        raise Exception(f"Chatterbox error: {resp.status_code} {resp.text}")


def generate_audio_with_piper(text: str, output_path: Path,
                              model_path: Optional[Path] = None):
    from piper.voice import PiperVoice
    import wave

    if model_path is None:
        model_path = PROJECT_DIR / "piper_models" / "pl_PL-gosia-medium.onnx"

    if not model_path.exists():
        raise Exception(f"Model Piper nie znaleziony: {model_path}")

    voice = PiperVoice.load(str(model_path))

    wav_path = output_path.with_suffix(".wav")
    with wave.open(str(wav_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    wav_size = wav_path.stat().st_size
    if wav_size == 0:
        raise Exception("Piper wygenerował pusty WAV")

    ffmpeg_path = resolve_ffmpeg_path()
    result = subprocess.run(
        [ffmpeg_path, "-i", str(wav_path), "-y", str(output_path)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHOME": "", "PYTHONPATH": ""}
    )
    wav_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise Exception(f"ffmpeg error: {result.stderr}")

    mp3_size = output_path.stat().st_size
    if mp3_size == 0:
        raise Exception("ffmpeg wygenerował pusty MP3")


def text_to_audio(output_dir: Path, tts_provider: str, speaker_wav: Optional[Path] = None,
                  api_key: Optional[str] = None, chatterbox_url: str = LLM_URLS["chatterbox"],
                  log_callback: Callable[[str], None] = None, progress_callback: Callable[[str, int, int], None] = None,
                  pause_event: threading.Event = None, stop_event: threading.Event = None,
                  language_code: str = "pl", edge_voice: Optional[str] = None,
                  piper_voice: str = "pl_PL-zenski-medium"):
    output_file = output_dir / "output.txt"
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    tts_state_file = output_dir / "tts_state.json"

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    current_tts_settings = {
        "tts_provider": tts_provider,
        "piper_voice": piper_voice if tts_provider == "piper" else None,
        "edge_voice": edge_voice if tts_provider == "edge_tts" else None,
        "content_hash": hashlib.sha1(content.encode("utf-8")).hexdigest(),
    }

    tts_state = load_json_file(tts_state_file, {})
    previous_tts_settings = tts_state.get("settings") if isinstance(tts_state, dict) else None
    if previous_tts_settings is None and isinstance(tts_state, dict):
        previous_tts_settings = {key: tts_state.get(key) for key in ["tts_provider", "piper_voice", "edge_voice"]}
        tts_state = {"settings": previous_tts_settings, "chunks": {}}

    if previous_tts_settings != current_tts_settings:
        removed_chunks = 0
        for chunk_path in chunks_dir.glob("chunk_*.mp3"):
            chunk_path.unlink(missing_ok=True)
            removed_chunks += 1

        for stale_file in [output_dir / "audiobook_final.mp3", output_dir / "filelist.txt"]:
            stale_file.unlink(missing_ok=True)

        if removed_chunks:
            log_callback("Zmieniono ustawienia glosu TTS - usuwam stare chunki audio.")

        tts_state = {"settings": current_tts_settings, "chunks": {}}
    else:
        tts_state = {"settings": current_tts_settings, "chunks": tts_state.get("chunks", {})}

    save_json_file(tts_state_file, tts_state)

    raw_chunks = content.split("\n\n")
    chunk_list = []
    for raw_chunk in raw_chunks:
        lines = [line for line in raw_chunk.splitlines() if line.strip() and not line.strip().startswith("===")]
        cleaned_chunk = "\n".join(lines).strip()
        if cleaned_chunk:
            chunk_list.append(cleaned_chunk)
    total_chunks = len(chunk_list)
    failed_chunks = []
    completed_chunks = 0

    for i, chunk in enumerate(chunk_list):
        if stop_event and stop_event.is_set():
            break

        if pause_event:
            while pause_event.is_set():
                time.sleep(0.5)
                if stop_event and stop_event.is_set():
                    break

        if stop_event and stop_event.is_set():
            break

        chunk_num = i + 1
        chunk_key = f"{chunk_num:03d}"
        chunk_file = chunks_dir / f"chunk_{chunk_key}.mp3"
        chunk_state = tts_state["chunks"].get(chunk_key, {})

        if should_skip_tts_chunk(chunk):
            if chunk_state.get("status") != "skipped":
                log_callback(f"Pominięto chunk {chunk_num}: wykryto pusty lub śmieciowy tekst")
            tts_state["chunks"][chunk_key] = {"status": "skipped", "reason": "garbage_text"}
            save_json_file(tts_state_file, tts_state)
            progress_callback("audio", chunk_num, total_chunks)
            continue

        if chunk_state.get("status") == "completed" and chunk_file.exists():
            log_callback(f"Pominięto chunk {i+1}")
            progress_callback("audio", i+1, total_chunks)
            completed_chunks += 1
            continue

        try:
            if tts_provider == "edge_tts":
                voice = edge_voice or "pl-PL-ZofiaNeural"
                generate_audio_with_edge_tts(chunk, chunk_file, voice=voice, log_callback=log_callback)
            elif tts_provider == "piper":
                piper_model = PROJECT_DIR / "piper_models" / f"{piper_voice}.onnx"
                generate_audio_with_piper(chunk, chunk_file, model_path=piper_model)
            elif tts_provider == "elevenlabs":
                if api_key:
                    generate_audio_with_elevenlabs(chunk, chunk_file, api_key)
            elif tts_provider == "openai_tts":
                if api_key:
                    generate_audio_with_openai_tts(chunk, chunk_file, api_key)
            elif tts_provider == "chatterbox":
                generate_audio_with_chatterbox(chunk, chunk_file, speaker_wav=speaker_wav, url=chatterbox_url)

            tts_state["chunks"][chunk_key] = {"status": "completed"}
            save_json_file(tts_state_file, tts_state)
            log_callback(f"Wygenerowano chunk {i+1}/{total_chunks}")
            completed_chunks += 1
        except Exception as e:
            chunk_file.unlink(missing_ok=True)
            tts_state["chunks"][chunk_key] = {"status": "failed", "error": str(e)}
            save_json_file(tts_state_file, tts_state)
            log_callback(f"Błąd chunk {i+1}: {e}")
            import traceback
            log_callback(traceback.format_exc())
            failed_chunks.append(i + 1)
            continue

        progress_callback("audio", i+1, total_chunks)

    if completed_chunks == 0 and not failed_chunks:
        raise Exception("Brak chunków do wygenerowania audio po odfiltrowaniu pustych lub śmieciowych fragmentów")

    if failed_chunks:
        raise Exception(f"Nie udalo sie wygenerowac chunkow: {', '.join(map(str, failed_chunks[:20]))}")

    log_callback("Generowanie audio zakończone")


def fix_polish_encoding(text: str) -> str:
    """Naprawia błędnie zdekodowane polskie znaki z MacRoman/Latin-2"""
    replacements = {
        "∏": "ł", "Ł": "Ł", "¸": "Ł",
        "˝": "ż", "˚": "ź",
        "Ê": "ś",
        "à": "ą", "À": "Ą",
        "´": "ę", "ę": "ę",
        "ó": "ó",
        "ç": "ć", "Ç": "Ć",
        "ñ": "ń", "Ñ": "Ń",
        "ö": "ö",
        "ź": "ź",
        "∑": "Ś",
        "„": "„", '"': '"',
        "ƒ": "ą",
        "Ω": "ż",
        "≤": "ś",
        "\x01": "", "\x02": "", "\x03": "",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def extract_text_pypdfium(pdf_path: Path, page_num: int) -> str:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        page = pdf[page_num - 1]
        textpage = page.get_textpage()
        return textpage.get_text_range().strip()
    finally:
        pdf.close()


def render_page_to_image(pdf_path: Path, page_num: int, output_dir: Path, dpi: int = 200) -> Path:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        page = pdf[page_num - 1]
        scale = dpi / 72
        bitmap = page.render(scale=scale, rotation=0)
        pil_image = bitmap.to_pil()
    finally:
        pdf.close()

    img_path = output_dir / "pages" / f"page_{page_num:03d}.jpg"
    img_path.parent.mkdir(exist_ok=True)
    pil_image.save(str(img_path), "JPEG")
    return img_path


def ocr_page_with_retries(image_path: Path, page_num: int, llm_url: str, model: str, api_key: Optional[str], log_callback: Callable[[str], None]) -> str:
    text = ocr_page_with_vision(image_path, llm_url, model, api_key)

    if len(text.strip()) == 0:
        log_callback(f"Strona {page_num}: pusta odpowiedź, retry 1...")
        time.sleep(2)
        text = ocr_page_with_vision(image_path, llm_url, model, api_key)

    if len(text.strip()) == 0:
        log_callback(f"Strona {page_num}: pusta odpowiedź, retry 2...")
        time.sleep(3)
        text = ocr_page_with_vision(image_path, llm_url, model, api_key)

    if len(text.strip()) == 0:
        log_callback(f"Strona {page_num}: BRAK TEKSTU po 3 próbach - pomijam")
        text = f"[STRONA {page_num} - nie udało się odczytać]"

    return text


def extract_pdf_text_direct(pdf_path: Path, output_dir: Path, llm_url: str, llm_model: str, api_key: Optional[str],
                            log_callback: Callable[[str], None], progress_callback: Callable[[str, int, int], None],
                            pause_event: threading.Event, stop_event: threading.Event,
                            extraction_mode: str = "pypdfium") -> Path:
    import pdfplumber

    output_file = output_dir / "output.txt"
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_pages = 0
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            existing_pages = f.read().count("=== Strona")
        if existing_pages > 0:
            log_callback(f"Wznów od strony {existing_pages + 1}")

    with pdfplumber.open(str(pdf_path)) as pdf, open(output_file, "a", encoding="utf-8") as handle:
        total_pages = len(pdf.pages)

        for index, page in enumerate(pdf.pages, start=1):
            if stop_event and stop_event.is_set():
                break

            page_num = index
            if page_num <= existing_pages:
                continue

            while pause_event and pause_event.is_set():
                time.sleep(0.5)
                if stop_event and stop_event.is_set():
                    break

            if stop_event and stop_event.is_set():
                break

            if extraction_mode == "llm_vision":
                try:
                    img_path = render_page_to_image(pdf_path, page_num, output_dir=output_dir)
                    text = ocr_page_with_retries(img_path, page_num, llm_url, llm_model, api_key, log_callback)
                    log_callback(f"Strona {page_num}: LLM Vision OCR ({len(text)} znakow)")
                except Exception as e:
                    text = ""
                    log_callback(f"Błąd Vision strony {page_num}: {e}")
            else:
                try:
                    text = extract_text_pypdfium(pdf_path, page_num)
                except Exception:
                    text = (page.extract_text() or "").strip()
                text = fix_polish_encoding(text)
                if len(text) > 20:
                    log_callback(f"Strona {page_num}: pypdfium ({len(text)} znakow)")
                else:
                    try:
                        img_path = render_page_to_image(pdf_path, page_num, output_dir=output_dir)
                        text = ocr_page_with_retries(img_path, page_num, llm_url, llm_model, api_key, log_callback)
                        log_callback(f"Strona {page_num}: skan OCR ({len(text)} znakow)")
                    except Exception as e:
                        log_callback(f"Błąd OCR strony {page_num}: {e}")

            handle.write(f"\n=== Strona {page_num} ===\n{text}\n")
            if len(text) <= 20 and extraction_mode == "llm_vision":
                log_callback(f"Strona {page_num}: brak tekstu po Vision OCR")
            elif len(text) <= 20 and extraction_mode != "llm_vision":
                log_callback(f"Strona {page_num}: zapisano pusty lub bardzo krótki tekst")

            handle.flush()
            progress_callback("translation", page_num, total_pages)

    return output_file


def pdf_to_audio_direct(pdf_path: Path, output_dir: Path, tts_provider: str, speaker_wav: Optional[Path],
                        api_key: Optional[str], chatterbox_url: str, pdf_language: str, llm_url: str, llm_model: str, llm_api_key: Optional[str], log_callback: Callable[[str], None],
                        progress_callback: Callable[[str, int, int], None], pause_event: threading.Event,
                        stop_event: threading.Event, piper_voice: str = "pl_PL-zenski-medium",
                        extraction_mode: str = "pypdfium", edge_voice: Optional[str] = None) -> Path:
    language = get_audio_language_settings(pdf_language)
    extracted_output = extract_pdf_text_direct(pdf_path, output_dir, llm_url, llm_model, llm_api_key, log_callback, progress_callback, pause_event, stop_event, extraction_mode)

    if not extracted_output.exists():
        raise Exception("Ekstrakcja tekstu nie utworzyła output.txt")

    if extracted_output.stat().st_size == 0:
        raise Exception("Ekstrakcja tekstu zakończyła się pustym output.txt")

    if stop_event and stop_event.is_set():
        return output_dir / "output.txt"

    text_to_audio(
        output_dir,
        tts_provider,
        speaker_wav,
        api_key,
        chatterbox_url,
        log_callback,
        progress_callback,
        pause_event,
        stop_event,
        language_code=language["language_code"],
        edge_voice=edge_voice or language["edge_voice"],
        piper_voice=piper_voice,
    )

    if stop_event and stop_event.is_set():
        return output_dir / "chunks"

    merge_audio_chunks(output_dir, log_callback, progress_callback)
    return output_dir / "audiobook_final.mp3"


def merge_audio_chunks(output_dir: Path, log_callback: Callable[[str], None], progress_callback: Callable[[str, int, int], None]):
    chunks_dir = output_dir / "chunks"
    chunks = sorted(chunks_dir.glob("chunk_*.mp3"), key=chunk_sort_key)

    filelist = output_dir / "filelist.txt"
    with open(filelist, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(f"file '{chunk.resolve()}'\n")

    output_file = output_dir / "audiobook_final.mp3"

    total = len(chunks)
    for i, chunk in enumerate(chunks):
        progress_callback("merge", i+1, total)

    ffmpeg_path = resolve_ffmpeg_path()
    cmd = [ffmpeg_path, "-f", "concat", "-safe", "0", "-i", str(filelist), "-c", "copy", "-y", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PYTHONHOME": "", "PYTHONPATH": ""})

    if result.returncode != 0:
        log_callback(f"Błąd ffmpeg: {result.stderr}")
        if not chunks:
            log_callback("BRAK CHUNKÓW — Piper nie wygenerował żadnego audio. Sprawdź czy model piper jest pobrany i czy piper-tts jest zainstalowany.")
            raise Exception("Merging failed — brak chunków audio")
        raise Exception("Merging failed")

    log_callback(f"Zapisano {output_file}")
    progress_callback("merge", total, total)


def export_translated_pdf(output_dir: Path, log_callback: Callable[[str], None]):
    output_file = output_dir / "output.txt"
    if not output_file.exists():
        log_callback("Brak pliku output.txt - pomijam eksport PDF")
        return None

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        pdf_file = output_dir / "output_przetlumaczony.pdf"

        font_path = PROJECT_DIR / "DejaVuSans.ttf"
        if not font_path.exists():
            import urllib.request
            font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
            urllib.request.urlretrieve(font_url, font_path)

        pdfmetrics.registerFont(TTFont('DejaVu', str(font_path)))

        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='DejaVu', fontSize=12, leading=16)

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        story = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("==="):
                continue
            if line.startswith("[BŁĄD"):
                continue
            story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 0.2*cm))

        doc.build(story)
        log_callback(f"Zapisano PDF: {pdf_file}")
        return pdf_file
    except Exception as e:
        log_callback(f"Błąd eksportu PDF: {e}")
        import traceback
        log_callback(traceback.format_exc())
        return None


def run_pipeline(config: dict, log_callback: Callable[[str], None], progress_callback: Callable[[str, int, int], None], pause_event: threading.Event, stop_event: threading.Event):
    started_at = time.time()
    pdf_path = Path(config.get("pdf_path", "book.pdf"))
    output_dir = resolve_project_path(config.get("output_dir", OUTPUT_DIR))
    speaker_wav = Path(config.get("speaker_wav", "speaker.wav")) if config.get("speaker_wav") else None
    txt_path = Path(config.get("txt_path")) if config.get("txt_path") else None
    mode = config.get("mode", "translate_to_audio")
    pdf_language = config.get("pdf_language", "pol")
    target_language = config.get("target_language", "pol")

    llm_provider = config.get("llm_provider", "lmstudio")
    llm_url = config.get("llm_url", LLM_URLS.get(llm_provider, ""))
    llm_model = config.get("llm_model") or None
    llm_api_key = config.get("llm_api_key")

    tts_provider = config.get("tts_provider", "chatterbox")
    piper_voice = config.get("piper_voice", "pl_PL-zenski-medium")
    edge_voice = config.get("edge_voice", "pl-PL-ZofiaNeural")
    extraction_mode = config.get("extraction_mode", "pypdfium")
    chatterbox_url = config.get("chatterbox_url", LLM_URLS["chatterbox"])
    tts_api_key = config.get("tts_api_key")
    export_pdf = config.get("export_pdf", True)

    prepare_output_dir_for_job(config, output_dir, log_callback)

    stage_timings = {}

    def persist_stats(current_stage: Optional[str] = None, completed: bool = False) -> dict:
        return collect_pipeline_stats(
            output_dir,
            started_at,
            mode=mode,
            stage_timings=stage_timings,
            current_stage=current_stage,
            completed=completed,
        )

    log_callback(f"MODE: {mode}")
    log_callback(f"TTS: {tts_provider}")
    if tts_provider == "piper":
        log_callback(f"Piper voice: {piper_voice}")
    log_callback(f"GPU: {detect_gpu()}")

    if mode == "txt_to_audio":
        if txt_path:
            log_callback(f"TXT: {txt_path.name}")
        else:
            log_callback(f"TXT: {output_dir / 'output.txt'}")
    else:
        log_callback(f"PDF: {pdf_path.name}")
        log_callback(f"Extraction: {extraction_mode}")
        log_callback(f"LLM: {llm_provider} @ {llm_url}")

    if mode != "txt_to_audio" and llm_model is None and llm_provider not in CLOUD_PROVIDERS:
        llm_model = detect_llm_model(llm_url, llm_api_key)
        log_callback(f"Wykryto model: {llm_model}")

    if not llm_model and mode in {"pdf_to_audio", "translate_to_audio", "translate_to_txt"}:
        raise Exception("Brak wybranego modelu LLM. Zeskanuj modele LLM albo wybierz model ręcznie.")

    if mode != "txt_to_audio":
        log_callback(f"LLM model: {llm_model}")

    if mode == "translate_to_txt":
        export_pdf = False

    if mode == "txt_to_audio":
        language = get_audio_language_settings(pdf_language)
        txt_path_value = config.get("txt_path")
        output_txt = output_dir / "output.txt"
        source_txt = Path(txt_path_value) if txt_path_value else output_txt
        if not source_txt.exists():
            log_callback(f"Brak pliku TXT: {source_txt}")
            return {"error": "Brak output.txt"}
        if source_txt.resolve() != output_txt.resolve():
            output_dir.mkdir(parents=True, exist_ok=True)
            output_txt.write_text(source_txt.read_text(encoding="utf-8"), encoding="utf-8")
            log_callback(f"Skopiowano TXT do {output_txt}")
        log_callback("Wczytano output.txt — generuję audio...")
        persist_stats("audio")
        audio_started_at = time.time()
        text_to_audio(
            output_dir,
            tts_provider,
            speaker_wav,
            tts_api_key,
            chatterbox_url,
            log_callback,
            progress_callback,
            pause_event,
            stop_event,
            language["language_code"],
            edge_voice,
            piper_voice,
        )
        if stop_event.is_set():
            stage_timings["audio"] = time.time() - audio_started_at
            return {"stopped": True, "stats": persist_stats("audio")}
        stage_timings["audio"] = time.time() - audio_started_at
        persist_stats("merge")
        merge_started_at = time.time()
        merge_audio_chunks(output_dir, log_callback, progress_callback)
        stage_timings["merge"] = time.time() - merge_started_at
        log_callback("Gotowe!")
        return {"completed": True, "stats": persist_stats(completed=True)}

    if mode == "pdf_to_audio":
        language = get_audio_language_settings(pdf_language)
        persist_stats("extraction")
        extraction_started_at = time.time()
        output_file = extract_pdf_text_direct(
            pdf_path,
            output_dir,
            llm_url,
            llm_model,
            llm_api_key,
            log_callback,
            progress_callback,
            pause_event,
            stop_event,
            extraction_mode,
        )
        stage_timings["extraction"] = time.time() - extraction_started_at
        if stop_event.is_set():
            log_callback("Zatrzymano w trybie PDF -> Audio")
            return {"stopped": True, "stats": persist_stats("extraction")}

        if not output_file.exists():
            raise Exception("Ekstrakcja tekstu nie utworzyła output.txt")

        if output_file.stat().st_size == 0:
            raise Exception("Ekstrakcja tekstu zakończyła się pustym output.txt")

        persist_stats("audio")
        audio_started_at = time.time()
        text_to_audio(
            output_dir,
            tts_provider,
            speaker_wav,
            tts_api_key,
            chatterbox_url,
            log_callback,
            progress_callback,
            pause_event,
            stop_event,
            language["language_code"],
            edge_voice,
            piper_voice,
        )
        if stop_event.is_set():
            stage_timings["audio"] = time.time() - audio_started_at
            log_callback("Zatrzymano w trybie PDF -> Audio")
            return {"stopped": True, "stats": persist_stats("audio")}
        stage_timings["audio"] = time.time() - audio_started_at

        persist_stats("merge")
        merge_started_at = time.time()
        merge_audio_chunks(output_dir, log_callback, progress_callback)
        stage_timings["merge"] = time.time() - merge_started_at
        log_callback("Gotowe!")
        return {"completed": True, "output_file": output_file, "stats": persist_stats(completed=True)}

    persist_stats("extraction")
    extraction_started_at = time.time()
    pdf_to_images(pdf_path, output_dir, log_callback, progress_callback)
    stage_timings["extraction"] = time.time() - extraction_started_at

    persist_stats("translation")
    translation_started_at = time.time()
    translate_pdf(pdf_path, output_dir, llm_url, llm_model, llm_api_key, pdf_language, target_language, log_callback, progress_callback, pause_event, stop_event)
    stage_timings["translation"] = time.time() - translation_started_at

    if stop_event.is_set():
        log_callback("Zatrzymano przed audio")
        return {"stopped": True, "stats": persist_stats("translation")}

    pdf_result = None
    if export_pdf:
        pdf_result = export_translated_pdf(output_dir, log_callback)

    if mode == "translate_to_txt":
        log_callback("Gotowe!")
        return {"completed": True, "txt_file": output_dir / "output.txt", "stats": persist_stats(completed=True)}

    if stop_event.is_set():
        log_callback("Zatrzymano przed generowaniem audio")
        return {"stopped": True, "stats": persist_stats("translation")}

    language = get_audio_language_settings(target_language)
    persist_stats("audio")
    audio_started_at = time.time()
    text_to_audio(output_dir, tts_provider, speaker_wav, tts_api_key, chatterbox_url, log_callback, progress_callback, pause_event, stop_event, language["language_code"], edge_voice, piper_voice)
    stage_timings["audio"] = time.time() - audio_started_at

    if stop_event.is_set():
        log_callback("Zatrzymano przed scalanie")
        return {"stopped": True, "stats": persist_stats("audio")}

    persist_stats("merge")
    merge_started_at = time.time()
    merge_audio_chunks(output_dir, log_callback, progress_callback)
    stage_timings["merge"] = time.time() - merge_started_at

    log_callback("Gotowe!")
    return {"completed": True, "pdf_file": pdf_result if export_pdf else None, "stats": persist_stats(completed=True)}


def get_pdf_info(pdf_path: Path) -> dict:
    from pdf2image import pdfinfo_from_path
    try:
        info = pdfinfo_from_path(str(pdf_path))
        return {"pages": info.get("Pages", 0), "filename": pdf_path.name}
    except:
        return {"pages": 0, "filename": pdf_path.name}


def save_config(config: dict, path: Path = PROJECT_DIR / "config.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def load_config(path: Path = PROJECT_DIR / "config.json") -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
