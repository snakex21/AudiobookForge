import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import traceback
from pipeline import run_pipeline, list_llm_models, LLM_URLS
from ui.state import state, PROJECT_DIR


BG = "#0d1117"
BG2 = "#161b22"
FG = "#c9d1d9"
FG_MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#e3b341"
FONT = ("Segoe UI", 10)
FONT_MONO = ("Cascadia Mono", 9)
FONT_TITLE = ("Segoe UI", 11, "bold")
EDGE_VOICES = [
    "pl-PL-ZofiaNeural",
    "pl-PL-MarekNeural",
    "pl-PL-AgnieszkaNeural",
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-DavisNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "de-DE-KatjaNeural",
    "de-DE-ConradNeural",
    "de-DE-AmalaNeural",
    "ru-RU-SvetlanaNeural",
    "ru-RU-DmitryNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-HenriNeural",
    "es-ES-ElviraNeural",
    "es-ES-AlvaroNeural",
    "it-IT-ElsaNeural",
    "it-IT-DiegoNeural",
    "cs-CZ-VlastaNeural",
    "cs-CZ-AntoninNeural",
    "uk-UA-PolinaNeural",
    "uk-UA-OstapNeural",
    "pt-BR-FranciscaNeural",
    "pt-BR-AntonioNeural",
    "nl-NL-ColetteNeural",
    "nl-NL-MaartenNeural",
    "sv-SE-SofieNeural",
    "sv-SE-MattiasNeural",
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "ko-KR-SunHiNeural",
    "ko-KR-InJoonNeural",
    "tr-TR-EmelNeural",
    "tr-TR-AhmetNeural",
]
PDF_LANGUAGES = [
    "pol", "eng", "deu", "rus", "ces", "slk", "ukr", "fra", "spa", "ita",
    "por", "nld", "hun", "ron", "bul", "slv", "hrv", "srp", "lit", "lav",
    "est", "fin", "swe", "dan", "nor", "tur",
]
TARGET_LANGUAGES = ["pol", "eng", "rus", "deu", "fra", "ces", "ukr", "spa", "ita"]
UI_LANGUAGE_OPTIONS = [
    ("Polski", "pl"),
    ("Cesky", "cs"),
    ("English", "en"),
    ("Deutsch", "de"),
    ("Francais", "fr"),
    ("Espanol", "es"),
    ("Italiano", "it"),
    ("Russkiy", "ru"),
    ("Ukrainska", "uk"),
    ("Turkce", "tr"),
    ("Portugues", "pt"),
    ("Nederlands", "nl"),
    ("Svenska", "sv"),
]
PIPER_MODEL_PRESETS = {
    "pl_PL-gosia-medium": [
        ("pl_PL-gosia-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"),
        ("pl_PL-gosia-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json"),
    ],
    "pl_PL-darkman-medium": [
        ("pl_PL-darkman-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx"),
        ("pl_PL-darkman-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx.json"),
    ],
    "pl_PL-zenski_wg_glos-medium": [
        ("pl_PL-zenski_wg_glos-medium.onnx", "https://huggingface.co/WitoldG/polish_piper_models/resolve/main/pl_PL-zenski_wg_glos-medium.onnx"),
        ("pl_PL-zenski_wg_glos-medium.onnx.json", "https://huggingface.co/WitoldG/polish_piper_models/resolve/main/pl_PL-zenski_wg_glos-medium.onnx.json"),
    ],
    "pl_PL-meski_wg_glos-medium": [
        ("pl_PL-meski_wg_glos-medium.onnx", "https://huggingface.co/WitoldG/polish_piper_models/resolve/main/pl_PL-meski_wg_glos-medium.onnx"),
        ("pl_PL-meski_wg_glos-medium.onnx.json", "https://huggingface.co/WitoldG/polish_piper_models/resolve/main/pl_PL-meski_wg_glos-medium.onnx.json"),
    ],
    "en_US-lessac-medium": [
        ("en_US-lessac-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"),
        ("en_US-lessac-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"),
    ],
    "en_GB-alan-medium": [
        ("en_GB-alan-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"),
        ("en_GB-alan-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"),
    ],
    "de_DE-thorsten-medium": [
        ("de_DE-thorsten-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"),
        ("de_DE-thorsten-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"),
    ],
    "fr_FR-siwis-medium": [
        ("fr_FR-siwis-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"),
        ("fr_FR-siwis-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"),
    ],
    "es_ES-sharvard-medium": [
        ("es_ES-sharvard-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"),
        ("es_ES-sharvard-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"),
    ],
    "it_IT-riccardo-medium": [
        ("it_IT-riccardo-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/riccardo/medium/it_IT-riccardo-medium.onnx"),
        ("it_IT-riccardo-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/riccardo/medium/it_IT-riccardo-medium.onnx.json"),
    ],
    "cs_CZ-jirka-medium": [
        ("cs_CZ-jirka-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/cs/cs_CZ/jirka/medium/cs_CZ-jirka-medium.onnx"),
        ("cs_CZ-jirka-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/cs/cs_CZ/jirka/medium/cs_CZ-jirka-medium.onnx.json"),
    ],
    "ru_RU-ruslan-medium": [
        ("ru_RU-ruslan-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx"),
        ("ru_RU-ruslan-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx.json"),
    ],
}
TRANSLATIONS = {
    "pl": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Język UI",
        "work_mode": "Tryb pracy",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Tłumaczenie → Audio",
        "mode_translate_txt": "PDF → Tłumaczenie → TXT",
        "mode_txt_audio": "TXT → Audio (gotowy output.txt)",
        "source_files": "Pliki źródłowe",
        "pdf_file": "Plik PDF",
        "txt_file": "Plik TXT",
        "output_dir": "Folder wyjściowy",
        "pdf_settings": "Ustawienia PDF",
        "pdf_language": "Język PDF",
        "target_language": "Język docelowy (tłumaczenie)",
        "text_extraction": "Ekstrakcja tekstu",
        "extract_fast": "pypdfium2 (szybki)",
        "extract_vision": "LLM Vision OCR (dla trudnych PDFów)",
        "tts": "TTS (Synteza mowy)",
        "provider": "Provider",
        "piper_voice": "Głos Piper",
        "edge_voice": "Głos Edge TTS",
        "speaker_sample": "Próbka głosu (WAV)",
        "llm": "LLM (Tłumaczenie)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Skanuj modele LLM",
        "piper_download_label": "Model Piper do pobrania",
        "save_config": "Zapisz config",
        "download_piper": "⬇ Pobierz model Piper",
        "run_pipeline": "▶  URUCHOM PIPELINE",
        "pause": "⏸ Pauza",
        "resume": "▶ Wznów",
        "stop": "⏹ Stop",
        "open_folder": "📂 Otwórz folder",
        "ready": "● GOTOWY",
        "progress": "Postęp",
        "progress_translation": "Ekstrakcja / Tłumaczenie",
        "progress_audio": "Audio",
        "progress_merge": "Scalanie",
        "console": "Konsola",
    },
    "cs": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Jazyk UI",
        "work_mode": "Rezim prace",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Preklad → Audio",
        "mode_translate_txt": "PDF → Preklad → TXT",
        "mode_txt_audio": "TXT → Audio (hotovy output.txt)",
        "source_files": "Zdrojove soubory",
        "pdf_file": "PDF soubor",
        "txt_file": "TXT soubor",
        "output_dir": "Vystupni slozka",
        "pdf_settings": "Nastaveni PDF",
        "pdf_language": "Jazyk PDF",
        "target_language": "Cilovy jazyk (preklad)",
        "text_extraction": "Extrahovani textu",
        "extract_fast": "pypdfium2 (rychly)",
        "extract_vision": "LLM Vision OCR (pro problemove PDF)",
        "tts": "TTS (syntetizace reci)",
        "provider": "Provider",
        "piper_voice": "Hlas Piper",
        "edge_voice": "Hlas Edge TTS",
        "speaker_sample": "Ukazka hlasu (WAV)",
        "llm": "LLM (Preklad)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Skenovat LLM modely",
        "piper_download_label": "Model Piper ke stazeni",
        "save_config": "Ulozit config",
        "download_piper": "⬇ Stahnout model Piper",
        "run_pipeline": "▶  SPUSTIT PIPELINE",
        "pause": "⏸ Pauza",
        "resume": "▶ Pokracovat",
        "stop": "⏹ Stop",
        "open_folder": "📂 Otevrit slozku",
        "ready": "● PRIPRAVENO",
        "progress": "Průběh",
        "progress_translation": "Extrakce / Překlad",
        "progress_audio": "Audio",
        "progress_merge": "Sloučení",
        "console": "Konzole",
    },
    "en": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI Language",
        "work_mode": "Work Mode",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Translation → Audio",
        "mode_translate_txt": "PDF → Translation → TXT",
        "mode_txt_audio": "TXT → Audio (existing output.txt)",
        "source_files": "Source Files",
        "pdf_file": "PDF File",
        "txt_file": "TXT File",
        "output_dir": "Output Folder",
        "pdf_settings": "PDF Settings",
        "pdf_language": "PDF Language",
        "target_language": "Target language (translation)",
        "text_extraction": "Text Extraction",
        "extract_fast": "pypdfium2 (fast)",
        "extract_vision": "LLM Vision OCR (for difficult PDFs)",
        "tts": "TTS (Speech Synthesis)",
        "provider": "Provider",
        "piper_voice": "Piper Voice",
        "edge_voice": "Edge TTS Voice",
        "speaker_sample": "Voice Sample (WAV)",
        "llm": "LLM (Translation)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Scan LLM Models",
        "piper_download_label": "Piper model to download",
        "save_config": "Save config",
        "download_piper": "⬇ Download Piper model",
        "run_pipeline": "▶  RUN PIPELINE",
        "pause": "⏸ Pause",
        "resume": "▶ Resume",
        "stop": "⏹ Stop",
        "open_folder": "📂 Open folder",
        "ready": "● READY",
        "progress": "Progress",
        "progress_translation": "Extraction / Translation",
        "progress_audio": "Audio",
        "progress_merge": "Merging",
        "console": "Console",
    },
    "de": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-Sprache",
        "work_mode": "Arbeitsmodus",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Ubersetzung → Audio",
        "mode_translate_txt": "PDF → Ubersetzung → TXT",
        "mode_txt_audio": "TXT → Audio (fertige output.txt)",
        "source_files": "Quelldateien",
        "pdf_file": "PDF-Datei",
        "txt_file": "TXT-Datei",
        "output_dir": "Ausgabeordner",
        "pdf_settings": "PDF-Einstellungen",
        "pdf_language": "PDF-Sprache",
        "target_language": "Zielsprache (Ubersetzung)",
        "text_extraction": "Textextraktion",
        "extract_fast": "pypdfium2 (schnell)",
        "extract_vision": "LLM Vision OCR (fur schwierige PDFs)",
        "tts": "TTS (Sprachausgabe)",
        "provider": "Provider",
        "piper_voice": "Piper-Stimme",
        "edge_voice": "Edge-TTS-Stimme",
        "speaker_sample": "Sprachprobe (WAV)",
        "llm": "LLM (Ubersetzung)",
        "url": "URL",
        "model": "Modell",
        "scan_models": "LLM-Modelle scannen",
        "piper_download_label": "Piper-Modell zum Herunterladen",
        "save_config": "Config speichern",
        "download_piper": "⬇ Piper-Modell herunterladen",
        "run_pipeline": "▶  PIPELINE STARTEN",
        "pause": "⏸ Pause",
        "resume": "▶ Fortsetzen",
        "stop": "⏹ Stop",
        "open_folder": "📂 Ordner offnen",
        "ready": "● BEREIT",
        "progress": "Fortschritt",
        "progress_translation": "Extraktion / Übersetzung",
        "progress_audio": "Audio",
        "progress_merge": "Zusammenführen",
        "console": "Konsole",
    },
    "fr": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Langue UI",
        "work_mode": "Mode de travail",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Traduction → Audio",
        "mode_translate_txt": "PDF → Traduction → TXT",
        "mode_txt_audio": "TXT → Audio (output.txt existant)",
        "source_files": "Fichiers source",
        "pdf_file": "Fichier PDF",
        "txt_file": "Fichier TXT",
        "output_dir": "Dossier de sortie",
        "pdf_settings": "Parametres PDF",
        "pdf_language": "Langue PDF",
        "text_extraction": "Extraction du texte",
        "extract_fast": "pypdfium2 (rapide)",
        "extract_vision": "LLM Vision OCR (pour PDF difficiles)",
        "tts": "TTS (synthese vocale)",
        "provider": "Provider",
        "piper_voice": "Voix Piper",
        "edge_voice": "Voix Edge TTS",
        "speaker_sample": "Echantillon de voix (WAV)",
        "llm": "LLM (Traduction)",
        "url": "URL",
        "model": "Modele",
        "scan_models": "Scanner les modeles LLM",
        "piper_download_label": "Modele Piper a telecharger",
        "save_config": "Enregistrer config",
        "download_piper": "⬇ Telecharger le modele Piper",
        "run_pipeline": "▶  LANCER PIPELINE",
        "pause": "⏸ Pause",
        "resume": "▶ Reprendre",
        "stop": "⏹ Stop",
        "open_folder": "📂 Ouvrir le dossier",
        "ready": "● PRET",
        "progress": "Progression",
        "progress_translation": "Extraction / Traduction",
        "progress_audio": "Audio",
        "progress_merge": "Fusion",
        "console": "Console",
    },
    "es": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Idioma UI",
        "work_mode": "Modo de trabajo",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Traduccion → Audio",
        "mode_translate_txt": "PDF → Traduccion → TXT",
        "mode_txt_audio": "TXT → Audio (output.txt existente)",
        "source_files": "Archivos fuente",
        "pdf_file": "Archivo PDF",
        "txt_file": "Archivo TXT",
        "output_dir": "Carpeta de salida",
        "pdf_settings": "Configuracion PDF",
        "pdf_language": "Idioma PDF",
        "text_extraction": "Extraccion de texto",
        "extract_fast": "pypdfium2 (rapido)",
        "extract_vision": "LLM Vision OCR (para PDF dificiles)",
        "tts": "TTS (sintesis de voz)",
        "provider": "Provider",
        "piper_voice": "Voz Piper",
        "edge_voice": "Voz Edge TTS",
        "speaker_sample": "Muestra de voz (WAV)",
        "llm": "LLM (Traduccion)",
        "url": "URL",
        "model": "Modelo",
        "scan_models": "Escanear modelos LLM",
        "piper_download_label": "Modelo Piper para descargar",
        "save_config": "Guardar config",
        "download_piper": "⬇ Descargar modelo Piper",
        "run_pipeline": "▶  EJECUTAR PIPELINE",
        "pause": "⏸ Pausa",
        "resume": "▶ Reanudar",
        "stop": "⏹ Detener",
        "open_folder": "📂 Abrir carpeta",
        "ready": "● LISTO",
        "progress": "Progreso",
        "progress_translation": "Extracción / Traducción",
        "progress_audio": "Audio",
        "progress_merge": "Unión",
        "console": "Consola",
    },
    "it": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Lingua UI",
        "work_mode": "Modalita di lavoro",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Traduzione → Audio",
        "mode_translate_txt": "PDF → Traduzione → TXT",
        "mode_txt_audio": "TXT → Audio (output.txt esistente)",
        "source_files": "File sorgente",
        "pdf_file": "File PDF",
        "txt_file": "File TXT",
        "output_dir": "Cartella di output",
        "pdf_settings": "Impostazioni PDF",
        "pdf_language": "Lingua PDF",
        "text_extraction": "Estrazione testo",
        "extract_fast": "pypdfium2 (veloce)",
        "extract_vision": "LLM Vision OCR (per PDF difficili)",
        "tts": "TTS (sintesi vocale)",
        "provider": "Provider",
        "piper_voice": "Voce Piper",
        "edge_voice": "Voce Edge TTS",
        "speaker_sample": "Campione vocale (WAV)",
        "llm": "LLM (Traduzione)",
        "url": "URL",
        "model": "Modello",
        "scan_models": "Scansiona modelli LLM",
        "piper_download_label": "Modello Piper da scaricare",
        "save_config": "Salva config",
        "download_piper": "⬇ Scarica modello Piper",
        "run_pipeline": "▶  AVVIA PIPELINE",
        "pause": "⏸ Pausa",
        "resume": "▶ Riprendi",
        "stop": "⏹ Stop",
        "open_folder": "📂 Apri cartella",
        "ready": "● PRONTO",
        "progress": "Avanzamento",
        "progress_translation": "Estrazione / Traduzione",
        "progress_audio": "Audio",
        "progress_merge": "Unione",
        "console": "Console",
    },
    "ru": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Yazyk UI",
        "work_mode": "Rezhim raboty",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Perevod → Audio",
        "mode_translate_txt": "PDF → Perevod → TXT",
        "mode_txt_audio": "TXT → Audio (gotovyy output.txt)",
        "source_files": "Ishodnye fayly",
        "pdf_file": "PDF fayl",
        "txt_file": "TXT fayl",
        "output_dir": "Papka vyvoda",
        "pdf_settings": "Nastroyki PDF",
        "pdf_language": "Yazyk PDF",
        "target_language": "Cilevoy yazyk (perevod)",
        "text_extraction": "Izvlechenie teksta",
        "extract_fast": "pypdfium2 (bystro)",
        "extract_vision": "LLM Vision OCR (dlya slozhnykh PDF)",
        "tts": "TTS (sintez rechi)",
        "provider": "Provider",
        "piper_voice": "Golos Piper",
        "edge_voice": "Golos Edge TTS",
        "speaker_sample": "Obrazets golosa (WAV)",
        "llm": "LLM (Perevod)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Skanirovat modeli LLM",
        "piper_download_label": "Model Piper dlya zagruzki",
        "save_config": "Sohranit config",
        "download_piper": "⬇ Zagruzit model Piper",
        "run_pipeline": "▶  ZAPUSTIT PIPELINE",
        "pause": "⏸ Pauza",
        "resume": "▶ Prodolzhit",
        "stop": "⏹ Stop",
        "open_folder": "📂 Otkryt papku",
        "ready": "● GOTOVO",
        "progress": "Прогресс",
        "progress_translation": "Извлечение / Перевод",
        "progress_audio": "Аудио",
        "progress_merge": "Слияние",
        "console": "Консоль",
    },
    "uk": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Mova UI",
        "work_mode": "Rezhym roboty",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Pereklad → Audio",
        "mode_translate_txt": "PDF → Pereklad → TXT",
        "mode_txt_audio": "TXT → Audio (hotovyy output.txt)",
        "source_files": "Vkhidni fayly",
        "pdf_file": "PDF fayl",
        "txt_file": "TXT fayl",
        "output_dir": "Tecka vyvodu",
        "pdf_settings": "Nalashtuvannya PDF",
        "pdf_language": "Mova PDF",
        "target_language": "Cilova mova (pereklad)",
        "text_extraction": "Vydobuvannya tekstu",
        "extract_fast": "pypdfium2 (shvydko)",
        "extract_vision": "LLM Vision OCR (dlya skladnykh PDF)",
        "tts": "TTS (syntez movy)",
        "provider": "Provider",
        "piper_voice": "Holos Piper",
        "edge_voice": "Holos Edge TTS",
        "speaker_sample": "Zrazok holosu (WAV)",
        "llm": "LLM (Pereklad)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Skanuvaty modeli LLM",
        "piper_download_label": "Model Piper dlya zavantazhennya",
        "save_config": "Zberehty config",
        "download_piper": "⬇ Zavantažyty model Piper",
        "run_pipeline": "▶  ZAPUSTYTY PIPELINE",
        "pause": "⏸ Pauza",
        "resume": "▶ Prodovzhyty",
        "stop": "⏹ Stop",
        "open_folder": "📂 Vidkryty teku",
        "ready": "● HOTOVO",
        "progress": "Прогрес",
        "progress_translation": "Витяг / Переклад",
        "progress_audio": "Аудіо",
        "progress_merge": "Злиття",
        "console": "Консоль",
    },
    "tr": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI Dili",
        "work_mode": "Calisma modu",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Ceviri → Audio",
        "mode_translate_txt": "PDF → Ceviri → TXT",
        "mode_txt_audio": "TXT → Audio (hazir output.txt)",
        "source_files": "Kaynak dosyalar",
        "pdf_file": "PDF dosyasi",
        "txt_file": "TXT dosyasi",
        "output_dir": "Cikti klasoru",
        "pdf_settings": "PDF ayarlari",
        "pdf_language": "PDF dili",
        "target_language": "Hedef dil (ceviri)",
        "text_extraction": "Metin cikarma",
        "extract_fast": "pypdfium2 (hizli)",
        "extract_vision": "LLM Vision OCR (zor PDF icin)",
        "tts": "TTS (ses sentezi)",
        "provider": "Provider",
        "piper_voice": "Piper sesi",
        "edge_voice": "Edge TTS sesi",
        "speaker_sample": "Ses ornegi (WAV)",
        "llm": "LLM (Ceviri)",
        "url": "URL",
        "model": "Model",
        "scan_models": "LLM modellerini tara",
        "piper_download_label": "Indirilecek Piper modeli",
        "save_config": "Config kaydet",
        "download_piper": "⬇ Piper modelini indir",
        "run_pipeline": "▶  PIPELINE CALISTIR",
        "pause": "⏸ Duraklat",
        "resume": "▶ Devam et",
        "stop": "⏹ Durdur",
        "open_folder": "📂 Klasoru ac",
        "ready": "● HAZIR",
        "progress": "İlerleme",
        "progress_translation": "Çıkarma / Çeviri",
        "progress_audio": "Ses",
        "progress_merge": "Birleştirme",
        "console": "Konsol",
    },
    "pt": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Idioma UI",
        "work_mode": "Modo de trabalho",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Traducao → Audio",
        "mode_translate_txt": "PDF → Traducao → TXT",
        "mode_txt_audio": "TXT → Audio (output.txt pronto)",
        "source_files": "Arquivos de origem",
        "pdf_file": "Arquivo PDF",
        "txt_file": "Arquivo TXT",
        "output_dir": "Pasta de saida",
        "pdf_settings": "Configuracoes PDF",
        "pdf_language": "Idioma PDF",
        "target_language": "Idioma alvo (traducao)",
        "text_extraction": "Extracao de texto",
        "extract_fast": "pypdfium2 (rapido)",
        "extract_vision": "LLM Vision OCR (para PDFs dificeis)",
        "tts": "TTS (sintese de voz)",
        "provider": "Provider",
        "piper_voice": "Voz Piper",
        "edge_voice": "Voz Edge TTS",
        "speaker_sample": "Amostra de voz (WAV)",
        "llm": "LLM (Traducao)",
        "url": "URL",
        "model": "Modelo",
        "scan_models": "Escanear modelos LLM",
        "piper_download_label": "Modelo Piper para baixar",
        "save_config": "Salvar config",
        "download_piper": "⬇ Baixar modelo Piper",
        "run_pipeline": "▶  EXECUTAR PIPELINE",
        "pause": "⏸ Pausar",
        "resume": "▶ Retomar",
        "stop": "⏹ Parar",
        "open_folder": "📂 Abrir pasta",
        "ready": "● PRONTO",
        "progress": "Progresso",
        "progress_translation": "Extração / Tradução",
        "progress_audio": "Áudio",
        "progress_merge": "União",
        "console": "Console",
    },
    "nl": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-taal",
        "work_mode": "Werkmodus",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Vertaling → Audio",
        "mode_translate_txt": "PDF → Vertaling → TXT",
        "mode_txt_audio": "TXT → Audio (bestaande output.txt)",
        "source_files": "Bronbestanden",
        "pdf_file": "PDF-bestand",
        "txt_file": "TXT-bestand",
        "output_dir": "Uitvoermap",
        "pdf_settings": "PDF-instellingen",
        "pdf_language": "PDF-taal",
        "target_language": "Doeltaal (vertaling)",
        "text_extraction": "Tekstextractie",
        "extract_fast": "pypdfium2 (snel)",
        "extract_vision": "LLM Vision OCR (voor moeilijke PDF's)",
        "tts": "TTS (spraaksyntese)",
        "provider": "Provider",
        "piper_voice": "Piper-stem",
        "edge_voice": "Edge TTS-stem",
        "speaker_sample": "Stemvoorbeeld (WAV)",
        "llm": "LLM (Vertaling)",
        "url": "URL",
        "model": "Model",
        "scan_models": "LLM-modellen scannen",
        "piper_download_label": "Piper-model om te downloaden",
        "save_config": "Config opslaan",
        "download_piper": "⬇ Piper-model downloaden",
        "run_pipeline": "▶  PIPELINE STARTEN",
        "pause": "⏸ Pauze",
        "resume": "▶ Hervatten",
        "stop": "⏹ Stop",
        "open_folder": "📂 Map openen",
        "ready": "● GEREED",
        "progress": "Voortgang",
        "progress_translation": "Extractie / Vertaling",
        "progress_audio": "Audio",
        "progress_merge": "Samenvoegen",
        "console": "Console",
    },
    "sv": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-sprak",
        "work_mode": "Arbetslage",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Oversattning → Audio",
        "mode_translate_txt": "PDF → Oversattning → TXT",
        "mode_txt_audio": "TXT → Audio (befintlig output.txt)",
        "source_files": "Kallfiler",
        "pdf_file": "PDF-fil",
        "txt_file": "TXT-fil",
        "output_dir": "Utdatamapp",
        "pdf_settings": "PDF-installningar",
        "pdf_language": "PDF-sprak",
        "target_language": "Målspråk (översättning)",
        "text_extraction": "Textextraktion",
        "extract_fast": "pypdfium2 (snabb)",
        "extract_vision": "LLM Vision OCR (for svara PDF)",
        "tts": "TTS (talsyntes)",
        "provider": "Provider",
        "piper_voice": "Piper-rost",
        "edge_voice": "Edge TTS-rost",
        "speaker_sample": "Rostprov (WAV)",
        "llm": "LLM (Oversattning)",
        "url": "URL",
        "model": "Modell",
        "scan_models": "Skanna LLM-modeller",
        "piper_download_label": "Piper-modell att ladda ner",
        "save_config": "Spara config",
        "download_piper": "⬇ Ladda ner Piper-modell",
        "run_pipeline": "▶  KOR PIPELINE",
        "pause": "⏸ Paus",
        "resume": "▶ Fortsatt",
        "stop": "⏹ Stop",
        "open_folder": "📂 Oppna mapp",
        "ready": "● REDO",
        "progress": "Framsteg",
        "progress_translation": "Extraktion / Översättning",
        "progress_audio": "Audio",
        "progress_merge": "Sammanfogning",
        "console": "Konsol",
    },
}
UI_RUNTIME_MESSAGES = {
    "en": {
        "llm_scan_start": "Scanning LLM models...",
        "llm_found": "Found {} LLM models",
        "llm_not_found": "No LLM models found",
        "llm_scan_error": "LLM model scan error: {}",
        "piper_preset_missing": "No download definition for model: {}",
        "file_exists": "OK {} already exists",
        "downloading": "Downloading {}...",
        "downloaded": "OK {} downloaded",
        "download_error": "Download error {}: {}",
        "piper_ready": "Piper model ready: {}",
        "config_saved": "Config saved",
        "old_output_removed": "Removed old output.txt - starting from scratch",
        "done": "OK Done!",
        "error": "ERROR: {}",
        "stopped": "Stopped",
        "app_ready": "AudiobookForge ready.",
        "status_ready": "● READY",
        "status_running": "● RUNNING",
        "status_completed": "● COMPLETED",
        "status_error": "● ERROR",
        "status_paused": "● PAUSED",
        "status_stopped": "● STOPPED",
        "pause_button": "⏸ Pause",
        "resume_button": "▶ Resume",
    },
    "pl": {
        "llm_scan_start": "Skanowanie modeli LLM...",
        "llm_found": "Znaleziono {} modeli LLM",
        "llm_not_found": "Nie znaleziono modeli LLM",
        "llm_scan_error": "Błąd skanowania modeli LLM: {}",
        "piper_preset_missing": "Brak definicji pobierania dla modelu: {}",
        "file_exists": "✓ {} już istnieje",
        "downloading": "Pobieranie {}...",
        "downloaded": "✓ {} pobrany",
        "download_error": "Błąd pobierania {}: {}",
        "piper_ready": "Model Piper gotowy: {}",
        "config_saved": "Config zapisany",
        "old_output_removed": "Usunięto stary output.txt — zaczynam od nowa",
        "done": "✓ Gotowe!",
        "error": "BŁĄD: {}",
        "stopped": "Zatrzymano",
        "app_ready": "AudiobookForge gotowy.",
        "status_ready": "● GOTOWY",
        "status_running": "● URUCHOMIONY",
        "status_completed": "● UKOŃCZONY",
        "status_error": "● BŁĄD",
        "status_paused": "● PAUZA",
        "status_stopped": "● ZATRZYMANY",
        "pause_button": "⏸ Pauza",
        "resume_button": "▶ Wznów",
    },
    "cs": {
        "llm_scan_start": "Skenování modelů LLM...",
        "llm_found": "Nalezeno modelů LLM: {}",
        "llm_not_found": "Modely LLM nebyly nalezeny",
        "llm_scan_error": "Chyba skenování modelů LLM: {}",
        "piper_preset_missing": "Chybí definice stahování pro model: {}",
        "file_exists": "✓ {} už existuje",
        "downloading": "Stahování {}...",
        "downloaded": "✓ {} stažen",
        "download_error": "Chyba stahování {}: {}",
        "piper_ready": "Model Piper připraven: {}",
        "config_saved": "Config uložen",
        "old_output_removed": "Starý output.txt odstraněn - začínám znovu",
        "done": "✓ Hotovo!",
        "error": "CHYBA: {}",
        "stopped": "Zastaveno",
        "app_ready": "AudiobookForge připraven.",
        "status_ready": "● PŘIPRAVENO",
        "status_running": "● SPUŠTĚNO",
        "status_completed": "● DOKONČENO",
        "status_error": "● CHYBA",
        "status_paused": "● PAUZA",
        "status_stopped": "● ZASTAVENO",
        "pause_button": "⏸ Pauza",
        "resume_button": "▶ Pokračovat",
    },
    "de": {
        "llm_scan_start": "LLM-Modelle werden gescannt...",
        "llm_found": "Gefundene LLM-Modelle: {}",
        "llm_not_found": "Keine LLM-Modelle gefunden",
        "llm_scan_error": "Fehler beim Scannen der LLM-Modelle: {}",
        "piper_preset_missing": "Keine Download-Definition für Modell: {}",
        "file_exists": "✓ {} existiert bereits",
        "downloading": "Lade {} herunter...",
        "downloaded": "✓ {} heruntergeladen",
        "download_error": "Download-Fehler {}: {}",
        "piper_ready": "Piper-Modell bereit: {}",
        "config_saved": "Config gespeichert",
        "old_output_removed": "Alte output.txt entfernt - starte neu",
        "done": "✓ Fertig!",
        "error": "FEHLER: {}",
        "stopped": "Gestoppt",
        "app_ready": "AudiobookForge bereit.",
        "status_ready": "● BEREIT",
        "status_running": "● LÄUFT",
        "status_completed": "● ABGESCHLOSSEN",
        "status_error": "● FEHLER",
        "status_paused": "● PAUSE",
        "status_stopped": "● GESTOPPT",
        "pause_button": "⏸ Pause",
        "resume_button": "▶ Fortsetzen",
    },
    "fr": {
        "llm_scan_start": "Analyse des modèles LLM...",
        "llm_found": "Modèles LLM trouvés : {}",
        "llm_not_found": "Aucun modèle LLM trouvé",
        "llm_scan_error": "Erreur d'analyse des modèles LLM : {}",
        "piper_preset_missing": "Aucune définition de téléchargement pour le modèle : {}",
        "file_exists": "✓ {} existe déjà",
        "downloading": "Téléchargement de {}...",
        "downloaded": "✓ {} téléchargé",
        "download_error": "Erreur de téléchargement {} : {}",
        "piper_ready": "Modèle Piper prêt : {}",
        "config_saved": "Config enregistrée",
        "old_output_removed": "Ancien output.txt supprimé - redémarrage complet",
        "done": "✓ Terminé !",
        "error": "ERREUR : {}",
        "stopped": "Arrêté",
        "app_ready": "AudiobookForge prêt.",
        "status_ready": "● PRÊT",
        "status_running": "● EN COURS",
        "status_completed": "● TERMINÉ",
        "status_error": "● ERREUR",
        "status_paused": "● PAUSE",
        "status_stopped": "● ARRÊTÉ",
        "pause_button": "⏸ Pause",
        "resume_button": "▶ Reprendre",
    },
    "es": {
        "llm_scan_start": "Escaneando modelos LLM...",
        "llm_found": "Modelos LLM encontrados: {}",
        "llm_not_found": "No se encontraron modelos LLM",
        "llm_scan_error": "Error al escanear modelos LLM: {}",
        "piper_preset_missing": "No hay definición de descarga para el modelo: {}",
        "file_exists": "✓ {} ya existe",
        "downloading": "Descargando {}...",
        "downloaded": "✓ {} descargado",
        "download_error": "Error de descarga {}: {}",
        "piper_ready": "Modelo Piper listo: {}",
        "config_saved": "Config guardado",
        "old_output_removed": "Se eliminó el output.txt anterior - iniciando desde cero",
        "done": "✓ ¡Listo!",
        "error": "ERROR: {}",
        "stopped": "Detenido",
        "app_ready": "AudiobookForge listo.",
        "status_ready": "● LISTO",
        "status_running": "● EN EJECUCIÓN",
        "status_completed": "● COMPLETADO",
        "status_error": "● ERROR",
        "status_paused": "● PAUSA",
        "status_stopped": "● DETENIDO",
        "pause_button": "⏸ Pausa",
        "resume_button": "▶ Reanudar",
    },
    "it": {
        "llm_scan_start": "Scansione dei modelli LLM...",
        "llm_found": "Modelli LLM trovati: {}",
        "llm_not_found": "Nessun modello LLM trovato",
        "llm_scan_error": "Errore scansione modelli LLM: {}",
        "piper_preset_missing": "Nessuna definizione di download per il modello: {}",
        "file_exists": "✓ {} esiste già",
        "downloading": "Download di {}...",
        "downloaded": "✓ {} scaricato",
        "download_error": "Errore download {}: {}",
        "piper_ready": "Modello Piper pronto: {}",
        "config_saved": "Config salvato",
        "old_output_removed": "Vecchio output.txt rimosso - riavvio da zero",
        "done": "✓ Fatto!",
        "error": "ERRORE: {}",
        "stopped": "Fermato",
        "app_ready": "AudiobookForge pronto.",
        "status_ready": "● PRONTO",
        "status_running": "● IN ESECUZIONE",
        "status_completed": "● COMPLETATO",
        "status_error": "● ERRORE",
        "status_paused": "● PAUSA",
        "status_stopped": "● FERMATO",
        "pause_button": "⏸ Pausa",
        "resume_button": "▶ Riprendi",
    },
    "ru": {
        "llm_scan_start": "Сканирование моделей LLM...",
        "llm_found": "Найдено моделей LLM: {}",
        "llm_not_found": "Модели LLM не найдены",
        "llm_scan_error": "Ошибка сканирования моделей LLM: {}",
        "piper_preset_missing": "Нет определения загрузки для модели: {}",
        "file_exists": "✓ {} уже существует",
        "downloading": "Загрузка {}...",
        "downloaded": "✓ {} загружен",
        "download_error": "Ошибка загрузки {}: {}",
        "piper_ready": "Модель Piper готова: {}",
        "config_saved": "Конфиг сохранён",
        "old_output_removed": "Старый output.txt удалён — начинаю заново",
        "done": "✓ Готово!",
        "error": "ОШИБКА: {}",
        "stopped": "Остановлено",
        "app_ready": "AudiobookForge готов.",
        "status_ready": "● ГОТОВ",
        "status_running": "● РАБОТАЕТ",
        "status_completed": "● ЗАВЕРШЕНО",
        "status_error": "● ОШИБКА",
        "status_paused": "● ПАУЗА",
        "status_stopped": "● ОСТАНОВЛЕНО",
        "pause_button": "⏸ Пауза",
        "resume_button": "▶ Продолжить",
    },
    "uk": {
        "llm_scan_start": "Сканування моделей LLM...",
        "llm_found": "Знайдено моделей LLM: {}",
        "llm_not_found": "Моделі LLM не знайдено",
        "llm_scan_error": "Помилка сканування моделей LLM: {}",
        "piper_preset_missing": "Немає опису завантаження для моделі: {}",
        "file_exists": "✓ {} уже існує",
        "downloading": "Завантаження {}...",
        "downloaded": "✓ {} завантажено",
        "download_error": "Помилка завантаження {}: {}",
        "piper_ready": "Модель Piper готова: {}",
        "config_saved": "Config збережено",
        "old_output_removed": "Старий output.txt видалено - починаю спочатку",
        "done": "✓ Готово!",
        "error": "ПОМИЛКА: {}",
        "stopped": "Зупинено",
        "app_ready": "AudiobookForge готовий.",
        "status_ready": "● ГОТОВО",
        "status_running": "● ПРАЦЮЄ",
        "status_completed": "● ЗАВЕРШЕНО",
        "status_error": "● ПОМИЛКА",
        "status_paused": "● ПАУЗА",
        "status_stopped": "● ЗУПИНЕНО",
        "pause_button": "⏸ Пауза",
        "resume_button": "▶ Продовжити",
    },
    "tr": {
        "llm_scan_start": "LLM modelleri taranıyor...",
        "llm_found": "Bulunan LLM modeli: {}",
        "llm_not_found": "LLM modeli bulunamadı",
        "llm_scan_error": "LLM model tarama hatası: {}",
        "piper_preset_missing": "Model için indirme tanımı yok: {}",
        "file_exists": "✓ {} zaten mevcut",
        "downloading": "{} indiriliyor...",
        "downloaded": "✓ {} indirildi",
        "download_error": "İndirme hatası {}: {}",
        "piper_ready": "Piper modeli hazır: {}",
        "config_saved": "Config kaydedildi",
        "old_output_removed": "Eski output.txt silindi - sıfırdan başlatılıyor",
        "done": "✓ Hazır!",
        "error": "HATA: {}",
        "stopped": "Durduruldu",
        "app_ready": "AudiobookForge hazır.",
        "status_ready": "● HAZIR",
        "status_running": "● ÇALIŞIYOR",
        "status_completed": "● TAMAMLANDI",
        "status_error": "● HATA",
        "status_paused": "● DURAKLATILDI",
        "status_stopped": "● DURDURULDU",
        "pause_button": "⏸ Duraklat",
        "resume_button": "▶ Devam et",
    },
    "pt": {
        "llm_scan_start": "A verificar modelos LLM...",
        "llm_found": "Modelos LLM encontrados: {}",
        "llm_not_found": "Nenhum modelo LLM encontrado",
        "llm_scan_error": "Erro ao verificar modelos LLM: {}",
        "piper_preset_missing": "Sem definição de download para o modelo: {}",
        "file_exists": "✓ {} já existe",
        "downloading": "A transferir {}...",
        "downloaded": "✓ {} transferido",
        "download_error": "Erro de download {}: {}",
        "piper_ready": "Modelo Piper pronto: {}",
        "config_saved": "Config guardado",
        "old_output_removed": "output.txt antigo removido - a começar do zero",
        "done": "✓ Pronto!",
        "error": "ERRO: {}",
        "stopped": "Parado",
        "app_ready": "AudiobookForge pronto.",
        "status_ready": "● PRONTO",
        "status_running": "● EM EXECUÇÃO",
        "status_completed": "● CONCLUÍDO",
        "status_error": "● ERRO",
        "status_paused": "● PAUSA",
        "status_stopped": "● PARADO",
        "pause_button": "⏸ Pausa",
        "resume_button": "▶ Retomar",
    },
    "nl": {
        "llm_scan_start": "LLM-modellen scannen...",
        "llm_found": "Gevonden LLM-modellen: {}",
        "llm_not_found": "Geen LLM-modellen gevonden",
        "llm_scan_error": "Fout bij scannen van LLM-modellen: {}",
        "piper_preset_missing": "Geen downloaddefinitie voor model: {}",
        "file_exists": "✓ {} bestaat al",
        "downloading": "{} wordt gedownload...",
        "downloaded": "✓ {} gedownload",
        "download_error": "Downloadfout {}: {}",
        "piper_ready": "Piper-model klaar: {}",
        "config_saved": "Config opgeslagen",
        "old_output_removed": "Oude output.txt verwijderd - opnieuw starten",
        "done": "✓ Klaar!",
        "error": "FOUT: {}",
        "stopped": "Gestopt",
        "app_ready": "AudiobookForge gereed.",
        "status_ready": "● GEREED",
        "status_running": "● ACTIEF",
        "status_completed": "● VOLTOOID",
        "status_error": "● FOUT",
        "status_paused": "● GEPAUZEERD",
        "status_stopped": "● GESTOPT",
        "pause_button": "⏸ Pauze",
        "resume_button": "▶ Hervatten",
    },
    "sv": {
        "llm_scan_start": "Skannar LLM-modeller...",
        "llm_found": "Hittade LLM-modeller: {}",
        "llm_not_found": "Inga LLM-modeller hittades",
        "llm_scan_error": "Fel vid skanning av LLM-modeller: {}",
        "piper_preset_missing": "Ingen nedladdningsdefinition för modell: {}",
        "file_exists": "✓ {} finns redan",
        "downloading": "Laddar ner {}...",
        "downloaded": "✓ {} nedladdad",
        "download_error": "Nedladdningsfel {}: {}",
        "piper_ready": "Piper-modell klar: {}",
        "config_saved": "Config sparad",
        "old_output_removed": "Gammal output.txt borttagen - startar om från början",
        "done": "✓ Klart!",
        "error": "FEL: {}",
        "stopped": "Stoppad",
        "app_ready": "AudiobookForge redo.",
        "status_ready": "● REDO",
        "status_running": "● KÖR",
        "status_completed": "● KLAR",
        "status_error": "● FEL",
        "status_paused": "● PAUSAD",
        "status_stopped": "● STOPPAD",
        "pause_button": "⏸ Paus",
        "resume_button": "▶ Fortsätt",
    },
}


