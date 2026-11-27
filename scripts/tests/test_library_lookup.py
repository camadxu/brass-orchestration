"""Black-box lookup tests; all library reads use temporary fixtures."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'library_lookup.py'
if os.name == 'nt':
    tempfile.tempdir = str(Path.home() / 'AppData/Local/hermes/cache/scratch')


def load_script():
    spec = importlib.util.spec_from_file_location('library_lookup', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding='utf-8')

    def test_find_snippets_slices_via_original_offsets(self):
        # casefold('ß')='ss' shifts folded positions; old code cut text by folded offsets.
        self.assertEqual(load_script().find_snippets('Straße ТРОМБОН', 'тромбон', 0), ['ТРОМБОН'])

    def test_find_snippets_case_insensitive_with_at_most_three_hits(self):
        module = load_script()
        text = 'Тромбон тромбон ТРОМБОН Тромбон'
        self.assertEqual(module.find_snippets(text, 'ТРОМБОН', 0), ['Тромбон', 'тромбон', 'ТРОМБОН'])
        self.assertEqual(module.find_snippets(text, ' отсутствует ', 5), [])

    def test_cli_reports_pdf_name_from_static_table(self):
        self.put('books/prout/prout.pages.json', json.dumps([
            {'pdf_page': 5, 'text': 'The trombone is rarely used casually'}]))
        result = self.run_cli('trombone', '--book', 'prout', '--root', str(self.root), '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(result.stdout)
        self.assertEqual(rows[0]['pdf'], 'books/prout/orchestra01prou.pdf')
        self.assertEqual(rows[0]['pdf_page'], 5)

    def test_new_book_ids_are_valid_choices_and_report_missing_index(self):
        for book in ['forsyth', 'kling', 'widor', 'prout', 'prout-v2']:
            with self.subTest(book=book):
                result = self.run_cli('trombone', '--book', book, '--root', str(self.root))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('Missing page index', result.stderr)
                self.assertNotIn('invalid choice', result.stderr)

    def test_static_books_table_matches_real_manifest(self):
        root = Path(os.environ.get('ORCH_LIBRARY', Path.home() / 'Documents' / 'orchestration-library'))
        manifest = root / 'books' / 'manifest.json'
        if not manifest.is_file():
            self.skipTest('no real library manifest on this host')
        module = load_script()
        entries = json.loads(manifest.read_text(encoding='utf-8'))
        self.assertEqual(set(module.BOOKS), {row['id'] for row in entries})
        for row in entries:
            pages_rel, title, pdf = module.BOOKS[row['id']]
            self.assertEqual(pages_rel, 'books/' + row['pages_index'])
            self.assertEqual(pdf, 'books/' + row['original'])


if __name__ == '__main__':
    unittest.main()
