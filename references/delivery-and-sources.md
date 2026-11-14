# Sending an existing edition and its sources («пришли X и исходники»)

The ask "send me the arrangement and the sources" is archaeology plus a labelled package, not
engraving. Nothing that already exists gets re-rendered.

## Where the truth lives

| Location | What it is |
|---|---|
| `/root/.hermes/artifacts/delivery/<slug>-<hash>/` | published packages on the VPS: score PDF, parts PDF, `*-complete.zip`, `delivery-manifest.json` |
| `/root/state/deliveries/…`, `/root/state/music-jobs/…` | working sets and older releases (v51, v54, v61 …) |
| `/root/.hermes/kanban/boards/<slug>/` | the task board; mtimes here change on read, so they do not date a build |
| `~/VPS-Storage/…` (on the PC) | **snapshot mirror**, can be weeks behind the VPS |
| `~/Загрузки/Telegram Desktop/` | what the owner already received, with the receipt mtime — sometimes the freshest PDF |

Compare mtimes on both sides before choosing:

```bash
find /root/.hermes/artifacts/delivery /root/state -maxdepth 3 -iname '*<slug>*' \
  -printf '%TY-%Tm-%Td %TH:%TM %10s %p\n' | sort -r | head -20
```

## The package's own numbers

`delivery-manifest.json` carries `sha256`, `pages` and page size in mm per file; `README.txt`
says what this revision changed (which bars, which accents, what was left untouched). Quote those
numbers instead of restating a version from memory, and check the manifest is the one belonging to
the files you are about to attach.

## Verify each PDF before attaching

```bash
pdfinfo   file.pdf | grep -E '^(Pages|Page size)'
pdftotext -f 1 -l 1 file.pdf - | head -15      # title, composer, voice list
```

Label every attachment with version, date, page count and instrumentation. A 16-page draft and a
21-page all-parts set are different deliverables; sending both unlabelled invites the owner to
print the wrong one.

## What «исходники» means

- **First reading: editable masters** — MusicXML / mscz, not the composer's scans. Bolero keeps
them inside the delivery zip under `editable-print-derivatives/` (one `.mscz` per part plus the
score layout); Parsifal as the working `.xml`. List the archive contents in the message (part
count, mscz count) so the owner need not unpack to find out.
- **Second reading: original scores.** Name them, their page counts and sizes, and offer to send:
  `source/wagner-original/*.pdf` (589 pages / 51 MB orchestral Peters, 262 pages / 24 MB vocal
  Schott), plus `source/originals/cello1-4.pdf` — the excerpt the transcription was actually typed
  from. Offer rather than dump: 50–75 MB through the messaging channel on this host is slow, the
gateway rides Tor, and the owner may not want them.
- If no original scan exists for the piece (Bolero has only a MusicXML), say so and offer the PD
  scan from IMSLP (`scripts/imslp_fetch.py`) instead of silence.

## Version honesty

A draft produced by a build script can leave no intermediate XML behind. Then "переложение новее
исходника" with both dates is the honest report; presenting an older master as the source of the
newer PDF is not. Same rule for a parts set that predates the score: say which is which.

## Small traps

- `ls -la --block-size=K` changes the size column to K units: `2872` there is 2.9 MB, not 2872
  bytes. Use `stat -c%s` when a size looks alarming.
- Keep attachment filenames ASCII and version-prefixed; Cyrillic paths can fail silently on the
  messaging side.
