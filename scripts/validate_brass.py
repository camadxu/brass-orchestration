#!/usr/bin/env python3
"""Mechanical validator for brass scores in MusicXML.

Checks (written pitch unless stated):
  * range: hard error outside practical range, warning outside comfortable range
  * endurance (high brass): continuous playing time, time spent above written G5
  * breathing: rest share per part
  * texture: adjacent-voice spacing, parallel fifths/octaves (sounding pitch)
  * notation: transposed parts whose key signature disagrees with the concert key

Usage:
  validate_brass.py score.musicxml [--level amateur|pro] [--json]
  validate_brass.py --write-demo demo.musicxml

Exit code 1 when a hard error is found, 0 otherwise.
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def n2m(name):
    letter = _PC[name[0].upper()]
    i, alt = 1, 0
    while i < len(name) and name[i] in '#b':
        alt += 1 if name[i] == '#' else -1
        i += 1
    return 12 * (int(name[i:]) + 1) + letter + alt


def m2n(x):
    return f"{_NAMES[x % 12]}{x // 12 - 1}"


SPECS = {
    'trumpet':     dict(fam='high', lo='F#3', hi='C6',  clo='A3',  chi='Bb5'),
    'cornet':      dict(fam='high', lo='F#3', hi='C6',  clo='A3',  chi='Bb5'),
    'flugel':      dict(fam='high', lo='F#3', hi='Bb5', clo='G3',  chi='G5'),
    'soprano':     dict(fam='high', lo='F#4', hi='E6',  clo='A4',  chi='C6'),
    'horn':        dict(fam='mid',  lo='C3',  hi='C6',  clo='G3',  chi='F5'),
    'trombone':    dict(fam='mid',  lo='E2',  hi='Bb4', clo='Bb2', chi='F4'),
    'bass trombone': dict(fam='low', lo='Bb1', hi='Bb4', clo='F2', chi='F4'),
    'euphonium':   dict(fam='mid',  lo='E2',  hi='Bb4', clo='Bb2', chi='F4'),
    'baritone':    dict(fam='mid',  lo='E2',  hi='Bb4', clo='Bb2', chi='F4'),
    'tuba':        dict(fam='low',  lo='D1',  hi='F3',  clo='G1',  chi='C3'),
}

ALIASES = {
    'contrabass tuba': 'tuba', 'bass tuba': 'tuba', 'tub': 'tuba', 'туба': 'tuba',
    'bass trombone': 'bass trombone', 'bass trb': 'bass trombone', 'bass trb.': 'bass trombone',
    'тромбон-бас': 'bass trombone',
    'trombone': 'trombone', 'trb': 'trombone', 'trb.': 'trombone', 'tbn': 'trombone',
    'тромбон': 'trombone', 'tb': 'trombone',
    'euphonium': 'euphonium', 'эуфониум': 'euphonium', 'euph': 'euphonium',
    'baritone': 'baritone', 'barit': 'baritone', 'баритон': 'baritone',
    'flugelhorn': 'flugel', 'flugel': 'flugel', 'флюгель': 'flugel', 'flgh': 'flugel',
    'soprano cornet': 'soprano', 'soprano': 'soprano',
    'cornet': 'cornet', 'corn': 'cornet', 'корнет': 'cornet',
    'trumpet': 'trumpet', 'trp': 'trumpet', 'trp.': 'trumpet', 'tp': 'trumpet',
    'труба': 'trumpet',
    'horn': 'horn', 'валторна': 'horn', 'hn': 'horn', 'hrn': 'horn',
    'tuba': 'tuba', 'tu': 'tuba',
}

# written -> sounding chromatic shift, used for the key-signature check
TRANS_SHIFT = {-2: 2, -7: 1, -9: 3, -5: 1}


@dataclass
class Ev:
    on: float          # quarter-note offset from the start
    dur: float
    written: int
    sounding: int
    measure: int


@dataclass
class Part:
    pid: str
    name: str
    kind: str | None = None
    trans: int = 0
    events: list = field(default_factory=list)
    fifths: int | None = None


def classify(name, instruments):
    hay = ' '.join([name] + instruments).lower()
    if 'bass' in hay and ('trombone' in hay or 'trb' in hay or 'тромбон' in hay):
        return 'bass trombone'
    best = None
    for a, k in ALIASES.items():
        if a in hay and (best is None or len(a) > len(best[0])):
            best = (a, k)
    return best[1] if best else None


def parse(path):
    root = ET.parse(path).getroot()
    names, instr = {}, {}
    for sp in root.iter('score-part'):
        pid = sp.get('id')
        names[pid] = (sp.findtext('part-name') or '').strip()
        instr[pid] = [n.text.strip() for n in sp.iter('instrument-name') if n.text]
    parts = []
    warnings = []
    for pel in root.iter('part'):
        p = Part(pid=pel.get('id'), name=names.get(pel.get('id'), ''))
        p.kind = classify(p.name, instr.get(pel.get('id'), []))
        tpos = 0.0          # quarter offset inside the current measure
        mstart = 0.0
        divisions = 1
        pending_tie = {}
        for mnum, mel in enumerate(pel.findall('measure'), start=1):
            tpos = 0.0
            for el in mel:
                tag = el.tag
                if tag == 'attributes':
                    if el.find('divisions') is not None:
                        divisions = int(el.findtext('divisions'))
                    key = el.find('key/fifths')
                    if key is not None and p.fifths is None:
                        p.fifths = int(key.text)
                    tr = el.find('transpose')
                    if tr is not None and tr.find('chromatic') is not None:
                        p.trans = int(tr.findtext('chromatic'))
                elif tag == 'backup':
                    tpos -= int(el.findtext('duration') or 0) / divisions
                elif tag == 'forward':
                    tpos += int(el.findtext('duration') or 0) / divisions
                elif tag == 'note':
                    dur = int(el.findtext('duration') or 0) / divisions
                    rest = el.find('rest') is not None
                    if rest or el.find('pitch') is None:
                        tpos += dur
                        continue
                    pit = el.find('pitch')
                    step = pit.findtext('step')
                    octv = int(pit.findtext('octave'))
                    alter = int(pit.findtext('alter') or 0)
                    written = 12 * (octv + 1) + _PC[step] + alter
                    ties = el.findall('tie')
                    is_stop = any(t.get('type') == 'stop' for t in ties)
                    voice = el.findtext('voice') or '1'
                    chord = el.find('chord') is not None
                    if is_stop and voice in pending_tie and not chord:
                        pending_tie[voice].dur += dur
                    else:
                        ev = Ev(mstart + tpos, dur, written, written + p.trans, mnum)
                        p.events.append(ev)
                        if any(t.get('type') == 'start' for t in ties):
                            pending_tie[voice] = ev
                        else:
                            pending_tie.pop(voice, None)
                    if not chord:
                        tpos += dur
            mstart += tpos if tpos > 0 else 4.0
        if not p.events:
            warnings.append(f"part '{p.name}' ({p.pid}) has no notes — check the file")
            continue
        parts.append(p)
    return parts, warnings


THRESH = {'amateur': dict(run=8.0, high_run=4.0, high_share=0.25),
          'pro': dict(run=16.0, high_run=8.0, high_share=0.45)}


def run_lengths(events, pred):
    """Longest continuous stretch (quarters) of events matching pred, gaps <= 0.5 allowed."""
    best = cur = 0.0
    prev_end = None
    for e in sorted(events, key=lambda x: x.on):
        ok = pred(e)
        if not ok:
            cur, prev_end = 0.0, None
            continue
        if prev_end is not None and e.on - prev_end <= 0.5:
            cur += e.dur
        else:
            cur = e.dur
        prev_end = e.on + e.dur
        best = max(best, cur)
    return best


def analyse(parts, level='amateur'):
    hard, warn = [], []
    th = THRESH[level]
    stats = []
    for p in parts:
        spec = SPECS.get(p.kind)
        if spec is None:
            warn.append(f"'{p.name}': unknown instrument — range checks skipped, name the part like 'Trumpet 1'")
            continue
        lo, hi = n2m(spec['lo']), n2m(spec['hi'])
        clo, chi = n2m(spec['clo']), n2m(spec['chi'])
        bad_lo = [e for e in p.events if e.written < lo]
        bad_hi = [e for e in p.events if e.written > hi]
        for e in bad_hi[:5]:
            hard.append(f"{p.name}: written {m2n(e.written)} above {spec['hi']} at bar {e.measure}")
        for e in bad_lo[:5]:
            hard.append(f"{p.name}: written {m2n(e.written)} below {spec['lo']} at bar {e.measure}")
        soft = [e for e in p.events if clo <= e.written <= chi]
        if p.events and len(soft) / len(p.events) < 0.85 and not (bad_lo or bad_hi):
            warn.append(f"{p.name}: only {100*len(soft)//len(p.events)}% of notes inside the comfortable register ({spec['clo']}-{spec['chi']})")
        total = sum(e.dur for e in p.events)
        span = (max(e.on + e.dur for e in p.events)) or 1.0
        rest_share = max(0.0, 1 - total / span)
        entry = dict(part=p.name, kind=p.kind,
                     used=[m2n(min(e.written for e in p.events)), m2n(max(e.written for e in p.events))],
                     sounding_used=[m2n(min(e.sounding for e in p.events)), m2n(max(e.sounding for e in p.events))],
                     rest_pct=round(100 * rest_share, 1), notes=len(p.events))
        if spec['fam'] == 'high':
            run = run_lengths(p.events, lambda e: True)
            hish = [e for e in p.events if e.written >= n2m('G5')]
            hrun = run_lengths(hish, lambda e: True)
            hshare = sum(e.dur for e in hish) / span if span else 0
            entry.update(longest_run_bars=round(run / 4, 2), high_run_bars=round(hrun / 4, 2),
                         high_time_pct=round(100 * hshare, 1))
            if run / 4 > th['run'] / 4:
                warn.append(f"{p.name}: {run/4:.1f} bars of continuous playing without a real rest (limit {th['run']/4:.0f} for {level}) — trumpet lip")
            if hrun / 4 > th['high_run'] / 4:
                warn.append(f"{p.name}: {hrun/4:.1f} bars continuous above written G5 (limit {th['high_run']/4:.0f} for {level})")
            if hshare > th['high_share']:
                warn.append(f"{p.name}: {100*hshare:.0f}% of the piece sits above written G5 — endurance risk for {level}")
        else:
            run = run_lengths(p.events, lambda e: True)
            entry.update(longest_run_bars=round(run / 4, 2))
            if run / 4 > 8:
                warn.append(f"{p.name}: {run/4:.1f} bars without a breath mark or rest — mark a breath")
        stats.append(entry)

    # spacing and parallels on sounding pitch
    onsets = sorted({round(e.on, 3) for p in parts for e in p.events})
    active = {}

    def voices_at(t):
        out = {}
        for p in parts:
            for e in p.events:
                if e.on - 1e-6 <= t < e.on + e.dur - 1e-6:
                    out.setdefault(p.pid, (p, e))
                    break
        return out

    prev = None
    for t in onsets:
        cur = voices_at(t)
        ordered = sorted(cur.values(), key=lambda x: x[1].sounding)
        for (ln, le), (un, ue) in zip(ordered, ordered[1:]):
            gap = ue.sounding - le.sounding
            lk = SPECS.get(ln.kind, {}).get('fam')
            uk = SPECS.get(un.kind, {}).get('fam')
            if gap > 12 and lk in ('high', 'mid') and uk in ('high', 'mid'):
                warn.append(f"bar {le.measure}: gap of {gap} semitones between {ln.name} and {un.name} — spread the chords, do not park an octave hole in the middle")
        if prev:
            for pid, (p, e) in cur.items():
                if pid in prev:
                    p0, e0 = prev[pid]
                    d0, d1 = e0.sounding, e.sounding
                    if d0 != d1:
                        for qid, (q, f) in cur.items():
                            if qid <= pid or qid not in prev:
                                continue
                            q0 = prev[qid][1].sounding
                            f1 = f.sounding
                            if q0 == f1:
                                continue
                            i0, i1 = abs(d0 - q0) % 12, abs(d1 - f1) % 12
                            same_dir = (d1 - d0) * (f1 - q0) > 0
                            if same_dir and i0 == i1 and i0 in (0, 7):
                                kind = 'octaves' if i0 == 0 else 'fifths'
                                warn.append(f"bar {e.measure}: parallel {kind} between {p.name} and {q.name}")
        prev = cur
    # key signatures
    concert = next((p for p in parts if p.trans == 0 and p.fifths is not None), None)
    if concert:
        for p in parts:
            if p.fifths is None or p.trans == 0:
                continue
            shift = TRANS_SHIFT.get(p.trans)
            if shift is None:
                continue
            want = concert.fifths + shift
            if p.fifths != want:
                warn.append(f"{p.name}: key signature {p.fifths:+d} fifths but the concert key {concert.fifths:+d} with a {p.trans:+d} transposition needs {want:+d}")
    return hard, warn, stats


def el_owner(p, e):
    return p.name


def report(parts, level, as_json=False):
    hard, warn, stats = analyse(parts, level)
    if as_json:
        print(json.dumps(dict(level=level, parts=stats, errors=hard, warnings=warn), ensure_ascii=False, indent=2))
    else:
        print(f"score: {len(parts)} parts, level={level}")
        for s in stats:
            extra = ''
            if 'high_time_pct' in s:
                extra = f" high>{'G5'}: {s['high_time_pct']}% run {s.get('high_run_bars')}b"
            print(f"  {s['part'][:22]:22} {s['kind']:14} written {s['used'][0]}-{s['used'][1]:5} "
                  f"sound {s['sounding_used'][0]}-{s['sounding_used'][1]:5} rest {s['rest_pct']:5}% "
                  f"longest {s['longest_run_bars']:5}b{extra}")
        print(f"\nHARD ERRORS: {len(hard)}")
        for x in hard:
            print(f"  ! {x}")
        print(f"WARNINGS: {len(warn)}")
        for x in warn:
            print(f"  ~ {x}")
        print("\nVerdict:", "REJECT" if hard else ("REVIEW warnings" if warn else "mechanically clean"))
    return 1 if hard else 0


DEMO = [
    # (part-name, transposed chromatic shift, [(written note or None per bar, duration in quarters)])
    ('Trumpet 1 in Bb', -2, [('C5', 4), ('E5', 4), ('G5', 4), ('D6', 4)]),
    ('Trumpet 2 in Bb', -2, [('G4', 4), ('B4', 4), ('D5', 4), ('F5', 4)]),
    ('Horn in F', -7, [('C4', 4), ('E4', 4), ('G4', 4), ('C5', 4)]),
    ('Trombone', 0, [('C3', 4), ('E3', 4), ('G3', 4), ('C4', 4)]),
    ('Tuba', 0, [('C2', 4), ('C2', 4), ('C2', 4), ('C1', 4)]),
]


def write_demo(path):
    def pitch_xml(name):
        letter = name[0]
        i, alt = 1, None
        while i < len(name) and name[i] in '#b':
            alt = (alt or 0) + (1 if name[i] == '#' else -1)
            i += 1
        alt_xml = '' if alt is None else f"<alter>{alt}</alter>"
        return f"<pitch><step>{letter}</step>{alt_xml}<octave>{name[i:]}</octave></pitch>"

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0"><part-list>']
    for i, (nm, _, _) in enumerate(DEMO, start=1):
        out.append(f'<score-part id="P{i}"><part-name>{nm}</part-name></score-part>')
    out.append('</part-list>')
    for i, (nm, trans, bars) in enumerate(DEMO, start=1):
        out.append(f'<part id="P{i}">')
        for bi, (pit, dur) in enumerate(bars, start=1):
            out.append('<measure number="%d">' % bi)
            if bi == 1:
                tr = f'<transpose><chromatic>{trans}</chromatic><diatonic>{ {0:0,-2:1,-7:4,-9:5 }.get(trans, 0) }</diatonic></transpose>' if trans else ''
                out.append(f'<attributes><divisions>1</divisions><key><fifths>0</fifths></key>'
                           f'<time><beats>4</beats><beat-type>4</beat-type></time>'
                           f'<clef><sign>G</sign><line>2</line></clef>{tr}</attributes>')
            type_ = {4: 'whole', 2: 'half', 1: 'quarter'}.get(dur, 'quarter')
            out.append(f'<note>{pitch_xml(pit)}<duration>{dur}</duration><type>{type_}</type></note>')
            out.append('</measure>')
        out.append('</part>')
    out.append('</score-partwise>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'demo written: {path}')


def main():
    ap = argparse.ArgumentParser(description='Validate a brass score in MusicXML.')
    ap.add_argument('score', nargs='?')
    ap.add_argument('--level', default='amateur', choices=['amateur', 'pro'])
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--write-demo', metavar='PATH')
    a = ap.parse_args()
    if a.write_demo:
        write_demo(a.write_demo)
        return 0
    if not a.score:
        ap.error('score path or --write-demo required')
    parts, pw = parse(a.score)
    rc = report(parts, a.level, a.json)
    for x in pw:
        print(f'~ {x}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
