from io import TextIOBase
from dataclasses import dataclass


class ParserError(Exception):
    def __init__(self, buff: "TextIOBase", message: "str"):
        told = buff.tell()
        buff.seek(0)
        prev = buff.read(told)
        prev = prev.split("\n")
        last = prev.pop()
        self.lineno = len(prev) + 1
        self.colno = len(last) + 1
        self.message = message

    def __str__(self):
        return f"{self.message} at line {self.lineno} column {self.colno}"


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
    solfa: "str"
    accid: "int | None"
    octav: "int"


Note = Rest | Tied | SAO


@dataclass
class AAO:
    alpha: "str"
    accid: "int | None"
    octav: "int"


@dataclass
class Mode:
    lft: "SAO"
    rgt: "AAO"


@dataclass
class Metre:
    n: "int"
    d: "int"


@dataclass
class Time:
    und: "int"
    dot: "int"


def parse_music(buff: "TextIOBase") -> "Music":
    groups = [parse_group(buff)]
    while True:
        told = buff.tell()
        try:
            parse_ch(buff, ";")
            groups.append(parse_group(buff))
        except ParserError:
            buff.seek(told)
            break
    final = parse_final(buff)
    parse_eof(buff)
    return Music(groups=groups, final=final)


def parse_group(buff: "TextIOBase") -> "Group":
    mod = parse_mod(buff)
    mtr = parse_mtr(buff)
    bmp = parse_bmp(buff)
    passages = [parse_passage(buff)]
    while True:
        told = buff.tell()
        try:
            parse_ch(buff, ",")
            passages.append(parse_passage(buff))
        except ParserError:
            buff.seek(told)
            break
    return Group(mod=mod, mtr=mtr, bmp=bmp, passages=passages)


def parse_passage(buff: "TextIOBase") -> "Passage":
    measures = [parse_measure(buff)]
    while True:
        told = buff.tell()
        try:
            measures.append(parse_measure(buff))
        except ParserError:
            buff.seek(told)
            break
    return Passage(measures=measures)


def parse_measure(buff: "TextIOBase") -> "Measure":
    elements = [parse_element(buff)]
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, "|")
    return Measure(elements=elements)


def parse_element(buff: "TextIOBase") -> "Element":
    told = buff.tell()
    try:
        return parse_timed_note(buff)
    except ParserError:
        buff.seek(told)
    try:
        return parse_braced(buff)
    except ParserError:
        buff.seek(told)
    try:
        return parse_angled(buff)
    except ParserError:
        buff.seek(told)
    try:
        return parse_rated(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected element")


def parse_timed_note(buff: "TextIOBase") -> "TimedNote":
    note = parse_note(buff)
    time = parse_time(buff)
    return TimedNote(note=note, time=time)


def parse_braced(buff: "TextIOBase") -> "Braced":
    parse_ch(buff, "{")
    elements = []
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, "}")
    return Braced(inners=elements)


def parse_angled(buff: "TextIOBase") -> "Angled":
    parse_ch(buff, "<")
    elements = []
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, ">")
    return Angled(inners=elements)


def parse_rated(buff: "TextIOBase") -> "Rated":
    rat = parse_rat(buff)
    inner = parse_element(buff)
    return Rated(ratio=rat, inner=inner)


def parse_rat(buff: "TextIOBase") -> "Ratio":
    parse_ch(buff, "[")
    n = parse_positive(buff)
    told = buff.tell()
    try:
        parse_ch(buff, ":")
        d = parse_positive(buff)
    except ParserError:
        buff.seek(told)
        d = None
    parse_ch(buff, "]")
    return Ratio(n=n, d=d)


