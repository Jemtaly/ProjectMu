from io import TextIOBase
from dataclasses import dataclass


class ParserError(Exception):
    def __init__(self, input: "TextIOBase", message: "str"):
        told = input.tell()
        input.seek(0)
        prev = input.read(told)
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
    order: "list[int] | None"


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


def parse_music(input: "TextIOBase") -> "Music":
    groups = [parse_group(input)]
    while True:
        told = input.tell()
        try:
            parse_ch(input, ";")
            groups.append(parse_group(input))
        except ParserError:
            input.seek(told)
            break
    order = parse_order(input)
    parse_eof(input)
    return Music(groups=groups, order=order)


def parse_order(input: "TextIOBase") -> "list[int] | None":
    told = input.tell()
    try:
        parse_ch(input, "|")
        return None
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, ":")
        nums = []
        while True:
            told = input.tell()
            try:
                nums.append(parse_positive(input))
            except ParserError:
                input.seek(told)
                break
        return nums
    except ParserError:
        input.seek(told)
    raise ParserError(input, "Expected order")


def parse_group(input: "TextIOBase") -> "Group":
    mod = parse_mod(input)
    mtr = parse_mtr(input)
    bmp = parse_bmp(input)
    passages = [parse_passage(input)]
    while True:
        told = input.tell()
        try:
            parse_ch(input, ",")
            passages.append(parse_passage(input))
        except ParserError:
            input.seek(told)
            break
    return Group(mod=mod, mtr=mtr, bmp=bmp, passages=passages)


def parse_passage(input: "TextIOBase") -> "Passage":
    measures = [parse_measure(input)]
    while True:
        told = input.tell()
        try:
            measures.append(parse_measure(input))
        except ParserError:
            input.seek(told)
            break
    return Passage(measures=measures)


def parse_measure(input: "TextIOBase") -> "Measure":
    elements = [parse_element(input)]
    while True:
        told = input.tell()
        try:
            elements.append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse_ch(input, "|")
    return Measure(elements=elements)


def parse_element(input: "TextIOBase") -> "Element":
    told = input.tell()
    try:
        return parse_timed_note(input)
    except ParserError:
        input.seek(told)
    try:
        return parse_braced(input)
    except ParserError:
        input.seek(told)
    try:
        return parse_angled(input)
    except ParserError:
        input.seek(told)
    try:
        return parse_rated(input)
    except ParserError:
        input.seek(told)
    raise ParserError(input, "Expected element")


def parse_timed_note(input: "TextIOBase") -> "TimedNote":
    note = parse_note(input)
    time = parse_time(input)
    return TimedNote(note=note, time=time)


def parse_braced(input: "TextIOBase") -> "Braced":
    parse_ch(input, "{")
    elements = []
    while True:
        told = input.tell()
        try:
            elements.append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse_ch(input, "}")
    return Braced(inners=elements)


def parse_angled(input: "TextIOBase") -> "Angled":
    parse_ch(input, "<")
    elements = []
    while True:
        told = input.tell()
        try:
            elements.append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse_ch(input, ">")
    return Angled(inners=elements)


def parse_rated(input: "TextIOBase") -> "Rated":
    rat = parse_rat(input)
    inner = parse_element(input)
    return Rated(ratio=rat, inner=inner)


def parse_rat(input: "TextIOBase") -> "Ratio":
    parse_ch(input, "[")
    n = parse_positive(input)
    told = input.tell()
    try:
        parse_ch(input, ":")
        d = parse_positive(input)
    except ParserError:
        input.seek(told)
        d = None
    parse_ch(input, "]")
    return Ratio(n=n, d=d)


def parse_note(input: "TextIOBase") -> "Note":
    told = input.tell()
    try:
        return parse_sao(input)
    except ParserError:
        input.seek(told)
    try:
        return parse_rest(input)
    except ParserError:
        input.seek(told)
    try:
        return parse_tied(input)
    except ParserError:
        input.seek(told)
    raise ParserError(input, "Expected note")


