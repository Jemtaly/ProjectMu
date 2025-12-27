import sys
from fractions import Fraction
from typing import TextIO

from . import ast
from .tone import Tone


SOLFA: dict[ast.Solfa, int] = {
    "1":  0,
    "2":  2,
    "3":  4,
    "4":  5,
    "5":  7,
    "6":  9,
    "7": 11,
}

ALPHA: dict[ast.Alpha, int] = {
    "C": -9,
    "D": -7,
    "E": -5,
    "F": -4,
    "G": -2,
    "A":  0,
    "B":  2,
}


def flatten(music: ast.Music, output: TextIO = sys.stderr) -> list[Tone]:
    unordered = {}
    i = 0
    for group in music.groups:
        sao = group.mod.sao
        srn = SOLFA[sao.solfa] + (sao.accid if sao.accid is not None else 0) + sao.octav * 12
        aao = group.mod.aao
        arn = ALPHA[aao.alpha] + (aao.accid if aao.accid is not None else 0) + aao.octav * 12
        mod = arn - srn
        bmp = group.bmp
        mtr = group.mtr
        mtn = mtr.n
        mtd = mtr.d
        mtr = Fraction(mtn, mtd)
        for passage in group.passages:
            i += 1
            curr = []
            j = 0
            for measure in passage.measures:
                j += 1
                Accid: dict[ast.Solfa, int] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
                ctr = Fraction(0)

                def visit(element: ast.Element, base=Fraction(1, 4)):
                    nonlocal ctr
                    if isinstance(element, ast.TimedNote):
                        note = element.note
                        if isinstance(note, ast.SAO):
                            if note.accid is not None:
                                Accid[note.solfa] = note.accid
                            rel = SOLFA[note.solfa] + Accid[note.solfa] + note.octav * 12
                            curr.append(Tone(pitch=mod + rel))
                        elif isinstance(note, ast.Rest):
                            curr.append(Tone(pitch=None))
                        elif isinstance(note, ast.Tied) and len(curr) == 0:
                            output.write(f"Warning: A tied note is found at the beginning of Passage {i}, which is considered as a rest\n")
                            curr.append(Tone(pitch=None))
                        time = element.time
                        time = Fraction(1, 2 ** time.und) * (2 - Fraction(1, 2 ** time.dot))
                        time = time * base
                        curr[-1].secs += time * 60 * mtd / bmp
                        ctr += time
                    else:
                        if isinstance(element, ast.Rated):
                            rat = element.ratio
                            rtn = rat.n
                            rtd = rat.d if rat.d is not None else 2 ** (rtn.bit_length() - 1)
                            rat = Fraction(rtn, rtd)
                            visit(element.inner, base / rat)
                        elif isinstance(element, ast.Angled):
                            for element in element.inners:
                                visit(element, base / 2)
                        elif isinstance(element, ast.Braced):
                            for element in element.inners:
                                visit(element, base)

                for element in measure.elements:
                    visit(element)
                if ctr != mtr:
                    output.write(f"Warning: Passage {i}, Measure {j} has wrong time signature, expected {mtr}, got {ctr}\n")
            unordered[i] = curr
    if music.final is not None:
        nums = music.final
    else:
        nums = unordered.keys()
    tones = []
    for num in nums:
        if num not in unordered:
            output.write(f"Warning: Passage {num} not found, skipping\n")
        else:
            tones.extend(unordered[num])
    return tones
