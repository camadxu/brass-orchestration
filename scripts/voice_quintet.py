#!/usr/bin/env python3
"""Search a brass-quintet voicing for a chord progression, then emit MusicXML.

Hard constraints (same rules the validator enforces):
  * every note inside the instrument's comfortable concert range
  * no gap > 12 semitones between adjacent voices above the tuba
  * no parallel fifths/octaves between any pair of voices
  * bass voice always the chord root in the low octave
Objective: minimal total voice movement + compact spacing.

Usage:
  voice_quintet.py --prog Bb, Eb, F, Bb --bars 2 --out score.musicxml
"""
from __future__ import annotations
import argparse
import itertools
import sys

NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'D#': 3, 'E': 4, 'F': 5,
      'F#': 6, 'Gb': 6, 'G': 7, 'Ab': 8, 'G#': 8, 'A': 9, 'Bb': 10, 'B': 11}

# written ranges used by the validator, converted to sounding here
PARTS = [
    # name, sounding transposition (+ = sounds above written), clef, key shift
    ('Trumpet 1 in Bb', -2, ('G', 2), 2),
    ('Trumpet 2 in Bb', -2, ('G', 2), 2),
    ('Horn in F', -7, ('G', 2), 1),
    ('Trombone', 0, ('F', 4), 0),
    ('Tuba', 0, ('F', 4), 0),
]

# comfortable SOUNDING ranges (midi): derived from written A3-Bb5 etc.
RANGES = [  # trp1, trp2, horn, trb, tuba  (high -> low)
    (67, 74),   # trumpet 1: sounds G4..D5 (amateur ceiling)
    (62, 70),   # trumpet 2: sounds D4..Bb4
    (53, 72),   # horn: sounds F3..C5
    (46, 65),   # trombone: sounds Bb2..F4
    (31, 48),   # tuba: sounds G1..C3
]

CHORDS = {
    'Bb': ([34], [58, 62, 65, 70], [10, 2, 5]),   # root octave, chord tones pc set
    'Eb': ([39], [51, 55, 58, 63], [3, 7, 10]),
    'F':  ([41], [53, 57, 60, 65], [5, 9, 0]),
    'Cm': ([36], [51, 55, 58, 63], [0, 3, 7]),
    'Gm': ([31], [50, 55, 58, 62], [7, 10, 2]),
    'Dm': ([38], [50, 53, 57, 62], [2, 5, 9]),
}


def candidates(lo, hi, pcs):
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def ic(a, b):
    return abs(a - b) % 12


def parallel(v1a, v1b, v2a, v2b):
    """True when the pair moves in the same direction into a fifth or octave."""
    if v1a == v1b or v2a == v2b:
        return False
    if (v1b - v1a) * (v2b - v2a) <= 0:
        return False
    return ic(v1a, v2a) == ic(v1b, v2b) and ic(v1b, v2b) in (0, 7)


def score(voicing, prev):
    """Lower is better: total movement + spacing penalty."""
    s = 0
    if prev:
        s += sum(abs(a - b) for a, b in zip(voicing, prev))
    upper = voicing[:-1]  # everything above the tuba
    for a, b in zip(upper, upper[1:]):
        gap = a - b
        if gap > 12:
            s += 100 * (gap - 12)
        if gap <= 0:
            s += 200
    return s


