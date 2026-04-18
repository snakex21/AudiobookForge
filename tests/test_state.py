import tempfile
import unittest
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

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            with patch("ui.state.CONFIG_PATH", config_path):
                app_state.save()

            self.assertIn('"llm_model": "test-model"', config_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
