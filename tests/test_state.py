import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from ui.state import AppState, build_recent_project_entry


class AppStateTests(unittest.TestCase):
    def test_reset_events_clears_pause_and_stop(self):
        app_state = AppState()
        app_state.pause_event.set()
        app_state.stop_event.set()

        app_state.reset_events()

        self.assertFalse(app_state.pause_event.is_set())
        self.assertFalse(app_state.stop_event.is_set())

    def test_save_writes_current_config(self):
        app_state = AppState()
        app_state.config["llm_model"] = "test-model"
        app_state.config["_job_start_action"] = "resume"

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            with patch("ui.state.CONFIG_PATH", config_path):
                app_state.save()

            saved = json.loads(config_path.read_text(encoding="utf-8"))

            self.assertEqual(saved["llm_model"], "test-model")
            self.assertNotIn("_job_start_action", saved)

    def test_recent_project_entry_keeps_project_source_copy(self):
        entry = build_recent_project_entry(
            {
                "mode": "pdf_to_audio",
                "pdf_path": r"C:\books\book.pdf",
                "project_source_file": r"C:\projects\book\source\book.pdf",
                "output_dir": r"C:\projects\book",
                "copy_source_to_project": True,
            }
        )

        self.assertIsNotNone(entry)
        self.assertEqual(entry["config"]["project_source_file"], r"C:\projects\book\source\book.pdf")
        self.assertTrue(entry["config"]["copy_source_to_project"])


if __name__ == "__main__":
    unittest.main()