def solve(prog, beam=600):
    """Beam search so one chord's greedy choice cannot dead-end the next one."""
    layers = []
    for name in prog:
        bass, _, pcs = CHORDS[name]
        cands = [candidates(lo, hi, pcs) for lo, hi in RANGES[:-1]]
        vs = []
        for combo in itertools.product(*cands):
            v = list(combo) + [bass[0]]
            if not (v[0] > v[1] > v[2] > v[3] > v[4]):
                continue
            if any(a - b > 12 for a, b in zip(v[:-1], v[1:-1])):
                continue
            vs.append(v)
        if not vs:
            return None, f'no valid voicing for {name}'
        layers.append(vs)

    # dp: (cost, voicing, backpointer)
    best = [(0, v, None) for v in layers[0]]
    best = sorted(best, key=lambda t: score(t[1], None))[:beam]
    trails = [best]
    for i in range(1, len(layers)):
        cand = []
        for v in layers[i]:
            for cost, pv, _ in trails[-1]:
                if any(parallel(pv[a], v[a], pv[b], v[b]) for a in range(5) for b in range(a + 1, 5)):
                    continue
                cand.append((cost + score(v, pv), v, pv))
        if not cand:
            return None, f'no valid continuation for {prog[i]}'
        cand.sort(key=lambda t: t[0])
        trails.append(cand[:beam])
    seq, cur = [], trails[-1][0][1]
    pv = trails[-1][0][2]
    seq.append(cur)
    for i in range(len(layers) - 1, 0, -1):
        seq.append(pv)
        # find the trail entry that produced pv at this layer
        nxt = None
        for cost, v, parent in trails[i - 1]:
            if v == pv:
                nxt = parent
                break
        pv = nxt
        if pv is None:
            break
    return list(reversed(seq)), None


def note_xml(midi):
    pc = midi % 12
    name = NAMES[pc]
    alt = 1 if name.endswith('#') else (-1 if name.endswith('b') else 0)
    alt_xml = '' if alt == 0 else f'<alter>{alt}</alter>'
    return f'<pitch><step>{name[0]}</step>{alt_xml}<octave>{midi // 12 - 1}</octave></pitch>'


def emit(path, seq, bars_each=2, concert_fifths=-2, rests=(), title='Brass quintet voicing'):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<score-partwise version="4.0">',
           f'<work><work-title>{title}</work-title></work>', '<part-list>']
    for i, (name, _, _, _) in enumerate(PARTS, start=1):
        out.append(f'<score-part id="P{i}"><part-name>{name}</part-name></score-part>')
    out.append('</part-list>')
    bar_no = 0
    for i, (name, trans, clef, shift) in enumerate(PARTS, start=1):
        out.append(f'<part id="P{i}">')
        bar_no = 0
        for ch in seq:
            for _ in range(bars_each):
                bar_no += 1
                sounding = ch[i - 1]
                out.append(f'<measure number="{bar_no}">')
                if bar_no == 1:
                    dia = {0: 0, -2: 1, -7: 4}.get(trans, 0)
                    tr = (f'<transpose><chromatic>{trans}</chromatic>'
                          f'<diatonic>{dia}</diatonic></transpose>') if trans else ''
                    out.append('<attributes><divisions>1</divisions>'
                               f'<key><fifths>{concert_fifths + shift}</fifths></key>'
                               '<time><beats>4</beats><beat-type>4</beat-type></time>'
                               f'<clef><sign>{clef[0]}</sign><line>{clef[1]}</line></clef>{tr}'
                               '</attributes>')
                if bar_no in rests and i <= 2:      # trumpet breath bars
                    out.append('<note><rest/><duration>4</duration><type>whole</type></note>')
                else:
                    out.append(f'<note>{note_xml(sounding - trans)}<duration>4</duration>'
                               '<type>whole</type></note>')
                out.append('</measure>')
        out.append('</part>')
    out.append('</score-partwise>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prog', required=True, help='comma separated chord symbols, e.g. "Bb,Eb,F,Bb"')
    ap.add_argument('--bars', type=int, default=2, help='bars per chord')
    ap.add_argument('--rests', default='', help='bar numbers where trumpets rest, e.g. 4,8')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    prog = [p.strip() for p in a.prog.split(',') if p.strip()]
    rests = {int(x) for x in a.rests.split(',') if x.strip()}
    seq, err = solve(prog)
    if err:
        print('ERROR:', err, file=sys.stderr)
        return 1
    for ch, v in zip(prog, seq):
        print(f'{ch:4} concert: ' + ' '.join(f'{NAMES[m % 12]}{m // 12 - 1}' for m in reversed(v)))
    print('written', emit(a.out, seq, a.bars, rests=rests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
