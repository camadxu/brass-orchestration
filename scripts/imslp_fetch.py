#!/usr/bin/env python3
"""List and download score files from an IMSLP work page.

Why this exists: IMSLP gates direct file access behind a JS "friendlyredirect"
challenge and a disclaimer cookie, but the work page itself contains, for every
file, the internal storage path (/images/A/BB/NAME.pdf) and the file label
("Complete Score", "Trumpet 1 (Bb)", ...). The bytes are served unmetered from
https://s9.imslp.org/files/imglnks/usimg/A/BB/NAME, so we map one to the other.

One-time setup (needed once per host, since the cookie is per browser session):
  1. open https://imslp.org/wiki/<work page> in the browser tool
  2. click through the disclaimer (link text "I understand") — that sets the
     imslpdisclaimeraccepted cookie; it is NOT needed for the s9 file host.
In practice the s9 host needs no cookie at all: try a download first.

Usage:
  imslp_fetch.py --list URL
  imslp_fetch.py URL --get all|score|parts --out DIR [--max-mb N] [--dry-run]

Labels are human text from IMSLP; --get score matches 'Complete Score' style
labels, --get parts matches labelled instrument parts.
"""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/120.0.0.0 Safari/537.36')
FILE_HOST = 'https://s9.imslp.org/files/imglnks/usimg'

ENTRY_RE = re.compile(
    r'<div id="IMSLP(\d+)" class="we_file[^"]*">(.*?)(?=<div id="IMSLP\d+" class="we_file|$)',
    re.S)
LABEL_RE = re.compile(r'we_file_dlarrow">&#160;</span></span>([^<]{1,80})(?:\s*</span>)*\s*</a>', re.S)
PATH_RE = re.compile(r'href="(/images/[^"]+\.(?:pdf|zip|mxl|xml))"', re.I)
SIZE_RE = re.compile(r'(\d+(?:\.\d+)?)\s*MB', re.I)


def curl(url, out=None, head=False):
    cmd = ['curl', '-sS', '-L', '--compressed', '-A', UA, url]
    if head:
        cmd = ['curl', '-sS', '-I', '-L', '-A', UA, url]
    if out:
        cmd += ['-o', out, '-w', '%{http_code} %{size_download}']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'curl failed for {url}: {r.stderr.strip()}')
    return r.stdout


def list_files(page_url):
    html = curl(page_url)
    # split on every file block start; class lists vary, so match the id only
    starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div id="IMSLP(\d+)"', html)]
    out = []
    for i, (pos, fid) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else min(len(html), pos + 8000)
        body = html[pos:end]
        label = LABEL_RE.search(body)
        path = PATH_RE.search(body)
        if not path:
            continue
        size = SIZE_RE.search(body)
        lab = re.sub(r'\s+', ' ', (label.group(1) if label else '')).strip()
        if not lab or lab == '?':
            base = path.group(1).rsplit('/', 1)[-1]
            lab = re.sub(r'^IMSLP\d+-|^PMLP\d+-', '', base).rsplit('.', 1)[0][:60]
        out.append(dict(id=fid, label=lab, path=path.group(1),
                        size_mb=float(size.group(1)) if size else None))
    return out


MIRRORS = [
    'https://s9.imslp.org/files/imglnks/usimg',          # IMSLP main (US-hosted files)
    'https://imslp.eu/files/imglnks/euimg',             # IMSLP-EU (files marked EU)
    'https://petruccimusiclibrary.ca/files/imglnks/caimg',  # PML Canada
]


def direct_urls(path, fid):
    """Candidate download URLs, tried in order.

    The internal path is /images/A/BB/NAME; the stored object is
    A/BB/IMSLP{id}-NAME (the wiki page hides the id prefix, and a URL without
    it 404s). Which mirror holds the object depends on the copyright region
    the file was uploaded for, so try each in turn.
    """
    m = re.match(r'/images/(.+)$', path)
    if not m:
        return []
    head, _, name = m.group(1).rpartition('/')
    return [f'{host}/{head}/IMSLP{fid}-{name}' for host in MIRRORS]


def safe(name):
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('_')[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--get', choices=['all', 'score', 'parts'], default=None)
    ap.add_argument('--match', default=None, help='only files whose label matches this regex')
    ap.add_argument('--id', action='append', default=[], help='download these file ids only (repeatable)')
    ap.add_argument('--out', default='.')
    ap.add_argument('--max-mb', type=float, default=0)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    files = list_files(a.url)
    if not files:
        print('no files parsed — the page layout may have changed', file=sys.stderr)
        return 2
    total = sum(f['size_mb'] or 0 for f in files)
    print(f'{len(files)} files, listed size {total:.1f} MB')
    for f in files:
        print(f"  {f['id']:>8}  {(f['size_mb'] or 0):6.2f} MB  {f['label'][:44]:44} {f['path']}")
    if a.list or not a.get:
        return 0

    sel = files
    if a.get == 'score':
        sel = [f for f in files if re.search(r'complete score|full score|score', f['label'], re.I)]
    elif a.get == 'parts':
        sel = [f for f in files if not re.search(r'score', f['label'], re.I)]
    if a.match:
        sel = [f for f in sel if re.search(a.match, f['label'], re.I)]
    if a.id:
        sel = [f for f in files if f['id'] in a.id]
    os.makedirs(a.out, exist_ok=True)
    got = 0
    for f in sel:
        urls = direct_urls(f['path'], f['id'])
        if not urls:
            print(f'  skip {f["label"]}: unusable path {f["path"]}', file=sys.stderr)
            continue
        dest = os.path.join(a.out, safe(os.path.basename(f['path'])))
        if os.path.exists(dest) and os.path.getsize(dest) > 10000:
            print(f'  have  {dest}')
            got += 1
            continue
        if a.dry_run:
            print(f'  would {urls[0]}')
            continue
        ok, last = False, ''
        for url in urls:
            try:
                res = curl(url, out=dest)
            except RuntimeError as e:
                last = str(e)
                continue
            code, size = (res.split() + ['0'])[:2]
            if code == '200' and int(size) > 10000:
                ok = True
                break
            last = f'HTTP {code}'
        if ok:
            print(f"  ok   {f['label'][:30]:30} {os.path.getsize(dest)/1e6:.2f} MB {dest}")
            got += 1
        else:
            print(f'  FAIL {f["label"][:30]:30} {last}', file=sys.stderr)
            if os.path.exists(dest):
                os.unlink(dest)
    print(f'downloaded {got}/{len(sel)}')
    return 0 if got == len(sel) else 1


if __name__ == '__main__':
    sys.exit(main())
