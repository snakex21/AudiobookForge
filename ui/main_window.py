import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import traceback
import time
import json
import zipfile
from pipeline import run_pipeline, list_llm_models, LLM_URLS, build_job_signature
from ui.state import state, PROJECT_DIR, RESOURCE_DIR, CONFIG_PATH


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
    "pt-PT-RaquelNeural",
    "pt-PT-DuarteNeural",
    "nl-NL-ColetteNeural",
    "nl-NL-MaartenNeural",
    "sv-SE-SofieNeural",
    "sv-SE-MattiasNeural",
    "fi-FI-NooraNeural",
    "fi-FI-SelmaNeural",
    "da-DK-ChristelNeural",
    "da-DK-JeppeNeural",
    "nb-NO-PernilleNeural",
    "nb-NO-FinnNeural",
    "hu-HU-NoemiNeural",
    "hu-HU-TamasNeural",
    "ro-RO-AlinaNeural",
    "ro-RO-EmilNeural",
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
TARGET_LANGUAGES = ["pol", "eng", "rus", "deu", "fra", "ces", "ukr", "spa", "ita", "por", "nld", "hun", "ron", "fin", "swe", "dan", "nor", "tur"]
UI_LANGUAGE_OPTIONS = [
    ("Polski", "pl"),
    ("Cesky", "cs"),
    ("Romana", "ro"),
    ("Magyar", "hu"),
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
    ("Suomi", "fi"),
    ("Dansk", "da"),
    ("Norsk", "no"),
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
        "recent_projects": "Ostatnie projekty",
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
        "recent_projects": "Poslední projekty",
    },
    "ro": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "Limba UI",
        "work_mode": "Mod de lucru",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Traducere → Audio",
        "mode_translate_txt": "PDF → Traducere → TXT",
        "mode_txt_audio": "TXT → Audio (output.txt existent)",
        "source_files": "Fisiere sursa",
        "pdf_file": "Fisier PDF",
        "txt_file": "Fisier TXT",
        "output_dir": "Folder iesire",
        "pdf_settings": "Setari PDF",
        "pdf_language": "Limba PDF",
        "target_language": "Limba tinta (traducere)",
        "text_extraction": "Extragere text",
        "extract_fast": "pypdfium2 (rapid)",
        "extract_vision": "LLM Vision OCR (pentru PDF-uri dificile)",
        "tts": "TTS (sinteza vocala)",
        "provider": "Provider",
        "piper_voice": "Voce Piper",
        "edge_voice": "Voce Edge TTS",
        "speaker_sample": "Mostra voce (WAV)",
        "llm": "LLM (Traducere)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Scaneaza modele LLM",
        "piper_download_label": "Model Piper de descarcat",
        "save_config": "Salveaza config",
        "download_piper": "⬇ Descarca modelul Piper",
        "run_pipeline": "▶  PORNESTE PIPELINE",
        "pause": "⏸ Pauza",
        "resume": "▶ Reia",
        "stop": "⏹ Stop",
        "open_folder": "📂 Deschide folderul",
        "ready": "● GATA",
        "progress": "Progres",
        "progress_translation": "Extragere / Traducere",
        "progress_audio": "Audio",
        "progress_merge": "Imbinare",
        "console": "Consola",
        "recent_projects": "Proiecte recente",
    },
    "hu": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI nyelv",
        "work_mode": "Munkamod",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Forditas → Audio",
        "mode_translate_txt": "PDF → Forditas → TXT",
        "mode_txt_audio": "TXT → Audio (meglevo output.txt)",
        "source_files": "Forrasfajlok",
        "pdf_file": "PDF fajl",
        "txt_file": "TXT fajl",
        "output_dir": "Kimeneti mappa",
        "pdf_settings": "PDF beallitasok",
        "pdf_language": "PDF nyelve",
        "target_language": "Celnyelv (forditas)",
        "text_extraction": "Szovegkinyeres",
        "extract_fast": "pypdfium2 (gyors)",
        "extract_vision": "LLM Vision OCR (nehez PDF-ekhez)",
        "tts": "TTS (beszedszintezis)",
        "provider": "Szolgaltato",
        "piper_voice": "Piper hang",
        "edge_voice": "Edge TTS hang",
        "speaker_sample": "Hangminta (WAV)",
        "llm": "LLM (Forditas)",
        "url": "URL",
        "model": "Modell",
        "scan_models": "LLM modellek keresese",
        "piper_download_label": "Letoltendo Piper modell",
        "save_config": "Config mentese",
        "download_piper": "⬇ Piper modell letoltese",
        "run_pipeline": "▶  PIPELINE INDITASA",
        "pause": "⏸ Szünet",
        "resume": "▶ Folytatas",
        "stop": "⏹ Stop",
        "open_folder": "📂 Mappa megnyitasa",
        "ready": "● KESZ",
        "progress": "Haladas",
        "progress_translation": "Kinyeres / Forditas",
        "progress_audio": "Audio",
        "progress_merge": "Egyesites",
        "console": "Konzol",
        "recent_projects": "Legutobbi projektek",
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
        "recent_projects": "Recent Projects",
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
        "recent_projects": "Letzte Projekte",
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
        "recent_projects": "Projets récents",
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
        "recent_projects": "Proyectos recientes",
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
        "recent_projects": "Progetti recenti",
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
        "recent_projects": "Недавние проекты",
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
        "recent_projects": "Останні проєкти",
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
        "recent_projects": "Son projeler",
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
        "recent_projects": "Projetos recentes",
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
        "recent_projects": "Recente projecten",
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
        "recent_projects": "Senaste projekt",
    },
    "fi": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-kieli",
        "work_mode": "Tyotila",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Kaannos → Audio",
        "mode_translate_txt": "PDF → Kaannos → TXT",
        "mode_txt_audio": "TXT → Audio (olemassa oleva output.txt)",
        "source_files": "Lahdetiedostot",
        "pdf_file": "PDF-tiedosto",
        "txt_file": "TXT-tiedosto",
        "output_dir": "Tulostekansio",
        "pdf_settings": "PDF-asetukset",
        "pdf_language": "PDF-kieli",
        "target_language": "Kohdekieli (kaannos)",
        "text_extraction": "Tekstin poiminta",
        "extract_fast": "pypdfium2 (nopea)",
        "extract_vision": "LLM Vision OCR (vaikeille PDF-tiedostoille)",
        "tts": "TTS (puhesynteesi)",
        "provider": "Palvelu",
        "piper_voice": "Piper-aani",
        "edge_voice": "Edge TTS -aani",
        "speaker_sample": "Aaninayte (WAV)",
        "llm": "LLM (Kaannos)",
        "url": "URL",
        "model": "Malli",
        "scan_models": "Skannaa LLM-mallit",
        "piper_download_label": "Ladattava Piper-malli",
        "save_config": "Tallenna config",
        "download_piper": "⬇ Lataa Piper-malli",
        "run_pipeline": "▶  KAYNNISTA PIPELINE",
        "pause": "⏸ Tauko",
        "resume": "▶ Jatka",
        "stop": "⏹ Stop",
        "open_folder": "📂 Avaa kansio",
        "ready": "● VALMIS",
        "progress": "Edistyminen",
        "progress_translation": "Poiminta / Kaannos",
        "progress_audio": "Audio",
        "progress_merge": "Yhdistaminen",
        "console": "Konsoli",
        "recent_projects": "Viimeisimmat projektit",
    },
    "da": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-sprog",
        "work_mode": "Arbejdstilstand",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Oversaettelse → Audio",
        "mode_translate_txt": "PDF → Oversaettelse → TXT",
        "mode_txt_audio": "TXT → Audio (eksisterende output.txt)",
        "source_files": "Kildefiler",
        "pdf_file": "PDF-fil",
        "txt_file": "TXT-fil",
        "output_dir": "Outputmappe",
        "pdf_settings": "PDF-indstillinger",
        "pdf_language": "PDF-sprog",
        "target_language": "Malsprog (oversaettelse)",
        "text_extraction": "Tekstudtraek",
        "extract_fast": "pypdfium2 (hurtig)",
        "extract_vision": "LLM Vision OCR (til svaere PDF-filer)",
        "tts": "TTS (talesyntese)",
        "provider": "Udbyder",
        "piper_voice": "Piper-stemme",
        "edge_voice": "Edge TTS-stemme",
        "speaker_sample": "Stemmeprove (WAV)",
        "llm": "LLM (Oversaettelse)",
        "url": "URL",
        "model": "Model",
        "scan_models": "Scan LLM-modeller",
        "piper_download_label": "Piper-model til download",
        "save_config": "Gem config",
        "download_piper": "⬇ Download Piper-model",
        "run_pipeline": "▶  START PIPELINE",
        "pause": "⏸ Pause",
        "resume": "▶ Fortsaet",
        "stop": "⏹ Stop",
        "open_folder": "📂 Aabn mappe",
        "ready": "● KLAR",
        "progress": "Fremskridt",
        "progress_translation": "Udtraek / Oversaettelse",
        "progress_audio": "Audio",
        "progress_merge": "Sammenfletning",
        "console": "Konsol",
        "recent_projects": "Seneste projekter",
    },
    "no": {
        "app_title": "AUDIOBOOK FORGE v1.0",
        "ui_language": "UI-sprak",
        "work_mode": "Arbeidsmodus",
        "mode_pdf_audio": "PDF → Audio",
        "mode_translate_audio": "PDF → Oversettelse → Audio",
        "mode_translate_txt": "PDF → Oversettelse → TXT",
        "mode_txt_audio": "TXT → Audio (eksisterende output.txt)",
        "source_files": "Kildefiler",
        "pdf_file": "PDF-fil",
        "txt_file": "TXT-fil",
        "output_dir": "Utdatamappe",
        "pdf_settings": "PDF-innstillinger",
        "pdf_language": "PDF-sprak",
        "target_language": "Malsprak (oversettelse)",
        "text_extraction": "Tekstuttrekk",
        "extract_fast": "pypdfium2 (rask)",
        "extract_vision": "LLM Vision OCR (for vanskelige PDF-er)",
        "tts": "TTS (talesyntese)",
        "provider": "Leverandor",
        "piper_voice": "Piper-stemme",
        "edge_voice": "Edge TTS-stemme",
        "speaker_sample": "Stemmeprove (WAV)",
        "llm": "LLM (Oversettelse)",
        "url": "URL",
        "model": "Modell",
        "scan_models": "Skann LLM-modeller",
        "piper_download_label": "Piper-modell for nedlasting",
        "save_config": "Lagre config",
        "download_piper": "⬇ Last ned Piper-modell",
        "run_pipeline": "▶  START PIPELINE",
        "pause": "⏸ Pause",
        "resume": "▶ Fortsett",
        "stop": "⏹ Stop",
        "open_folder": "📂 Aapne mappe",
        "ready": "● KLAR",
        "progress": "Fremdrift",
        "progress_translation": "Uttrekk / Oversettelse",
        "progress_audio": "Audio",
        "progress_merge": "Sammenslaing",
        "console": "Konsoll",
        "recent_projects": "Siste prosjekter",
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
    "ro": {
        "llm_scan_start": "Se scaneaza modelele LLM...",
        "llm_found": "Modele LLM gasite: {}",
        "llm_not_found": "Nu s-au gasit modele LLM",
        "llm_scan_error": "Eroare la scanarea modelelor LLM: {}",
        "piper_preset_missing": "Lipseste definitia de descarcare pentru modelul: {}",
        "file_exists": "✓ {} exista deja",
        "downloading": "Se descarca {}...",
        "downloaded": "✓ {} descarcat",
        "download_error": "Eroare la descarcarea {}: {}",
        "piper_ready": "Modelul Piper este gata: {}",
        "config_saved": "Config salvat",
        "old_output_removed": "Output.txt vechi a fost sters - pornire de la zero",
        "done": "✓ Gata!",
        "error": "EROARE: {}",
        "stopped": "Oprit",
        "app_ready": "AudiobookForge este gata.",
        "status_ready": "● GATA",
        "status_running": "● RULEAZA",
        "status_completed": "● FINALIZAT",
        "status_error": "● EROARE",
        "status_paused": "● PAUZA",
        "status_stopped": "● OPRIT",
        "pause_button": "⏸ Pauza",
        "resume_button": "▶ Reia",
    },
    "hu": {
        "llm_scan_start": "LLM modellek keresese...",
        "llm_found": "Talalt LLM modellek: {}",
        "llm_not_found": "Nem talalhato LLM modell",
        "llm_scan_error": "LLM modellkereses hiba: {}",
        "piper_preset_missing": "Nincs letoltesi definicio ehhez a modellhez: {}",
        "file_exists": "✓ {} mar letezik",
        "downloading": "{} letoltese...",
        "downloaded": "✓ {} letoltve",
        "download_error": "Letoltesi hiba {}: {}",
        "piper_ready": "Piper modell keszen all: {}",
        "config_saved": "Config mentve",
        "old_output_removed": "A regi output.txt torolve - ujrainditas nullarol",
        "done": "✓ Keszen!",
        "error": "HIBA: {}",
        "stopped": "Leallitva",
        "app_ready": "Az AudiobookForge keszen all.",
        "status_ready": "● KESZ",
        "status_running": "● FUT",
        "status_completed": "● BEFEJEZVE",
        "status_error": "● HIBA",
        "status_paused": "● SZUNET",
        "status_stopped": "● LEALLITVA",
        "pause_button": "⏸ Szünet",
        "resume_button": "▶ Folytatas",
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
    "fi": {
        "llm_scan_start": "Skannataan LLM-malleja...",
        "llm_found": "Loydetyt LLM-mallit: {}",
        "llm_not_found": "LLM-malleja ei loytynyt",
        "llm_scan_error": "Virhe LLM-mallien skannauksessa: {}",
        "piper_preset_missing": "Mallille ei ole latausmaaritysta: {}",
        "file_exists": "✓ {} on jo olemassa",
        "downloading": "Ladataan {}...",
        "downloaded": "✓ {} ladattu",
        "download_error": "Latausvirhe {}: {}",
        "piper_ready": "Piper-malli valmis: {}",
        "config_saved": "Config tallennettu",
        "old_output_removed": "Vanha output.txt poistettu - aloitetaan alusta",
        "done": "✓ Valmis!",
        "error": "VIRHE: {}",
        "stopped": "Pysaytetty",
        "app_ready": "AudiobookForge on valmis.",
        "status_ready": "● VALMIS",
        "status_running": "● KAYNNISSA",
        "status_completed": "● VALMIS",
        "status_error": "● VIRHE",
        "status_paused": "● TAUKO",
        "status_stopped": "● PYSAYTETTY",
        "pause_button": "⏸ Tauko",
        "resume_button": "▶ Jatka",
    },
    "da": {
        "llm_scan_start": "Scanner LLM-modeller...",
        "llm_found": "Fundne LLM-modeller: {}",
        "llm_not_found": "Ingen LLM-modeller fundet",
        "llm_scan_error": "Fejl ved scanning af LLM-modeller: {}",
        "piper_preset_missing": "Ingen downloaddefinition for modellen: {}",
        "file_exists": "✓ {} findes allerede",
        "downloading": "Downloader {}...",
        "downloaded": "✓ {} downloadet",
        "download_error": "Downloadfejl {}: {}",
        "piper_ready": "Piper-model klar: {}",
        "config_saved": "Config gemt",
        "old_output_removed": "Gammel output.txt fjernet - starter forfra",
        "done": "✓ Faerdig!",
        "error": "FEJL: {}",
        "stopped": "Stoppet",
        "app_ready": "AudiobookForge er klar.",
        "status_ready": "● KLAR",
        "status_running": "● KORER",
        "status_completed": "● FULDFORT",
        "status_error": "● FEJL",
        "status_paused": "● PAUSE",
        "status_stopped": "● STOPPET",
        "pause_button": "⏸ Pause",
        "resume_button": "▶ Fortsaet",
    },
    "no": {
        "llm_scan_start": "Skanner LLM-modeller...",
        "llm_found": "Fant LLM-modeller: {}",
        "llm_not_found": "Ingen LLM-modeller funnet",
        "llm_scan_error": "Feil ved skanning av LLM-modeller: {}",
        "piper_preset_missing": "Ingen nedlastingsdefinisjon for modellen: {}",
        "file_exists": "✓ {} finnes allerede",
        "downloading": "Laster ned {}...",
        "downloaded": "✓ {} lastet ned",
        "download_error": "Nedlastingsfeil {}: {}",
        "piper_ready": "Piper-modell klar: {}",
        "config_saved": "Config lagret",
        "old_output_removed": "Gammel output.txt fjernet - starter pa nytt",
        "done": "✓ Ferdig!",
        "error": "FEIL: {}",
        "stopped": "Stoppet",
        "app_ready": "AudiobookForge er klar.",
        "status_ready": "● KLAR",
        "status_running": "● KJORER",
        "status_completed": "● FULLFORT",
        "status_error": "● FEIL",
        "status_paused": "● PAUSE",
        "status_stopped": "● STOPPET",
        "pause_button": "⏸ Pause",
        "resume_button": "▶ Fortsett",
    },
}

EXTRA_UI_TEXTS = {
    "pl": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Eksport ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Eksport ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Eksport ZIP",
        "import_zip_success": "Zaimportowano config: {}\nZaimportowane pliki Piper: {}",
        "export_zip_success": "Wyeksportowano pliki: {}",
        "import_zip_error_title": "Błąd importu ZIP",
        "export_zip_error_title": "Błąd eksportu ZIP",
        "zip_missing": "ZIP nie zawiera config.json ani plików modelu Piper",
        "zip_nothing_to_export": "Brak plików do eksportu",
        "resume_title": "Wznowić poprzednie zadanie",
        "resume_message": "W wybranym folderze wyjściowym znaleziono zapisane postępy dla tego zadania.\n\n{}\n\nTak = Wznów\nNie = Zacznij od nowa\nAnuluj = Anuluj",
        "overwrite_title": "Folder wyjściowy jest już używany",
        "overwrite_message": "Wybrany folder wyjściowy zawiera inne zadanie.\n\n{}\n\nTak = Nadpisz stare zadanie w tym folderze\nNie = Anuluj i wybierz inny folder\nAnuluj = Anuluj",
        "summary_source": "Źródło: {}",
        "summary_mode": "Tryb: {}",
        "summary_pages": "Zapisane strony: {}",
        "summary_chunks": "Zapisane chunki: {}",
        "summary_final_audio": "Finalne audio: {}",
        "yes": "tak",
        "no": "nie",
        "recent_empty": "Brak ostatnich projektów.",
        "recent_load": "Wczytaj",
        "recent_open": "Otwórz",
        "recent_source": "Źródło: {}",
        "recent_output": "Wyjście: {}",
        "recent_status_configured": "Skonfigurowany",
        "recent_status_in_progress": "Nieukończony",
        "recent_status_completed": "Ukończony",
    },
    "cs": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Export ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Export ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Export ZIP",
        "import_zip_success": "Importovany config: {}\nImportovane soubory Piper: {}",
        "export_zip_success": "Exportovane soubory: {}",
        "import_zip_error_title": "Chyba importu ZIP",
        "export_zip_error_title": "Chyba exportu ZIP",
        "zip_missing": "ZIP neobsahuje config.json ani soubory modelu Piper",
        "zip_nothing_to_export": "Neni co exportovat",
        "resume_title": "Obnovit předchozí úlohu",
        "resume_message": "Ve vybrané výstupní složce byl nalezen uložený postup pro tuto úlohu.\n\n{}\n\nAno = Obnovit\nNe = Začít znovu\nZrušit = Zrušit",
        "overwrite_title": "Výstupní složka je již používána",
        "overwrite_message": "Vybraná výstupní složka obsahuje jinou úlohu.\n\n{}\n\nAno = Přepsat starou úlohu v této složce\nNe = Zrušit a vybrat jinou složku\nZrušit = Zrušit",
        "summary_source": "Zdroj: {}",
        "summary_mode": "Rezim: {}",
        "summary_pages": "Ulozene strany: {}",
        "summary_chunks": "Ulozene chunky: {}",
        "summary_final_audio": "Finalni audio: {}",
        "yes": "ano",
        "no": "ne",
        "recent_empty": "Zatím žádné poslední projekty.",
        "recent_load": "Načíst",
        "recent_open": "Otevřít",
        "recent_source": "Zdroj: {}",
        "recent_output": "Výstup: {}",
        "recent_status_configured": "Nastaveno",
        "recent_status_in_progress": "Nedokončeno",
        "recent_status_completed": "Dokončeno",
    },
    "ro": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Export ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Export ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Export ZIP",
        "import_zip_success": "Config importat: {}\nFisiere Piper importate: {}",
        "export_zip_success": "Fisiere exportate: {}",
        "import_zip_error_title": "Eroare import ZIP",
        "export_zip_error_title": "Eroare export ZIP",
        "zip_missing": "ZIP-ul nu contine config.json sau fisiere de model Piper",
        "zip_nothing_to_export": "Nu exista fisiere de exportat",
        "resume_title": "Reia taskul anterior",
        "resume_message": "A fost gasit progres salvat pentru acest task in folderul de iesire selectat.\n\n{}\n\nDa = Reia\nNu = Incepe de la zero\nAnuleaza = Anuleaza",
        "overwrite_title": "Folderul de iesire este deja folosit",
        "overwrite_message": "Folderul de iesire selectat contine alt task.\n\n{}\n\nDa = Suprascrie taskul vechi din acest folder\nNu = Anuleaza si alege alt folder\nAnuleaza = Anuleaza",
        "summary_source": "Sursa: {}",
        "summary_mode": "Mod: {}",
        "summary_pages": "Pagini salvate: {}",
        "summary_chunks": "Chunk-uri salvate: {}",
        "summary_final_audio": "Audio final: {}",
        "yes": "da",
        "no": "nu",
        "recent_empty": "Inca nu exista proiecte recente.",
        "recent_load": "Incarca",
        "recent_open": "Deschide",
        "recent_source": "Sursa: {}",
        "recent_output": "Iesire: {}",
        "recent_status_configured": "Configurat",
        "recent_status_in_progress": "Incomplet",
        "recent_status_completed": "Finalizat",
    },
    "hu": {
        "import_zip_button": "⬆ ZIP import (config + Piper)",
        "export_zip_button": "⬇ ZIP export (config + output)",
        "import_zip_title": "ZIP import",
        "export_zip_title": "ZIP export",
        "import_zip_success_title": "ZIP import",
        "export_zip_success_title": "ZIP export",
        "import_zip_success": "Importalt config: {}\nImportalt Piper fajlok: {}",
        "export_zip_success": "Exportalt fajlok: {}",
        "import_zip_error_title": "ZIP import hiba",
        "export_zip_error_title": "ZIP export hiba",
        "zip_missing": "A ZIP nem tartalmaz config.json vagy Piper modellfajlokat",
        "zip_nothing_to_export": "Nincs exportalhato fajl",
        "resume_title": "Elozo feladat folytatasa",
        "resume_message": "A kijelolt kimeneti mappaban mentett elorehaladas talalhato ehhez a feladathoz.\n\n{}\n\nIgen = Folytatas\nNem = Ujrakezdes\nMegse = Megse",
        "overwrite_title": "A kimeneti mappa mar hasznalatban van",
        "overwrite_message": "A kijelolt kimeneti mappa masik feladatot tartalmaz.\n\n{}\n\nIgen = Regi feladat felulirasa ebben a mappaban\nNem = Megse es masik mappa valasztasa\nMegse = Megse",
        "summary_source": "Forras: {}",
        "summary_mode": "Mod: {}",
        "summary_pages": "Mentett oldalak: {}",
        "summary_chunks": "Mentett chunkok: {}",
        "summary_final_audio": "Vegso audio: {}",
        "yes": "igen",
        "no": "nem",
        "recent_empty": "Meg nincsenek legutobbi projektek.",
        "recent_load": "Betoltes",
        "recent_open": "Megnyitas",
        "recent_source": "Forras: {}",
        "recent_output": "Kimenet: {}",
        "recent_status_configured": "Beallitva",
        "recent_status_in_progress": "Befejezetlen",
        "recent_status_completed": "Befejezve",
    },
    "en": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Export ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Export ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Export ZIP",
        "import_zip_success": "Imported config: {}\nImported Piper files: {}",
        "export_zip_success": "Exported files: {}",
        "import_zip_error_title": "ZIP import error",
        "export_zip_error_title": "ZIP export error",
        "zip_missing": "ZIP does not contain config.json or Piper model files",
        "zip_nothing_to_export": "No files available to export",
        "resume_title": "Resume previous job",
        "resume_message": "Found existing work for this job in the selected output folder.\n\n{}\n\nYes = Resume\nNo = Start over\nCancel = Cancel",
        "overwrite_title": "Output folder already used",
        "overwrite_message": "The selected output folder contains another job.\n\n{}\n\nYes = Overwrite old job in this folder\nNo = Cancel and choose another folder\nCancel = Cancel",
        "summary_source": "Source: {}",
        "summary_mode": "Mode: {}",
        "summary_pages": "Pages saved: {}",
        "summary_chunks": "Chunks saved: {}",
        "summary_final_audio": "Final audio: {}",
        "summary_elapsed": "Elapsed: {}",
        "summary_stage": "Last stage: {}",
        "yes": "yes",
        "no": "no",
        "recent_empty": "No recent projects yet.",
        "recent_load": "Load",
        "recent_open": "Open",
        "recent_source": "Source: {}",
        "recent_output": "Output: {}",
        "recent_status_configured": "Configured",
        "recent_status_in_progress": "Incomplete",
        "recent_status_completed": "Completed",
    },
    "de": {
        "import_zip_button": "⬆ ZIP importieren (Config + Piper)",
        "export_zip_button": "⬇ ZIP exportieren (Config + Output)",
        "import_zip_title": "ZIP importieren",
        "export_zip_title": "ZIP exportieren",
        "import_zip_success_title": "ZIP importieren",
        "export_zip_success_title": "ZIP exportieren",
        "import_zip_success": "Importierte Config: {}\nImportierte Piper-Dateien: {}",
        "export_zip_success": "Exportierte Dateien: {}",
        "import_zip_error_title": "ZIP-Importfehler",
        "export_zip_error_title": "ZIP-Exportfehler",
        "zip_missing": "ZIP enthält weder config.json noch Piper-Modelldateien",
        "zip_nothing_to_export": "Keine Dateien zum Exportieren vorhanden",
        "resume_title": "Vorherige Aufgabe fortsetzen",
        "resume_message": "Im gewählten Ausgabeordner wurde ein gespeicherter Fortschritt für diese Aufgabe gefunden.\n\n{}\n\nJa = Fortsetzen\nNein = Neu starten\nAbbrechen = Abbrechen",
        "overwrite_title": "Ausgabeordner wird bereits verwendet",
        "overwrite_message": "Der gewählte Ausgabeordner enthält eine andere Aufgabe.\n\n{}\n\nJa = Alte Aufgabe in diesem Ordner überschreiben\nNein = Abbrechen und anderen Ordner wählen\nAbbrechen = Abbrechen",
        "summary_source": "Quelle: {}",
        "summary_mode": "Modus: {}",
        "summary_pages": "Gespeicherte Seiten: {}",
        "summary_chunks": "Gespeicherte Chunks: {}",
        "summary_final_audio": "Finales Audio: {}",
        "yes": "ja",
        "no": "nein",
        "recent_empty": "Noch keine letzten Projekte.",
        "recent_load": "Laden",
        "recent_open": "Öffnen",
        "recent_source": "Quelle: {}",
        "recent_output": "Ausgabe: {}",
        "recent_status_configured": "Konfiguriert",
        "recent_status_in_progress": "Unvollständig",
        "recent_status_completed": "Abgeschlossen",
    },
    "fr": {
        "import_zip_button": "⬆ Importer ZIP (config + Piper)",
        "export_zip_button": "⬇ Exporter ZIP (config + sortie)",
        "import_zip_title": "Importer ZIP",
        "export_zip_title": "Exporter ZIP",
        "import_zip_success_title": "Importer ZIP",
        "export_zip_success_title": "Exporter ZIP",
        "import_zip_success": "Config importee : {}\nFichiers Piper importes : {}",
        "export_zip_success": "Fichiers exportes : {}",
        "import_zip_error_title": "Erreur d'import ZIP",
        "export_zip_error_title": "Erreur d'export ZIP",
        "zip_missing": "Le ZIP ne contient ni config.json ni fichiers de modele Piper",
        "zip_nothing_to_export": "Aucun fichier a exporter",
        "resume_title": "Reprendre la tache precedente",
        "resume_message": "Une progression enregistree pour cette tache a ete trouvee dans le dossier de sortie selectionne.\n\n{}\n\nOui = Reprendre\nNon = Recommencer\nAnnuler = Annuler",
        "overwrite_title": "Dossier de sortie deja utilise",
        "overwrite_message": "Le dossier de sortie selectionne contient une autre tache.\n\n{}\n\nOui = Ecraser l'ancienne tache dans ce dossier\nNon = Annuler et choisir un autre dossier\nAnnuler = Annuler",
        "summary_source": "Source : {}",
        "summary_mode": "Mode : {}",
        "summary_pages": "Pages enregistrees : {}",
        "summary_chunks": "Chunks enregistres : {}",
        "summary_final_audio": "Audio final : {}",
        "yes": "oui",
        "no": "non",
        "recent_empty": "Aucun projet récent pour le moment.",
        "recent_load": "Charger",
        "recent_open": "Ouvrir",
        "recent_source": "Source : {}",
        "recent_output": "Sortie : {}",
        "recent_status_configured": "Configuré",
        "recent_status_in_progress": "Incomplet",
        "recent_status_completed": "Terminé",
    },
    "es": {
        "import_zip_button": "⬆ Importar ZIP (config + Piper)",
        "export_zip_button": "⬇ Exportar ZIP (config + salida)",
        "import_zip_title": "Importar ZIP",
        "export_zip_title": "Exportar ZIP",
        "import_zip_success_title": "Importar ZIP",
        "export_zip_success_title": "Exportar ZIP",
        "import_zip_success": "Config importada: {}\nArchivos Piper importados: {}",
        "export_zip_success": "Archivos exportados: {}",
        "import_zip_error_title": "Error al importar ZIP",
        "export_zip_error_title": "Error al exportar ZIP",
        "zip_missing": "El ZIP no contiene config.json ni archivos del modelo Piper",
        "zip_nothing_to_export": "No hay archivos para exportar",
        "resume_title": "Reanudar tarea anterior",
        "resume_message": "Se encontro progreso guardado para esta tarea en la carpeta de salida seleccionada.\n\n{}\n\nSi = Reanudar\nNo = Empezar de nuevo\nCancelar = Cancelar",
        "overwrite_title": "La carpeta de salida ya esta en uso",
        "overwrite_message": "La carpeta de salida seleccionada contiene otra tarea.\n\n{}\n\nSi = Sobrescribir la tarea antigua en esta carpeta\nNo = Cancelar y elegir otra carpeta\nCancelar = Cancelar",
        "summary_source": "Origen: {}",
        "summary_mode": "Modo: {}",
        "summary_pages": "Paginas guardadas: {}",
        "summary_chunks": "Chunks guardados: {}",
        "summary_final_audio": "Audio final: {}",
        "yes": "si",
        "no": "no",
        "recent_empty": "Aún no hay proyectos recientes.",
        "recent_load": "Cargar",
        "recent_open": "Abrir",
        "recent_source": "Origen: {}",
        "recent_output": "Salida: {}",
        "recent_status_configured": "Configurado",
        "recent_status_in_progress": "Incompleto",
        "recent_status_completed": "Completado",
    },
    "it": {
        "import_zip_button": "⬆ Importa ZIP (config + Piper)",
        "export_zip_button": "⬇ Esporta ZIP (config + output)",
        "import_zip_title": "Importa ZIP",
        "export_zip_title": "Esporta ZIP",
        "import_zip_success_title": "Importa ZIP",
        "export_zip_success_title": "Esporta ZIP",
        "import_zip_success": "Config importata: {}\nFile Piper importati: {}",
        "export_zip_success": "File esportati: {}",
        "import_zip_error_title": "Errore import ZIP",
        "export_zip_error_title": "Errore export ZIP",
        "zip_missing": "Lo ZIP non contiene config.json ne file del modello Piper",
        "zip_nothing_to_export": "Nessun file da esportare",
        "resume_title": "Riprendi attività precedente",
        "resume_message": "Nel percorso di output selezionato e stato trovato un avanzamento salvato per questa attivita.\n\n{}\n\nSi = Riprendi\nNo = Ricomincia\nAnnulla = Annulla",
        "overwrite_title": "Cartella di output gia usata",
        "overwrite_message": "La cartella di output selezionata contiene un'altra attivita.\n\n{}\n\nSi = Sovrascrivi la vecchia attivita in questa cartella\nNo = Annulla e scegli un'altra cartella\nAnnulla = Annulla",
        "summary_source": "Origine: {}",
        "summary_mode": "Modalita: {}",
        "summary_pages": "Pagine salvate: {}",
        "summary_chunks": "Chunk salvati: {}",
        "summary_final_audio": "Audio finale: {}",
        "yes": "si",
        "no": "no",
        "recent_empty": "Nessun progetto recente.",
        "recent_load": "Carica",
        "recent_open": "Apri",
        "recent_source": "Origine: {}",
        "recent_output": "Output: {}",
        "recent_status_configured": "Configurato",
        "recent_status_in_progress": "Incompleto",
        "recent_status_completed": "Completato",
    },
    "ru": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Export ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Export ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Export ZIP",
        "import_zip_success": "Importirovan config: {}\nImportirovano failov Piper: {}",
        "export_zip_success": "Eksportirovano failov: {}",
        "import_zip_error_title": "Oshibka importa ZIP",
        "export_zip_error_title": "Oshibka eksporta ZIP",
        "zip_missing": "ZIP ne soderzhit config.json ili failov modeli Piper",
        "zip_nothing_to_export": "Net failov dlya eksporta",
        "resume_title": "Prodolzhit predydushchuyu zadachu",
        "resume_message": "V vybrannoy papke vyvoda nayden sohranennyy progress dlya etoy zadachi.\n\n{}\n\nDa = Prodolzhit\nNet = Nachat zanovo\nOtmena = Otmena",
        "overwrite_title": "Papka vyvoda uzhe ispolzuetsya",
        "overwrite_message": "Vybrannaya papka vyvoda soderzhit druguyu zadachu.\n\n{}\n\nDa = Perepisat staruyu zadachu v etoy papke\nNet = Otmenit i vybrat druguyu papku\nOtmena = Otmena",
        "summary_source": "Istochnik: {}",
        "summary_mode": "Rezhim: {}",
        "summary_pages": "Sohraneno stranits: {}",
        "summary_chunks": "Sohraneno chunkov: {}",
        "summary_final_audio": "Finalnoe audio: {}",
        "yes": "da",
        "no": "net",
        "recent_empty": "Пока нет недавних проектов.",
        "recent_load": "Загрузить",
        "recent_open": "Открыть",
        "recent_source": "Источник: {}",
        "recent_output": "Вывод: {}",
        "recent_status_configured": "Настроено",
        "recent_status_in_progress": "Не завершено",
        "recent_status_completed": "Завершено",
    },
    "uk": {
        "import_zip_button": "⬆ Import ZIP (config + Piper)",
        "export_zip_button": "⬇ Export ZIP (config + output)",
        "import_zip_title": "Import ZIP",
        "export_zip_title": "Export ZIP",
        "import_zip_success_title": "Import ZIP",
        "export_zip_success_title": "Export ZIP",
        "import_zip_success": "Importovano config: {}\nImportovano failiv Piper: {}",
        "export_zip_success": "Eksportovano failiv: {}",
        "import_zip_error_title": "Pomylka importu ZIP",
        "export_zip_error_title": "Pomylka eksportu ZIP",
        "zip_missing": "ZIP ne mistyt config.json abo fayliv modeli Piper",
        "zip_nothing_to_export": "Nemaie failiv dlya eksportu",
        "resume_title": "Vidnovyty poperednye zavdannya",
        "resume_message": "U vybranij tektsi vyvodu znaydeno zberezhenyj progres dlya tsogo zavdannya.\n\n{}\n\nTak = Vidnovyty\nNi = Pochaty znovu\nSkasuvaty = Skasuvaty",
        "overwrite_title": "Teku vyvodu uzhe vykorystano",
        "overwrite_message": "Vybrana teka vyvodu mistyt inshe zavdannya.\n\n{}\n\nTak = Perekryty stare zavdannya u tsiy teci\nNi = Skasuvaty i vybraty inshu teku\nSkasuvaty = Skasuvaty",
        "summary_source": "Dzherelo: {}",
        "summary_mode": "Rezhym: {}",
        "summary_pages": "Zberezheno storinok: {}",
        "summary_chunks": "Zberezheno chunkiv: {}",
        "summary_final_audio": "Finalne audio: {}",
        "yes": "tak",
        "no": "ni",
        "recent_empty": "Поки немає останніх проєктів.",
        "recent_load": "Завантажити",
        "recent_open": "Відкрити",
        "recent_source": "Джерело: {}",
        "recent_output": "Вивід: {}",
        "recent_status_configured": "Налаштовано",
        "recent_status_in_progress": "Не завершено",
        "recent_status_completed": "Завершено",
    },
    "tr": {
        "import_zip_button": "⬆ ZIP Ice Aktar (config + Piper)",
        "export_zip_button": "⬇ ZIP Disa Aktar (config + output)",
        "import_zip_title": "ZIP Ice Aktar",
        "export_zip_title": "ZIP Disa Aktar",
        "import_zip_success_title": "ZIP Ice Aktar",
        "export_zip_success_title": "ZIP Disa Aktar",
        "import_zip_success": "Ice aktarilan config: {}\nIce aktarilan Piper dosyalari: {}",
        "export_zip_success": "Disa aktarilan dosyalar: {}",
        "import_zip_error_title": "ZIP ice aktarma hatasi",
        "export_zip_error_title": "ZIP disa aktarma hatasi",
        "zip_missing": "ZIP, config.json veya Piper model dosyalari icermiyor",
        "zip_nothing_to_export": "Disa aktarilacak dosya yok",
        "resume_title": "Onceki goreve devam et",
        "resume_message": "Secilen cikti klasorunde bu gorev icin kayitli ilerleme bulundu.\n\n{}\n\nEvet = Devam et\nHayir = Bastan basla\nIptal = Iptal",
        "overwrite_title": "Cikti klasoru zaten kullaniliyor",
        "overwrite_message": "Secilen cikti klasoru baska bir gorev iceriyor.\n\n{}\n\nEvet = Bu klasordeki eski gorevin ustune yaz\nHayir = Iptal et ve baska klasor sec\nIptal = Iptal",
        "summary_source": "Kaynak: {}",
        "summary_mode": "Mod: {}",
        "summary_pages": "Kaydedilen sayfa: {}",
        "summary_chunks": "Kaydedilen chunk: {}",
        "summary_final_audio": "Final ses: {}",
        "yes": "evet",
        "no": "hayir",
        "recent_empty": "Henüz son proje yok.",
        "recent_load": "Yükle",
        "recent_open": "Aç",
        "recent_source": "Kaynak: {}",
        "recent_output": "Çıktı: {}",
        "recent_status_configured": "Yapılandırıldı",
        "recent_status_in_progress": "Tamamlanmadı",
        "recent_status_completed": "Tamamlandı",
    },
    "pt": {
        "import_zip_button": "⬆ Importar ZIP (config + Piper)",
        "export_zip_button": "⬇ Exportar ZIP (config + saida)",
        "import_zip_title": "Importar ZIP",
        "export_zip_title": "Exportar ZIP",
        "import_zip_success_title": "Importar ZIP",
        "export_zip_success_title": "Exportar ZIP",
        "import_zip_success": "Config importada: {}\nArquivos Piper importados: {}",
        "export_zip_success": "Arquivos exportados: {}",
        "import_zip_error_title": "Erro de importacao ZIP",
        "export_zip_error_title": "Erro de exportacao ZIP",
        "zip_missing": "O ZIP nao contem config.json nem arquivos do modelo Piper",
        "zip_nothing_to_export": "Nao ha arquivos para exportar",
        "resume_title": "Retomar tarefa anterior",
        "resume_message": "Foi encontrado progresso salvo para esta tarefa na pasta de saida selecionada.\n\n{}\n\nSim = Retomar\nNao = Recomeçar\nCancelar = Cancelar",
        "overwrite_title": "A pasta de saida ja esta em uso",
        "overwrite_message": "A pasta de saida selecionada contem outra tarefa.\n\n{}\n\nSim = Sobrescrever a tarefa antiga nesta pasta\nNao = Cancelar e escolher outra pasta\nCancelar = Cancelar",
        "summary_source": "Fonte: {}",
        "summary_mode": "Modo: {}",
        "summary_pages": "Paginas salvas: {}",
        "summary_chunks": "Chunks salvos: {}",
        "summary_final_audio": "Audio final: {}",
        "yes": "sim",
        "no": "nao",
        "recent_empty": "Ainda não há projetos recentes.",
        "recent_load": "Carregar",
        "recent_open": "Abrir",
        "recent_source": "Fonte: {}",
        "recent_output": "Saída: {}",
        "recent_status_configured": "Configurado",
        "recent_status_in_progress": "Incompleto",
        "recent_status_completed": "Concluído",
    },
    "nl": {
        "import_zip_button": "⬆ ZIP importeren (config + Piper)",
        "export_zip_button": "⬇ ZIP exporteren (config + output)",
        "import_zip_title": "ZIP importeren",
        "export_zip_title": "ZIP exporteren",
        "import_zip_success_title": "ZIP importeren",
        "export_zip_success_title": "ZIP exporteren",
        "import_zip_success": "Geimporteerde config: {}\nGeimporteerde Piper-bestanden: {}",
        "export_zip_success": "Geexporteerde bestanden: {}",
        "import_zip_error_title": "ZIP-importfout",
        "export_zip_error_title": "ZIP-exportfout",
        "zip_missing": "ZIP bevat geen config.json of Piper-modelbestanden",
        "zip_nothing_to_export": "Geen bestanden om te exporteren",
        "resume_title": "Vorige taak hervatten",
        "resume_message": "Er is opgeslagen voortgang voor deze taak gevonden in de geselecteerde uitvoermap.\n\n{}\n\nJa = Hervatten\nNee = Opnieuw beginnen\nAnnuleren = Annuleren",
        "overwrite_title": "Uitvoermap wordt al gebruikt",
        "overwrite_message": "De geselecteerde uitvoermap bevat een andere taak.\n\n{}\n\nJa = Oude taak in deze map overschrijven\nNee = Annuleren en andere map kiezen\nAnnuleren = Annuleren",
        "summary_source": "Bron: {}",
        "summary_mode": "Modus: {}",
        "summary_pages": "Opgeslagen pagina's: {}",
        "summary_chunks": "Opgeslagen chunks: {}",
        "summary_final_audio": "Definitieve audio: {}",
        "yes": "ja",
        "no": "nee",
        "recent_empty": "Nog geen recente projecten.",
        "recent_load": "Laden",
        "recent_open": "Openen",
        "recent_source": "Bron: {}",
        "recent_output": "Uitvoer: {}",
        "recent_status_configured": "Geconfigureerd",
        "recent_status_in_progress": "Onvoltooid",
        "recent_status_completed": "Voltooid",
    },
    "sv": {
        "import_zip_button": "⬆ Importera ZIP (config + Piper)",
        "export_zip_button": "⬇ Exportera ZIP (config + output)",
        "import_zip_title": "Importera ZIP",
        "export_zip_title": "Exportera ZIP",
        "import_zip_success_title": "Importera ZIP",
        "export_zip_success_title": "Exportera ZIP",
        "import_zip_success": "Importerad config: {}\nImporterade Piper-filer: {}",
        "export_zip_success": "Exporterade filer: {}",
        "import_zip_error_title": "ZIP-importfel",
        "export_zip_error_title": "ZIP-exportfel",
        "zip_missing": "ZIP innehaller inte config.json eller Piper-modellfiler",
        "zip_nothing_to_export": "Inga filer att exportera",
        "resume_title": "Ateruppta foregaende jobb",
        "resume_message": "Sparat framsteg for detta jobb hittades i den valda utdatamappen.\n\n{}\n\nJa = Ateruppta\nNej = Starta om\nAvbryt = Avbryt",
        "overwrite_title": "Utdatamappen används redan",
        "overwrite_message": "Den valda utdatamappen innehaller ett annat jobb.\n\n{}\n\nJa = Skriv over det gamla jobbet i denna mapp\nNej = Avbryt och valj en annan mapp\nAvbryt = Avbryt",
        "summary_source": "Kalla: {}",
        "summary_mode": "Lage: {}",
        "summary_pages": "Sparade sidor: {}",
        "summary_chunks": "Sparade chunkar: {}",
        "summary_final_audio": "Slutligt ljud: {}",
        "yes": "ja",
        "no": "nej",
        "recent_empty": "Inga senaste projekt ännu.",
        "recent_load": "Ladda",
        "recent_open": "Öppna",
        "recent_source": "Källa: {}",
        "recent_output": "Utdata: {}",
        "recent_status_configured": "Konfigurerad",
        "recent_status_in_progress": "Ofullständig",
        "recent_status_completed": "Slutförd",
    },
    "fi": {
        "import_zip_button": "⬆ Tuo ZIP (config + Piper)",
        "export_zip_button": "⬇ Vie ZIP (config + output)",
        "import_zip_title": "Tuo ZIP",
        "export_zip_title": "Vie ZIP",
        "import_zip_success_title": "Tuo ZIP",
        "export_zip_success_title": "Vie ZIP",
        "import_zip_success": "Tuotu config: {}\nTuodut Piper-tiedostot: {}",
        "export_zip_success": "Viedyt tiedostot: {}",
        "import_zip_error_title": "ZIP-tuontivirhe",
        "export_zip_error_title": "ZIP-vientivirhe",
        "zip_missing": "ZIP ei sisalla config.json-tiedostoa tai Piper-mallitiedostoja",
        "zip_nothing_to_export": "Ei vietavia tiedostoja",
        "resume_title": "Jatka aiempaa tyota",
        "resume_message": "Valitusta tulostekansiosta loytyi tallennettu edistyminen talle tyolle.\n\n{}\n\nKyllä = Jatka\nEi = Aloita alusta\nPeruuta = Peruuta",
        "overwrite_title": "Tulostekansio on jo kaytossa",
        "overwrite_message": "Valittu tulostekansio sisaltaa toisen tyon.\n\n{}\n\nKyllä = Korvaa vanha tyo tassa kansiossa\nEi = Peruuta ja valitse toinen kansio\nPeruuta = Peruuta",
        "summary_source": "Lahde: {}",
        "summary_mode": "Tila: {}",
        "summary_pages": "Tallennetut sivut: {}",
        "summary_chunks": "Tallennetut chunkit: {}",
        "summary_final_audio": "Lopullinen audio: {}",
        "yes": "kylla",
        "no": "ei",
        "recent_empty": "Viimeisimpiä projekteja ei viela ole.",
        "recent_load": "Lataa",
        "recent_open": "Avaa",
        "recent_source": "Lahde: {}",
        "recent_output": "Tuloste: {}",
        "recent_status_configured": "Määritetty",
        "recent_status_in_progress": "Kesken",
        "recent_status_completed": "Valmis",
    },
    "da": {
        "import_zip_button": "⬆ Importer ZIP (config + Piper)",
        "export_zip_button": "⬇ Eksporter ZIP (config + output)",
        "import_zip_title": "Importer ZIP",
        "export_zip_title": "Eksporter ZIP",
        "import_zip_success_title": "Importer ZIP",
        "export_zip_success_title": "Eksporter ZIP",
        "import_zip_success": "Importeret config: {}\nImporterede Piper-filer: {}",
        "export_zip_success": "Eksporterede filer: {}",
        "import_zip_error_title": "ZIP-importfejl",
        "export_zip_error_title": "ZIP-eksportfejl",
        "zip_missing": "ZIP indeholder ikke config.json eller Piper-modelfiler",
        "zip_nothing_to_export": "Ingen filer at eksportere",
        "resume_title": "Genoptag tidligere job",
        "resume_message": "Der blev fundet gemt fremdrift for dette job i den valgte outputmappe.\n\n{}\n\nJa = Genoptag\nNej = Start forfra\nAnnuller = Annuller",
        "overwrite_title": "Outputmappen er allerede i brug",
        "overwrite_message": "Den valgte outputmappe indeholder et andet job.\n\n{}\n\nJa = Overskriv det gamle job i denne mappe\nNej = Annuller og vaelg en anden mappe\nAnnuller = Annuller",
        "summary_source": "Kilde: {}",
        "summary_mode": "Tilstand: {}",
        "summary_pages": "Gemte sider: {}",
        "summary_chunks": "Gemte chunks: {}",
        "summary_final_audio": "Endelig audio: {}",
        "yes": "ja",
        "no": "nej",
        "recent_empty": "Ingen seneste projekter endnu.",
        "recent_load": "Indlaes",
        "recent_open": "Aabn",
        "recent_source": "Kilde: {}",
        "recent_output": "Output: {}",
        "recent_status_configured": "Konfigureret",
        "recent_status_in_progress": "Ufuldstaendig",
        "recent_status_completed": "Fuldfort",
    },
    "no": {
        "import_zip_button": "⬆ Importer ZIP (config + Piper)",
        "export_zip_button": "⬇ Eksporter ZIP (config + output)",
        "import_zip_title": "Importer ZIP",
        "export_zip_title": "Eksporter ZIP",
        "import_zip_success_title": "Importer ZIP",
        "export_zip_success_title": "Eksporter ZIP",
        "import_zip_success": "Importert config: {}\nImporterte Piper-filer: {}",
        "export_zip_success": "Eksporterte filer: {}",
        "import_zip_error_title": "ZIP-importfeil",
        "export_zip_error_title": "ZIP-eksportfeil",
        "zip_missing": "ZIP inneholder ikke config.json eller Piper-modellfiler",
        "zip_nothing_to_export": "Ingen filer a eksportere",
        "resume_title": "Fortsett forrige jobb",
        "resume_message": "Det ble funnet lagret fremdrift for denne jobben i den valgte utdatamappen.\n\n{}\n\nJa = Fortsett\nNei = Start pa nytt\nAvbryt = Avbryt",
        "overwrite_title": "Utdatamappen er allerede i bruk",
        "overwrite_message": "Den valgte utdatamappen inneholder en annen jobb.\n\n{}\n\nJa = Overskriv den gamle jobben i denne mappen\nNei = Avbryt og velg en annen mappe\nAvbryt = Avbryt",
        "summary_source": "Kilde: {}",
        "summary_mode": "Modus: {}",
        "summary_pages": "Lagrede sider: {}",
        "summary_chunks": "Lagrede chunks: {}",
        "summary_final_audio": "Endelig audio: {}",
        "yes": "ja",
        "no": "nei",
        "recent_empty": "Ingen siste prosjekter ennå.",
        "recent_load": "Last inn",
        "recent_open": "Aapne",
        "recent_source": "Kilde: {}",
        "recent_output": "Utdata: {}",
        "recent_status_configured": "Konfigurert",
        "recent_status_in_progress": "Ufullfort",
        "recent_status_completed": "Fullfort",
    },
}


