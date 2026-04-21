# AudiobookForge

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)

AudiobookForge is a Python `tkinter` desktop application for converting PDFs and text files into audiobooks. It combines direct PDF extraction via `pypdfium2`, fallback LLM Vision OCR for difficult scans, and TTS generation with Piper or Edge TTS, with multilingual UI and built-in Piper model download support.

Open-source desktop tooling for local-first audiobook generation from PDFs and TXT files.

## Project Highlights

- `PDF -> Audio`, `PDF -> Translation -> Audio`, `PDF -> Translation -> TXT`, `TXT -> Audio`
- `pypdfium2` rendering and extraction without Poppler
- `LLM Vision OCR` fallback for scanned or badly encoded PDFs
- `Piper`, `Edge TTS`, `Chatterbox`, `OpenAI TTS`, `ElevenLabs`
- multilingual desktop UI with runtime language switching
- current UI languages: Polish, Czech, Romanian, Hungarian, English, German, French, Spanish, Italian, Russian, Ukrainian, Turkish, Portuguese, Dutch, Swedish, Finnish, Danish, Norwegian
- built-in Piper model download workflow
- robust handling of legacy PDFs with broken encoding and OCR fallback

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Requirements:
- Python `3.10+`
- `ffmpeg` in `PATH`
- optional `LM Studio` for local OCR/translation workflows

## Choosing A Mode / Provider

- `PDF -> Audio`: best when you want the source language spoken back without translation.
- `PDF -> Translation -> Audio`: use for full OCR/translation plus audiobook output.
- `PDF -> Translation -> TXT`: use when you only want the translated `output.txt` for later editing or reuse.
- `TXT -> Audio`: fastest resume path when `output.txt` already exists and you only need TTS/merge again.
- `Piper`: offline and privacy-friendly, but requires a downloaded `.onnx` voice model.
- `Edge TTS`: easiest voice setup and usually better naturalness, but requires network access.
- `pypdfium2`: first choice for normal text PDFs.
- `LLM Vision OCR`: fallback for scans, image PDFs, or broken encodings; slower and depends on a vision-capable model.

Resume / progress notes:

- each output folder stores `job_state.json`, `tts_state.json`, and `pipeline_stats.json`
- rerunning the same job in the same output folder can resume from saved pages/chunks
- changing TTS voice/provider clears stale audio chunks so resumed audio stays consistent

## Screenshot

![AudiobookForge screenshot](docs/screenshot.png)

## Build / Packaging

Release artifacts:

- `release\AudiobookForgeSetup.exe` - Windows installer for the faster `onedir` build
- `dist\AudiobookForge.exe` - portable single-file build

Build helper scripts:

- `build_release.bat` - builds the portable `onefile` executable
- `build_folder.bat` - builds the faster `onedir` folder version
- `build_installer.bat` - builds the `onedir` version and then compiles the installer with Inno Setup 6

PyInstaller spec files:

- `AudiobookForge.spec` - `onefile` build config
- `AudiobookForge_onedir.spec` - `onedir` build config

Installer config:

- `AudiobookForge.iss` - Inno Setup script used to create `AudiobookForgeSetup.exe`

Portable build:

```bash
build_release.bat
```

Folder build:

```bash
build_folder.bat
```

Installer build:

```bash
build_installer.bat
```

Requirements for installer build:

- Inno Setup 6 installed
- `ISCC.exe` available in `PATH`, or installed in the default Inno Setup folder
- installer languages include English, Polish, Czech, Hungarian, Finnish, Danish, Norwegian, German, French, Spanish, Italian, Russian, Ukrainian, Turkish, Portuguese, Dutch, and Swedish

Manual PyInstaller example:

