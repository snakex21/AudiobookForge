import json
import tempfile
import unittest
from pathlib import Path

from pipeline import collect_pipeline_stats


class PipelineStatsTests(unittest.TestCase):
    def test_collect_pipeline_stats_persists_stage_details(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            (output_dir / "pages").mkdir()
            (output_dir / "chunks").mkdir()
            (output_dir / "pages" / "page_001.jpg").write_bytes(b"page")
            (output_dir / "pages" / "page_002.jpg").write_bytes(b"page")
            (output_dir / "chunks" / "chunk_001.mp3").write_bytes(b"mp3")
            (output_dir / "audiobook_final.mp3").write_bytes(b"mp3")
            (output_dir / "output.txt").write_text(
                "\n=== Strona 1 ===\nHello\n\n=== Strona 2 ===\nWorld\n",
                encoding="utf-8",
            )

            stats = collect_pipeline_stats(
                output_dir,
                start_time=0,
                mode="translate_to_audio",
                stage_timings={
                    "extraction": 1.25,
                    "translation": 2.5,
                    "audio": 3.75,
                    "merge": 0.5,
                },
                completed=True,
            )

            self.assertTrue((output_dir / "pipeline_stats.json").exists())
            persisted = json.loads((output_dir / "pipeline_stats.json").read_text(encoding="utf-8"))

            self.assertEqual(stats["page_count"], 2)
            self.assertEqual(persisted["chunk_count"], 1)
            self.assertTrue(persisted["completed"])
            self.assertEqual(persisted["stages"]["extraction"]["page_count"], 2)
            self.assertEqual(persisted["stages"]["translation"]["status"], "completed")
            self.assertEqual(persisted["stages"]["audio"]["chunk_count"], 1)
            self.assertTrue(persisted["stages"]["merge"]["final_audio_exists"])


if __name__ == "__main__":
    unittest.main()
