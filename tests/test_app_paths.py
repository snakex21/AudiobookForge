import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app_paths
import pipeline
from app_paths import compute_paths, find_piper_model, list_piper_models, migrate_legacy_config

REPO_DIR = Path(__file__).resolve().parent.parent


class ComputePathsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.install = self.tmp / "Program Files" / "AudiobookForge"
        self.docs = self.tmp / "Documents"
        self.env = {"APPDATA": str(self.tmp / "Roaming"), "LOCALAPPDATA": str(self.tmp / "Local")}

    def tearDown(self):
        self._tmp.cleanup()

    def test_frozen_build_keeps_user_data_out_of_install_dir(self):
        paths = compute_paths(frozen=True, install_dir=self.install, resource_dir=self.install,
                              env=self.env, documents_dir=self.docs)

        self.assertFalse(paths.portable)
        self.assertEqual(paths.config_path, self.tmp / "Roaming" / "AudiobookForge" / "config.json")
        self.assertEqual(paths.models_dir, self.tmp / "Local" / "AudiobookForge" / "piper_models")
        self.assertEqual(paths.output_root, self.docs / "AudiobookForge")
        for user_path in (paths.config_path, paths.models_dir, paths.output_root):
            self.assertNotIn(self.install, user_path.parents)
        self.assertEqual(paths.legacy_config_path, self.install / "config.json")
        self.assertEqual(paths.model_search_dirs, [paths.models_dir, self.install / "piper_models"])

    def test_source_checkout_stays_portable_in_repo_dir(self):
        paths = compute_paths(frozen=False, install_dir=self.install, resource_dir=self.install,
                              env=self.env, documents_dir=self.docs)

        self.assertTrue(paths.portable)
        self.assertEqual(paths.config_path, self.install / "config.json")
        self.assertEqual(paths.output_root, self.install / "audiobook_output")
        self.assertEqual(paths.model_search_dirs, [self.install / "piper_models"])
        self.assertIsNone(app_paths.migrate_if_needed(paths))

    def test_data_dir_env_override(self):
        env = {**self.env, app_paths.DATA_DIR_ENV: str(self.tmp / "custom")}
        paths = compute_paths(frozen=True, install_dir=self.install, resource_dir=self.install,
                              env=env, documents_dir=self.docs)

        self.assertEqual(paths.config_path, self.tmp / "custom" / "config.json")
        self.assertEqual(paths.models_dir, self.tmp / "custom" / "piper_models")


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.legacy_root = self.tmp / "app"
        self.legacy_root.mkdir()
        self.legacy_config = self.legacy_root / "config.json"
        self.new_config = self.tmp / "Roaming" / "AudiobookForge" / "config.json"
        self.new_output_root = self.tmp / "Documents" / "AudiobookForge"

    def tearDown(self):
        self._tmp.cleanup()

    def migrate(self):
        return migrate_legacy_config(self.legacy_config, self.new_config, self.legacy_root, self.new_output_root)

    def write_legacy(self, config):
        self.legacy_config.write_text(json.dumps(config), encoding="utf-8")

    def test_copies_legacy_config_and_keeps_original(self):
        self.write_legacy({"llm_model": "m", "output_dir": str(self.tmp / "Books" / "MyBook")})

        migrated = self.migrate()

        self.assertIsNotNone(migrated)
        saved = json.loads(self.new_config.read_text(encoding="utf-8"))
        self.assertEqual(saved["llm_model"], "m")
        self.assertEqual(saved["output_dir"], str(self.tmp / "Books" / "MyBook"))
        self.assertNotIn("legacy_output_dir", saved)
        self.assertTrue(self.legacy_config.exists())

    def test_output_inside_install_dir_moves_to_new_root(self):
        legacy_job = self.legacy_root / "audiobook_output" / "MyBook"
        self.write_legacy({"output_dir": str(legacy_job)})

        self.migrate()

        saved = json.loads(self.new_config.read_text(encoding="utf-8"))
        self.assertEqual(Path(saved["output_dir"]), self.new_output_root / "MyBook")
        self.assertEqual(Path(saved["legacy_output_dir"]), legacy_job)

    def test_relative_paths_resolve_against_old_install_dir(self):
        self.write_legacy({"output_dir": "audiobook_output", "pdf_path": "books/a.pdf", "speaker_wav": ""})

        self.migrate()

        saved = json.loads(self.new_config.read_text(encoding="utf-8"))
        self.assertEqual(Path(saved["output_dir"]), self.new_output_root)
        self.assertEqual(Path(saved["pdf_path"]), self.legacy_root / "books" / "a.pdf")
        self.assertEqual(saved["speaker_wav"], "")

    def test_empty_output_dir_gets_new_default(self):
        self.write_legacy({"output_dir": ""})

        self.migrate()

        saved = json.loads(self.new_config.read_text(encoding="utf-8"))
        self.assertEqual(Path(saved["output_dir"]), self.new_output_root)

    def test_existing_new_config_is_never_overwritten(self):
        self.write_legacy({"llm_model": "old"})
        self.new_config.parent.mkdir(parents=True)
        self.new_config.write_text(json.dumps({"llm_model": "new"}), encoding="utf-8")

        self.assertIsNone(self.migrate())
        self.assertEqual(json.loads(self.new_config.read_text(encoding="utf-8"))["llm_model"], "new")

    def test_no_legacy_or_broken_legacy_does_nothing(self):
        self.assertIsNone(self.migrate())
        self.legacy_config.write_text("{not json", encoding="utf-8")
        self.assertIsNone(self.migrate())
        self.assertFalse(self.new_config.exists())

    def test_app_state_load_runs_migration(self):
        from ui import state as state_module

        self.write_legacy({"llm_model": "from-legacy"})
        paths = compute_paths(frozen=True, install_dir=self.legacy_root, resource_dir=self.legacy_root,
                              env={"APPDATA": str(self.tmp / "Roaming"), "LOCALAPPDATA": str(self.tmp / "Local")},
                              documents_dir=self.tmp / "Documents")
        with patch.object(state_module, "PATHS", paths), patch.object(state_module, "CONFIG_PATH", paths.config_path):
            app_state = state_module.AppState()
            app_state.load()

        self.assertEqual(app_state.config["llm_model"], "from-legacy")
        self.assertIsNotNone(app_state.migrated_config)
        self.assertTrue(paths.config_path.exists())


