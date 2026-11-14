#!/usr/bin/env python3
"""Extract one part (by score-part id) into a standalone single-part score.

Why not make_parts.py: that one splits all parts at once. When the task is
"render bar 98 of the bass trombone" this is the shortest path, and it is
immune to filename collisions from localised part names.

Usage:
  split_part.py score.musicxml P10 out.musicxml [--title "..."]

The result keeps the global <work>, the transposition/clef attributes and the
original measure sequence untouched, so a render of it is a fair check of what
the part will print.
"""
import argparse
import sys

from lxml import etree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('score')
    ap.add_argument('part_id')
    ap.add_argument('out')
    ap.add_argument('--title', default=None)
    a = ap.parse_args()

    root = etree.parse(a.score).getroot()
    pl = root.find('part-list')
    if pl is None:
        raise SystemExit('no <part-list> — not a partwise MusicXML score')

    keep = [sp for sp in pl.findall('score-part') if sp.get('id') == a.part_id]
    if not keep:
        ids = [sp.get('id') for sp in pl.findall('score-part')]
        raise SystemExit(f'{a.part_id} not in part-list; have {ids}')
    for sp in pl.findall('score-part'):
        if sp.get('id') != a.part_id:
            pl.remove(sp)

    removed = 0
    for p in root.findall('part'):
        if p.get('id') != a.part_id:
            root.remove(p)
            removed += 1

    if a.title:
        w = root.find('work/work-title')
        if w is not None:
            w.text = a.title

    etree.ElementTree(root).write(a.out, xml_declaration=True,
                                  encoding='UTF-8', pretty_print=True)
    n = len(root.findall('part')[0].findall('measure'))
    print(f"{a.out}: 1 part ({a.part_id}), {n} measures, removed {removed}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
