# Comparing an arrangement with its source score

Read this before quoting any number from `scripts/compare_scores.py`. Half the
metrics it prints look alarming on a healthy transcription; two of them decide
the answer.

## Inputs

- Arrangement: the **master** MusicXML from the delivery archive, never the PDF.
  If the question is "is this the file you sent me", compare `sha256sum`, not
  mtimes: a PDF's internal `CreationDate` is when it was rendered, the file mtime
  is when the archive was unpacked, and the two can sit an hour apart.
- Source: the orchestral score as MusicXML. Both `.mxl` files are zips;
  `unzip -o x.mxl -d /tmp/x` and use `score.musicxml`.
- Check the source's part list first: a "working" transcription may have staves
  deliberately removed (a percussion staff dropped for an earlier pass will look
  like "extra hits" in the arrangement). Compare part counts and read any meta
  file that describes the removals before calling anything an error.
- Write every probe as a script file and run it, rather than an inline heredoc:
  a multi-megabyte `score.musicxml` referenced from the command line is refused
  by the command scanner before it runs. `scripts/check_delivery.py` covers the
  integrity pass; keep one-off probes next to it as files.

## Structural map before pitch comparison

Before extracting a selected MusicXML range, traverse each part from its beginning and carry forward active `divisions`, time signature and transposition, updating attributes before filtering measures; these attributes are inherited, so initializing at the first selected bar can corrupt onset, duration and concert-pitch comparisons. Process `backup`, `forward`, chords and grace notes when building the timeline, and check representative multi-voice bars explicitly before trusting a match score.

Before interpreting pitch-coverage metrics, build a compact source-to-arrangement map of meter changes, rehearsal marks, tempo directions, and bar-number anchors. Do not trust a filename such as “bars 1–59” or identical-looking measure numbers as proof of alignment; establish at least two distinctive musical anchors with stable timing and transposition. As a diagnostic only, compare sounding pitch-class sets on a fine time grid while sweeping possible global mod-12 transpositions, then inspect per-bar matches and deviations; pitch-class coverage cannot establish exact spelling, voice provenance, or editorial intent. Confirm a proposed map with distinctive rhythm/line contours and structural anchors, not its aggregate score alone. Compare rehearsal marks as a separate textual layer: a missing, shifted, or renumbered mark is an editorial discrepancy and a cross-check on alignment, but do not automatically correct it or treat it alone as proof of a shifted map. Treat absence of `<metronome>` independently from absence of tempo guidance: inspect `<words>`, `<sound tempo>`, and visible score text before declaring tempo information omitted.

**Pitfall:** Map rehearsal numbers, meter changes, and tempo directions before trusting same-numbered bars — MusicXML pitch comparators cannot detect shifted or omitted editorial landmarks.

## The two metrics that decide

1. **Added pitch classes per bar** (section 2 of the script): the arrangement
   contains a pitch class the whole source bar does not. Short list, each entry
   either a wrong note or a deliberately added line. Wind and horn colour never
   shows up here, so the list stays small — in a 356-bar movement it was 20 bars.
2. **Line relation + deviations** (section 5): a copied line keeps one constant
   interval to its source (an octave, two octaves, a twelfth). The modal interval
   is the copy transposition; the few notes off it are the candidates. Worked
   case: one trombone part tracked the first violins at −24 semitones for 65 of
   68 notes; the three deviations were the whole question, and one of them was
   the *source's* octave typo that the arrangement had silently fixed.

## Metrics that mislead

