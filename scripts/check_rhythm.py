#!/usr/bin/env python3
"""Rhythm and notation consistency check for a MusicXML score (score order, not engraving).

Checks, per part:
  * measure length: every voice (between backup/forward) fills the time signature in force
  * written value: <type> and <dot> of every note and rest agree with <duration>/<divisions>
    (a half note labelled "whole" is what makes a bar read as six beats in a 4/4)
  * ties (per voice and pitch) and slurs: a stop without a start, a start without a stop
  * hairpins: a stop without a start, a start without a stop, nested or duplicated numbers
  * rehearsal marks: numbers in order, none twice (reported for the first part only)
  * bar numbers: sequential from 1 (a pickup may be 0), same count in every part

Grace notes, tuplets (time-modification) and whole-measure rests are skipped by the value check.

Usage:
  check_rhythm.py score.musicxml [--json]

Exit code 1 when anything is found, 0 otherwise.
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET

VALUES = [('breve', 8.0), ('whole', 4.0), ('half', 2.0), ('quarter', 1.0), ('eighth', 0.5),
          ('16th', 0.25), ('32nd', 0.125), ('64th', 0.0625), ('128th', 0.03125), ('256th', 0.015625)]


def shape(q):
    """(type, dots) of the plain value equal to q quarters, else None."""
    for dots in range(5):
        for name, v in VALUES:
            if abs(q - v * (2 - 0.5 ** dots)) < 1e-6:
                return name, dots
    return None


def beats(time):
    """Length of a <time> element in quarters (sum of beats * beat-type/4), plus its symbol string."""
    if time.get('symbol') == 'common':
        return 4.0, '4/4'
    if time.get('symbol') == 'cut':
        return 2.0, '2/2'
    bs = [int(x.text) for x in time.findall('beats')]
    bt = [int(x.text) for x in time.findall('beat-type')]
    return sum(b * 4 / t for b, t in zip(bs, bt)), '/'.join(f'{b}/{t}' for b, t in zip(bs, bt))




def tie_key(n):
    """(voice, step, accidental, octave): a chord ties several notes at once, so a tie is tracked per pitch."""
    p = n.find('pitch')
    if p is None:
        return n.findtext('voice') or '1', n.findtext('instrument') or 'rest', '', ''
    alter = p.findtext('alter') or '0'
    return (n.findtext('voice') or '1', p.findtext('step'), ('#' * int(float(alter)) if float(alter) > 0 else 'b' * -int(float(alter))),
            p.findtext('octave'))


def check_part(part, first=False):
    """List of dicts: part, bar, kind, text."""
    out, name = [], part.get('id')
    div, want, sig = None, None, '?'
    ties, slurs, wedges, reh = {}, {}, {}, []
    numbers = [m.get('number') for m in part.findall('measure')]
    digits = [int(n) for n in numbers if n.isdigit()]
    if digits[:1] == [0]:
        digits = digits[1:]            # a pickup excluded from the bar count is numbered 0
    if digits != list(range(1, len(digits) + 1)):
        out.append(dict(part=name, bar='', kind='bar numbers', text='not sequential from 1'))
    for m in part.findall('measure'):
        bar = m.get('number')
        a = m.find('attributes')
        if a is not None:
            div = int(a.findtext("divisions")) if a.find("divisions") is not None else div
            t = a.find('time')
            if t is not None:
                want, sig = beats(t)
        if div is None or want is None:
            out.append(dict(part=name, bar=bar, kind='measure length', text='no divisions or time signature in force'))
            continue
        full = m.get('implicit') == 'yes' or any(r.get('measure') == 'yes' for r in m.findall('note/rest'))
        pos, voices = 0, []
        for ch in m:
            if ch.tag == 'backup':
                voices.append(pos)
                pos -= int(ch.findtext('duration') or 0)
            elif ch.tag == 'forward':
                pos += int(ch.findtext('duration') or 0)
            elif ch.tag == 'note':
                d = int(ch.findtext('duration') or 0)
                if ch.find('chord') is None and ch.find('grace') is None:
                    pos += d
                t = ch.find('type')
                if t is not None and ch.find('grace') is None and ch.find('time-modification') is None \
                        and ch.find('rest[@measure="yes"]') is None:
                    expect = shape(d / div)
                    have = (t.text, len(ch.findall('dot')))
                    if expect is None:
                        out.append(dict(part=name, bar=bar, kind='value', text=f'{have[0]} of {d / div:g} quarters is no plain value'))
                    elif have != expect:
                        out.append(dict(part=name, bar=bar, kind='value', text=f'{have[0]}{"." * have[1]} written, duration {expect[0]}{"." * expect[1]}'))
        voices.append(pos)
        if not full:
            for i, v in enumerate(voices):
                if abs(v - want * div) > div * 1e-3:
                    out.append(dict(part=name, bar=bar, kind='measure length', text=f'voice {i + 1}: {v / div:g} of {want:g} quarters ({sig})'))
        for n in m.findall('note'):
            k = tie_key(n)
            for t in n.findall('tie'):
                if t.get('type') == 'stop':
                    if not ties.pop(k, False):
                        out.append(dict(part=name, bar=bar, kind='tie', text='stop without a start'))
                else:
                    ties[k] = True
            for s in n.iter('slur'):
                k = s.get('number') or '1'
                if s.get('type') == 'stop':
                    if not slurs.pop(k, False):
                        out.append(dict(part=name, bar=bar, kind='slur', text=f'number {k}: stop without a start'))
                else:
                    if slurs.get(k):
                        out.append(dict(part=name, bar=bar, kind='slur', text=f'number {k}: start while open'))
                    slurs[k] = True
        for w in m.iter('wedge'):
            k = w.get('number') or '1'
            if w.get('type') == 'stop':
                if not wedges.pop(k, False):
                    out.append(dict(part=name, bar=bar, kind='hairpin', text=f'number {k}: stop without a start'))
            else:
                if wedges.get(k):
                    out.append(dict(part=name, bar=bar, kind='hairpin', text=f'number {k}: start while open'))
                wedges[k] = w.get('type')
        if first:
            reh += [int(r.text) for r in m.iter('rehearsal') if r.text and r.text.isdigit()]
    for k in ties:
        out.append(dict(part=name, bar='', kind='tie', text=f'tie on {k[1]}{k[2]}{k[3]}, voice {k[0]}: no stop to the end of the part'))
    for kind, open_ in (('slur', slurs), ('hairpin', wedges)):
        for k in open_:
            out.append(dict(part=name, bar='', kind=kind, text=f'number {k if k else "1"}: no stop to the end of the part'))
    if first:
        nums = reh
        dup = sorted({x for x in reh if reh.count(x) > 1})
        order = [b for a_, b in zip(nums, nums[1:]) if b <= a_]
        if dup:
            out.append(dict(part=name, bar='', kind='rehearsal', text=f'used more than once: {dup}'))
        if order:
            out.append(dict(part=name, bar='', kind='rehearsal', text=f'out of order at: {order}'))
    return out


def report(path, as_json=False):
    root = ET.parse(path).getroot()
    parts = root.findall('part')
    issues = [i for k, p in enumerate(parts) for i in check_part(p, first=k == 0)]
    counts = len({len(p.findall('measure')) for p in parts})
    if counts > 1:
        issues.insert(0, dict(part='*', bar='', kind='bar count', text='parts have different numbers of bars'))
    if as_json:
        return json.dumps(issues, ensure_ascii=False, indent=1)
    by = {}
    for i in issues:
        by.setdefault(i['kind'], []).append(i)
    lines = [f'{path}: {len(issues)} issue(s), {len(parts)} part(s), {len(parts[0].findall("measure"))} bars']
    for kind, rows in by.items():
        lines.append(f'  {kind}: {len(rows)}')
        for i in rows[:40]:
            lines.append(f'    {i["part"]} bar {i["bar"]}: {i["text"]}')
        if len(rows) > 40:
            lines.append(f'    ... {len(rows) - 40} more')
    lines.append('RESULT ' + ('PASS' if not issues else 'FAIL'))
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description='Rhythm and notation consistency check of a MusicXML score.')
    ap.add_argument('score')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    text = report(a.score, a.json)
    print(text)
    sys.exit(1 if (json.loads(text) if a.json else not text.endswith('PASS')) else 0)


if __name__ == '__main__':
    main()
