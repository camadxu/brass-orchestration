#!/usr/bin/env python3
"""Compare a brass arrangement against the score it reduces, bar by bar, in concert pitch.

Usage:
    python3 compare_scores.py SOURCE.musicxml ARRANGEMENT.musicxml

Recreate the inputs first (an .mxl is a zip; the root file is named in
META-INF/container.xml, usually score.musicxml):

    unzip -o source.mxl -d /tmp/src && unzip -o arrangement.mxl -d /tmp/arr

The output is measurements, not a verdict. Read them with
references/source-comparison.md before reporting anything as an error.
"""
import sys
from collections import Counter

from lxml import etree

STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
# practical written range per instrument, concert pitch (MIDI); first match wins
RANGES = [('alto trombone', 53, 74, 'F3-D5 (top = pro edge)'),
          ('bass trombone', 34, 70, 'Bb1-Bb4'),
          ('trombone', 40, 70, 'E2-Bb4'),
          ('tuba', 26, 53, 'D1-F3')]
PERC = [('snare', 'snare'), ('cymbal', 'cymbal'), ('bass drum', 'bass drum'),
        ('timpan', 'timpan'), ('xylophon', 'xylophon')]
# candidate octave/register relations between an arrangement line and its source line
OFFSETS = list(range(-36, 13, 12))


def tag(e):
    return etree.QName(e).localname


