# Reference corpus (local)

Root: `/home/uui33/orchestration/reference` — 44 MB, 59 PDFs, all public domain,
collected 2026-10-30 with `scripts/imslp_fetch.py`.

## Study scores: brass ensemble

- `imslp/ewald_op5/` — Victor Ewald, Brass Quintet No.1 Op.5: 25 files, several
  editions (Sibley scans of the original 5 parts + PMLP typeset score and parts).
  The oldest and cleanest example of functional 5-voice brass writing.
- `imslp/ewald_op6/` — Quintet No.2 Op.6, 11 files (typeset score + 5 parts,
  hosted on IMSLP-EU).
- `imslp/ewald_op7/` — Quintet No.3 Op.7, 5 files.
- `gabrieli/` — Giovanni Gabrieli, Canzon septimi toni a 8 (brass octet full score
  + parts) and Canzon septimi et octavi toni a 12, Ch.182 (score + parts).
  Study these for antiphonal cori spezzati placement and for how a 12-voice
  texture is thinned to 8 without losing the harmony.

## Study scores: orchestral brass

- `wagner_tannhauser/PMLP21243-Wagner_Tannh_..._overture.pdf` — Tannhäuser
  overture, full score, 22 pp. Horns 1-4, trumpets 1-3, trombones 1-3, tuba;
  check how Wagner builds the climax without letting the trumpets run high for
  long, and how horn 1-4 pair against the trombones.

## Treatises

- `rimsky_principles/` — Rimsky-Korsakov, Principles of Orchestration, per-chapter
  English PDFs (Ch.1-4, 6, plus complete text). Chapter 2 (melody) and Chapter 3
  (harmony) are the ones to re-read before any arrangement; the string/woodwind
  chapters still teach doubling logic.
- `berlioz_treatise_djvu.txt` — Berlioz, A Treatise on Modern Instrumentation and
  Orchestration (Novello translation, OCR text, 637 KB). Searchable prose on
  instrument character; OCR errors are frequent, quote with care.

## How to extend

```
python3 scripts/imslp_fetch.py --list 'https://imslp.org/wiki/<Work>_(<Composer>)'
python3 scripts/imslp_fetch.py URL --get score --out DIR
python3 scripts/imslp_fetch.py URL --get all --match '^Chapter' --out DIR
python3 scripts/imslp_fetch.py URL --get all --id 461955 --out DIR
```

Only fetch works that are public domain in the relevant jurisdiction, and say in
any deliverable which edition the arrangement was based on.
