#!/usr/bin/env python3
"""Delivery integrity check for a multi-part MusicXML delivery.

Answers, in one run:
  * does every part file carry exactly the master's music, bar by bar
    (pitch events, rests and unpitched onsets included)?
  * do the per-part note totals match, and what is the grand total?
  * with --baseline: which bars a later build actually changed, and does
    changed + unchanged == parts x bars?
  * with --markings: every <words>/<dynamics> direction of one part, for
    checking a README's claims about labels (invisible to pitch diffs).

The comparison core is the code that verified a 15-part / 356-bar delivery
(15/15 parts matched the master, and the note totals matched the arranger's own
check file). The argparse wrapper around it has not been exercised as-is — run it
once where the answer is already known and compare before trusting a clean
verdict.

Usage (lxml lives in ~/.venvs/tools):
  ~/.venvs/tools/bin/python check_delivery.py master.musicxml --parts parts/
  ~/.venvs/tools/bin/python check_delivery.py master.musicxml --parts parts/ \
      --baseline build10.musicxml
  ~/.venvs/tools/bin/python check_delivery.py master.musicxml --markings P15

Part files are matched to the master by internal part id, then by part name;
--order matches them by sorted filename instead, for archives whose ids and
names were localised on the way out.
"""
import argparse
import glob
import os
import sys
import zipfile

from lxml import etree


def ln(e):
    return etree.QName(e).localname


def load(path):
    """Return the XML root of a .musicxml or a .mxl (zip)."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist()
                        if n.endswith('.musicxml') and 'META-INF' not in n)
            return etree.fromstring(z.read(name))
    return etree.parse(path).getroot()


def sig(part_el):
    """Per bar: ((onset, token, duration), ...) with tokens r (rest),
    u<step><octave> (unpitched) or <step><alter><octave>."""
    out = []
    for m in part_el.findall('measure'):
        cur, last, ev = 0, None, []
        for el in m.findall('note'):
            dur = int(el.findtext('duration') or 0)
            if el.find('chord') is not None and last is not None:
                onset = last
            else:
                onset = last = cur
            if el.find('rest') is not None:
                tok = 'r'
            elif el.find('unpitched') is not None:
                u = el.find('unpitched')
                tok = 'u%s%s' % (u.findtext('display-step'), u.findtext('display-octave'))
            else:
                p = el.find('pitch')
                tok = '%s%s%s' % (p.findtext('step'), p.findtext('alter') or '0',
                                  p.findtext('octave'))
            ev.append((onset, tok, dur))
            if el.find('chord') is None:
                cur += dur
        for el in m:
            if ln(el) == 'backup':
                cur -= int(el.findtext('duration') or 0)
            elif ln(el) == 'forward':
                cur += int(el.findtext('duration') or 0)
        out.append(tuple(ev))
    return out


def note_count(part_el):
    return sum(1 for m in part_el.findall('measure')
               for n in m.findall('note') if n.find('rest') is None)


def part_names(root):
    return {sp.get('id'): (sp.findtext('part-name') or '')
            for sp in root.findall('part-list/score-part')}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('master')
    ap.add_argument('--parts')
    ap.add_argument('--baseline')
    ap.add_argument('--markings')
    ap.add_argument('--order', action='store_true')
    a = ap.parse_args(argv)

    mroot = load(a.master)
    mparts = mroot.findall('part')
    mids = [p.get('id') for p in mparts]
    names = part_names(mroot)
    msig = {i: sig(p) for i, p in zip(mids, mparts)}
    mcount = {i: note_count(p) for i, p in zip(mids, mparts)}
    bars = len(next(iter(msig.values())))
    bad = 0

    if a.markings:
        if a.markings not in msig:
            print('no such part id:', a.markings, 'have', mids)
            return 2
        p = mparts[mids.index(a.markings)]
        print('# %s %s' % (a.markings, names.get(a.markings, '')))
        for m in p.findall('measure'):
            dirs = []
            for d in m.findall('direction'):
                words = [w.text for w in d.iter('words')]
                dyn = [ln(x) for x in d.iter()
                       if ln(x) in ('f', 'ff', 'fff', 'mf', 'mp', 'p', 'pp', 'sf',
                                    'sffz', 'fp', 'ffz')]
                if words or dyn:
                    dirs.append('%s%s%s' % (d.get('placement') or '-', words or '',
                                            dyn or ''))
            if dirs:
                print('  bar %s: %s' % (m.get('number'), dirs))

    if a.parts:
        files = sorted(glob.glob(os.path.join(a.parts, '*.musicxml')) +
                       glob.glob(os.path.join(a.parts, '*.mxl')) +
                       glob.glob(os.path.join(a.parts, '*', '*.musicxml')) +
                       glob.glob(os.path.join(a.parts, '*', '*.mxl')))
        print('part files found: %d (master parts: %d)' % (len(files), len(mids)))
        if a.order and len(files) == len(mids):
            mapping = dict(zip(files, mids))
        else:
            mapping = {}
            for f in files:
                r = load(f)
                ps = r.findall('part')
                if len(ps) != 1:
                    print('  %-40s has %d parts, skipped' % (os.path.basename(f), len(ps)))
                    continue
                pid = ps[0].get('id')
                if pid not in msig:
                    want = (part_names(r).get(pid) or '').strip().lower()
                    pid = next((k for k, v in names.items()
                                if v.strip().lower() == want and want), None)
                if pid is None:
                    print('  %-40s UNMAPPED - retry with --order' % os.path.basename(f))
                    bad += 1
                    continue
                mapping[f] = pid

        seen = {}
        for f, pid in mapping.items():
            r = load(f)
            ps = r.findall('part')
            sub = sig(ps[0] if len(ps) == 1 else ps[mids.index(pid)])
            seen[pid] = seen.get(pid, 0) + 1
            if len(sub) != bars:
                print('  %-34s %s bars %d != master %d' % (pid, names.get(pid, ''), len(sub), bars))
                bad += 1
                continue
            diff = [i + 1 for i in range(bars) if sub[i] != msig[pid][i]]
            n = note_count(ps[0] if len(ps) == 1 else ps[mids.index(pid)])
            flag = 'MATCH' if not diff else 'DIFF ' + str(diff[:12])
            print('  %-4s %-22s notes %4d/%4d  %s'
                  % (pid, names.get(pid, '')[:22], n, mcount[pid], flag))
            if diff:
                bad += 1
        for pid in mids:
            if seen.get(pid, 0) == 0:
                print('  %-4s %-22s NO PART FILE' % (pid, names.get(pid, '')))
                bad += 1
        print('total notes in master: %d' % sum(mcount.values()))

    if a.baseline:
        broot = load(a.baseline)
        bids = [p.get('id') for p in broot.findall('part')]
        bparts = dict(zip(bids, broot.findall('part')))
        print('baseline parts: %d' % len(bids))
        changed = equal = 0
        for pid in mids:
            if pid not in bparts:
                print('  %-4s missing from baseline' % pid)
                bad += 1
                continue
            b = sig(bparts[pid])
            d = [i + 1 for i in range(min(bars, len(b))) if b[i] != msig[pid][i]]
            equal += bars - len(d)
            changed += len(d)
            if d:
                print('  %-4s %-22s changed bars: %s'
                      % (pid, names.get(pid, '')[:22], d))
        total = bars * len(mids)
        print('changed %d + unchanged %d = %d (parts x bars = %d): %s'
              % (changed, equal, changed + equal, total,
                 'consistent' if changed + equal == total else 'MISMATCH'))
        if changed + equal != total:
            bad += 1

    print('VERDICT:', 'clean' if not bad else '%d problem(s)' % bad)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
