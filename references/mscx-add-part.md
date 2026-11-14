# Adding an instrument to a MuseScore 4 master (.mscx)

Use when the owner approves "впишем <instrument> с начала" on an already
accepted edition. Goal: the same score plus one part, everything else byte-stable,
same style, and a fresh rev number.

## 0. Unpack and read the real format first

```bash
unzip -o score.mscz -d ms/          # -> ms/masterfix.mscx + ms/score_style.mss
head -c 120 ms/masterfix.mscx       # <museScore version="4.70"> = MuseScore 4 native
```

A MuseScore 3 install cannot open that file and there is no converter. Do the edit
where MuseScore 4 exists (this host keeps it as an AppImage at `/opt/musescore`
with `/usr/local/bin/mscore` as the wrapper); run it headless with
`QT_QPA_PLATFORM=offscreen HOME=/root`.

## 1. Render the untouched master first

```bash
mscore -S score_style.mss -o orig.pdf masterfix.mscx
pdfinfo orig.pdf | grep -E 'Pages|Page size'
```

The page geometry is in `score_style.mss` (A3 = `pageWidth 11.6929 in`), **not** in
the `.mscx`. Drop `-S` and the identical file renders 49 A4 pages instead of 11 A3
— which reads as "the layout is lost" when nothing was actually broken. Always
compare pages and page size against `delivery-manifest.json` before and after.

Do not use a MusicXML round-trip to get room for a new part: `-o x.musicxml` →
`-o x.pdf` on the same score gave 49 A4 pages. Breaks, frames and the style do not
survive it.

## 2. Part skeleton for a grand staff

Inspect a file that already contains a piano if possible (build a two-measure
test score from MusicXML, convert, and read the result) — the shape must be exact:

```xml
<Part id="14">
  <Staff>
    <eid>...</eid>
    <StaffType group="pitched"><name>stdNormal</name></StaffType>
    <bracket type="1" span="2" col="1" visible="1"/>
    <barLineSpan>1</barLineSpan>
  </Staff>
  <Staff>
    <eid>...</eid>
    <StaffType group="pitched"><name>stdNormal</name></StaffType>
  </Staff>
  <trackName>Piano</trackName>
  <Instrument id="piano">
    <longName>Piano</longName>
    <shortName>Pno</shortName>
    <trackName>Piano</trackName>
    <minPitchP>21</minPitchP><maxPitchP>108</maxPitchP>
    <minPitchA>21</minPitchA><maxPitchA>108</maxPitchA>
    <instrumentId>keyboard.piano</instrumentId>
    <clef staff="2">F</clef>
    <Channel><program value="0"/><controller ctrl="10" value="63"/><synti>Fluid</synti></Channel>
  </Instrument>
</Part>
```

- `<shortName>` is what prints on systems after the first; without it the staff
  has no name at all.
- Staff ids follow Part order. To insert above an existing part, renumber that part
  first (`<Part id="14">`/`<Staff id="14">` → 16 — count the occurrences, there are
exactly two), then insert the new Part before it and the new Staff bodies before
its body.
- Each staff body: `<Staff id="14">` → `<Measure>` per bar → `<voice>` with the
first measure carrying `<Clef>`, `<TimeSig>` and `<isHeader>1</isHeader>`.
- Unique `<eid>` per element; generate them deterministically (base64 of a counter)
and MuseScore accepts them.

## 3. What the new part plays

Deriving the notes from the bar's own material keeps the addition free of invented
harmony:

- read the source bars from the existing staves, per element: `<durationType>`,
  `<dots>`, `<Tuplet>` (`actualNotes`/`normalNotes`), `<Note><pitch><tpc>`;
- compute absolute ticks (`Division` is 480 per quarter) so beats are exact;
- take one attack per beat, or keep two eighths when the bar really has two plain
  eighths — copying tuplet chords verbatim drags in tuplet markers, so flatten to
  the beat instead;
- pad a short bar with a trailing rest so it sums to the meter;
- copy dynamics from the source staff you follow (`<Dynamic><subtype>pp</subtype>`),
  otherwise the part plays flat and the printed score looks unfinished.

## 4. Stems

MuseScore flips stems by pitch position when the direction is absent. Where the
owner wants a fixed direction, write it per chord:

```python
re.sub(r'<Chord>.*?</Chord>', force_up, block, flags=re.S)   # percussion: every chord
```

Insert `<StemDirection>up</StemDirection>` right after `<durationType>` when it is
missing and replace `down` when present. Piano: right hand up, left hand down — and
after renumbering the staff ids re-check the `staff_id == N` conditions in the
generator: one inverted comparison flips both hands while everything else looks
right.

## 5. Verification pass (quote these numbers)

Parse the produced `.mscx` back and assert:

- every bar of the new part sums exactly to the meter (`142/142`, none off);
- every note's pitch class also exists in that bar's source material (`0` invented);
- the untouched staves parse identical to the input (`1..13 identical`, renumbered
  percussion identical to its old self);
- explicit stem directions count matches the intent (`1688/1688 up`).

The same XML re-parsed by `ElementTree` is enough — no need to trust the generator's
own counters, which is where an inverted condition hides.

## 6. Render and look

```bash
mscore -S score_style.mss -o rev13.pdf  rev13.mscx
mscore -S score_style.mss -o rev13.mscz rev13.mscx
pdftoppm -r 300 -png -f 1 -l 1 rev13.pdf page1   # 300 dpi, then crop
```

Check page 1, one dense tutti page and the last page at 300 dpi: instrument name,
bracket, clefs, stem directions, the piano's notes against the staves above, the
final chord. A 110-dpi thumbnail makes a correct grand staff look squashed — crop
instead of judging the whole page.

## 7. Delivery

New rev folder, previous rev untouched, README with what was added, what plays,
what was verified, sha256 of both outputs, and the honest layout sentence
("12 страниц A3 вместо 11, перевороты сдвинулись; вернуть 11 — подгоню межстрочные").