def nm(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def load(path):
    root = etree.parse(path).getroot()
    names = {sp.get('id'): (sp.findtext('part-name') or '')
             for sp in root.findall('part-list/score-part')}
    out = []
    for p in root.findall('part'):
        div, tr, bars = 1, (0, 0), []
        for meas in p.findall('measure'):
            cur, last, pit, ons = 0, None, [], []
            for el in meas:
                t = tag(el)
                if t == 'attributes':
                    d = el.findtext('divisions')
                    if d:
                        div = int(d)
                    te = el.find('transpose')
                    if te is not None:
                        ch = int(te.findtext('chromatic') or 0)
                        oc = int(te.findtext('octave-change') or 0)
                        if ch or oc:
                            tr = (ch, oc)
                elif t == 'note':
                    dur = int(el.findtext('duration') or 0)
                    if el.find('chord') is not None and last is not None:
                        onset = last
                    else:
                        onset = cur
                        last = cur
                    pe = el.find('pitch')
                    if pe is not None:
                        pc = (STEP[pe.findtext('step')] + int(pe.findtext('alter') or 0)) % 12
                        pit.append((onset, (int(pe.findtext('octave')) + 1) * 12 + pc))
                    elif el.find('unpitched') is not None:
                        # percussion is never <pitch>: without this branch it reads as silence
                        ons.append(onset)
                    if el.find('chord') is None:
                        cur += dur
                elif t == 'backup':
                    cur -= int(el.findtext('duration') or 0)
                elif t == 'forward':
                    cur += int(el.findtext('duration') or 0)
            shift = -(tr[0] + 12 * tr[1])
            d = div or 1
            bars.append({'pc': {m % 12 for _, m in pit},
                         'ev': sorted({(round(o / d, 4), m + shift) for o, m in pit}),
                         'ons': sorted({round(o / d, 4) for o in ons})})
        out.append({'id': p.get('id'), 'name': names.get(p.get('id'), ''), 'bars': bars})
    return out


def rr(nums):
    out = []
    for b in nums:
        if out and b == out[-1][1] + 1:
            out[-1][1] = b
        else:
            out.append([b, b])
    return ', '.join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def bar_exact(a_bar, s_bar, off):
    ea, es = a_bar['ev'], s_bar['ev']
    return (len(ea) == len(es) > 0
            and all(oa == os and ma == ms + off for (oa, ma), (os, ms) in zip(ea, es)))


def relation(a_part, s_pit, n):
    """(source part, semitone offset, exact bars) that best explains this line."""
    votes = Counter()
    for i in range(n):
        for p in s_pit:
            for off in OFFSETS:
                if bar_exact(a_part['bars'][i], p['bars'][i], off):
                    votes[(p['id'], off)] += 1
    return votes.most_common(1)[0] if votes else None


def deviations(a_part, s_part, off, n, limit=14):
    out = []
    for i in range(n):
        ea, es = a_part['bars'][i]['ev'], s_part['bars'][i]['ev']
        if not ea or len(ea) != len(es):
            continue
        for (oa, ma), (os, ms) in zip(ea, es):
            if oa == os and ma != ms + off:
                out.append((i + 1, nm(ma), nm(ms), ma - (ms + off)))
    return out[:limit], len(out)


def tempo_report(path, label):
    root = etree.parse(path).getroot()
    met = sorted({(m.findtext('beat-unit'), m.findtext('per-minute'))
                  for m in root.iter('metronome')})
    snd = sorted({s.get('tempo') for s in root.iter('sound') if s.get('tempo')})
    print(f"   {label}: printed metronome {met or 'none'}; playback <sound tempo> {snd or 'none'}")


def main(src_path, arr_path):
    src, arr = load(src_path), load(arr_path)
    n = min(len(p['bars']) for p in src + arr)
    print(f"source: {len(src)} parts, {len(src[0]['bars'])} bars | "
          f"arrangement: {len(arr)} parts, {len(arr[0]['bars'])} bars")
    if len(src[0]['bars']) != len(arr[0]['bars']):
        print("!! bar counts differ - align on a bar where a distinctive line matches exactly before trusting any number below")

    s_pit = [p for p in src if any(b['pc'] for b in p['bars'])]
    a_pit = [p for p in arr if any(b['pc'] for b in p['bars'])]
    by_id = {p['id']: p for p in src}

    def s_pcs(i):
        s = set()
        for p in s_pit:
            s |= p['bars'][i]['pc']
        return s

    def a_pcs(i):
        s = set()
        for p in a_pit:
            s |= p['bars'][i]['pc']
        return s

    print("\n1) per source part: pitch classes that survive in the arrangement")
    for p in s_pit:
        playing = [i for i in range(n) if p['bars'][i]['pc']]
        lost = [i + 1 for i in playing if p['bars'][i]['pc'] - a_pcs(i)]
        print(f"   {p['name'][:20]:20s} plays {len(playing):3d} bars, PCs lost in {len(lost):3d}"
              + (f"   first: {rr(lost[:12])}" if lost else ''))

    full = [i + 1 for i in range(n) if not (s_pcs(i) - a_pcs(i))]
    added = [i + 1 for i in range(n) if a_pcs(i) - s_pcs(i)]
    print(f"\n2) whole-score coverage: {len(full)}/{n} bars hold every source pitch class")
    print(f"   bars where the arrangement adds a pitch class the bar does not contain: {len(added)}")
    if added:
        print(f"   {rr(added)}")
        for b in added[:8]:
            i = b - 1
            print(f"     bar {b}: extra {[nm(x) for x in sorted(a_pcs(i) - s_pcs(i))]}")

    print("\n3) register: arrangement notes outside practical range")
    for p in a_pit:
        ms = [m for b in p['bars'] for _, m in b['ev']]
        rng = next((r for r in RANGES if r[0] in p['name'].lower()), None)
        line = f"   {p['name'][:20]:20s} {nm(min(ms))}-{nm(max(ms))}"
        if rng:
            out = [(i + 1, nm(m)) for i in range(n) for _, m in p['bars'][i]['ev']
                   if m < rng[1] or m > rng[2]]
            line += f"  [{rng[3]}] outside: {len(out)}"
            if out:
                line += f" {out[:10]}"
        print(line)

    print("\n4) percussion: attack count per part")
    for p in arr:
        if any(b['ev'] for b in p['bars']) or not any(b['ons'] for b in p['bars']):
            continue
        low = p['name'].lower()
        key = next((k for k, v in PERC if v in low), None)
        mate = next((s for s in src if key and key in s['name'].lower()), None)
        a_total = sum(len(b['ons']) for b in p['bars'])
        if mate is None:
            print(f"   {p['name'][:20]:20s} {a_total:4d} attacks, no source part matched by name")
            continue
        s_total = sum(len(b['ons']) for b in mate['bars'])
        diff = [i + 1 for i in range(n) if len(p['bars'][i]['ons']) != len(mate['bars'][i]['ons'])]
        print(f"   {p['name'][:20]:20s} {a_total:4d} vs {s_total:4d} ({mate['name']}), differs in {len(diff)} bars"
              + (f": {rr(diff[:20])}" if diff else ''))

    print("\n5) line relations: arrangement part -> the source part it copies, and deviations")
    print("   (a part can change source mid-piece; read deviations in phrase context)")
    for p in a_pit:
        rel = relation(p, s_pit, n)
        if not rel:
            print(f"   {p['name'][:20]:20s} no source line matches even by octaves - independent material")
            continue
        (sid, off), hits = rel
        dev, total = deviations(p, by_id[sid], off, n)
        print(f"   {p['name'][:20]:20s} ~ {by_id[sid]['name'][:18]:18s} {off:+3d} semitones, "
              f"{hits} bars exact, {total} note deviations")
        for b, a, s, d in dev:
            print(f"       bar {b}: arrangement {a}, source {s} ({d:+d} off the relation)")

    print("\n6) tempo: printed mark vs playback tempo")
    tempo_report(src_path, 'source     ')
    tempo_report(arr_path, 'arrangement')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