def parse_sao(input: "TextIOBase") -> "SAO":
    accid = parse_accid(input)
    solfa = parse_solfa(input)
    octav = parse_octav(input)
    return SAO(solfa=solfa, accid=accid, octav=octav)


def parse_rest(input: "TextIOBase") -> "Rest":
    parse_ch(input, "0")
    return Rest()


def parse_tied(input: "TextIOBase") -> "Tied":
    parse_ch(input, "-")
    return Tied()


def parse_aao(input: "TextIOBase") -> "AAO":
    alpha = parse_alpha(input)
    accid = parse_accid(input)
    octav = parse_octav(input)
    return AAO(alpha=alpha, accid=accid, octav=octav)


def parse_mod(input: "TextIOBase") -> "Mode":
    lft = parse_sao(input)
    parse_ch(input, "=")
    rgt = parse_aao(input)
    return Mode(lft=lft, rgt=rgt)


def parse_mtr(input: "TextIOBase") -> "Metre":
    n = parse_positive(input)
    parse_ch(input, "/")
    d = parse_positive(input)
    return Metre(n=n, d=d)


def parse_bmp(input: "TextIOBase") -> "int":
    return parse_positive(input)


def parse_accid(input: "TextIOBase") -> "int | None":
    told = input.tell()
    try:
        parse_ch(input, "@")
        return 0
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, "#")
        i = +1
        while True:
            told = input.tell()
            try:
                parse_ch(input, "#")
                i += 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, "b")
        i = -1
        while True:
            told = input.tell()
            try:
                parse_ch(input, "b")
                i -= 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    return None


def parse_octav(input: "TextIOBase") -> "int":
    told = input.tell()
    try:
        parse_ch(input, "'")
        i = +1
        while True:
            told = input.tell()
            try:
                parse_ch(input, "'")
                i += 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, ",")
        i = -1
        while True:
            told = input.tell()
            try:
                parse_ch(input, ",")
                i -= 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    return 0


def parse_time(input: "TextIOBase") -> "Time":
    und = 0
    while True:
        told = input.tell()
        try:
            parse_ch(input, "/")
            und += 1
        except ParserError:
            input.seek(told)
            break
    dot = 0
    while True:
        told = input.tell()
        try:
            parse_ch(input, ".")
            dot += 1
        except ParserError:
            input.seek(told)
            break
    return Time(und=und, dot=dot)


def parse_positive(input: "TextIOBase") -> "int":
    parse_ws(input)
    told = input.tell()
    char = input.read(1)
    if char not in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
        input.seek(told)
        raise ParserError(input, "Expected a positive integer")
    num = char
    while True:
        told = input.tell()
        char = input.read(1)
        if char not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            input.seek(told)
            break
        num += char
    return int(num)


def parse_alpha(input: "TextIOBase") -> "str":
    parse_ws(input)
    told = input.tell()
    read = input.read(1)
    if read not in {"C", "D", "E", "F", "G", "A", "B"}:
        input.seek(told)
        raise ParserError(input, "Expected A-G")
    return read


def parse_solfa(input: "TextIOBase") -> "str":
    parse_ws(input)
    told = input.tell()
    read = input.read(1)
    if read not in {"1", "2", "3", "4", "5", "6", "7"}:
        input.seek(told)
        raise ParserError(input, "Expected 1-7")
    return read


def parse_ch(input: "TextIOBase", char) -> "None":
    parse_ws(input)
    told = input.tell()
    read = input.read(1)
    if read != char:
        input.seek(told)
        raise ParserError(input, f"Expected {char}")


def parse_eof(input: "TextIOBase") -> "None":
    parse_ws(input)
    told = input.tell()
    read = input.read(1)
    if read:
        input.seek(told)
        raise ParserError(input, "Expected end of file")


def parse_ws(input: "TextIOBase") -> "None":
    while True:
        told = input.tell()
        char = input.read(1)
        if not char.isspace():
            input.seek(told)
            break


def try_parse(input: "TextIOBase", parse):
    told = input.tell()
    try:
        return parse(told)
    except ParserError:
        input.seek(told)
        return None
