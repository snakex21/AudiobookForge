import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from ui.state import AppState


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


if __name__ == "__main__":
    unittest.main()
