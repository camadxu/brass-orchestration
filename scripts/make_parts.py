#!/usr/bin/env python3
"""Split a partwise MusicXML score into individual parts, optionally as PDF.

MuseScore's own `-P` flag only exports parts that already exist inside a
`.mscz`; after importing MusicXML it produces nothing. Players still need
parts, so generate them here from the score itself: one MusicXML per part,
keeping the part name, its transposition, key, time and clef.

Usage:
  make_parts.py score.musicxml --out DIR [--pdf] [--mscore mscore3]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


def safe(name):
    """Filename-safe, but Unicode-preserving.

    Part names are routinely localised ("Бас-тромбон 1", "Туба"). An ASCII-only
    whitelist collapses every Cyrillic name to '_', so several parts land on the
    same destination and overwrite each other while the run still reports a full
    part count. Strip only what a path cannot hold.
    """
    return re.sub(r'[/\\:*?"<>|\x00-\x1f]+', '_', name).strip(' .')[:80] or 'part'


def split(path, outdir):
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != 'score-partwise':
        raise SystemExit('only partwise MusicXML is supported')
    parts = root.findall('part')
    name_by_id = {sp.get('id'): (sp.findtext('part-name') or sp.get('id'))
                  for sp in root.iter('score-part')}
    work = root.findtext('work/work-title') or os.path.splitext(os.path.basename(path))[0]
    os.makedirs(outdir, exist_ok=True)
    made = []
    seen = set()
    for i, p in enumerate(parts, 1):
        pid = p.get('id')
        name = name_by_id.get(pid, pid)
        new = ET.Element('score-partwise', {'version': root.get('version', '4.0')})
        w = ET.SubElement(new, 'work')
        ET.SubElement(w, 'work-title').text = f'{work} — {name}'
        pl = ET.SubElement(new, 'part-list')
        sp = ET.SubElement(pl, 'score-part', {'id': pid})
        ET.SubElement(sp, 'part-name').text = name
        # copy instrument metadata so playback/transposition stays intact
        for old in root.iter('score-part'):
            if old.get('id') == pid:
                for child in list(old):
                    if child.tag != 'part-name':
                        sp.append(child)
        new.append(p)
        dest = os.path.join(outdir, f'{i:02d}_{safe(name)}.musicxml')
        if dest in seen:
            raise SystemExit(f'two parts map to {dest} ({name}) — refusing to overwrite')
        seen.add(dest)
        ET.ElementTree(new).write(dest, encoding='utf-8', xml_declaration=True)
        made.append((name, dest))
    return made


def to_pdf(score, outdir, mscore='mscore3'):
    env = dict(os.environ, TMPDIR='/tmp')
    if mscore.startswith('mscore3'):
        env['QT_QPA_PLATFORM'] = 'offscreen'
    else:
        env['MU_QT_QPA_PLATFORM'] = 'offscreen'
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(score))[0] + '.pdf')
    r = subprocess.run([mscore, score, '-o', pdf] if not mscore.startswith('mscore3')
                       else [mscore, '-o', pdf, score],
                       capture_output=True, text=True, env=env, timeout=300)
    return pdf if os.path.exists(pdf) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('score')
    ap.add_argument('--out', required=True)
    ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--mscore', default='mscore3')
    a = ap.parse_args()
    made = split(a.score, a.out)
    ok = 0
    for name, dest in made:
        line = f'{name:28} {dest}'
        if a.pdf:
            p = to_pdf(dest, a.out, a.mscore)
            line += f'  -> {os.path.basename(p) if p else "PDF FAILED"}'
            ok += bool(p)
        print(line)
    print(f'parts: {len(made)}' + (f', pdfs: {ok}' if a.pdf else ''))
    return 0 if (not a.pdf or ok == len(made)) else 1


if __name__ == '__main__':
    sys.exit(main())
