# Correcting a delivered MusicXML master without disturbing anything else

Use when the owner approves a small, enumerated set of fixes to a master they sent
(a misplaced label, a broken rest, one wrong note). The output is the same score
with those changes and nothing else touched — provable by diff, not by assertion.

## 1. Identify the input

```bash
sha256sum master.musicxml          # must match the hash quoted in their report
cp master.musicxml work.musicxml
```

Their report often names the build (`сборка 13`), a hash prefix and the delivery
archive. A stale cached copy from an earlier build is the usual reason an edit
lands in the wrong file.

## 2. Instrument substitution without changing the music

When an approved edit replaces an instrument on existing staves, first distinguish an identity/name change from deleting and redistributing the lines. List the exact parts and metadata to change, resolve duplicate names/numbering across the whole section, and select the destination clef by the intended notation convention. In MusicXML, changing the part name or clef does not move `<pitch>` values; `<transpose>` is a separate sounding-pitch instruction. Preserve all pitch events unless the owner separately approves transposition or octave displacement. If the new instrument makes some passages unusually high or low, report those passages for a separate decision rather than silently rewriting them. Verify after the edit that each part's event sequence (pitch, onset, duration, ties) is unchanged, and render the affected pages to inspect clefs, labels, ledger lines, and collisions.

## 3. Anchored string surgery

Delivered masters mix formatting: some parts are pretty-printed, others are one
2 MB line. Parse-and-reserialize would reflow the whole document, so the diff stops
being evidence. Replace text instead, scoped to the part:

```python
src = open('work.musicxml', encoding='utf-8').read()

i = src.index('<part id="P15">')          # part that owns the bar
j = src.index('<part id="P16">', i)       # next part, or len(src) for the last
seg = src[i:j]

old = '<measure number="342"><direction placement="below">'
new = ('<measure number="342"><direction placement="above"><direction-type>'
       '<words>Там-там</words></direction-type></direction>'
       '<direction placement="below">')
assert seg.count(old) == 1, seg.count(old)   # never edit without this
out = src[:i] + seg.replace(old, new) + src[j:]
```

- Copy the exact markup of a neighbouring, correct instance (here bars 97 and 286)
  so attribute order and `<placement>` match what the rest of the file uses.
- `<measure number="N">` is not unique across the file — it appears once per part.
  Only the part slice makes it unique.
- Verify uniqueness with `count(...) == 1` before replacing; a silent 0-or-2 match is
  how the wrong bar gets edited.

## 4. Rebuild the `.mxl`

`.mxl` is a zip whose first entry must be an uncompressed `mimetype`:

```python
import zipfile
with zipfile.ZipFile('master.mxl') as z:
    container = z.read('META-INF/container.xml')
with zipfile.ZipFile('fixed.mxl', 'w') as z:
    zi = zipfile.ZipInfo('mimetype')
    z.writestr(zi, 'application/vnd.recordare.musicxml', compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml', container, compress_type=zipfile.ZIP_DEFLATED)
    z.write('work.musicxml', 'score.musicxml', compress_type=zipfile.ZIP_DEFLATED)
```

Then render the `.mxl` itself once (`QT_QPA_PLATFORM=offscreen mscore3 -o check.pdf fixed.mxl`).
A container that no app can open is not a delivery. Compare
`unzip -p fixed.mxl score.musicxml | sha256sum` with the loose file: they must be
identical.

## 5. Verification pass (run it, quote it)

For each part, build concert-pitch events per bar (`compare.py::concert` does this)
and assert:

- every part's pitch multiset equals the input's — the fix moved no note;
- total pitched/unpitched notes unchanged;
- the set of bars whose event tuples differ is exactly the list you intended;
- for a `<words>` fix, the part's word map gained exactly the new bar and lost none;
- `validate_brass.py` hard-error and warning counts are identical before/after.

A useful summary line to report: `measures changed (music-level): [('P10', 98)]`,
`notes 7416 → 7416`, `words before {97,110,286} → after {97,110,286,342}`.

## 6. Show the two bars

Renders beat prose for a notation fix. Split the touched part out, render both
versions at the same dpi, crop the same box and stack them:

```bash
python3 scripts/split_part.py before.musicxml P10 before_p10.musicxml
python3 scripts/split_part.py after.musicxml  P10 after_p10.musicxml
pdftoppm -r 300 -png -f 1 -l 1 before_p10.pdf before_p10
pdftoppm -r 300 -png -f 1 -l 1 after_p10.pdf  after_p10
```

Then crop identical rectangles (`Image.crop`) and stack. Render both at the same
dpi — stacking a 130-dpi crop against a 150-dpi one produces a comparison nobody
can read. Attach the result; label the halves "до / после" in the caption.

## 7. Delivering

- ASCII filenames only (`Shostakovich10-II-build13-fixed.musicxml`), both formats,
  plus the `sha256` of each in the message so the owner can verify by hash.
- Keep the untouched input and the fixed output in one folder with a short
  `FIX-REPORT.md` (what changed, what was verified, what was deliberately not
  done) — the owner forwards that to their other assistant instead of retyping
  your chat message.
