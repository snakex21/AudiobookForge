"""Where AudiobookForge keeps program files, settings, models and output.

Installed (frozen) build:
    program files  -> install dir (read-only for users, e.g. Program Files)
    config.json    -> %APPDATA%\\AudiobookForge\\config.json
    piper models   -> %LOCALAPPDATA%\\AudiobookForge\\piper_models
    output         -> Documents\\AudiobookForge (or the folder the user picks)

Source checkout (python app.py): everything stays in the repository folder,
exactly as before, so development setups keep working unchanged.

Older installers stored config.json and audiobook_output next to the exe.
``migrate_legacy_config`` copies that config to the new location on first run.
The legacy files are never deleted.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional

APP_NAME = "AudiobookForge"
CONFIG_FILENAME = "config.json"
LEGACY_OUTPUT_DIRNAME = "audiobook_output"
MODELS_DIRNAME = "piper_models"
DATA_DIR_ENV = "AUDIOBOOKFORGE_DATA_DIR"
PATH_CONFIG_KEYS = ("pdf_path", "txt_path", "project_source_file", "speaker_wav")


@dataclass(frozen=True)
class AppPaths:
    install_dir: Path
    resource_dir: Path
    data_dir: Path
    config_path: Path
    models_dir: Path
    output_root: Path
    portable: bool

    @property
    def legacy_config_path(self) -> Path:
        return self.install_dir / CONFIG_FILENAME

    @property
    def model_search_dirs(self) -> list[Path]:
        dirs = [self.models_dir, self.install_dir / MODELS_DIRNAME]
        unique: list[Path] = []
        for directory in dirs:
            if directory not in unique:
                unique.append(directory)
        return unique


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_install_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_resource_dir() -> Path:
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
    return Path(__file__).resolve().parent


def get_documents_dir() -> Path:
    """Documents folder, honouring folder redirection (e.g. OneDrive) on Windows."""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            import uuid

            class GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                            ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

            folder_id = uuid.UUID("{FDD39AD0-238F-46AF-ADB4-6C85480369C7}")  # FOLDERID_Documents
            guid = GUID.from_buffer_copy(folder_id.bytes_le)
            path_ptr = ctypes.c_wchar_p()
            shell32 = ctypes.windll.shell32
            if shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(path_ptr)) == 0:
                try:
                    if path_ptr.value:
                        return Path(path_ptr.value)
                finally:
                    ctypes.windll.ole32.CoTaskMemFree(path_ptr)
        except Exception:
            pass
    return Path.home() / "Documents"


def compute_paths(*, frozen: bool, install_dir: Path, resource_dir: Path,
                  env: Mapping[str, str], documents_dir: Path) -> AppPaths:
    install_dir = Path(install_dir)
    override = (env.get(DATA_DIR_ENV) or "").strip()
    if override:
        data_dir = Path(override)
        return AppPaths(
            install_dir=install_dir,
            resource_dir=Path(resource_dir),
            data_dir=data_dir,
            config_path=data_dir / CONFIG_FILENAME,
            models_dir=data_dir / MODELS_DIRNAME,
            output_root=Path(documents_dir) / APP_NAME,
            portable=False,
        )

    if not frozen:
        return AppPaths(
            install_dir=install_dir,
            resource_dir=Path(resource_dir),
            data_dir=install_dir,
            config_path=install_dir / CONFIG_FILENAME,
            models_dir=install_dir / MODELS_DIRNAME,
            output_root=install_dir / LEGACY_OUTPUT_DIRNAME,
            portable=True,
        )

    home = Path.home()
    roaming = Path(env.get("APPDATA") or home / "AppData" / "Roaming")
    local = Path(env.get("LOCALAPPDATA") or home / "AppData" / "Local")
    data_dir = roaming / APP_NAME
    return AppPaths(
        install_dir=install_dir,
        resource_dir=Path(resource_dir),
        data_dir=data_dir,
        config_path=data_dir / CONFIG_FILENAME,
        models_dir=local / APP_NAME / MODELS_DIRNAME,
        output_root=Path(documents_dir) / APP_NAME,
        portable=False,
    )


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def migrate_legacy_config(legacy_config: Path, new_config: Path,
                          legacy_root: Path, new_output_root: Path) -> Optional[dict]:
    """Copy an old install-dir config.json to the per-user location.

    Runs only when the new config does not exist yet and the legacy one does.
    Relative paths are made absolute against the old install dir (where they
    used to resolve). An output_dir inside the old install dir is moved to the
    new output root because the install dir is no longer user-writable.
    Existing audiobooks are left where they are. Returns the migrated config,
    or None when nothing was migrated.
    """
    legacy_config = Path(legacy_config)
    new_config = Path(new_config)
    if new_config.exists() or not legacy_config.is_file():
        return None
    try:
        if legacy_config.resolve() == new_config.resolve():
            return None
    except OSError:
        return None
    try:
        config = json.loads(legacy_config.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(config, dict):
        return None

    legacy_root = Path(legacy_root)
    new_output_root = Path(new_output_root)

    for key in PATH_CONFIG_KEYS:
        value = config.get(key)
        if isinstance(value, str) and value and not Path(value).is_absolute():
            config[key] = str(legacy_root / value)

    output_value = config.get("output_dir")
    output_path = Path(output_value) if isinstance(output_value, str) and output_value else None
    if output_path is None:
        config["output_dir"] = str(new_output_root)
    else:
        if not output_path.is_absolute():
            output_path = legacy_root / output_path
        if _is_within(output_path, legacy_root):
            legacy_output_root = legacy_root / LEGACY_OUTPUT_DIRNAME
            target = new_output_root
            if _is_within(output_path, legacy_output_root):
                target = new_output_root / output_path.resolve().relative_to(legacy_output_root.resolve())
            config["output_dir"] = str(target)
            config["legacy_output_dir"] = str(output_path)
        else:
            config["output_dir"] = str(output_path)

    new_config.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = new_config.with_name(new_config.name + ".tmp")
    tmp_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    os.replace(tmp_path, new_config)
    return config


def find_piper_model(voice: str, search_dirs: Iterable[Path]) -> Path:
    """Return the first existing <voice>.onnx; otherwise the path in the first (writable) dir."""
    dirs = list(search_dirs)
    filename = voice if voice.endswith(".onnx") else f"{voice}.onnx"
    for directory in dirs:
        candidate = Path(directory) / filename
        if candidate.exists():
            return candidate
    return Path(dirs[0]) / filename


def list_piper_models(search_dirs: Iterable[Path]) -> list[str]:
    names: list[str] = []
    for directory in search_dirs:
        directory = Path(directory)
        if not directory.is_dir():
            continue
        for model in sorted(directory.glob("*.onnx")):
            if model.stem not in names:
                names.append(model.stem)
    return names


def list_piper_model_files(search_dirs: Iterable[Path]) -> list[Path]:
    """All model files (.onnx and .onnx.json), first directory wins on duplicate names."""
    files: dict[str, Path] = {}
    for directory in search_dirs:
        directory = Path(directory)
        if not directory.is_dir():
            continue
        for model_file in sorted(directory.glob("*.onnx*")):
            files.setdefault(model_file.name, model_file)
    return list(files.values())


PATHS = compute_paths(
    frozen=is_frozen(),
    install_dir=get_install_dir(),
    resource_dir=get_resource_dir(),
    env=os.environ,
    documents_dir=get_documents_dir(),
)


def migrate_if_needed(paths: AppPaths = PATHS) -> Optional[dict]:
    if paths.portable:
        return None
    try:
        return migrate_legacy_config(
            paths.legacy_config_path, paths.config_path, paths.install_dir, paths.output_root
        )
    except OSError:
        return None
