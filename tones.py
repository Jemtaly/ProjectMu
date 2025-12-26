import sys
from dataclasses import dataclass
from fractions import Fraction
from typing import TextIO

import numpy as np

from .core import *


SOLFA = {
    "1":  0,
    "2":  2,
    "3":  4,
    "4":  5,
    "5":  7,
    "6":  9,
    "7": 11,
}

ALPHA = {
    "A":  9,
    "B": 11,
    "C": 12,
    "D": 14,
    "E": 16,
    "F": 17,
    "G": 19,
}


@dataclass
class Tone:
    pitch: "float"
    secs: "float" = 0.0


def flatten(music: Music, output: TextIO = sys.stderr) -> list[Tone]:
    unordered = {}
    i = 0
    for group in music.groups:
        lft = group.mod.lft
        lft = SOLFA[lft.solfa] + (lft.accid if lft.accid is not None else 0) + lft.octav * 12
        rgt = group.mod.rgt
        rgt = ALPHA[rgt.alpha] + (rgt.accid if rgt.accid is not None else 0) + rgt.octav * 12
        mod = rgt - lft
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
                Accid = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
                ctr = Fraction(0)

                def visit(element: Element, base=Fraction(1, 4)):
                    nonlocal ctr
                    if isinstance(element, TimedNote):
                        note = element.note
                        if isinstance(note, SAO):
                            if note.accid is not None:
                                Accid[note.solfa] = note.accid
                            note = SOLFA[note.solfa] + Accid[note.solfa] + note.octav * 12
                            curr.append(Tone(pitch=mod + note))
                        elif isinstance(note, Rest):
                            curr.append(Tone(pitch=-np.inf))
                        elif isinstance(note, Tied) and len(curr) == 0:
                            output.write(f"Warning: A tied note is found at the beginning of Passage {i}, which is considered as a rest\n")
                            curr.append(Tone(pitch=-np.inf))
                        time = element.time
                        time = Fraction(1, 2 ** time.und) * (2 - Fraction(1, 2 ** time.dot))
                        time = time * base
                        curr[-1].secs += time * 60 * mtd / bmp
                        ctr += time
                    else:
                        if isinstance(element, Rated):
                            rat = element.ratio
                            rtn = rat.n
                            rtd = rat.d if rat.d is not None else 2 ** (rtn.bit_length() - 1)
                            rat = Fraction(rtn, rtd)
                            visit(element.inner, base / rat)
                        elif isinstance(element, Angled):
                            for element in element.inners:
                                visit(element, base / 2)
                        elif isinstance(element, Braced):
                            for element in element.inners:
                                visit(element, base)

                for element in measure.elements:
                    visit(element)
                unordered[i] = curr
                if ctr != mtr:
                    output.write(f"Warning: Passage {i}, Measure {j} has wrong time signature, expected {mtr}, got {ctr}\n")
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
