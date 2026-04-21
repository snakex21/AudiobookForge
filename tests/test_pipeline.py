import unittest
import tempfile
import threading

from pipeline import run_pipeline, should_skip_tts_chunk


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


if __name__ == "__main__":
    unittest.main()