- **Whole-score bar coverage** ("only 65 of 356 bars hold every source pitch
  class"). In dense chromatic bars no 11-voice brass choir can hold ten pitch
  classes; the number says nothing about quality. Use per-source-part survival
  instead: it shows what the reduction drops on purpose (horns and trumpets lose
  most of their bars' pitch classes; trombone, bass trombone and tuba lines
  survive with one bar lost each).
- **Provenance by best match.** Octave doublings make piccolo@−12, flute@−24 and
  oboe@−12 identical, so "this line comes from the piccolo" is usually wrong and
  always unfalsifiable. Report the interval relation, not an instrument name.
- **Attack counts on unpitched staves.** Percussion is `<unpitched>`, not
  `<pitch>`; a pitch-only parser reads every percussion part as silence.

## Turning a deviation into a verdict

- One transcription disagreeing with the arrangement = candidate, not error. Say
  which evidence would decide it.
- Two or three independent editions agreeing against the arrangement = error.
  Per-bar ledgers of several editions are the cheapest source of that proof:
  `{'parts': {'P23': {'bars': {'155': [[onset, duration, midi], ...]}}}}`, midi in
  concert pitch, bar keys as strings.
- Check the source for its own defects before blaming the arrangement: octave
  typos (a B6 where every edition has B5) and transposition slips are common in
  machine transcriptions, and the arrangement is sometimes the correct one.
- Lineage is not evidence. A deviation carried unchanged through several builds
  looks deliberate and still can be wrong: an octave-typo-shaped candidate stayed
  the same from build 4 to build 9 while all three editions disagreed with it, so
  it was an inherited slip, not a decision. Say "present since build N" as a fact
  about the file, never as a reason to downgrade a proven error.

## Tempo

MusicXML can carry a printed `<metronome>` and a different `<sound tempo>`. "The
score says quarter = 175" is wrong when the printed mark is `half = 116` and 175
is only playback. Report printed mark and playback separately, then compare the
arrangement's own mark against both.

## After a fix lands (the owner sends build N+1)

A README that says the fix was applied is a claim. Verify three things, in this
order:

1. **The master.** Parse the new master and print the bar's events: the agreed
   note must be there with the new `step`/`alter`/`octave`.
2. **Every part file.** Delivery archives ship parts as separate `.mxl` (zips):
   unzip each before parsing, or the parser dies on `Start tag expected, '<' not
   found`. Part names inside those files may be localised (`Тромбон 6`) while the
   master uses English (`Trombone 6`), so match by **position in the archive**, not
   by name — name matching reports every part as missing. Compare pitch events and
   the unpitched onset lists; expect zero differences per part.
3. **The deciding metric.** Re-run the interval profile of that line: the count of
   notes on the modal interval must rise by exactly the number of notes fixed
   (65/68 → 67/68 for two notes), and no new deviations may appear elsewhere.

When the owner sends build N+1 with several changes bundled, also diff it against
the previous build per part and bar (pitch events and onsets) and report the counts
with bar lists: it separates "what this build changed" from "what I asked for",
and it catches a change nobody mentioned in the README.

Do the arithmetic on that diff: changed + unchanged must equal parts x bars
(11 changed + 5329 unchanged = 15 x 356 on a 15-part, 356-bar delivery). A proof
file concluding "differences exist" usually only means the two files are not
byte-identical - reconcile the numbers before reporting a lineage break, and
recount the per-part note totals the delivery's own check file prints (rests
excluded, `<unpitched>` counted): a full match settles the whole integrity
paragraph, one mismatch names the wrong file.

When the new build adds an instrument to an existing staff (a tam-tam written on
 the bass-drum staff), verify it structurally: that `score-part` now carries two
`score-instrument` children, and that the new hits appear as extra `<unpitched>`
onsets on that staff's bars. A pitch-only view of the part shows those bars empty,
which reads as "the addition was forgotten" when it is in fact there.

Then read the text layer, which no pitch diff sees. `<words>` and `<dynamics>` are
invisible to event comparison, so check each label the README promises one at a
time: three tam-tam strikes with the word over two of them and only `ff` over the
third is a real, small defect that every pitch check passes. Same for an
instrument switch ("B. drum" after a tam-tam passage) - a missing switch word
leaves the player reading the previous instrument. Print directions per bar with
`scripts/check_delivery.py master.musicxml --markings P15`, then confirm on the
rendered part page, because that is where the player sees it.

## Reporting

Verdict first — bar, note, what it should be, and the evidence that decides it.
Then, separately: the arranger's own additions (pedals, counter-lines) as
choices, not errors. Then what was not checked (dynamics, articulations, live
play). A report that is only a list of "candidates for review" is not a report.

When the fixes will be applied or forwarded one at a time, write **one small
`.md` per fix** plus an index. Each file stands alone: the location (master file,
part and its internal id, bar, which note of the bar), what stands and what it
must become (concert pitch plus the MusicXML `step`/`alter`/`octave` edit), the
evidence, and the command that re-checks it after the edit. Put the status on
line one — proved fix / proposal awaiting a decision / choice to be made by ear —
because the owner forwards each file to the section it concerns and never reads
two files together.
