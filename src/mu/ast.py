from dataclasses import dataclass
from typing import Literal


Solfa = Literal["1", "2", "3", "4", "5", "6", "7"]
Alpha = Literal["C", "D", "E", "F", "G", "A", "B"]


@dataclass
class Music:
    groups: "list[Group]"
    final: "list[int] | None"


@dataclass
class Group:
    mod: "Mode"
    mtr: "Metre"
    bmp: "int"
    passages: "list[Passage]"


@dataclass
class Passage:
    measures: "list[Measure]"


@dataclass
class Measure:
    elements: "list[Element]"


@dataclass
class TimedNote:
    note: "Note"
    time: "Time"


@dataclass
class Braced:
    inners: "list[Element]"


@dataclass
class Angled:
    inners: "list[Element]"


@dataclass
class Rated:
    ratio: "Ratio"
    inner: "Element"


Element = TimedNote | Braced | Angled | Rated


@dataclass
class Ratio:
    n: "int"
    d: "int | None"


@dataclass
class Rest:
    pass


@dataclass
class Tied:
    pass


@dataclass
class SAO:
    solfa: "Solfa"
    accid: "int | None"
    octav: "int"


Note = Rest | Tied | SAO


@dataclass
class AAO:
    alpha: "Alpha"
    accid: "int | None"
    octav: "int"


@dataclass
class Mode:
    sao: "SAO"
    aao: "AAO"


@dataclass
class Metre:
    n: "int"
    d: "int"


@dataclass
class Time:
    und: "int"
    dot: "int"
