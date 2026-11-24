#!/usr/bin/env python3
"""Inventory an orchestration library using only the Python standard library."""
import argparse
import hashlib
import json
import os
import re
import sys
import html
from pathlib import Path

EXCLUDED = {'catalog.json', 'scores/CATALOG.md'}
EXCLUDED_KEYS = {os.path.normcase(path) for path in EXCLUDED}


def safe_relative(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(ord(char) < 32 for char in value)
            or any(part in ('', '.', '..') or part.endswith((' ', '.'))
                   or any(c in part for c in '<>"|?*')
                   or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])', part.split('.')[0], re.I)
                   for part in value.split('/'))):
        raise ValueError(f'unsafe relative path: {value!r}')
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def load_catalog(path):
    data = load_json(path)
    if (not isinstance(data, dict) or type(data.get('schema_version')) is not int
            or data['schema_version'] != 1 or not isinstance(data.get('files'), list)):
        raise ValueError('invalid catalog schema')
    result = {}
    for row in data['files']:
        if not isinstance(row, dict) or not {'path', 'size', 'sha256', 'type', 'purpose'} <= row.keys():
            raise ValueError('invalid catalog entry')
        relative = safe_relative(row['path'])
        if os.path.normcase(relative) in EXCLUDED_KEYS or relative in result:
            raise ValueError(f'duplicate or excluded catalog path: {relative}')
        if (type(row['size']) is not int or row['size'] < 0 or not valid_hash(row['sha256'])
                or not isinstance(row['type'], str) or not row['type']):
            raise ValueError(f'invalid technical fields: {relative}')
        result[relative] = row
    return result


def reject_link(path):
    if path.is_symlink() or path.is_junction():
        raise ValueError(f'symlink or junction refused: {path}')


def walk_files(root):
    reject_link(root)
    for path in root.iterdir():
        reject_link(path)
        if path.is_dir():
            yield from walk_files(path)
        elif path.is_file():
            yield path
        else:
            raise ValueError(f'not a regular file: {path}')


def inventory(root):
    # Keep the lexical path: resolve() would hide junctions in its ancestry.
    root = root.absolute()
    for ancestor in (root, *root.parents):
        reject_link(ancestor)
    rows = []
    for path in walk_files(root):
        relative = safe_relative(path.relative_to(root).as_posix())
        if os.path.normcase(relative) not in EXCLUDED_KEYS:
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            rows.append({'path': relative, 'size': path.stat().st_size,
                         'sha256': digest,
                         'type': {'.txt': 'text', '.pdf': 'pdf', '.zip': 'archive',
                                  '.md': 'markdown', '.json': 'json', '.musicxml': 'musicxml'}.get(path.suffix.lower(), 'other'),
                         'purpose': None})
    return sorted(rows, key=lambda row: row['path'])


def check_books(root, actual):
    manifest = load_json(root / 'books/manifest.json')
    if not isinstance(manifest, list) or not manifest:
        raise ValueError('invalid or empty books manifest')
    seen = set()
    errors = []
    for entry in manifest:
        if not isinstance(entry, dict) or not valid_hash(entry.get('sha256')):
            raise ValueError('invalid book manifest entry')
        relative = safe_relative(entry.get('original'))
        if not relative.lower().endswith('.pdf') or relative.casefold() in seen:
            raise ValueError(f'duplicate or non-PDF book path: {relative}')
        seen.add(relative.casefold())
        row = actual.get('books/' + relative)
        if row is None or row['sha256'] != entry['sha256']:
            errors.append(f'book hash mismatch or missing: {relative}')
    return errors


def render_scores(root, metadata):
    def cell(value):
        return html.escape(str(value) if value is not None else 'не установлено').replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')
    lines = ['# Каталог нотных файлов', '',
             'Сгенерировано из catalog.json. Описание первых страниц не доказывает комплектность и права на издание.', '',
             '| Файл | Издание | Состав | Назначение | Основание |',
             '|---|---|---|---|---|']
    for path, row in sorted(metadata.items()):
        if path.startswith('scores/'):
            lines.append('| ' + ' | '.join(cell(row.get(key)) for key in ('path', 'edition', 'instrumentation', 'purpose', 'basis')) + ' |')
    target = root / 'scores/CATALOG.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(os.environ.get('ORCH_LIBRARY') or Path.home() / 'Documents/orchestration-library'))
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ('write', 'check', 'render'):
        modes.add_argument('--' + mode, action='store_true')
    args = parser.parse_args()
    args.root = args.root.expanduser()
    if not args.root.is_dir():
        print(f'error: library root is not a directory: {args.root}', file=sys.stderr)
        return 1
    # Scan before reading excluded files so even generated-path links fail closed.
    rows = inventory(args.root)
    previous = args.root / 'catalog.json'
    metadata = load_catalog(previous) if previous.exists() or not args.write else {}
    if args.render:
        render_scores(args.root, metadata)
        print('Rendered scores/CATALOG.md')
        return 0
    if args.check:
        actual = {row['path']: row for row in rows}
        errors = []
        for path in sorted(metadata.keys() - actual.keys()):
            errors.append(f'missing: {path}')
        for path in sorted(actual.keys() - metadata.keys()):
            errors.append(f'untracked: {path}')
        for path in sorted(metadata.keys() & actual.keys()):
            if any(metadata[path][key] != actual[path][key] for key in ('size', 'sha256', 'type')):
                errors.append(f'changed: {path}')
        try:
            errors.extend(check_books(args.root, actual))
        except (OSError, ValueError) as exc:
            errors.append(f'books manifest error: {exc}')
        for error in errors:
            print(error, file=sys.stderr)
        if not errors:
            print(f'OK: {len(rows)} files; book manifest hashes match')
        return int(bool(errors))
    for row in rows:
        manual = {key: value for key, value in metadata.get(row['path'], {}).items()
                  if key not in {'path', 'size', 'sha256', 'type'}}
        row.update(manual)
    data = {'schema_version': 1, 'files': rows}
    (args.root / 'catalog.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        raise SystemExit(1)