def run_app():
    current_lang = state.config.get("app_language", "pl")

    def sanitize_job_name(name: str) -> str:
        cleaned = re.sub(r'[<>:"/\\|?*]+', '_', name).strip().strip('.')
        return cleaned or "job"

    def get_suggested_output_dir(source_path: str) -> Path:
        source = Path(source_path) if source_path else None
        job_name = sanitize_job_name(source.stem) if source_path else "audiobook_job"
        return PROJECT_DIR / "audiobook_output" / job_name

    def resolve_output_dir(value: str) -> Path:
        candidate = Path(value) if value else PROJECT_DIR / "audiobook_output"
        return candidate if candidate.is_absolute() else PROJECT_DIR / candidate

    def summarize_existing_job(output_dir: Path) -> tuple[dict | None, str]:
        state_file = output_dir / "job_state.json"
        if not state_file.exists():
            return None, ""
        try:
            with open(state_file, "r", encoding="utf-8") as handle:
                previous_state = json.load(handle)
        except Exception:
            return None, ""

        output_file = output_dir / "output.txt"
        chunks_dir = output_dir / "chunks"
        page_count = 0
        if output_file.exists():
            try:
                page_count = output_file.read_text(encoding="utf-8").count("=== Strona")
            except Exception:
                page_count = 0
        chunk_count = len(list(chunks_dir.glob("chunk_*.mp3"))) if chunks_dir.exists() else 0
        final_exists = (output_dir / "audiobook_final.mp3").exists()
        pipeline_stats = None
        stats_file = output_dir / "pipeline_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, "r", encoding="utf-8") as handle:
                    pipeline_stats = json.load(handle)
            except Exception:
                pipeline_stats = None
        source_name = Path(previous_state.get("pdf_path") or previous_state.get("txt_path") or "").name or "unknown"
        summary_lines = [
            tr_extra('summary_source', source_name),
            tr_extra('summary_mode', previous_state.get('mode', 'unknown')),
            tr_extra('summary_pages', page_count),
            tr_extra('summary_chunks', chunk_count),
            tr_extra('summary_final_audio', tr_extra('yes') if final_exists else tr_extra('no')),
        ]
        if pipeline_stats:
            summary_lines.append(tr_extra("summary_elapsed", format_duration(pipeline_stats.get("elapsed_seconds", 0))))
            current_stage = pipeline_stats.get("current_stage") or ("done" if pipeline_stats.get("completed") else "-")
            summary_lines.append(tr_extra("summary_stage", current_stage))
        summary = "\n".join(summary_lines)
        return previous_state, summary

    def get_recent_project_status(project: dict) -> str:
        output_dir_value = project.get("output_dir") or project.get("config", {}).get("output_dir", "")
        output_dir = resolve_output_dir(output_dir_value)
        if (output_dir / "audiobook_final.mp3").exists():
            return "completed"
        if (output_dir / "job_state.json").exists():
            return "in_progress"
        return project.get("status", "configured")

    def remember_current_project(status: str | None = None):
        state.remember_recent_project(state.config, status=status)

    def persist_current_config(status: str | None = None):
        remember_current_project(status=status)
        state.save()

    def tr(key: str) -> str:
        return TRANSLATIONS.get(current_lang, TRANSLATIONS["en"]).get(key, key)

    def tr_runtime(key: str, *args) -> str:
        template = UI_RUNTIME_MESSAGES.get(current_lang, UI_RUNTIME_MESSAGES["en"]).get(
            key, UI_RUNTIME_MESSAGES["en"].get(key, key)
        )
        return template.format(*args)

    def tr_extra(key: str, *args) -> str:
        template = EXTRA_UI_TEXTS.get(current_lang, EXTRA_UI_TEXTS["en"]).get(
            key, EXTRA_UI_TEXTS["en"].get(key, key)
        )
        return template.format(*args)

    root = tk.Tk()
    root.title("AudiobookForge v1.0")
    icon_ico_path = RESOURCE_DIR / "assets" / "app_icon.ico"
    icon_png_path = RESOURCE_DIR / "assets" / "app_icon.png"
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AudiobookForge.App")
    except Exception:
        pass
    if icon_ico_path.exists():
        try:
            root.iconbitmap(str(icon_ico_path))
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

    left_container = tk.Frame(content, bg=BG, width=396)
    left_container.pack(side="left", fill="y", padx=(0, 12))
    left_container.pack_propagate(False)

    left_canvas = tk.Canvas(left_container, bg=BG, highlightthickness=0, bd=0)
    left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=left_canvas.yview)
    left_canvas.configure(yscrollcommand=left_scrollbar.set)
    left_canvas.pack(side="left", fill="both", expand=True)

    left = tk.Frame(left_canvas, bg=BG)
    left_window = left_canvas.create_window((0, 0), window=left, anchor="nw")
    section_state = state.config.setdefault("ui_sections", {})

    def update_left_scrollbar_visibility():
        bbox = left_canvas.bbox("all")
        content_height = bbox[3] - bbox[1] if bbox else 0
        visible_height = left_canvas.winfo_height()
        needs_scrollbar = content_height > visible_height + 1
        if needs_scrollbar and not left_scrollbar.winfo_ismapped():
            left_scrollbar.pack(side="right", fill="y")
        elif not needs_scrollbar and left_scrollbar.winfo_ismapped():
            left_scrollbar.pack_forget()

    def update_left_scrollregion(_event=None):
        left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        root.after_idle(update_left_scrollbar_visibility)

    def update_left_width(event):
        left_canvas.itemconfigure(left_window, width=event.width)
        root.after_idle(update_left_scrollbar_visibility)

    def on_left_mousewheel(event):
        left_canvas.yview_scroll(int(-event.delta / 120), "units")

    def bind_left_mousewheel(_event):
        left_canvas.bind_all("<MouseWheel>", on_left_mousewheel)

    def unbind_left_mousewheel(_event):
        left_canvas.unbind_all("<MouseWheel>")

    left.bind("<Configure>", update_left_scrollregion)
    left_canvas.bind("<Configure>", update_left_width)
    left.bind("<Enter>", bind_left_mousewheel)
    left.bind("<Leave>", unbind_left_mousewheel)
    left_canvas.bind("<Enter>", bind_left_mousewheel)
    left_canvas.bind("<Leave>", unbind_left_mousewheel)

    def create_collapsible_section(parent, section_id: str, title: str):
        outer = tk.Frame(parent, bg=BG, bd=1, relief="solid")
        title_var = tk.StringVar()
        body = tk.Frame(outer, bg=BG)

        def apply_state(save_state: bool = False):
            expanded = section_state.get(section_id, True)
            title_var.set(f"{'▼' if expanded else '▶'} {title}")
            if expanded:
                body.pack(fill="x", padx=0, pady=0)
            else:
                body.pack_forget()
            if save_state:
                state.save()
            root.after_idle(update_left_scrollregion)

        def toggle():
            section_state[section_id] = not section_state.get(section_id, True)
            apply_state(save_state=True)

        header = tk.Button(
            outer,
            textvariable=title_var,
            bg=BG2,
            fg=ACCENT,
            font=FONT,
            relief="flat",
            anchor="w",
            cursor="hand2",
            activebackground=BG2,
            activeforeground=ACCENT,
            command=toggle,
        )
        header.pack(fill="x", padx=1, pady=1)
        apply_state()
        return outer, body

    right = tk.Frame(content, bg=BG)
    right.pack(side="left", fill="both", expand=True)

    mode_section, mode_frame = create_collapsible_section(left, "work_mode", tr("work_mode"))
    mode_section.pack(fill="x", pady=(0, 8))

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

    files_section, files_frame = create_collapsible_section(left, "source_files", tr("source_files"))
    files_section.pack(fill="x", pady=(0, 8))

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
                suggested_output_dir = str(get_suggested_output_dir(path))
                state.config["output_dir"] = suggested_output_dir
                source_var.set(path)
                output_dir_var.set(suggested_output_dir)
        else:
            path = filedialog.askopenfilename(
                title=tr("pdf_file"),
                filetypes=[("pdf files", "*.pdf")],
            )
            if path:
                state.config["pdf_path"] = path
                source_var.set(path)
                suggested_output_dir = str(get_suggested_output_dir(path))
                state.config["output_dir"] = suggested_output_dir
                output_dir_var.set(suggested_output_dir)

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

    if not state.config.get("output_dir"):
        initial_source_path = state.config.get("txt_path") if mode_var.get() == "txt_to_audio" else state.config.get("pdf_path")
        if initial_source_path:
            output_dir_var.set(str(get_suggested_output_dir(initial_source_path)))

    recent_section, recent_frame = create_collapsible_section(left, "recent_projects", tr("recent_projects"))
    recent_section.pack(fill="x", pady=(0, 8))

    def update_source_config(*_):
        current_path = source_var.get().strip()
        if mode_var.get() == "txt_to_audio":
            state.config["txt_path"] = current_path
        else:
            state.config["pdf_path"] = current_path

    source_var.trace_add("write", update_source_config)

    lang_section, lang_frame = create_collapsible_section(left, "pdf_settings", tr("pdf_settings"))
    lang_section.pack(fill="x", pady=(0, 8))

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

    extraction_section, extraction_frame = create_collapsible_section(left, "text_extraction", tr("text_extraction"))
    extraction_section.pack(fill="x", pady=(0, 8))

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

    tts_section, tts_frame = create_collapsible_section(left, "tts", tr("tts"))
    tts_section.pack(fill="x", pady=(0, 8))

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
    voice_var = tk.StringVar(value=state.config.get("piper_voice", ""))
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
            voice_var.set("")
            state.config.update(piper_voice="")
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

    speaker_sample_frame = tk.Frame(tts_frame, bg=BG)
    speaker_wav_var = make_path_row(speaker_sample_frame, tr("speaker_sample"), "speaker_wav", "wav")

    tts_visibility_widgets = {}

    def update_tts_voice_visibility(*_):
        provider = tts_var.get()
        piper_voice_frame.pack_forget()
        edge_voice_frame.pack_forget()
        piper_download_frame.pack_forget()
        speaker_sample_frame.pack_forget()
        download_button = tts_visibility_widgets.get("download_piper_btn")
        if download_button:
            download_button.pack_forget()
        if provider == "piper":
            piper_voice_frame.pack(fill="x")
            piper_download_frame.pack(fill="x")
            if download_button:
                download_button.pack(fill="x", pady=2)
        elif provider == "edge_tts":
            edge_voice_frame.pack(fill="x")
        elif provider == "chatterbox":
            speaker_sample_frame.pack(fill="x")

    tts_var.trace_add("write", update_tts_voice_visibility)

    llm_section, llm_frame = create_collapsible_section(left, "llm", tr("llm"))
    llm_section.pack(fill="x", pady=(0, 8))

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

        lang_section.pack_forget()
        extraction_section.pack_forget()
        llm_section.pack_forget()
        target_lang_frame.pack_forget()

        if mode == "txt_to_audio":
            root.after_idle(update_left_scrollregion)
            return
        if mode == "pdf_to_audio":
            lang_section.pack(fill="x", pady=(0, 8), before=tts_section)
            extraction_section.pack(fill="x", pady=(0, 8), before=tts_section)
            root.after_idle(update_left_scrollregion)
            return

        lang_section.pack(fill="x", pady=(0, 8), before=tts_section)
        target_lang_frame.pack(fill="x")
        extraction_section.pack(fill="x", pady=(0, 8), before=tts_section)
        llm_section.pack(fill="x", pady=(0, 8), before=btn_frame)
        root.after_idle(update_left_scrollregion)

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

    def open_output_folder(output_path: str | Path | None = None):
        import subprocess

        output = resolve_output_dir(str(output_path) if output_path else state.config.get("output_dir", ""))
        output.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{output}"')

    def load_recent_project(project: dict):
        saved_config = dict(project.get("config") or {})
        if not saved_config:
            return

        for key, value in saved_config.items():
            state.config[key] = value

        mode_var.set(saved_config.get("mode", "pdf_to_audio"))
        output_dir_var.set(saved_config.get("output_dir", ""))
        lang_var.set(saved_config.get("pdf_language", "pol"))
        target_lang_var.set(saved_config.get("target_language", "pol"))
        ocr_var.set(saved_config.get("extraction_mode", "pypdfium"))
        tts_var.set(saved_config.get("tts_provider", "piper"))
        voice_var.set(saved_config.get("piper_voice", state.config.get("piper_voice", "")))
        edge_voice_var.set(saved_config.get("edge_voice", "pl-PL-ZofiaNeural"))
        piper_preset_var.set(saved_config.get("piper_download_preset", "pl_PL-gosia-medium"))
        speaker_wav_var.set(saved_config.get("speaker_wav", ""))
        llm_provider_var.set(saved_config.get("llm_provider", "lmstudio"))
        url_var.set(saved_config.get("llm_url", LLM_URLS.get(saved_config.get("llm_provider", "lmstudio"), "")))
        model_var.set(saved_config.get("llm_model", ""))

        if saved_config.get("mode") == "txt_to_audio":
            source_var.set(saved_config.get("txt_path", ""))
        else:
            source_var.set(saved_config.get("pdf_path", ""))

        persist_current_config(status=get_recent_project_status(project))
        render_recent_projects()

    def render_recent_projects():
        for child in recent_frame.winfo_children():
            child.destroy()

        projects = state.config.get("recent_projects", [])
        if not projects:
            tk.Label(
                recent_frame,
                text=tr_extra("recent_empty"),
                bg=BG,
                fg=FG_MUTED,
                font=FONT,
                anchor="w",
                justify="left",
            ).pack(fill="x", padx=8, pady=8)
            root.after_idle(update_left_scrollregion)
            return

        status_labels = {
            "configured": tr_extra("recent_status_configured"),
            "in_progress": tr_extra("recent_status_in_progress"),
            "completed": tr_extra("recent_status_completed"),
        }

        for project in projects:
            project_status = get_recent_project_status(project)
            source_path = project.get("source_path") or project.get("config", {}).get("txt_path") or project.get("config", {}).get("pdf_path") or ""
            source_name = Path(source_path).name if source_path else project.get("name", "project")
            output_dir = project.get("output_dir") or project.get("config", {}).get("output_dir", "")

            card = tk.Frame(recent_frame, bg=BG2, bd=1, relief="solid")
            card.pack(fill="x", padx=8, pady=(6, 0))

            header = tk.Frame(card, bg=BG2)
            header.pack(fill="x", padx=8, pady=(8, 2))
            tk.Label(
                header,
                text=source_name,
                bg=BG2,
                fg=FG,
                font=FONT_TITLE,
                anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Label(
                header,
                text=status_labels.get(project_status, project_status),
                bg=BG2,
                fg=YELLOW if project_status == "in_progress" else (GREEN if project_status == "completed" else FG_MUTED),
                font=FONT,
                anchor="e",
            ).pack(side="right")

            tk.Label(
                card,
                text=tr_extra("recent_source", source_path or source_name),
                bg=BG2,
                fg=FG_MUTED,
                font=FONT,
                anchor="w",
                justify="left",
                wraplength=330,
            ).pack(fill="x", padx=8)
            tk.Label(
                card,
                text=tr_extra("recent_output", output_dir or "-"),
                bg=BG2,
                fg=FG_MUTED,
                font=FONT,
                anchor="w",
                justify="left",
                wraplength=330,
            ).pack(fill="x", padx=8, pady=(0, 6))

            actions = tk.Frame(card, bg=BG2)
            actions.pack(fill="x", padx=8, pady=(0, 8))
            tk.Button(
                actions,
                text=tr_extra("recent_load"),
                bg=BG,
                fg=ACCENT,
                font=FONT,
                relief="flat",
                cursor="hand2",
                command=lambda item=project: load_recent_project(item),
            ).pack(side="left")
            tk.Button(
                actions,
                text=tr_extra("recent_open"),
                bg=BG,
                fg=FG,
                font=FONT,
                relief="flat",
                cursor="hand2",
                command=lambda output=output_dir: open_output_folder(output),
            ).pack(side="left", padx=(6, 0))

        root.after_idle(update_left_scrollregion)

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

    def import_zip_bundle():
        zip_path = filedialog.askopenfilename(
            title=tr_extra("import_zip_title"),
            filetypes=[("ZIP files", "*.zip")],
        )
        if not zip_path:
            return

        try:
            with zipfile.ZipFile(zip_path, "r") as archive:
                members = [name for name in archive.namelist() if not name.endswith("/")]
                config_member = next(
                    (
                        name for name in sorted(members, key=len)
                        if Path(name).name.lower() == "config.json"
                    ),
                    None,
                )
                model_members = [
                    name for name in members
                    if name.lower().endswith(".onnx") or name.lower().endswith(".onnx.json")
                ]
                output_members = [
                    name for name in members
                    if name.startswith("output/") and not name.endswith("/")
                ]

                imported_config = None
                if config_member:
                    imported_config = json.loads(archive.read(config_member).decode("utf-8"))

                if imported_config is None and not model_members and not output_members:
                    raise Exception(tr_extra("zip_missing"))

                models_dir = PROJECT_DIR / "piper_models"
                models_dir.mkdir(exist_ok=True)
                imported_models = 0
                for member in model_members:
                    destination = models_dir / Path(member).name
                    destination.write_bytes(archive.read(member))
                    imported_models += 1

                if imported_config:
                    state.config.update(imported_config)
                    state.config.setdefault(
                        "ui_sections",
                        {
                            "work_mode": True,
                            "source_files": True,
                            "recent_projects": True,
                            "pdf_settings": True,
                            "text_extraction": True,
                            "tts": True,
                            "llm": True,
                        },
                    )
                    persist_current_config(status=get_recent_project_status(state.config))

                imported_output_files = 0
                if output_members:
                    import_output_dir = resolve_output_dir(state.config.get("output_dir", ""))
                    import_output_dir.mkdir(parents=True, exist_ok=True)
                    for member in output_members:
                        relative_output = Path(member).relative_to("output")
                        destination = import_output_dir / relative_output
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(archive.read(member))
                        imported_output_files += 1

                messagebox.showinfo(
                    tr_extra("import_zip_success_title"),
                    tr_extra(
                        "import_zip_success",
                        tr_extra("yes") if imported_config else tr_extra("no"),
                        imported_models + imported_output_files,
                    ),
                )
                root.after(50, lambda: (root.destroy(), run_app()))
        except Exception as exc:
            messagebox.showerror(tr_extra("import_zip_error_title"), str(exc))

    def export_zip_bundle():
        state.save()
        suggested_name = sanitize_job_name(Path(state.config.get("pdf_path") or state.config.get("txt_path") or "AudiobookForge").stem)
        zip_path = filedialog.asksaveasfilename(
            title=tr_extra("export_zip_title"),
            defaultextension=".zip",
            initialfile=f"{suggested_name}_bundle.zip",
            filetypes=[("ZIP files", "*.zip")],
        )
        if not zip_path:
            return

        output_dir = resolve_output_dir(state.config.get("output_dir", ""))
        export_entries = []

        if CONFIG_PATH.exists():
            export_entries.append((CONFIG_PATH, Path("config.json")))

        models_dir = PROJECT_DIR / "piper_models"
        if models_dir.exists():
            for model_path in sorted(models_dir.glob("*.onnx*")):
                export_entries.append((model_path, Path("piper_models") / model_path.name))

        for output_name in [
            "output.txt",
            "audiobook_final.mp3",
            "output_przetlumaczony.pdf",
            "pipeline_stats.json",
            "job_state.json",
            "tts_state.json",
        ]:
            candidate = output_dir / output_name
            if candidate.exists():
                export_entries.append((candidate, Path("output") / candidate.name))

        if not export_entries:
            messagebox.showerror(tr_extra("export_zip_error_title"), tr_extra("zip_nothing_to_export"))
            return

        try:
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for source_path, archive_name in export_entries:
                    archive.write(source_path, archive_name.as_posix())
            messagebox.showinfo(
                tr_extra("export_zip_success_title"),
                tr_extra("export_zip_success", len(export_entries)),
            )
        except Exception as exc:
            messagebox.showerror(tr_extra("export_zip_error_title"), str(exc))

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
        command=lambda: (persist_current_config(status=get_recent_project_status(state.config)), render_recent_projects(), log(tr_runtime("config_saved"))),
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text=tr_extra("export_zip_button"),
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=export_zip_bundle,
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text=tr_extra("import_zip_button"),
        bg=BG2,
        fg=ACCENT,
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=import_zip_bundle,
    ).pack(fill="x", pady=2)

    download_piper_btn = tk.Button(
        btn_frame,
        text=tr("download_piper"),
        bg="#0d2818",
        fg="#3fb950",
        font=FONT,
        relief="flat",
        cursor="hand2",
        command=install_piper_model,
    )
    tts_visibility_widgets["download_piper_btn"] = download_piper_btn

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
    timing_var = tk.StringVar(value="Elapsed: 00:00 | ETA: --:-- | Avg: --")
    tk.Label(status_frame, textvariable=timing_var, bg=BG2, fg=FG_MUTED, font=FONT_MONO).pack(padx=12, pady=(4, 0))
    stats_var = tk.StringVar(value="")
    tk.Label(status_frame, textvariable=stats_var, bg=BG2, fg=FG_MUTED, font=FONT_MONO).pack(padx=12, pady=(4, 0))

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
        if threading.current_thread() is not threading.main_thread():
            root.after(0, lambda value=msg: log(value))
            return
        state.logs.append(msg)
        console.configure(state="normal")
        console.insert("end", msg + "\n")
        console.see("end")
        console.configure(state="disabled")

    def format_duration(seconds: float) -> str:
        total_seconds = max(0, int(seconds))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def summarize_stage_stats(stats: dict) -> str:
        if not stats:
            return ""
        current_stage = stats.get("current_stage") or ("done" if stats.get("completed") else "-")
        return (
            f"Stage: {current_stage} | "
            f"Pages: {stats.get('page_count', 0)} | "
            f"Chunks: {stats.get('chunk_count', 0)} | "
            f"Elapsed: {format_duration(stats.get('elapsed_seconds', 0))}"
        )

    def log_stage_stats(stats: dict):
        if not stats:
            return
        stage_parts = []
        for stage_name, stage_stats in stats.get("stages", {}).items():
            if stage_stats.get("status") == "skipped":
                continue
            stage_parts.append(
                f"{stage_name}={stage_stats.get('status')}:{format_duration(stage_stats.get('elapsed_seconds', 0))}"
            )
        if stage_parts:
            log("Stage stats: " + " | ".join(stage_parts))

    progress_state = {"started_at": None, "stages": {}}

    def progress_cb(stage: str, current: int, total: int):
        if threading.current_thread() is not threading.main_thread():
            root.after(0, lambda s=stage, c=current, t=total: progress_cb(s, c, t))
            return
        pct = int(current / total * 100) if total > 0 else 0
        if stage in prog_vars:
            prog_vars[stage].set(pct)
        if stage in pct_labels:
            pct_labels[stage].config(text=f"{pct}%")
        if progress_state["started_at"] is None or total <= 0 or current <= 0:
            return
        now = time.time()
        stage_state = progress_state["stages"].setdefault(
            stage,
            {
                "started_at": now,
                "last_time": now,
                "last_current": current,
                "avg_item_seconds": None,
            },
        )
        if current > stage_state["last_current"]:
            delta_items = current - stage_state["last_current"]
            delta_time = max(0.0, now - stage_state["last_time"])
            sample_avg = delta_time / delta_items if delta_items else 0.0
            if stage_state["avg_item_seconds"] is None:
                stage_state["avg_item_seconds"] = sample_avg
            else:
                stage_state["avg_item_seconds"] = (stage_state["avg_item_seconds"] * 0.7) + (sample_avg * 0.3)
            stage_state["last_time"] = now
            stage_state["last_current"] = current

        elapsed = time.time() - progress_state["started_at"]
        stage_elapsed = time.time() - stage_state["started_at"]
        remaining = max(0, total - current)
        avg_item_seconds = stage_state["avg_item_seconds"]
        if avg_item_seconds is None and current > 0:
            avg_item_seconds = stage_elapsed / current
        eta = avg_item_seconds * remaining if avg_item_seconds is not None else None
        avg_text = f"{avg_item_seconds:.1f}s/item" if avg_item_seconds is not None else "--"
        eta_text = format_duration(eta) if eta is not None and remaining else ("00:00" if remaining == 0 else "--:--")
        timing_var.set(f"Elapsed: {format_duration(elapsed)} | ETA: {eta_text} | Avg: {avg_text}")

    def start_pipeline():
        if state.running:
            return
        state.running = True
        state.reset_events()
        output_dir = resolve_output_dir(state.config.get("output_dir", ""))
        state.config["output_dir"] = str(output_dir)

        previous_state, existing_job_summary = summarize_existing_job(output_dir)
        current_state = build_job_signature(state.config)
        start_action = "resume"

        if previous_state:
            same_job = previous_state == current_state
            if same_job:
                choice = messagebox.askyesnocancel(
                    tr_extra("resume_title"),
                    tr_extra("resume_message", existing_job_summary),
                )
                if choice is None:
                    state.running = False
                    status_var.set(tr_runtime("status_ready"))
                    return
                start_action = "resume" if choice else "overwrite"
            else:
                choice = messagebox.askyesnocancel(
                    tr_extra("overwrite_title"),
                    tr_extra("overwrite_message", existing_job_summary),
                )
                if not choice:
                    state.running = False
                    status_var.set(tr_runtime("status_ready"))
                    return
                start_action = "overwrite"

        state.config["_job_start_action"] = start_action
        persist_current_config(status="in_progress")
        render_recent_projects()
        progress_state["started_at"] = time.time()
        progress_state["stages"] = {}

        status_var.set(tr_runtime("status_running"))
        timing_var.set("Elapsed: 00:00 | ETA: --:-- | Avg: --")
        stats_var.set("")
        console.configure(state="normal")
        console.delete("1.0", "end")
        console.configure(state="disabled")
        for v in prog_vars.values():
            v.set(0)

        def run():
            try:
                result = run_pipeline(state.config, log, progress_cb, state.pause_event, state.stop_event)
                stats = result.get("stats", {}) if isinstance(result, dict) else {}
                elapsed_seconds = stats.get("elapsed_seconds", time.time() - progress_state["started_at"])
                stopped = isinstance(result, dict) and result.get("stopped")
                root.after(0, lambda: status_var.set(tr_runtime("status_stopped") if stopped else tr_runtime("status_completed")))
                root.after(0, lambda: timing_var.set(f"Elapsed: {format_duration(elapsed_seconds)} | ETA: 00:00 | Avg: done"))
                root.after(0, lambda: stats_var.set(summarize_stage_stats(stats)))
                persist_current_config(status="in_progress" if stopped else "completed")
                root.after(0, render_recent_projects)
                log(tr_runtime("stopped") if stopped else tr_runtime("done"))
                if stats:
                    log(
                        "Stats: "
                        f"time={format_duration(stats.get('elapsed_seconds', 0))} | "
                        f"pages={stats.get('page_count', 0)} | "
                        f"chunks={stats.get('chunk_count', 0)} | "
                        f"chars={stats.get('character_count', 0)} | "
                        f"est_tokens={stats.get('estimated_tokens', 0)}"
                    )
                    log_stage_stats(stats)
            except Exception as e:
                persist_current_config(status="in_progress")
                root.after(0, render_recent_projects)
                log(tr_runtime("error", e))
                log(traceback.format_exc())
                root.after(0, lambda: status_var.set(tr_runtime("status_error")))
            finally:
                state.config.pop("_job_start_action", None)
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

    start_btn.config(command=start_pipeline)
    pause_btn.config(command=pause_pipeline)
    stop_btn.config(command=stop_pipeline)
    open_btn.config(command=open_output_folder)

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
    render_recent_projects()
    root.after_idle(update_left_scrollregion)

    log(tr_runtime("app_ready"))
    root.mainloop()