```bash
pip install pyinstaller
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

Notes:
- `--onedir` is the preferred mode for this project
- `--onefile` may be problematic with `piper-tts` and `pypdfium2`
- bundle `ffmpeg` separately or ensure it is available in `PATH`
- if you use `icon.ico`, add `--icon=icon.ico`

Repository hygiene:
- generated assets such as `piper_models/`, `audiobook_output/`, `pages/`, `chunks/`, `dist/`, and `build/` are ignored via `.gitignore`
- generated installer output in `release/` is ignored via `.gitignore`
- `config.json` is intentionally ignored to keep machine-local settings out of version control

## Known Limitations

- difficult scanned PDFs still depend on a working Vision-capable LLM endpoint
- OCR quality depends on source quality and selected model quality
- some legacy PDFs may still require OCR fallback even after direct extraction and encoding fixes
- `Edge TTS` requires network access
- `Piper` requires downloaded `.onnx` models and available disk space
- `PyInstaller --onefile` is not recommended for this stack

## Architecture

High-level architecture notes are available here:

- [`docs/architecture.md`](docs/architecture.md)

## Table of Contents

- [Project Highlights](#project-highlights)
- [Quick Start](#quick-start)
- [Screenshot](#screenshot)
- [Build / Packaging](#build--packaging)
- [Known Limitations](#known-limitations)
- [Architecture](#architecture)
- [Polski](#polski)
- [English](#english)
- [Deutsch](#deutsch)
- [Русский](#русский)
- [Українська](#українська)
- [Čeština](#čeština)
- [Français](#français)
- [Español](#español)
- [Italiano](#italiano)
- [Türkçe](#türkçe)

---

## Polski

### Spis treści

- [Funkcje](#pl-features)
- [Wymagania](#pl-requirements)
- [Instalacja](#pl-installation)
- [Użytkowanie](#pl-usage)
- [Konfiguracja](#pl-configuration)
- [Dostawcy TTS](#pl-tts-providers)
- [Obsługiwane języki](#pl-supported-languages)
- [Contributing](#pl-contributing)
- [Licencja](#pl-license)

<a id="pl-features"></a>
### Features

- Desktopowa aplikacja Python `tkinter` do konwersji `PDF -> audiobook` oraz `TXT -> audiobook`.
- Tryby pracy: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Szybka ekstrakcja tekstu przez `pypdfium2`, bez zależności od Popplera.
- Tryb `LLM Vision OCR` dla trudnych, skanowanych lub niestandardowych PDF-ów.
- Automatyczny retry OCR przy pustej odpowiedzi modelu.
- Obsługa starych i źle zakodowanych PDF-ów, w tym korekty problematycznych znaków.
- TTS lokalny przez `Piper` oraz sieciowy przez `Edge TTS`.
- Wielojęzyczny interfejs użytkownika.
- Pobieranie modeli Piper bezpośrednio z GUI.
- Łączenie chunków audio do końcowego pliku `audiobook_final.mp3`.

<a id="pl-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter` dostępny w instalacji Pythona
- `ffmpeg` dostępny w `PATH`
- `piper-tts`
- `pypdfium2`
- Pakiety z `requirements.txt`
- Opcjonalnie `LM Studio` lub inny zgodny endpoint OpenAI API dla Vision OCR / tłumaczenia

