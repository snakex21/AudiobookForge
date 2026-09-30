import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline


class PerformancePathTests(unittest.TestCase):
    def run_audio(self, root, **kwargs):
        pipeline.text_to_audio(root, kwargs.pop('provider', 'piper'),
            log_callback=lambda *_: None, progress_callback=lambda *_: None,
            pause_event=threading.Event(), stop_event=kwargs.pop('stop', threading.Event()), **kwargs)

    def make_book(self, root):
        (root / 'output.txt').write_text('This is the first sentence.\n\nThis is the second sentence.', encoding='utf-8')

    def synthesize(self, text, output, **kwargs):
        self.assertTrue(output.name.startswith('.'), 'pending audio must be excluded from chunk_*.mp3')
        output.write_bytes(b'synthetic-audio-fixture')

    def test_piper_loads_once_and_resume_does_not_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            with patch('pipeline.load_piper_voice', return_value=object()) as load, patch('pipeline.generate_audio_with_piper', side_effect=self.synthesize) as synth:
                self.run_audio(root)
                self.assertEqual(load.call_count, 1)
                self.assertEqual(synth.call_count, 2)
                self.assertIs(synth.call_args_list[0].kwargs['voice'], synth.call_args_list[1].kwargs['voice'])
                self.run_audio(root)
                self.assertEqual(load.call_count, 1)
                self.assertEqual(synth.call_count, 2)
                # Job-scoped: another voice/job must not reuse the prior engine.
                self.run_audio(root, piper_voice='another-voice')
                self.assertEqual(load.call_count, 2)
                self.assertEqual(synth.call_count, 4)

    def test_empty_completed_chunk_is_regenerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            with patch('pipeline.load_piper_voice'), patch('pipeline.generate_audio_with_piper', side_effect=self.synthesize) as synth:
                self.run_audio(root)
                (root / 'chunks/chunk_001.mp3').write_bytes(b'')
                self.run_audio(root)
                self.assertEqual(synth.call_count, 3)

    def test_missing_key_cannot_mark_nonexistent_audio_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            with self.assertRaisesRegex(Exception, 'Nie udalo'):
                self.run_audio(root, provider='openai_tts')
            state = json.loads((root / 'tts_state.json').read_text())
            self.assertTrue(all(c['status'] == 'failed' for c in state['chunks'].values()))

    def test_stale_noncompleted_audio_cannot_be_reused_as_new_success(self):
        import hashlib
        for provider, key in [('openai_tts', None), ('openai_tts', 'synthetic-test-key'), ('unknown', None)]:
            with self.subTest(provider=provider, key=bool(key)), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_book(root)
                (root / 'chunks').mkdir()
                content = (root / 'output.txt').read_text()
                state = {'settings': {'tts_provider': provider, 'piper_voice': None, 'edge_voice': None,
                         'content_hash': hashlib.sha1(content.encode()).hexdigest()}, 'chunks': {}}
                for number in ('001', '002'):
                    (root / f'chunks/chunk_{number}.mp3').write_bytes(b'stale-partial-attempt')
                    state['chunks'][number] = {'status': 'failed'}
                (root / 'tts_state.json').write_text(json.dumps(state))
                # Deliberately simulate a provider returning without writing bytes.
                with patch('pipeline.generate_audio_with_openai_tts') as generate:
                    with self.assertRaisesRegex(Exception, 'Nie udalo'):
                        self.run_audio(root, provider=provider, api_key=key)
                    if key is None:
                        generate.assert_not_called()
                final = json.loads((root / 'tts_state.json').read_text())
                self.assertTrue(all(c['status'] == 'failed' for c in final['chunks'].values()))
                self.assertEqual(list((root / 'chunks').glob('*.mp3')), [])

    def test_failed_atomic_publish_never_marks_chunk_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            with patch('pipeline.load_piper_voice'), patch('pipeline.generate_audio_with_piper', side_effect=self.synthesize), patch('pipeline.os.replace', side_effect=PermissionError('synthetic publish failure')):
                with self.assertRaisesRegex(Exception, 'Nie udalo'):
                    self.run_audio(root)
            state = json.loads((root / 'tts_state.json').read_text())
            self.assertTrue(all(c['status'] == 'failed' for c in state['chunks'].values()))
            self.assertEqual(list((root / 'chunks').glob('*.mp3')), [])

    def test_cancellation_skips_remaining_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            stop = threading.Event()
            def synth(text, output, **kwargs):
                self.synthesize(text, output, **kwargs)
                stop.set()
            with patch('pipeline.load_piper_voice') as load, patch('pipeline.generate_audio_with_piper', side_effect=synth) as generate:
                self.run_audio(root, stop=stop)
                self.assertEqual(generate.call_count, 1)
                self.assertEqual(load.call_count, 1)

    def test_real_pdf_shared_document_matches_individual_reads(self):
        import pypdfium2 as pdfium
        from reportlab.pdfgen.canvas import Canvas
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / 'book.pdf'
            canvas = Canvas(str(pdf_path))
            for i in range(4):
                canvas.drawString(30, 700, f'This is page {i + 1} with enough text to avoid OCR.')
                canvas.showPage()
            canvas.save()
            expected = [pipeline.extract_text_pypdfium(pdf_path, i) for i in range(1, 5)]
            original = pdfium.PdfDocument
            with patch('pypdfium2.PdfDocument', wraps=original) as opens:
                output = pipeline.extract_pdf_text_direct(pdf_path, Path(tmp) / 'out', '', '', None,
                    lambda *_: None, lambda *_: None, threading.Event(), threading.Event())
                self.assertEqual(opens.call_count, 1)
            actual = output.read_text()
            for text in expected:
                self.assertIn(text, actual)
            # Resume is byte-stable and does not append duplicate pages.
            pipeline.extract_pdf_text_direct(pdf_path, Path(tmp) / 'out', '', '', None,
                lambda *_: None, lambda *_: None, threading.Event(), threading.Event())
            self.assertEqual(output.read_text(), actual)

if __name__ == '__main__':
    unittest.main()