def run_app():
    current_lang = state.config.get("app_language", "pl")

    def tr(key: str) -> str:
        return TRANSLATIONS.get(current_lang, TRANSLATIONS["en"]).get(key, key)

    def tr_runtime(key: str, *args) -> str:
        template = UI_RUNTIME_MESSAGES.get(current_lang, UI_RUNTIME_MESSAGES["en"]).get(
            key, UI_RUNTIME_MESSAGES["en"].get(key, key)
        )
        return template.format(*args)

    root = tk.Tk()
    root.title("AudiobookForge v1.0")
    icon_ico_path = PROJECT_DIR / "assets" / "app_icon.ico"
    icon_png_path = PROJECT_DIR / "assets" / "app_icon.png"
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AudiobookForge.App")
    except Exception:
        pass
    if icon_ico_path.exists():
        try:
            root.iconbitmap(default=str(icon_ico_path))
            root.wm_iconbitmap(str(icon_ico_path))
        except Exception:
            pass
    if icon_png_path.exists():
        try:
            icon_image = tk.PhotoImage(file=str(icon_png_path))
            root.iconphoto(True, icon_image)
            root._icon_image = icon_image
        except Exception:
            pass
    root.configure(bg=BG)
    root.geometry("1200x800")
    root.minsize(900, 600)

    topbar = tk.Frame(root, bg="#0a0f15", pady=10)
    topbar.pack(fill="x", padx=0)
    title_label = tk.Label(
        topbar,
        text=tr("app_title"),
        bg="#0a0f15",
        fg=ACCENT,
        font=("Consolas", 16, "bold"),
    )
    title_label.pack(side="left", padx=20)

    tk.Label(topbar, text=tr("ui_language"), bg="#0a0f15", fg=FG_MUTED, font=FONT).pack(side="right", padx=(8, 8))
    app_language_var = tk.StringVar(value=current_lang)
    app_language_combo = ttk.Combobox(
        topbar,
        textvariable=app_language_var,
        state="readonly",
        values=[label for label, _ in UI_LANGUAGE_OPTIONS],
        font=FONT,
        width=14,
    )
    app_language_combo.pack(side="right", padx=(0, 16))
    current_label = next((label for label, code in UI_LANGUAGE_OPTIONS if code == current_lang), "English")
    app_language_var.set(current_label)

    def change_app_language(*_):
        selected = app_language_var.get()
        code = next((code for label, code in UI_LANGUAGE_OPTIONS if label == selected), current_lang)
        if code == state.config.get("app_language"):
            return
        state.config["app_language"] = code
        state.save()
        root.after(50, lambda: (root.destroy(), run_app()))

    app_language_var.trace_add("write", change_app_language)

    content = tk.Frame(root, bg=BG)
    content.pack(fill="both", expand=True, padx=16, pady=16)

    left = tk.Frame(content, bg=BG, width=380)
    left.pack(side="left", fill="y", padx=(0, 12))
    left.pack_propagate(False)

    right = tk.Frame(content, bg=BG)
    right.pack(side="left", fill="both", expand=True)

    mode_frame = tk.LabelFrame(
        left,
        text=tr("work_mode"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    mode_frame.pack(fill="x", pady=(0, 8))

    mode_var = tk.StringVar(value=state.config.get("mode", "pdf_to_audio"))
    modes = [
        (tr("mode_pdf_audio"), "pdf_to_audio"),
        (tr("mode_translate_audio"), "translate_to_audio"),
        (tr("mode_translate_txt"), "translate_to_txt"),
        (tr("mode_txt_audio"), "txt_to_audio"),
    ]
    for label, val in modes:
        tk.Radiobutton(
            mode_frame,
            text=label,
            variable=mode_var,
            value=val,
            bg=BG,
            fg=FG,
            selectcolor=BG2,
            activebackground=BG,
            font=FONT,
        ).pack(anchor="w", padx=8, pady=2)

    files_frame = tk.LabelFrame(
        left,
        text=tr("source_files"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    files_frame.pack(fill="x", pady=(0, 8))

    def make_path_row(parent, label, config_key, filetype=None):
        tk.Label(parent, text=label, bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=8, pady=(0, 4))
        var = tk.StringVar(value=state.config.get(config_key, ""))
        entry = tk.Entry(
            row,
            textvariable=var,
            bg=BG2,
            fg=FG,
            font=FONT,
            insertbackground=FG,
            relief="flat",
            bd=4,
        )
        entry.pack(side="left", fill="x", expand=True)

        def pick():
            if filetype == "folder":
                path = filedialog.askdirectory(title=f"Wybierz {label}")
            elif filetype:
                path = filedialog.askopenfilename(
                    title=f"Wybierz {label}",
                    filetypes=[(f"{filetype} files", f"*.{filetype}")],
                )
            else:
                path = filedialog.askopenfilename(title=f"Wybierz {label}")
            if path:
                var.set(path)
                state.config[config_key] = path

        tk.Button(
            row,
            text="📁",
            bg=BG2,
            fg=ACCENT,
            font=FONT,
            relief="flat",
            cursor="hand2",
            command=pick,
        ).pack(side="left", padx=(4, 0))
        var.trace_add("write", lambda *_: state.config.update({config_key: var.get()}))
        return var

    source_label_var = tk.StringVar(value=tr("pdf_file"))
    tk.Label(files_frame, textvariable=source_label_var, bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
    source_row = tk.Frame(files_frame, bg=BG)
    source_row.pack(fill="x", padx=8, pady=(0, 4))
    source_var = tk.StringVar(value=state.config.get("pdf_path", ""))
    source_entry = tk.Entry(
        source_row,
        textvariable=source_var,
        bg=BG2,
        fg=FG,
        font=FONT,
        insertbackground=FG,
        relief="flat",
        bd=4,
    )
    source_entry.pack(side="left", fill="x", expand=True)

    def sync_source_field(*_):
        if mode_var.get() == "txt_to_audio":
            source_label_var.set(tr("txt_file"))
            source_var.set(state.config.get("txt_path", str(Path(state.config.get("output_dir", "")) / "output.txt")))
        else:
            source_label_var.set(tr("pdf_file"))
            source_var.set(state.config.get("pdf_path", ""))

    def pick_source():
        if mode_var.get() == "txt_to_audio":
            path = filedialog.askopenfilename(
                title=tr("txt_file"),
                filetypes=[("txt files", "*.txt")],
            )
            if path:
                state.config["txt_path"] = path
                state.config["output_dir"] = str(Path(path).parent)
                source_var.set(path)
                output_dir_var.set(state.config["output_dir"])
        else:
            path = filedialog.askopenfilename(
                title=tr("pdf_file"),
                filetypes=[("pdf files", "*.pdf")],
            )
            if path:
                state.config["pdf_path"] = path
                source_var.set(path)

    tk.Button(
        source_row,
        text="📁",
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=pick_source,
    ).pack(side="left", padx=(4, 0))

    output_dir_var = make_path_row(files_frame, tr("output_dir"), "output_dir", "folder")

    lang_frame = tk.LabelFrame(
        left,
        text=tr("pdf_settings"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    lang_frame.pack(fill="x", pady=(0, 8))

    tk.Label(lang_frame, text=tr("pdf_language"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
    lang_var = tk.StringVar(value=state.config.get("pdf_language", "pol"))
    lang_combo = ttk.Combobox(
        lang_frame,
        textvariable=lang_var,
        state="readonly",
        values=PDF_LANGUAGES,
        font=FONT,
    )
    lang_combo.pack(fill="x", padx=8, pady=(0, 6))
    lang_var.trace_add("write", lambda *_: state.config.update(pdf_language=lang_var.get()))

    target_lang_frame = tk.Frame(lang_frame, bg=BG)
    target_lang_label = tk.Label(target_lang_frame, text=tr("target_language"), bg=BG, fg=FG_MUTED, font=FONT)
    target_lang_label.pack(anchor="w", padx=8)
    target_lang_var = tk.StringVar(value=state.config.get("target_language", "pol"))
    target_lang_combo = ttk.Combobox(
        target_lang_frame,
        textvariable=target_lang_var,
        state="readonly",
        values=TARGET_LANGUAGES,
        font=FONT,
    )
    target_lang_combo.pack(fill="x", padx=8, pady=(0, 6))
    target_lang_var.trace_add("write", lambda *_: state.config.update(target_language=target_lang_var.get()))

    extraction_frame = tk.LabelFrame(
        left,
        text=tr("text_extraction"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    extraction_frame.pack(fill="x", pady=(0, 8))

    ocr_var = tk.StringVar(value=state.config.get("extraction_mode", "pypdfium"))
    tk.Radiobutton(
        extraction_frame,
        text=tr("extract_fast"),
        variable=ocr_var,
        value="pypdfium",
        bg=BG,
        fg=FG,
        selectcolor=BG2,
        activebackground=BG,
        font=FONT,
        command=lambda: state.config.update(extraction_mode="pypdfium"),
    ).pack(anchor="w", padx=16)
    tk.Radiobutton(
        extraction_frame,
        text=tr("extract_vision"),
        variable=ocr_var,
        value="llm_vision",
        bg=BG,
        fg=FG,
        selectcolor=BG2,
        activebackground=BG,
        font=FONT,
        command=lambda: state.config.update(extraction_mode="llm_vision"),
    ).pack(anchor="w", padx=16, pady=(0, 6))

    tts_frame = tk.LabelFrame(
        left,
        text=tr("tts"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    tts_frame.pack(fill="x", pady=(0, 8))

    tk.Label(tts_frame, text=tr("provider"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
    tts_var = tk.StringVar(value=state.config.get("tts_provider", "piper"))
    tts_combo = ttk.Combobox(
        tts_frame,
        textvariable=tts_var,
        state="readonly",
        values=["piper", "edge_tts", "chatterbox", "elevenlabs", "openai_tts"],
        font=FONT,
    )
    tts_combo.pack(fill="x", padx=8, pady=(0, 4))
    tts_var.trace_add("write", lambda *_: state.config.update(tts_provider=tts_var.get()))

    piper_voice_frame = tk.Frame(tts_frame, bg=BG)
    tk.Label(piper_voice_frame, text=tr("piper_voice"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(4, 0))
    voice_var = tk.StringVar(value=state.config.get("piper_voice", "pl_PL-zenski-medium"))
    voice_row = tk.Frame(piper_voice_frame, bg=BG)
    voice_row.pack(fill="x", padx=8, pady=(0, 6))
    voice_combo = ttk.Combobox(
        voice_row,
        textvariable=voice_var,
        state="readonly",
        values=[],
        font=FONT,
    )
    voice_combo.pack(side="left", fill="x", expand=True)
    voice_var.trace_add("write", lambda *_: state.config.update(piper_voice=voice_var.get()))

    def scan_piper_models():
        models_dir = PROJECT_DIR / "piper_models"
        models_dir.mkdir(exist_ok=True)
        models = [f.stem for f in models_dir.glob("*.onnx")]
        if models:
            voice_combo["values"] = models
            if state.config.get("piper_voice") not in models:
                voice_var.set(models[0])
                state.config.update(piper_voice=models[0])
        else:
            voice_combo["values"] = ["brak modeli - pobierz"]
        return models

    tk.Button(
        voice_row,
        text="🔄",
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=scan_piper_models,
    ).pack(side="left", padx=(4, 0))

    edge_voice_frame = tk.Frame(tts_frame, bg=BG)
    tk.Label(edge_voice_frame, text=tr("edge_voice"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(4, 0))
    edge_voice_var = tk.StringVar(value=state.config.get("edge_voice", "pl-PL-ZofiaNeural"))
    edge_voice_combo = ttk.Combobox(
        edge_voice_frame,
        textvariable=edge_voice_var,
        state="readonly",
        values=EDGE_VOICES,
        font=FONT,
    )
    edge_voice_combo.pack(fill="x", padx=8, pady=(0, 6))
    edge_voice_var.trace_add("write", lambda *_: state.config.update(edge_voice=edge_voice_var.get()))

    piper_download_frame = tk.Frame(tts_frame, bg=BG)
    tk.Label(piper_download_frame, text=tr("piper_download_label"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(4, 0))
    piper_preset_var = tk.StringVar(value=state.config.get("piper_download_preset", "pl_PL-gosia-medium"))
    piper_preset_combo = ttk.Combobox(
        piper_download_frame,
        textvariable=piper_preset_var,
        state="readonly",
        values=list(PIPER_MODEL_PRESETS.keys()),
        font=FONT,
    )
    piper_preset_combo.pack(fill="x", padx=8, pady=(0, 6))
    piper_preset_var.trace_add("write", lambda *_: state.config.update(piper_download_preset=piper_preset_var.get()))

    def update_tts_voice_visibility(*_):
        provider = tts_var.get()
        piper_voice_frame.pack_forget()
        edge_voice_frame.pack_forget()
        piper_download_frame.pack_forget()
        if provider == "piper":
            piper_voice_frame.pack(fill="x")
            piper_download_frame.pack(fill="x")
        elif provider == "edge_tts":
            edge_voice_frame.pack(fill="x")

    tts_var.trace_add("write", update_tts_voice_visibility)

    make_path_row(tts_frame, tr("speaker_sample"), "speaker_wav", "wav")

    llm_frame = tk.LabelFrame(
        left,
        text=tr("llm"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    llm_frame.pack(fill="x", pady=(0, 8))

    tk.Label(llm_frame, text=tr("provider"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
    llm_provider_var = tk.StringVar(value=state.config.get("llm_provider", "lmstudio"))
    llm_provider_combo = ttk.Combobox(
        llm_frame,
        textvariable=llm_provider_var,
        state="readonly",
        values=["lmstudio", "ollama", "openai_compatible", "chatterbox", "custom"],
        font=FONT,
    )
    llm_provider_combo.pack(fill="x", padx=8, pady=(0, 4))

    tk.Label(llm_frame, text=tr("url"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8, pady=(6, 0))
    url_var = tk.StringVar(value=state.config.get("llm_url", "http://localhost:1234/v1"))
    tk.Entry(
        llm_frame,
        textvariable=url_var,
        bg=BG2,
        fg=FG,
        font=FONT,
        insertbackground=FG,
        relief="flat",
        bd=4,
    ).pack(fill="x", padx=8, pady=(0, 4))

    updating_llm_url = {"active": False}

    def on_llm_provider_change(*_):
        provider = llm_provider_var.get()
        state.config.update(llm_provider=provider)
        if provider != "custom" and provider in LLM_URLS:
            updating_llm_url["active"] = True
            url_var.set(LLM_URLS[provider])
            state.config.update(llm_url=url_var.get())
            updating_llm_url["active"] = False

    def on_llm_url_change(*_):
        state.config.update(llm_url=url_var.get())
        if updating_llm_url["active"]:
            return
        provider = llm_provider_var.get()
        if provider != "custom" and url_var.get() != LLM_URLS.get(provider, ""):
            llm_provider_var.set("custom")

    llm_provider_var.trace_add("write", on_llm_provider_change)
    url_var.trace_add("write", on_llm_url_change)

    def update_mode(*_):
        mode = mode_var.get()
        state.config.update(mode=mode)
        sync_source_field()

        lang_frame.pack_forget()
        extraction_frame.pack_forget()
        llm_frame.pack_forget()
        target_lang_frame.pack_forget()

        if mode == "txt_to_audio":
            return
        if mode == "pdf_to_audio":
            lang_frame.pack(fill="x", pady=(0, 8), before=tts_frame)
            extraction_frame.pack(fill="x", pady=(0, 8), before=tts_frame)
            return

        lang_frame.pack(fill="x", pady=(0, 8), before=tts_frame)
        target_lang_frame.pack(fill="x")
        extraction_frame.pack(fill="x", pady=(0, 8), before=tts_frame)
        llm_frame.pack(fill="x", pady=(0, 8), before=btn_frame)

    mode_var.trace_add("write", update_mode)

    tk.Label(llm_frame, text=tr("model"), bg=BG, fg=FG_MUTED, font=FONT).pack(anchor="w", padx=8)
    model_var = tk.StringVar(value=state.config.get("llm_model", ""))
    model_combo = ttk.Combobox(
        llm_frame,
        textvariable=model_var,
        state="normal",
        values=[model_var.get()] if model_var.get() else [],
        font=FONT,
    )
    model_combo.pack(fill="x", padx=8, pady=(0, 4))
    model_var.trace_add("write", lambda *_: state.config.update(llm_model=model_var.get()))

    def scan_llm_models():
        def worker():
            try:
                log(tr_runtime("llm_scan_start"))
                models = list_llm_models(
                    state.config.get("llm_url", ""),
                    state.config.get("llm_api_key") or None,
                    log_callback=None,
                )

                def apply_models():
                    if models:
                        model_combo.configure(values=models)
                        if not model_var.get() or model_var.get() not in models:
                            model_var.set(models[0])
                        log(tr_runtime("llm_found", len(models)))
                    else:
                        log(tr_runtime("llm_not_found"))

                root.after(0, apply_models)
            except Exception as e:
                root.after(0, lambda: log(tr_runtime("llm_scan_error", e)))

        threading.Thread(target=worker, daemon=True).start()

    tk.Button(
        llm_frame,
        text=tr("scan_models"),
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=scan_llm_models,
    ).pack(fill="x", padx=8, pady=(0, 6))

    btn_frame = tk.Frame(left, bg=BG)
    btn_frame.pack(fill="x", pady=(0, 8))

    def install_piper_model():
        import urllib.request

        models_dir = PROJECT_DIR / "piper_models"
        models_dir.mkdir(exist_ok=True)
        preset = piper_preset_var.get()
        files = PIPER_MODEL_PRESETS.get(preset, [])

        def download():
            if not files:
                log(tr_runtime("piper_preset_missing", preset))
                return
            for fname, url in files:
                dest = models_dir / fname
                if dest.exists():
                    log(tr_runtime("file_exists", fname))
                    continue
                log(tr_runtime("downloading", fname))
                try:
                    urllib.request.urlretrieve(url, dest)
                    log(tr_runtime("downloaded", fname))
                except Exception as e:
                    log(tr_runtime("download_error", fname, e))
            log(tr_runtime("piper_ready", preset))
            root.after(0, scan_piper_models)

        threading.Thread(target=download, daemon=True).start()

    tk.Button(
        btn_frame,
        text=tr("save_config"),
        bg=BG2,
        fg=FG,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=lambda: (state.save(), log(tr_runtime("config_saved"))),
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text=tr("download_piper"),
        bg="#0d2818",
        fg="#3fb950",
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=install_piper_model,
    ).pack(fill="x", pady=2)

    start_btn = tk.Button(
        right,
        text=tr("run_pipeline"),
        bg="#0d2818",
        fg=GREEN,
        font=("Consolas", 18, "bold"),
        relief="flat",
        cursor="hand2",
        height=3,
        activebackground="#0d2818",
        activeforeground=GREEN,
    )
    start_btn.pack(fill="x", pady=(0, 8))

    ctrl_frame = tk.Frame(right, bg=BG)
    ctrl_frame.pack(fill="x", pady=(0, 8))

    pause_btn = tk.Button(
        ctrl_frame,
        text=tr("pause"),
        bg=BG2,
        fg=YELLOW,
        font=FONT,
        relief="flat",
        cursor="hand2",
        width=12,
    )
    pause_btn.pack(side="left", padx=(0, 4))

    stop_btn = tk.Button(
        ctrl_frame,
        text=tr("stop"),
        bg=BG2,
        fg=RED,
        font=FONT,
        relief="flat",
        cursor="hand2",
        width=12,
    )
    stop_btn.pack(side="left", padx=(0, 4))

    open_btn = tk.Button(
        ctrl_frame,
        text=tr("open_folder"),
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
    )
    open_btn.pack(side="left")

    status_frame = tk.Frame(right, bg=BG2, pady=8)
    status_frame.pack(fill="x", pady=(0, 8))
    status_var = tk.StringVar(value=tr_runtime("status_ready"))
    tk.Label(status_frame, textvariable=status_var, bg=BG2, fg=GREEN, font=("Consolas", 12, "bold")).pack(padx=12)

    prog_frame = tk.LabelFrame(
        right,
        text=tr("progress"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    prog_frame.pack(fill="x", pady=(0, 8))

    prog_vars = {}
    pct_labels = {}
    for stage, label in [
        ("translation", tr("progress_translation")),
        ("audio", tr("progress_audio")),
        ("merge", tr("progress_merge")),
    ]:
        row = tk.Frame(prog_frame, bg=BG)
        row.pack(fill="x", padx=8, pady=2)
        tk.Label(row, text=label, bg=BG, fg=FG, font=FONT, width=26, anchor="w").pack(side="left")
        var = tk.DoubleVar(value=0)
        prog_vars[stage] = var
        ttk.Progressbar(row, variable=var, maximum=100, length=200).pack(
            side="left", fill="x", expand=True, padx=4
        )
        pct_label = tk.Label(row, text="0%", bg=BG, fg=FG_MUTED, font=FONT, width=5)
        pct_label.pack(side="left")
        pct_labels[stage] = pct_label

    console_frame = tk.LabelFrame(
        right,
        text=tr("console"),
        bg=BG,
        fg=ACCENT,
        font=FONT,
        bd=1,
        relief="solid",
    )
    console_frame.pack(fill="both", expand=True)

    console = scrolledtext.ScrolledText(
        console_frame,
        bg="#050708",
        fg=GREEN,
        font=FONT_MONO,
        relief="flat",
        state="normal",
        wrap="word",
        height=12,
    )
    console.pack(fill="both", expand=True, padx=4, pady=4)

    def log(msg: str):
        state.logs.append(msg)
        console.configure(state="normal")
        console.insert("end", msg + "\n")
        console.see("end")
        console.configure(state="disabled")

    def progress_cb(stage: str, current: int, total: int):
        pct = int(current / total * 100) if total > 0 else 0
        if stage in prog_vars:
            prog_vars[stage].set(pct)
        if stage in pct_labels:
            pct_labels[stage].config(text=f"{pct}%")

    def start_pipeline():
        if state.running:
            return
        state.running = True
        state.reset_events()

        output_dir = Path(state.config.get("output_dir", ""))
        output_txt = output_dir / "output.txt"
        if state.config.get("mode") != "txt_to_audio" and output_txt.exists():
            output_txt.unlink()
            log(tr_runtime("old_output_removed"))

        status_var.set(tr_runtime("status_running"))
        console.configure(state="normal")
        console.delete("1.0", "end")
        console.configure(state="disabled")
        for v in prog_vars.values():
            v.set(0)

        def run():
            try:
                run_pipeline(state.config, log, progress_cb, state.pause_event, state.stop_event)
                status_var.set(tr_runtime("status_completed"))
                log(tr_runtime("done"))
            except Exception as e:
                log(tr_runtime("error", e))
                log(traceback.format_exc())
                status_var.set(tr_runtime("status_error"))
            finally:
                state.running = False

        threading.Thread(target=run, daemon=True).start()

    def pause_pipeline():
        if state.pause_event.is_set():
            state.pause_event.clear()
            pause_btn.config(text=tr_runtime("pause_button"))
            status_var.set(tr_runtime("status_running"))
        else:
            state.pause_event.set()
            pause_btn.config(text=tr_runtime("resume_button"))
            status_var.set(tr_runtime("status_paused"))

    def stop_pipeline():
        state.stop_event.set()
        state.pause_event.clear()
        status_var.set(tr_runtime("status_stopped"))
        log(tr_runtime("stopped"))

    def open_folder():
        import subprocess

        output = Path(state.config.get("output_dir", str(PROJECT_DIR / "audiobook_output")))
        output.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{output}"')

    start_btn.config(command=start_pipeline)
    pause_btn.config(command=pause_pipeline)
    stop_btn.config(command=stop_pipeline)
    open_btn.config(command=open_folder)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TCombobox",
        fieldbackground="#161b22",
        background="#161b22",
        foreground="#c9d1d9",
        selectbackground="#161b22",
        selectforeground="#c9d1d9",
        insertcolor="#c9d1d9",
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "#161b22")],
        foreground=[("readonly", "#c9d1d9")],
    )
    style.configure("TProgressbar", troughcolor=BG2, background=ACCENT)

    scan_piper_models()
    update_tts_voice_visibility()
    update_mode()

    log(tr_runtime("app_ready"))
    root.mainloop()