class PiperModelLookupTests(unittest.TestCase):
    def test_user_dir_wins_and_install_dir_is_fallback(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_dir = Path(tmp_dir) / "user"
            install_dir = Path(tmp_dir) / "install"
            user_dir.mkdir()
            install_dir.mkdir()
            (install_dir / "old-voice.onnx").write_bytes(b"x")
            (install_dir / "shared.onnx").write_bytes(b"x")
            (user_dir / "shared.onnx").write_bytes(b"x")
            dirs = [user_dir, install_dir]

            self.assertEqual(find_piper_model("old-voice", dirs), install_dir / "old-voice.onnx")
            self.assertEqual(find_piper_model("shared", dirs), user_dir / "shared.onnx")
            self.assertEqual(find_piper_model("missing", dirs), user_dir / "missing.onnx")
            self.assertEqual(list_piper_models(dirs), ["shared", "old-voice"])


class FfmpegResolutionTests(unittest.TestCase):
    def setUp(self):
        pipeline._ffmpeg_cache.clear()
        self._tmp = tempfile.TemporaryDirectory()
        self.bundled = Path(self._tmp.name) / "ffmpeg" / "ffmpeg.exe"

    def tearDown(self):
        pipeline._ffmpeg_cache.clear()
        self._tmp.cleanup()

    def resolve(self, *, bundled=False, on_path=None, configured="", working=()):
        if bundled:
            self.bundled.parent.mkdir(parents=True, exist_ok=True)
            self.bundled.write_bytes(b"x")
        else:
            self.bundled.unlink(missing_ok=True)
        with patch.object(pipeline, "bundled_ffmpeg_candidates", return_value=[self.bundled]), \
                patch.object(pipeline.shutil, "which", return_value=on_path), \
                patch.object(pipeline, "ffmpeg_works", side_effect=lambda p: p in working):
            return pipeline.resolve_ffmpeg_path(configured)

    def test_order_is_bundled_then_settings_then_path(self):
        all_ok = {str(self.bundled), "C:/path/ffmpeg.exe", "D:/custom/ffmpeg.exe"}
        self.assertEqual(self.resolve(bundled=True, on_path="C:/path/ffmpeg.exe",
                                      configured="D:/custom/ffmpeg.exe", working=all_ok), str(self.bundled))
        self.assertEqual(self.resolve(on_path="C:/path/ffmpeg.exe", configured="D:/custom/ffmpeg.exe",
                                      working=all_ok), "D:/custom/ffmpeg.exe")
        self.assertEqual(self.resolve(on_path="C:/path/ffmpeg.exe", working=all_ok), "C:/path/ffmpeg.exe")

    def test_broken_candidates_fall_through(self):
        self.assertEqual(self.resolve(bundled=True, on_path="C:/path/ffmpeg.exe", configured="D:/custom/ffmpeg.exe",
                                      working={"C:/path/ffmpeg.exe"}), "C:/path/ffmpeg.exe")
        self.assertEqual(self.resolve(on_path="C:/shim/ffmpeg.exe", configured="D:/custom/ffmpeg.exe",
                                      working={"D:/custom/ffmpeg.exe"}), "D:/custom/ffmpeg.exe")

    def test_no_working_ffmpeg_raises(self):
        with self.assertRaises(Exception):
            self.resolve(on_path="C:/shim/ffmpeg.exe")

    def test_no_hardcoded_machine_paths(self):
        source = (REPO_DIR / "pipeline.py").read_text(encoding="utf-8")
        self.assertNotIn("Replay", source)
        self.assertNotIn("panda3d_tools", source)

    def test_run_ffmpeg_passes_timeout_and_reports_expiry(self):
        with patch.object(pipeline, "resolve_ffmpeg_path", return_value="ffmpeg"), \
                patch.object(pipeline.subprocess, "run",
                             side_effect=subprocess.TimeoutExpired(cmd="ffmpeg", timeout=5)) as run:
            with self.assertRaisesRegex(Exception, "limit czasu"):
                pipeline.run_ffmpeg(["-i", "a.wav", "b.mp3"], 5)
        self.assertEqual(run.call_args.kwargs["timeout"], 5)


class VersionTests(unittest.TestCase):
    def test_installer_reads_version_from_version_py(self):
        from version import __version__

        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertGreater(tuple(int(p) for p in __version__.split(".")), (1, 0, 5))
        iss = (REPO_DIR / "AudiobookForge.iss").read_text(encoding="utf-8")
        self.assertIn("version.py", iss)
        self.assertIsNone(re.search(r'#define\s+MyAppVersion\s+"', iss))

    def test_release_bundles_pinned_ffmpeg_with_license(self):
        fetch = (REPO_DIR / "scripts" / "fetch_ffmpeg.ps1").read_text(encoding="utf-8")
        archive_sha = re.search(r'\$ArchiveSha256\s*=\s*"([0-9a-f]{64})"', fetch)
        exe_sha = re.search(r'\$ExeSha256\s*=\s*"([0-9a-f]{64})"', fetch)
        self.assertIsNotNone(archive_sha)
        self.assertIsNotNone(exe_sha)
        self.assertIn("-lgpl", fetch)
        notices = (REPO_DIR / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn(archive_sha.group(1), notices)
        self.assertIn(exe_sha.group(1), notices)
        self.assertIn("ffmpeg\\ffmpeg.exe", (REPO_DIR / "AudiobookForge.iss").read_text(encoding="utf-8"))
        build = (REPO_DIR / "build_folder.bat").read_text(encoding="utf-8")
        self.assertIn("fetch_ffmpeg.ps1", build)
        self.assertIn("LICENSE.txt", build)

    def test_installer_does_not_open_permissions_or_wipe_app_dir(self):
        iss = (REPO_DIR / "AudiobookForge.iss").read_text(encoding="utf-8")
        self.assertNotIn("users-modify", iss)
        self.assertNotIn("[UninstallDelete]", iss)


if __name__ == "__main__":
    unittest.main()
