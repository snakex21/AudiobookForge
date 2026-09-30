"""Offline microbenchmark. Real PDFium extraction, no OCR/API/model downloads.
Reports 7 alternating runs and verifies byte-identical extracted text. This is
not an end-to-end audiobook speedup or Piper-inference benchmark.
"""
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pypdfium2 as pdfium
from reportlab.pdfgen.canvas import Canvas
from pipeline import extract_text_pypdfium

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'synthetic.pdf'
    c = Canvas(str(path))
    for i in range(100):
        for line in range(12):
            c.drawString(30, 750 - 20 * line, f'Page {i + 1}. Deterministic fixture line {line}: readable book content.')
        c.showPage()
    c.save()
    results = {'reopen_per_page_ms': [], 'job_scoped_document_ms': []}
    expected = None
    for repeat in range(7):
        for shared in ([False, True] if repeat % 2 == 0 else [True, False]):
            begin = time.perf_counter()
            if shared:
                with pdfium.PdfDocument(str(path)) as doc:
                    values = [extract_text_pypdfium(path, i, doc) for i in range(1, 101)]
            else:
                values = [extract_text_pypdfium(path, i) for i in range(1, 101)]
            elapsed = (time.perf_counter() - begin) * 1000
            if expected is None:
                expected = values
            assert values == expected, 'Extraction output changed'
            results['job_scoped_document_ms' if shared else 'reopen_per_page_ms'].append(round(elapsed, 3))
    results['pages'] = 100
    results['output_identical'] = True
    results['median_reopen_ms'] = statistics.median(results['reopen_per_page_ms'])
    results['median_shared_ms'] = statistics.median(results['job_scoped_document_ms'])
    results['microbenchmark_speedup'] = round(results['median_reopen_ms'] / results['median_shared_ms'], 3)
    print(json.dumps(results, indent=2))