def parse_note(buff: "TextIOBase") -> "Note":
    told = buff.tell()
    try:
        return parse_sao(buff)
    except ParserError:
        buff.seek(told)
    try:
        return parse_rest(buff)
    except ParserError:
        buff.seek(told)
    try:
        return parse_tied(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected note")


def parse_sao(buff: "TextIOBase") -> "SAO":
    accid = parse_accid(buff)
    solfa = parse_solfa(buff)
    octav = parse_octav(buff)
    return SAO(solfa=solfa, accid=accid, octav=octav)


def parse_rest(buff: "TextIOBase") -> "Rest":
    parse_ch(buff, "0")
    return Rest()


def parse_tied(buff: "TextIOBase") -> "Tied":
    parse_ch(buff, "-")
    return Tied()


def parse_aao(buff: "TextIOBase") -> "AAO":
    alpha = parse_alpha(buff)
    accid = parse_accid(buff)
    octav = parse_octav(buff)
    return AAO(alpha=alpha, accid=accid, octav=octav)


def parse_mod(buff: "TextIOBase") -> "Mode":
    lft = parse_sao(buff)
    parse_ch(buff, "=")
    rgt = parse_aao(buff)
    return Mode(lft=lft, rgt=rgt)


def parse_mtr(buff: "TextIOBase") -> "Metre":
    n = parse_positive(buff)
    parse_ch(buff, "/")
    d = parse_positive(buff)
    return Metre(n=n, d=d)


def parse_bmp(buff: "TextIOBase") -> "int":
    return parse_positive(buff)


def parse_accid(buff: "TextIOBase") -> "int | None":
    told = buff.tell()
    try:
        parse_ch(buff, "@")
        return 0
    except ParserError:
        buff.seek(told)
    try:
        parse_ch(buff, "#")
        i = +1
        while True:
            told = buff.tell()
            try:
                parse_ch(buff, "#")
                i += 1
            except ParserError:
                buff.seek(told)
                break
        return i
    except ParserError:
        buff.seek(told)
    try:
        parse_ch(buff, "b")
        i = -1
        while True:
            told = buff.tell()
            try:
                parse_ch(buff, "b")
                i -= 1
            except ParserError:
                buff.seek(told)
                break
        return i
    except ParserError:
        buff.seek(told)
    return None


def parse_octav(buff: "TextIOBase") -> "int":
    told = buff.tell()
    try:
        parse_ch(buff, "'")
        i = +1
        while True:
            told = buff.tell()
            try:
                parse_ch(buff, "'")
                i += 1
            except ParserError:
                buff.seek(told)
                break
        return i
    except ParserError:
        buff.seek(told)
    try:
        parse_ch(buff, ",")
        i = -1
        while True:
            told = buff.tell()
            try:
                parse_ch(buff, ",")
                i -= 1
            except ParserError:
                buff.seek(told)
                break
        return i
    except ParserError:
        buff.seek(told)
    return 0


def parse_time(buff: "TextIOBase") -> "Time":
    und = 0
    while True:
        told = buff.tell()
        try:
            parse_ch(buff, "/")
            und += 1
        except ParserError:
            buff.seek(told)
            break
    dot = 0
    while True:
        told = buff.tell()
        try:
            parse_ch(buff, ".")
            dot += 1
        except ParserError:
            buff.seek(told)
            break
    return Time(und=und, dot=dot)


def parse_final(buff: "TextIOBase") -> "list[int] | None":
    told = buff.tell()
    try:
        return parse_ch(buff, "|")
    except ParserError:
        buff.seek(told)
    try:
        return parse_order(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected order")


def parse_order(buff: "TextIOBase") -> "list[int]":
    parse_ch(buff, ":")
    nums = []
    while True:
        told = buff.tell()
        try:
            nums.append(parse_positive(buff))
        except ParserError:
            buff.seek(told)
            break
    return nums


def parse_positive(buff: "TextIOBase") -> "int":
    parse_ws(buff)
    told = buff.tell()
    char = buff.read(1)
    if char not in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
        buff.seek(told)
        raise ParserError(buff, "Expected a positive integer")
    num = char
    while True:
        told = buff.tell()
        char = buff.read(1)
        if char not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            buff.seek(told)
            break
        num += char
    return int(num)


def parse_alpha(buff: "TextIOBase") -> "str":
    parse_ws(buff)
    told = buff.tell()
    read = buff.read(1)
    if read not in {"C", "D", "E", "F", "G", "A", "B"}:
        buff.seek(told)
        raise ParserError(buff, "Expected A-G")
    return read


def parse_solfa(buff: "TextIOBase") -> "str":
    parse_ws(buff)
    told = buff.tell()
    read = buff.read(1)
    if read not in {"1", "2", "3", "4", "5", "6", "7"}:
        buff.seek(told)
        raise ParserError(buff, "Expected 1-7")
    return read


def parse_ch(buff: "TextIOBase", char) -> "None":
    parse_ws(buff)
    told = buff.tell()
    read = buff.read(1)
    if read != char:
        buff.seek(told)
        raise ParserError(buff, f"Expected {char}")


def parse_eof(buff: "TextIOBase") -> "None":
    parse_ws(buff)
    told = buff.tell()
    read = buff.read(1)
    if read:
        buff.seek(told)
        raise ParserError(buff, "Expected end of file")


def parse_ws(buff: "TextIOBase") -> "None":
    while True:
        told = buff.tell()
        char = buff.read(1)
        if not char.isspace():
            buff.seek(told)
            break
