import unittest

from pipeline import should_skip_tts_chunk


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


if __name__ == "__main__":
    unittest.main()