<a id="pl-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
```

Zainstaluj `ffmpeg` i upewnij się, że polecenie `ffmpeg` działa w terminalu.

Uruchomienie:

```bash
python app.py
```

Uwagi buildowe z `PyInstaller`:

- `--onefile` może być problematyczne przy `piper-tts` i `pypdfium2`.
- Preferowany build:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="pl-usage"></a>
### Usage

1. Wybierz tryb pracy.
2. Wskaż plik PDF lub TXT oraz folder wyjściowy.
3. Wybierz metodę ekstrakcji: szybkie `pypdfium2` albo `LLM Vision OCR`.
4. Skonfiguruj dostawcę TTS: `Piper` albo `Edge TTS`.
5. W razie potrzeby pobierz model Piper z poziomu aplikacji.
6. Uruchom pipeline i poczekaj na wygenerowanie chunków oraz finalnego MP3.

`pdf_to_audio`:
Bezpośrednia ekstrakcja tekstu z PDF i synteza audio.

`translate_to_audio`:
OCR / ekstrakcja, tłumaczenie przez model LLM, a następnie synteza audio.

`txt_to_audio`:
Wczytanie gotowego pliku `.txt` i wygenerowanie audiobooka.

<a id="pl-configuration"></a>
### Configuration

Główna konfiguracja jest przechowywana w `config.json`.

Najważniejsze pola:

- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

Uwagi techniczne:

- `pypdfium2` jest główną ścieżką ekstrakcji i renderowania stron.
- Dla trudnych stron aplikacja może przełączyć się na OCR obrazowy.
- OCR ma retry przy pustym wyniku.
- Końcowe MP3 jest składane przez `ffmpeg`.

<a id="pl-tts-providers"></a>
### TTS Providers

`Piper`
- Lokalny, offline.
- Wymaga `piper-tts` oraz modelu `.onnx`.
- Najlepszy wybór dla prywatności i pracy offline.

`Edge TTS`
- Głosy neuralne Microsoft Edge.
- Prosta konfiguracja i dobra jakość głosu.
- Wymaga połączenia sieciowego.

<a id="pl-supported-languages"></a>
### Supported Languages

Języki interfejsu:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Języki docelowe audio / tłumaczenia:
- `pol`
- `eng`
- `deu`
- `rus`
- `ukr`
- `ces`
- `fra`
- `spa`
- `ita`

Języki źródłowe PDF w UI obejmują dodatkowo m.in.:
- `slk`, `por`, `nld`, `hun`, `ron`, `bul`, `slv`, `hrv`, `srp`, `lit`, `lav`, `est`, `fin`, `swe`, `dan`, `nor`, `tur`

<a id="pl-contributing"></a>
### Contributing

Pull requesti i zgłoszenia issue są mile widziane. Warto dołączyć:

- opis scenariusza użycia
- przykładowy PDF lub TXT reprodukujący problem
- log z aplikacji
- informacje o środowisku i konfiguracji TTS / LLM

<a id="pl-license"></a>
### License

Licencja: `MIT`. Szczegóły w pliku `LICENSE`.

---

## English

### Mini TOC

- [Features](#en-features)
- [Requirements](#en-requirements)
- [Installation](#en-installation)
- [Usage](#en-usage)
- [Configuration](#en-configuration)
- [TTS Providers](#en-tts-providers)
- [Supported Languages](#en-supported-languages)
- [Contributing](#en-contributing)
- [License](#en-license)

<a id="en-features"></a>
### Features

- Python `tkinter` desktop app for `PDF -> audiobook` and `TXT -> audiobook`.
- Main modes: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Fast direct extraction with `pypdfium2`, without Poppler.
- `LLM Vision OCR` for scanned or difficult PDFs.
- OCR retry logic for empty model responses.
- Better handling of legacy or badly encoded PDFs.
- Local `Piper` TTS and cloud-based `Edge TTS`.
- Multilingual UI.
- Built-in Piper model download workflow.
- Chunk-based audio generation merged into `audiobook_final.mp3`.

<a id="en-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg` in `PATH`
- `piper-tts`
- `pypdfium2`
- Dependencies from `requirements.txt`
- Optional `LM Studio` or another OpenAI-compatible endpoint for Vision OCR / translation

<a id="en-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

PyInstaller notes:

- `--onefile` may be problematic with `piper-tts` and `pypdfium2`.
- Preferred build:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="en-usage"></a>
### Usage

1. Select a mode.
2. Choose the input PDF or TXT file and output folder.
3. Pick extraction mode: `pypdfium2` or `LLM Vision OCR`.
4. Select `Piper` or `Edge TTS`.
5. Download a Piper model if needed.
6. Run the pipeline to generate chunks and the final audiobook.

<a id="en-configuration"></a>
### Configuration

Primary settings are stored in `config.json`.

Key fields:

- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

Technical notes:

- `pypdfium2` is the primary extraction and rendering backend.
- Difficult pages can fall back to image-based OCR.
- Empty OCR responses are retried.
- Final MP3 assembly is handled by `ffmpeg`.

<a id="en-tts-providers"></a>
### TTS Providers

