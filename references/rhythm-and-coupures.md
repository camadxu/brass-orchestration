# Rhythm, written values and coupures

Two independent checks that the brass validator does not make: `validate_brass.py` judges pitches
and load, it does not read measure length or the written value of a note. Run both before a delivery.

## 1. Rhythm and notation consistency

```bash
"$PY" "$SK/scripts/check_rhythm.py score.musicxml            # text, RESULT PASS / FAIL, exit 1 on any issue
"$PY" "$SK/scripts/check_rhythm.py score.musicxml --json     # [{part, bar, kind, text}]
```

| kind | meaning | usual cause |
|---|---|---|
| `measure length` | a voice does not fill the time signature in force | a rest dropped when a part was rewritten; a wrong `<duration>` |
| `value` | `<type>`/`<dot>` disagree with `<duration>/<divisions>` | a merge step that relabels notes from a table written for other divisions |
| `tie`, `slur`, `hairpin` | a stop without a start, a start without a stop; a tie is tracked per voice and pitch | one end removed or left in a bar that became a rest; a note under a tie moved to another pitch or octave |
| `rehearsal` | a number used twice or out of order (first part) | a coupure that renumbers bars, not marks |
| `bar numbers`, `bar count` | numbers not sequential (a pickup may be 0); parts of different length | a hand edit |

Engraving programs draw the written value, not the duration: a half note labelled `whole` sounds
right and reads as six beats in a 4/4 bar. The owner sees it on the page, the pitch checks do not.
After any script that touches `<type>`, rerun the check on the built file, not on the plan.

Tuplets (`<time-modification>`), grace notes and whole-measure rests are outside the value check;
a value that is no plain note value is reported as such.

## 2. Coupures

A coupure removes bars from every part of a built master. It is a stage of its own on top of the
current master; the passes that write notes keep working in the original bar numbers.

- Cut whole phrases: from the bar before an entry to the bar before the next entry, so that the
  theme statements kept are complete ones. Write the map down (original numbers) before building.
- A seam is a new junction of two keys, tempos and dynamics. At the first kept bar, in every part:
  clef, key and time in force are what they were in the source; a part that plays and carries no
  dynamic gets the one in force in the source; the tempo in force is restated.
- Ties, slurs and hairpins whose other end was cut lose that end; a crescendo that lost its stop is
  closed after the last note before the seam. A hairpin left open into a rest is an error.
- Rehearsal marks keep their original numbers. A mark that fell into the cut is gone; do not renumber.
- Bar numbers change, original numbers do not: in the report and to the owner, name original numbers.

Prove the cut, do not assert it:

1. every bar of the cut file equals the source bar it came from, element by element, except the
   seam bars, and each of those differs only where the build report lists a fix;
2. `check_rhythm.py` on the cut file: nothing new against the source;
3. dynamics in force at every seam bar equal the source, in every part that plays;
4. rehearsal marks of the cut file = those of the source minus the cut bars;
5. render the pages with both seams and look at them: the text of the coupure over the seam bar,
   the dynamic under the first note, no line hanging over the barline;
6. duration of the rendered audio against the expected one.

Make the alternative (a shorter cut that keeps a climax, a longer one that keeps a solo) as a second
file from the same master; the owner chooses between built variants, not between descriptions.

## 3. Before a delivery

```bash
"$PY" "$SK/scripts/validate_brass.py" score.musicxml --json > validate.json
"$PY" "$SK/scripts/check_rhythm.py" score.musicxml > rhythm.txt; echo "rc=$?"
"$PY" "$SK/scripts/check_rhythm.py" parts/<part>.musicxml | tail -1     # every part
```

Read `validate_brass.py` by kind: range-profile limits for a professional choir (written C5–F5 in
trombones, pedal notes in the bass trombones) are the arrangement's register, not errors, when the
owner has accepted it; thousands of parallel-octave warnings in a unison passage are the texture.
What is never acceptable: a measure that does not add up, a value that disagrees with its duration,
a line end without its start.
