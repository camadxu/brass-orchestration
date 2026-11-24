"""Black-box catalog tests; all library writes use temporary fixtures."""
import hashlib
import importlib.util
from unittest.mock import patch
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'library_catalog.py'
if os.name == 'nt':
    tempfile.tempdir = str(Path.home() / 'AppData/Local/hermes/cache/scratch')


def load_script():
    spec = importlib.util.spec_from_file_location('library_catalog', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def run_cli(self, *args, root=True, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *(['--root', str(self.root)] if root else []), *args], capture_output=True, text=True, encoding='utf-8', env=env)

    def catalog(self):
        return json.loads((self.root / 'catalog.json').read_text(encoding='utf-8'))

    def save_catalog(self, catalog):
        self.put('catalog.json', json.dumps(catalog))

    def test_write_inventories_sorted_files_with_only_two_exclusions(self):
        self.put('z.txt', 'hello')
        self.put('.hidden', 'hidden')
        self.put('scores/CATALOG.md', 'generated')
        self.put('scores/a.pdf', '%PDF-test')
        result = self.run_cli('--write')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = self.catalog()
        self.assertEqual(data['schema_version'], 1)
        self.assertEqual([f['path'] for f in data['files']], ['.hidden', 'scores/a.pdf', 'z.txt'])
        row = data['files'][-1]
        self.assertEqual(row, {'path': 'z.txt', 'size': 5, 'sha256': hashlib.sha256(b'hello').hexdigest(), 'type': 'text', 'purpose': None})

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive paths')
    def test_windows_generated_case_variants_are_excluded(self):
        self.put('books/A/Book.PDF', '%PDF-test')
        self.put('books/manifest.json', json.dumps([{
            'original': 'A/Book.PDF', 'sha256': hashlib.sha256(b'%PDF-test').hexdigest()}]))
        self.put('CATALOG.JSON', json.dumps({'schema_version': 1, 'files': []}))
        self.put('scores/catalog.md', 'generated')
        result = self.run_cli('--write')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([row['path'] for row in self.catalog()['files']],
                         ['books/A/Book.PDF', 'books/manifest.json'])
        result = self.run_cli('--check')
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive paths')
    def test_windows_catalog_rejects_generated_case_variant_entries(self):
        for path in ['CATALOG.JSON', 'scores/catalog.md']:
            raw = json.dumps({'schema_version': 1, 'files': [{
                'path': path, 'size': 0, 'sha256': hashlib.sha256(b'').hexdigest(),
                'type': 'json', 'purpose': None}]})
            for mode in ['--write', '--check', '--render']:
                with self.subTest(path=path, mode=mode):
                    self.put('CATALOG.JSON', raw)
                    result = self.run_cli(mode)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn('excluded catalog path: ' + path, result.stderr)
                    self.assertEqual((self.root / 'CATALOG.JSON').read_text(encoding='utf-8'), raw)
                    self.assertFalse((self.root / 'scores').exists())

    def test_write_preserves_all_manual_metadata_and_refreshes_technical_fields(self):
        self.put('a.txt', 'old')
        self.assertEqual(self.run_cli('--write').returncode, 0)
        data = self.catalog()
        data['files'][0].update(purpose='study', edition='verified edition', custom={'nested': [1, None]}, type='stale')
        self.save_catalog(data)
        self.put('a.txt', 'new contents')
        self.assertEqual(self.run_cli('--write').returncode, 0)
        row = self.catalog()['files'][0]
        self.assertEqual(row['purpose'], 'study')
        self.assertEqual(row['edition'], 'verified edition')
        self.assertEqual(row['custom'], {'nested': [1, None]})
        self.assertEqual(row['type'], 'text')
        self.assertEqual(row['size'], 12)
        self.assertEqual(row['sha256'], hashlib.sha256(b'new contents').hexdigest())

    def test_cli_root_resolution_and_required_exclusive_mode(self):
        env = dict(os.environ, ORCH_LIBRARY=str(self.root))
        self.put('env.txt', 'environment')
        result = self.run_cli('--write', root=False, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.catalog()['files'][0]['path'], 'env.txt')
        for flags in [[], ['--write', '--check'], ['--write', '--render'], ['--check', '--render']]:
            with self.subTest(flags=flags):
                self.assertEqual(self.run_cli(*flags).returncode, 2)
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, ORCH_LIBRARY='', USERPROFILE=home, HOME=home)
            result = self.run_cli('--write', root=False, env=env)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('orchestration-library', result.stderr)
            self.assertFalse((Path(home) / 'Documents').exists())
        env['ORCH_LIBRARY'] = str(self.root / 'absent')
        self.assertEqual(self.run_cli('--write', env=env).returncode, 0)

    def test_check_detects_all_drift_without_writing(self):
        self.put('gone.txt', 'gone')
        self.put('changed.txt', 'before')
        self.assertEqual(self.run_cli('--write').returncode, 0)
        before = (self.root / 'catalog.json').read_bytes()
        (self.root / 'gone.txt').unlink()
        self.put('changed.txt', 'after')
        self.put('new.txt', 'new')
        result = self.run_cli('--check')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for message in ['missing: gone.txt', 'changed: changed.txt', 'untracked: new.txt']:
            self.assertIn(message, result.stdout + result.stderr)
        self.assertEqual((self.root / 'catalog.json').read_bytes(), before)
        self.assertFalse((self.root / 'scores').exists())

    def test_invalid_catalog_fails_closed_without_overwrite(self):
        self.put('a.txt', 'data')
        self.assertEqual(self.run_cli('--write').returncode, 0)
        valid = self.catalog()
        row = valid['files'][0]
        invalid = ['{', 'null', '[]', '{"schema_version": 1, "files": [], "files": []}']
        cases = [dict(valid, schema_version=2), dict(valid, schema_version=True), dict(valid, files={}),
                 dict(valid, files=[row, row]), dict(valid, files=[{'path': 'a.txt'}])]
        for path in ['../outside', '/absolute', 'C:/outside', 'a\\b', '', './a', 'a//b', 'a/../b', 'a/', 'catalog.json', 'scores/CATALOG.md', 'file:stream', 'NUL', 'a.']:
            cases.append(dict(valid, files=[dict(row, path=path)]))
        for fields in [{'size': -1}, {'size': True}, {'sha256': 'bad'}, {'type': None}]:
            cases.append(dict(valid, files=[dict(row, **fields)]))
        invalid.extend(json.dumps(value) for value in cases)
        for raw in invalid:
            for mode in ['--write', '--check', '--render']:
                with self.subTest(raw=raw, mode=mode):
                    self.put('catalog.json', raw)
                    result = self.run_cli(mode)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn('error:', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertEqual((self.root / 'catalog.json').read_text(encoding='utf-8'), raw)
        (self.root / 'catalog.json').unlink()
        for mode in ['--check', '--render']:
            result = self.run_cli(mode)
            self.assertEqual(result.returncode, 1)
            self.assertFalse((self.root / 'catalog.json').exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows junction regression')
    def test_windows_root_ancestor_junction_is_refused_without_writing(self):
        import _winapi

        base = self.root
        self.root = base / 'real/library'
        self.put('books/a.pdf', '%PDF-test')
        self.put('books/manifest.json', json.dumps([{
            'original': 'a.pdf', 'sha256': hashlib.sha256(b'%PDF-test').hexdigest()}]))
        result = self.run_cli('--write')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.put('untracked.txt', 'must not be cataloged through the junction')
        real_root = self.root
        before = {p.relative_to(real_root).as_posix(): p.read_bytes()
                  for p in real_root.rglob('*') if p.is_file()}
        alias = base / 'alias'
        _winapi.CreateJunction(str(base / 'real'), str(alias))
        # Remove only the junction, before TemporaryDirectory cleans the fixture.
        self.addCleanup(os.rmdir, alias)
        self.assertTrue(alias.is_junction())
        self.assertTrue(alias.samefile(base / 'real'))
        self.root = alias / 'library'
        for mode in ['--write', '--check', '--render']:
            with self.subTest(mode=mode):
                result = self.run_cli(mode)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('symlink or junction refused:', result.stderr)
                self.assertIn(str(alias), result.stderr)
            with self.subTest(mode=mode, unchanged=True):
                after = {p.relative_to(real_root).as_posix(): p.read_bytes()
                         for p in real_root.rglob('*') if p.is_file()}
                self.assertEqual(after, before)

    def test_symlinks_are_refused_including_excluded_files(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'target'
            target.write_text('outside', encoding='utf-8')
            for name in ['link.txt', 'catalog.json', 'scores/CATALOG.md', 'directory-link', 'broken']:
                link = self.root / name
                link.parent.mkdir(parents=True, exist_ok=True)
                try:
                    link.symlink_to(Path(outside) if name == 'directory-link' else target if name != 'broken' else Path(outside) / 'absent', target_is_directory=name == 'directory-link')
                except OSError as exc:
                    self.skipTest(f'symlink creation unavailable: {exc}')
                for mode in ['--write', '--check', '--render']:
                    with self.subTest(name=name, mode=mode):
                        result = self.run_cli(mode)
                        self.assertEqual(result.returncode, 1, result.stderr)
                        self.assertIn('symlink', result.stderr.lower())
                link.unlink()
            self.assertEqual(target.read_text(encoding='utf-8'), 'outside')

    def test_check_requires_valid_book_manifest_and_matches_pdf_hashes(self):
        self.put('books/a/a.pdf', '%PDF-test')
        digest = hashlib.sha256(b'%PDF-test').hexdigest()
        manifest = [{'id': 'a', 'original': 'a/a.pdf', 'sha256': digest}]
        self.assertEqual(self.run_cli('--write').returncode, 0)
        self.assertEqual(self.run_cli('--check').returncode, 1)
        for bad in [None, [], {}, [{'original': '../escape', 'sha256': digest}],
                    [{'original': 'a/a.pdf', 'sha256': 'bad'}], manifest * 2,
                    [{'original': 'a/a.pdf', 'sha256': '0' * 64}],
                    [{'original': 'missing.pdf', 'sha256': digest}]]:
            self.put('books/manifest.json', json.dumps(bad))
            self.assertEqual(self.run_cli('--write').returncode, 0)
            result = self.run_cli('--check')
            self.assertEqual(result.returncode, 1, str(bad))
            self.assertNotIn('Traceback', result.stderr)
        self.put('books/manifest.json', json.dumps(manifest))
        self.assertEqual(self.run_cli('--write').returncode, 0)
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.run_cli('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('OK', result.stdout)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_render_scores_preserves_catalog_and_escapes_cells(self):
        self.put('scores/a.pdf', '%PDF-test')
        self.put('scores/b.zip', 'zip')
        self.put('other.txt', 'not a score')
        self.assertEqual(self.run_cli('--write').returncode, 0)
        data = self.catalog()
        row = next(r for r in data['files'] if r['path'] == 'scores/a.pdf')
        row.update(edition='Редактор | имя', instrumentation='Труба\nТуба', purpose='Изучение', basis='<page>')
        self.save_catalog(data)
        before = (self.root / 'catalog.json').read_bytes()
        result = self.run_cli('--render')
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.root / 'scores/CATALOG.md'
        self.assertTrue(target.exists())
        text = target.read_text(encoding='utf-8')
        for expected in ['a.pdf', 'b.zip', 'Редактор &#124; имя', 'Труба<br>Туба', '&lt;page&gt;', 'не установлено']:
            self.assertIn(expected, text)
        self.assertNotIn('other.txt', text)
        self.assertEqual((self.root / 'catalog.json').read_bytes(), before)

    def test_inventory_identifies_library_file_types(self):
        expected = {'a.pdf': 'pdf', 'a.zip': 'archive', 'a.md': 'markdown',
                    'a.json': 'json', 'a.musicxml': 'musicxml', 'a.txt': 'text', 'a.bin': 'other'}
        for name in expected:
            self.put(name, 'data')
        result = self.run_cli('--write')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({r['path']: r['type'] for r in self.catalog()['files']}, expected)

    def test_inventory_refuses_symlink_signal_when_windows_privilege_unavailable(self):
        # Only the OS symlink signal is mocked: this host denies actual creation.
        self.put('catalog.json', '{}')
        module = load_script()
        with patch.object(Path, 'is_symlink', return_value=True):
            with self.assertRaisesRegex(ValueError, 'symlink'):
                module.inventory(self.root)


if __name__ == '__main__':
    unittest.main()