`Piper`
- Local and offline
- Requires `piper-tts` and a `.onnx` voice model

`Edge TTS`
- Neural cloud voices
- Easy setup, network required

<a id="en-supported-languages"></a>
### Supported Languages

UI languages:
- Polish
- English
- German
- Russian
- Ukrainian
- Czech
- Romanian
- Hungarian
- French
- Spanish
- Italian
- Turkish
- Portuguese
- Dutch
- Swedish
- Finnish
- Danish
- Norwegian

Audio / translation target languages:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

Additional PDF source language codes are available in the UI.

<a id="en-contributing"></a>
### Contributing

Issues and pull requests are welcome. Include a reproducible sample, logs, environment details, and TTS / LLM configuration when possible.

<a id="en-license"></a>
### License

License: `MIT`. See `LICENSE`.

---

## Deutsch

### Mini TOC

- [Features](#de-features)
- [Requirements](#de-requirements)
- [Installation](#de-installation)
- [Usage](#de-usage)
- [Configuration](#de-configuration)
- [TTS Providers](#de-tts-providers)
- [Supported Languages](#de-supported-languages)
- [Contributing](#de-contributing)
- [License](#de-license)

<a id="de-features"></a>
### Features

- Python-`tkinter`-Desktop-App fur `PDF -> Horbuch` und `TXT -> Horbuch`.
- Hauptmodi: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Schnelle Extraktion mit `pypdfium2`, ohne Poppler.
- `LLM Vision OCR` fur schwierige oder gescannte PDFs.
- OCR-Retries bei leeren Modellantworten.
- Bessere Verarbeitung alter oder fehlerhaft kodierter PDFs.
- `Piper` fur lokale Offline-TTS und `Edge TTS` fur Cloud-Stimmen.
- Mehrsprachige Benutzeroberflache.
- Integrierter Download von Piper-Modellen.
- Zusammenfuhrung der Audio-Chunks zu `audiobook_final.mp3`.

<a id="de-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg` in `PATH`
- `piper-tts`
- `pypdfium2`
- Abhangigkeiten aus `requirements.txt`
- Optional `LM Studio` oder kompatibler OpenAI-Endpoint

<a id="de-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

PyInstaller-Hinweis:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

`--onefile` kann mit `piper-tts` und `pypdfium2` problematisch sein.

<a id="de-usage"></a>
### Usage

1. Modus auswahlen.
2. PDF- oder TXT-Datei und Ausgabeordner festlegen.
3. Extraktion uber `pypdfium2` oder `LLM Vision OCR` auswahlen.
4. `Piper` oder `Edge TTS` konfigurieren.
5. Optional ein Piper-Modell herunterladen.
6. Pipeline starten.

<a id="de-configuration"></a>
### Configuration

Die Hauptkonfiguration liegt in `config.json`.

Wichtige Felder:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="de-tts-providers"></a>
### TTS Providers

`Piper`
- Lokal, offline
- Benotigt `piper-tts` und `.onnx`-Modell

`Edge TTS`
- Neuronale Online-Stimmen
- Netzwerk erforderlich

<a id="de-supported-languages"></a>
### Supported Languages

UI-Sprachen:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Zielsprachen fur Audio / Ubersetzung:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="de-contributing"></a>
### Contributing

Fehlermeldungen und Pull Requests sind willkommen. Reproduzierbare Beispiele und Logs helfen bei der Analyse.

<a id="de-license"></a>
### License

Lizenz: `MIT`. Siehe `LICENSE`.

---

## Русский

### Мини TOC

- [Features](#ru-features)
- [Requirements](#ru-requirements)
- [Installation](#ru-installation)
- [Usage](#ru-usage)
- [Configuration](#ru-configuration)
- [TTS Providers](#ru-tts-providers)
- [Supported Languages](#ru-supported-languages)
- [Contributing](#ru-contributing)
- [License](#ru-license)

<a id="ru-features"></a>
### Features

- Настольное приложение на Python `tkinter` для `PDF -> аудиокнига` и `TXT -> аудиокнига`.
- Основные режимы: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Быстрое извлечение текста через `pypdfium2` без Poppler.
- `LLM Vision OCR` для сложных и сканированных PDF.
- Повторные попытки OCR при пустом ответе модели.
- Обработка старых и некорректно закодированных PDF.
- Локальный `Piper` и сетевой `Edge TTS`.
- Многоязычный интерфейс.
- Загрузка моделей Piper из GUI.
- Склейка чанков в `audiobook_final.mp3`.

<a id="ru-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- зависимости из `requirements.txt`
- опционально `LM Studio`

<a id="ru-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Сборка:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

`--onefile` может создавать проблемы с `piper-tts` и `pypdfium2`.

<a id="ru-usage"></a>
### Usage

1. Выберите режим.
2. Укажите PDF или TXT и выходную папку.
3. Выберите `pypdfium2` или `LLM Vision OCR`.
4. Настройте `Piper` или `Edge TTS`.
5. При необходимости загрузите модель Piper.
6. Запустите pipeline.

<a id="ru-configuration"></a>
### Configuration

Основные настройки хранятся в `config.json`.

Ключевые поля:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="ru-tts-providers"></a>
### TTS Providers

`Piper`
- локально и офлайн
- требует `piper-tts` и модель `.onnx`

`Edge TTS`
- нейросетевые облачные голоса
- требуется сеть

<a id="ru-supported-languages"></a>
### Supported Languages

Языки интерфейса:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Языки аудио / перевода:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="ru-contributing"></a>
### Contributing

Issue и pull request приветствуются. Желательно приложить пример файла, логи и параметры среды.

<a id="ru-license"></a>
### License

Лицензия: `MIT`. См. `LICENSE`.

---

## Українська

### Міні TOC

- [Features](#uk-features)
- [Requirements](#uk-requirements)
- [Installation](#uk-installation)
- [Usage](#uk-usage)
- [Configuration](#uk-configuration)
- [TTS Providers](#uk-tts-providers)
- [Supported Languages](#uk-supported-languages)
- [Contributing](#uk-contributing)
- [License](#uk-license)

<a id="uk-features"></a>
### Features

- Настільний Python `tkinter` застосунок для `PDF -> аудіокнига` та `TXT -> аудіокнига`.
- Режими: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Швидке вилучення тексту через `pypdfium2` без Poppler.
- `LLM Vision OCR` для складних PDF та сканів.
- Retry OCR при порожній відповіді моделі.
- Краща робота зі старими або некоректно закодованими PDF.
- Локальний `Piper` і мережевий `Edge TTS`.
- Багатомовний UI.
- Завантаження моделей Piper з інтерфейсу.
- Збирання фінального `audiobook_final.mp3`.

<a id="uk-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- залежності з `requirements.txt`
- опційно `LM Studio`

<a id="uk-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Рекомендована збірка:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="uk-usage"></a>
### Usage

1. Оберіть режим.
2. Вкажіть PDF або TXT та папку виводу.
3. Оберіть `pypdfium2` або `LLM Vision OCR`.
4. Налаштуйте `Piper` чи `Edge TTS`.
5. За потреби завантажте модель Piper.
6. Запустіть обробку.

<a id="uk-configuration"></a>
### Configuration

Основні налаштування зберігаються у `config.json`.

Ключові поля:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="uk-tts-providers"></a>
### TTS Providers

`Piper`
- локально, офлайн
- потрібні `piper-tts` і модель `.onnx`

`Edge TTS`
- хмарні neural voices
- потрібне мережеве підключення

<a id="uk-supported-languages"></a>
### Supported Languages

Мови інтерфейсу:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Мови аудіо / перекладу:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="uk-contributing"></a>
### Contributing

Pull request та issue вітаються. Додавайте приклади, логи та параметри середовища.

<a id="uk-license"></a>
### License

Ліцензія: `MIT`. Див. `LICENSE`.

---

## Čeština

### Mini TOC

- [Features](#cs-features)
- [Requirements](#cs-requirements)
- [Installation](#cs-installation)
- [Usage](#cs-usage)
- [Configuration](#cs-configuration)
- [TTS Providers](#cs-tts-providers)
- [Supported Languages](#cs-supported-languages)
- [Contributing](#cs-contributing)
- [License](#cs-license)

<a id="cs-features"></a>
### Features

- Desktopova aplikace v Python `tkinter` pro `PDF -> audiokniha` a `TXT -> audiokniha`.
- Rezimy: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Rychla extrakce pres `pypdfium2` bez Poppleru.
- `LLM Vision OCR` pro slozite nebo skenovane PDF.
- Retry OCR pri prazdne odpovedi modelu.
- Lepsi prace se starymi nebo spatne kodovanymi PDF.
- Lokalni `Piper` a sitovy `Edge TTS`.
- Vicejazycne UI.
- Stahovani Piper modelu primo z aplikace.
- Slouceni chunku do `audiobook_final.mp3`.

<a id="cs-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- zavislosti z `requirements.txt`
- volitelne `LM Studio`

<a id="cs-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Preferovany build:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="cs-usage"></a>
### Usage

1. Vyberte rezim.
2. Zadejte PDF nebo TXT a vystupni slozku.
3. Zvolte `pypdfium2` nebo `LLM Vision OCR`.
4. Nastavte `Piper` nebo `Edge TTS`.
5. V pripade potreby stahnete Piper model.
6. Spustte pipeline.

<a id="cs-configuration"></a>
### Configuration

Hlavni konfigurace je v `config.json`.

Klicova pole:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="cs-tts-providers"></a>
### TTS Providers

`Piper`
- lokalni offline TTS
- vyzaduje `piper-tts` a `.onnx` model

`Edge TTS`
- cloudove neural hlasy
- vyzaduje internet

<a id="cs-supported-languages"></a>
### Supported Languages

Jazyky rozhrani:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Jazyky audia / prekladu:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="cs-contributing"></a>
### Contributing

Issue a pull requesty jsou vitany. Pomahaji ukazkove soubory, logy a popis prostredi.

<a id="cs-license"></a>
### License

Licence: `MIT`. Viz `LICENSE`.

---

## Français

### Mini TOC

- [Features](#fr-features)
- [Requirements](#fr-requirements)
- [Installation](#fr-installation)
- [Usage](#fr-usage)
- [Configuration](#fr-configuration)
- [TTS Providers](#fr-tts-providers)
- [Supported Languages](#fr-supported-languages)
- [Contributing](#fr-contributing)
- [License](#fr-license)

<a id="fr-features"></a>
### Features

- Application desktop Python `tkinter` pour `PDF -> livre audio` et `TXT -> livre audio`.
- Modes principaux: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Extraction rapide avec `pypdfium2`, sans Poppler.
- `LLM Vision OCR` pour les PDF difficiles ou scannes.
- Retry OCR en cas de reponse vide.
- Meilleure gestion des PDF anciens ou mal encodes.
- `Piper` en local et `Edge TTS` en ligne.
- Interface multilingue.
- Telechargement integre des modeles Piper.
- Fusion des chunks dans `audiobook_final.mp3`.

<a id="fr-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- dependances de `requirements.txt`
- `LM Studio` en option

<a id="fr-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Build recommande:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="fr-usage"></a>
### Usage

1. Selectionnez un mode.
2. Choisissez le PDF ou TXT et le dossier de sortie.
3. Utilisez `pypdfium2` ou `LLM Vision OCR`.
4. Configurez `Piper` ou `Edge TTS`.
5. Telechargez un modele Piper si necessaire.
6. Lancez le pipeline.

<a id="fr-configuration"></a>
### Configuration

La configuration principale est stockee dans `config.json`.

Champs importants:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="fr-tts-providers"></a>
### TTS Providers

`Piper`
- local, hors ligne
- necessite `piper-tts` et un modele `.onnx`

`Edge TTS`
- voix neural en ligne
- connexion reseau requise

<a id="fr-supported-languages"></a>
### Supported Languages

Langues de l'interface:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Langues cible audio / traduction:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="fr-contributing"></a>
### Contributing

Les issues et pull requests sont bienvenues. Fournissez si possible un exemple reproductible et les logs.

<a id="fr-license"></a>
### License

Licence : `MIT`. Voir `LICENSE`.

---

## Español

### Mini TOC

- [Features](#es-features)
- [Requirements](#es-requirements)
- [Installation](#es-installation)
- [Usage](#es-usage)
- [Configuration](#es-configuration)
- [TTS Providers](#es-tts-providers)
- [Supported Languages](#es-supported-languages)
- [Contributing](#es-contributing)
- [License](#es-license)

<a id="es-features"></a>
### Features

- Aplicacion de escritorio Python `tkinter` para `PDF -> audiolibro` y `TXT -> audiolibro`.
- Modos: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Extraccion rapida con `pypdfium2`, sin Poppler.
- `LLM Vision OCR` para PDF escaneados o dificiles.
- Retry OCR cuando el modelo devuelve respuesta vacia.
- Mejor manejo de PDF antiguos o mal codificados.
- `Piper` local y `Edge TTS` en red.
- Interfaz multilingue.
- Descarga integrada de modelos Piper.
- Union de fragmentos en `audiobook_final.mp3`.

<a id="es-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- dependencias de `requirements.txt`
- `LM Studio` opcional

<a id="es-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Build recomendado:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="es-usage"></a>
### Usage

1. Selecciona un modo.
2. Elige PDF o TXT y carpeta de salida.
3. Usa `pypdfium2` o `LLM Vision OCR`.
4. Configura `Piper` o `Edge TTS`.
5. Descarga un modelo Piper si hace falta.
6. Ejecuta el pipeline.

<a id="es-configuration"></a>
### Configuration

La configuracion principal se guarda en `config.json`.

Campos clave:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="es-tts-providers"></a>
### TTS Providers

`Piper`
- local, offline
- requiere `piper-tts` y modelo `.onnx`

`Edge TTS`
- voces neuronales online
- requiere red

<a id="es-supported-languages"></a>
### Supported Languages

Idiomas de la interfaz:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Idiomas de audio / traduccion:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="es-contributing"></a>
### Contributing

Issues y pull requests son bienvenidos. Adjunta ejemplos reproducibles, logs y detalles del entorno.

<a id="es-license"></a>
### License

Licencia: `MIT`. Ver `LICENSE`.

---

## Italiano

### Mini TOC

- [Features](#it-features)
- [Requirements](#it-requirements)
- [Installation](#it-installation)
- [Usage](#it-usage)
- [Configuration](#it-configuration)
- [TTS Providers](#it-tts-providers)
- [Supported Languages](#it-supported-languages)
- [Contributing](#it-contributing)
- [License](#it-license)

<a id="it-features"></a>
### Features

- Applicazione desktop Python `tkinter` per `PDF -> audiolibro` e `TXT -> audiolibro`.
- Modalita principali: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Estrazione rapida con `pypdfium2`, senza Poppler.
- `LLM Vision OCR` per PDF difficili o scannerizzati.
- Retry OCR in caso di risposta vuota.
- Migliore gestione di PDF legacy o con codifica problematica.
- `Piper` locale e `Edge TTS` online.
- Interfaccia multilingue.
- Download integrato dei modelli Piper.
- Merge dei chunk in `audiobook_final.mp3`.

<a id="it-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- dipendenze da `requirements.txt`
- `LM Studio` opzionale

<a id="it-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Build consigliata:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

<a id="it-usage"></a>
### Usage

1. Seleziona una modalita.
2. Scegli PDF o TXT e cartella di output.
3. Usa `pypdfium2` o `LLM Vision OCR`.
4. Configura `Piper` o `Edge TTS`.
5. Scarica un modello Piper se necessario.
6. Avvia la pipeline.

<a id="it-configuration"></a>
### Configuration

La configurazione principale e salvata in `config.json`.

Campi chiave:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="it-tts-providers"></a>
### TTS Providers

`Piper`
- locale, offline
- richiede `piper-tts` e modello `.onnx`

`Edge TTS`
- voci neurali online
- richiede rete

<a id="it-supported-languages"></a>
### Supported Languages

Lingue UI:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Lingue audio / traduzione:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="it-contributing"></a>
### Contributing

Issue e pull request sono benvenute. Utile includere file di esempio, log e dettagli dell'ambiente.

<a id="it-license"></a>
### License

Licenza: `MIT`. Vedi `LICENSE`.

---

## Türkçe

### Mini TOC

- [Features](#tr-features)
- [Requirements](#tr-requirements)
- [Installation](#tr-installation)
- [Usage](#tr-usage)
- [Configuration](#tr-configuration)
- [TTS Providers](#tr-tts-providers)
- [Supported Languages](#tr-supported-languages)
- [Contributing](#tr-contributing)
- [License](#tr-license)

<a id="tr-features"></a>
### Features

- `PDF -> sesli kitap` ve `TXT -> sesli kitap` icin Python `tkinter` masaustu uygulamasi.
- Ana modlar: `pdf_to_audio`, `translate_to_audio`, `txt_to_audio`.
- Poppler gerektirmeden `pypdfium2` ile hizli metin cikarma.
- Zor ve taranmis PDF'ler icin `LLM Vision OCR`.
- Bos model cevabinda OCR retry mantigi.
- Eski veya bozuk kodlanmis PDF'ler icin daha iyi dayaniklilik.
- Yerel `Piper` ve ag uzerinden `Edge TTS`.
- Cok dilli arayuz.
- Uygulama icinden Piper model indirme.
- Chunk birlestirme ile `audiobook_final.mp3` uretimi.

<a id="tr-requirements"></a>
### Requirements

- Python `3.10+`
- `tkinter`
- `ffmpeg`
- `piper-tts`
- `pypdfium2`
- `requirements.txt` bagimliliklari
- istege bagli `LM Studio`

<a id="tr-installation"></a>
### Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pypdfium2 piper-tts
python app.py
```

Onerilen paketleme:

```bash
pyinstaller --onedir --windowed --name AudiobookForge app.py
```

`--onefile`, `piper-tts` ve `pypdfium2` ile sorun cikarabilir.

<a id="tr-usage"></a>
### Usage

1. Mod secin.
2. PDF veya TXT dosyasi ve cikti klasoru belirleyin.
3. `pypdfium2` ya da `LLM Vision OCR` secin.
4. `Piper` veya `Edge TTS` ayarlayin.
5. Gerekirse Piper modeli indirin.
6. Pipeline'i calistirin.

<a id="tr-configuration"></a>
### Configuration

Ana ayarlar `config.json` icinde tutulur.

Temel alanlar:
- `pdf_path`
- `txt_path`
- `output_dir`
- `mode`
- `pdf_language`
- `target_language`
- `extraction_mode`
- `tts_provider`
- `piper_voice`
- `edge_voice`
- `llm_provider`
- `llm_url`
- `llm_model`
- `llm_api_key`

<a id="tr-tts-providers"></a>
### TTS Providers

`Piper`
- yerel, offline
- `piper-tts` ve `.onnx` model gerekir

`Edge TTS`
- neural bulut sesleri
- internet gerekir

<a id="tr-supported-languages"></a>
### Supported Languages

Arayuz dilleri:
- Polski
- English
- Deutsch
- Русский
- Українська
- Čeština
- Romana
- Magyar
- Français
- Español
- Italiano
- Türkçe
- Portugues
- Nederlands
- Svenska
- Suomi
- Dansk
- Norsk

Ses / ceviri hedef dilleri:
- `pol`, `eng`, `deu`, `rus`, `ukr`, `ces`, `fra`, `spa`, `ita`

<a id="tr-contributing"></a>
### Contributing

Issue ve pull request'ler memnuniyetle kabul edilir. Loglar, ornek dosyalar ve ortam bilgileri faydalidir.

<a id="tr-license"></a>
### License

Lisans: `MIT`. Bkz. `LICENSE`.
