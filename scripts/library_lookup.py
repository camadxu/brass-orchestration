#!/usr/bin/env python3
"""Offline OCR search for books in orchestration-library.

Examples:
  python library_lookup.py "тромбон" --book rimsky --limit 20
  python library_lookup.py "валторн" --book rimsky --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

BOOKS = {
    "rimsky": ("books/rimsky/rimsky.pages.json", "Римский-Корсаков — Основы оркестровки"),
    "anisimov": ("books/anisimov/anisimov.pages.json", "Анисимов — Практическое пособие по инструментовке"),
    "malter": ("books/malter/malter.pages.json", "Мальтер — Таблицы по инструментоведению"),
    "blum": ("books/blum/blum.pages.json", "Блюм — Краткий курс инструментоведения"),
}


def default_root() -> Path:
    return Path(os.environ.get("ORCH_LIBRARY", Path.home() / "Documents" / "orchestration-library"))


def find_snippets(text: str, term: str, context: int) -> list[str]:
    folded, needle = text.casefold(), term.casefold()
    hits: list[str] = []
    pos = 0
    while len(hits) < 3:
        pos = folded.find(needle, pos)
        if pos < 0:
            break
        left = max(0, pos - context)
        right = min(len(text), pos + len(term) + context)
        hits.append(re.sub(r"\s+", " ", text[left:right]).strip())
        pos += max(1, len(term))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("term", help="literal OCR search term; try spelling variants for historical texts")
    parser.add_argument("--book", choices=[*BOOKS, "all"], default="all")
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--context", type=int, default=100, help="characters around each match")
    parser.add_argument("--limit", type=int, default=40, help="maximum matching pages")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args()
    if args.context < 0 or args.limit < 1:
        parser.error("--context must be nonnegative and --limit must be positive")

    books = BOOKS if args.book == "all" else {args.book: BOOKS[args.book]}
    results: list[dict[str, object]] = []
    errors = 0
    for book_id, (index_rel, title) in books.items():
        index_path = args.root / index_rel
        if not index_path.is_file():
            print(f"Missing page index: {index_path}", file=sys.stderr)
            errors += 1
            continue
        try:
            pages = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Cannot read {index_path}: {exc}", file=sys.stderr)
            errors += 1
            continue
        for page in pages:
            excerpts = find_snippets(str(page.get("text", "")), args.term, args.context)
            if excerpts:
                results.append({
                    "book": book_id,
                    "title": title,
                    "pdf_page": page.get("pdf_page"),
                    "printed_page": None,
                    "pdf": index_rel.removesuffix(".pages.json") + ".pdf",
                    "snippets": excerpts,
                })
    book_order = {book: i for i, book in enumerate(BOOKS)}
    results.sort(key=lambda row: (book_order[str(row["book"])], int(row["pdf_page"] or 0)))
    results = results[:args.limit]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for row in results:
            print(f"{row['book']} · PDF p. {row['pdf_page']} · {row['pdf']}")
            for excerpt in row["snippets"]:
                print(f"  {excerpt}")
    if not results:
        if not errors:
            print(f"No OCR matches for {args.term!r}; try spelling variants/word stems or inspect the manifest.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())