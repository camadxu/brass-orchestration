"""Black-box tests of check_rhythm.py; every fixture is a temporary file."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'check_rhythm.py'


def score(*parts, rehearsal=''):
    """Minimal partwise score; each part is the body of its measures."""
    body = ''.join(f'<part id="P{i + 1}">{p}</part>' for i, p in enumerate(parts))
    return ("<?xml version='1.0' encoding='UTF-8'?><score-partwise version='4.0'><part-list>"
            "<score-part id=\"P1\"><part-name>Trombone 1</part-name></score-part></part-list>"
            f'{rehearsal}{body}</score-partwise>')


ATTR = ('<attributes><divisions>48</divisions><key><fifths>-3</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time>'
        '<clef><sign>C</sign><line>4</line></clef></attributes>')


def note(kind, pitch, ties=()):
    """A note of the written value `kind`; ties is a subset of ('start', 'stop')."""
    dur = {'whole': 192, 'half': 96, 'quarter': 48}[kind]
    step, octv = pitch[0], pitch[-1]
    alter = f"<alter>{-len(pitch[1:-1])}</alter>" if pitch[1:-1] else ''
    t = ''.join(f'<tie type="{x}" />' for x in ties)
    n = '<notations>' + ''.join(f'<tied type="{x}" />' for x in ties) + '</notations>' if ties else ''
    return (f'<note><pitch><step>{step}</step>{alter}<octave>{octv}</octave></pitch><duration>{dur}</duration>'
            f'{t}<type>{kind}</type>{n}</note>')


def rest(kind):
    dur = {'whole': 192, 'half': 96, 'quarter': 48}[kind]
    return f'<note><rest /><duration>{dur}</duration><type>{kind}</type></note>'


def bar(number, *content):
    return f'<measure number="{number}">{"".join(content)}</measure>'


class RhythmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, text, *extra):
        path = self.root / 'score.musicxml'
        path.write_text(text, encoding='utf-8')
        r = subprocess.run([sys.executable, '-I', str(SCRIPT), str(path), *extra], capture_output=True, text=True, encoding='utf-8')
        return r.returncode, r.stdout, r.stderr

    def issues(self, text):
        rc, out, err = self.run_cli(text, '--json')
        self.assertEqual(rc, 1, err)
        return [(i['part'], i['bar'], i['kind']) for i in json.loads(out)]

    def test_clean_score_passes_with_exit_zero(self):
        part = bar(1, ATTR, note('half', 'Gb3'), note('half', 'Gb4', ('start',))) + bar(2, note('half', 'Gb4', ('stop',)), rest('half'))
        rc, out, err = self.run_cli(score(part))
        self.assertEqual((rc, err), (0, ''))
        self.assertIn('0 issue(s)', out)
        self.assertTrue(out.endswith('RESULT PASS\n'), out)

    def test_half_note_labelled_whole_is_reported(self):
        """The defect of the delivered pass 1: 2 quarters of sound written as a whole note."""
        wrong = '<note><pitch><step>G</step><alter>-1</alter><octave>3</octave></pitch><duration>96</duration><type>whole</type></note>'
        part = bar(1, ATTR, wrong, rest('half'))
        self.assertEqual(self.issues(score(part)), [('P1', '1', 'value')])
        self.assertIn('whole written, duration half', self.run_cli(score(part))[1])

    def test_dotted_value_and_tuplet_are_not_flagged(self):
        dotted = '<note><pitch><step>C</step><octave>4</octave></pitch><duration>144</duration><type>half</type><dot /></note>'
        tuplet = ('<note><pitch><step>D</step><octave>4</octave></pitch><duration>32</duration>'
                  '<time-modification><actual-notes>3</actual-notes><normal-notes>2</normal-notes></time-modification>'
                  '<type>quarter</type></note>')
        part = bar(1, ATTR, dotted, note('quarter', 'C5')) + bar(2, tuplet * 3, rest('half'))
        rc, out, _ = self.run_cli(score(part))
        self.assertEqual(rc, 0, out)

    def test_grace_note_is_not_flagged(self):
        """A grace note carries <type> but no <duration>; it is outside the value check."""
        grace = '<note><grace slash="yes" /><pitch><step>D</step><octave>4</octave></pitch><type>eighth</type></note>'
        rc, out, _ = self.run_cli(score(bar(1, ATTR, note('half', 'C4'), grace, note('half', 'Eb4'))))
        self.assertEqual((rc, out.endswith('RESULT PASS\n')), (0, True), out)

    def test_tied_chord_is_clean_and_a_missing_stop_is_reported(self):
        """Ties are tracked per pitch: a chord ties several notes at once."""
        def chord(n):
            return n.replace('<note>', '<note><chord />')
        start = bar(1, ATTR, note('whole', 'Gb3', ('start',)), chord(note('whole', 'Gb4', ('start',))))
        tied = score(start + bar(2, note('whole', 'Gb3', ('stop',)), chord(note('whole', 'Gb4', ('stop',)))))
        rc, out, _ = self.run_cli(tied)
        self.assertEqual((rc, out.endswith('RESULT PASS\n')), (0, True), out)
        broken = score(start + bar(2, note('whole', 'Gb3', ('stop',)), chord(note('whole', 'Gb4'))))
        self.assertEqual(self.issues(broken), [('P1', '', 'tie')])
        self.assertIn('Gb4', self.run_cli(broken)[1])
        leap = score(start + bar(2, note('whole', 'Gb3', ('stop',)), chord(note('whole', 'G4', ('stop',)))))
        self.assertEqual(self.issues(leap), [('P1', '2', 'tie'), ('P1', '', 'tie')])   # a tie that ends on another pitch

    def test_pickup_numbered_zero_is_not_flagged(self):
        one = ATTR.replace('<beats>4</beats>', '<beats>1</beats>')
        four = '<attributes><time><beats>4</beats><beat-type>4</beat-type></time></attributes>'
        pickup = f'<measure number="0" implicit="yes">{one}{note("quarter", "C4")}</measure>'
        rc, out, _ = self.run_cli(score(pickup + bar(1, four, note('whole', 'C4'))))
        self.assertEqual((rc, out.endswith('RESULT PASS\n')), (0, True), out)

    def test_short_voice_after_backup_is_reported(self):
        part = bar(1, ATTR, note('whole', 'C4'), '<backup><duration>192</duration></backup>', note('half', 'G3'))
        self.assertEqual(self.issues(score(part)), [('P1', '1', 'measure length')])

    def test_wrong_time_signature_length_is_reported(self):
        five = ATTR.replace('<beats>4</beats>', '<beats>5</beats>')
        part = bar(1, five, note('whole', 'C4'))
        self.assertEqual(self.issues(score(part)), [('P1', '1', 'measure length')])
        self.assertIn('4 of 5 quarters (5/4)', self.run_cli(score(part))[1])

    def test_tie_slur_and_hairpin_without_a_start_or_stop(self):
        tie = bar(1, ATTR, note('half', 'C4', ('stop',)), rest('half'))
        slur = ('<note><pitch><step>C</step><octave>4</octave></pitch><duration>192</duration><type>whole</type>'
                '<notations><slur type="stop" number="1" /></notations></note>')
        wedge = '<direction><direction-type><wedge type="stop" number="1" /></direction-type></direction>'
        kinds = {k for _, _, k in self.issues(score(tie, bar(1, ATTR, slur), bar(1, ATTR, note('whole', 'C4'), wedge)))}
        self.assertEqual(kinds, {'tie', 'slur', 'hairpin'})
        open_ = ('<direction><direction-type><wedge type="crescendo" number="1" /></direction-type></direction>'
                 '<note><pitch><step>C</step><octave>4</octave></pitch><duration>192</duration><type>whole</type></note>')
        self.assertEqual(self.issues(score(bar(1, ATTR, open_))), [('P1', '', 'hairpin')])

    def test_parts_with_different_bar_counts(self):
        two = bar(1, ATTR, note('whole', 'C4')) + bar(2, note('whole', 'C4'))
        rc, out, _ = self.run_cli(score(bar(1, ATTR, note('whole', 'C4')), two))
        self.assertEqual(rc, 1)
        self.assertIn('parts have different numbers of bars', out)

    def test_rehearsal_numbers_twice_or_out_of_order(self):
        part = bar(1, ATTR, '<direction><direction-type><rehearsal>9</rehearsal></direction-type></direction>', note('whole', 'C4')) \
            + bar(2, '<direction><direction-type><rehearsal>9</rehearsal></direction-type></direction>', note('whole', 'C4'))
        self.assertEqual(self.issues(score(part)), [('P1', '', 'rehearsal')] * 2)      # twice, and out of order
        self.assertIn('used more than once: [9]', self.run_cli(score(part))[1])


if __name__ == '__main__':
    unittest.main()
