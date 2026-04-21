import unittest
import tempfile
import threading
from pathlib import Path

from pipeline import ensure_project_source_copy, run_pipeline, should_skip_tts_chunk


class PipelineTests(unittest.TestCase):
    def test_skips_punctuation_only_chunk(self):
        self.assertTrue(should_skip_tts_chunk("... --- !!!"))

    def test_skips_page_number_only_chunk(self):
        self.assertTrue(should_skip_tts_chunk("Page 123"))
        self.assertTrue(should_skip_tts_chunk("XIV"))

    def test_keeps_sentence_with_numbers(self):
        self.assertFalse(should_skip_tts_chunk("In 2024, the team shipped 3 updates."))

    def test_keeps_short_legitimate_text(self):
        self.assertFalse(should_skip_tts_chunk("Tak."))

    def test_run_pipeline_rejects_empty_pdf_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = {
                "mode": "translate_to_audio",
                "pdf_path": "",
                "output_dir": tmp_dir,
                "llm_provider": "lmstudio",
                "llm_url": "http://localhost:1234/v1",
                "llm_model": "test-model",
                "tts_provider": "piper",
                "piper_voice": "pl_PL-darkman-medium",
                "extraction_mode": "llm_vision",
            }

            with self.assertRaisesRegex(FileNotFoundError, "Nieprawidlowy plik PDF"):
                run_pipeline(
                    config,
                    lambda _message: None,
                    lambda *_args: None,
                    threading.Event(),
                    threading.Event(),
                )

    def test_ensure_project_source_copy_copies_source_into_project(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_file = tmp_path / "book.pdf"
            source_file.write_text("pdf", encoding="utf-8")
            output_dir = tmp_path / "project"

            config = {
                "pdf_path": str(source_file),
                "copy_source_to_project": True,
            }

            copied_path = ensure_project_source_copy(config, output_dir, lambda _message: None)

            self.assertIsNotNone(copied_path)
            self.assertTrue(copied_path.exists())
            self.assertEqual(copied_path.read_text(encoding="utf-8"), "pdf")
            self.assertEqual(config["project_source_file"], str(copied_path))


if __name__ == "__main__":
    unittest.main()
