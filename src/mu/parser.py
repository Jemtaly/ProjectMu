from dataclasses import dataclass

from . import ast


@dataclass
class TextBuffer:
    _text: str
    _curr: int = 0

    def tell(self) -> int:
        return self._curr

    def seek(self, pos: int) -> None:
        self._curr = pos

    def peek(self, length: int | None = None) -> str:
        if length is None:
            return self._text[self._curr :]
        return self._text[self._curr : self._curr + length]

    def move(self, length: int) -> None:
        self._curr += length

    def linecol(self) -> tuple[int, int]:
        prev = self._text[: self._curr]
        lines = prev.splitlines()
        line = lines.pop()
        lineno = len(lines) + 1
        colno = len(line) + 1
        return lineno, colno


class ParserError(Exception):
    def __init__(self, buff: TextBuffer, message: str):
        self.lineno, self.colno = buff.linecol()
        self.message = message

    def __str__(self):
        return f"{self.message} at line {self.lineno} column {self.colno}"


def parse_music(buff: TextBuffer) -> ast.Music:
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
    return ast.Music(groups=groups, final=final)


def parse_group(buff: TextBuffer) -> ast.Group:
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
    return ast.Group(mod=mod, mtr=mtr, bmp=bmp, passages=passages)


def parse_passage(buff: TextBuffer) -> ast.Passage:
    measures = [parse_measure(buff)]
    while True:
        told = buff.tell()
        try:
            measures.append(parse_measure(buff))
        except ParserError:
            buff.seek(told)
            break
    return ast.Passage(measures=measures)


def parse_measure(buff: TextBuffer) -> ast.Measure:
    elements = [parse_element(buff)]
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, "|")
    return ast.Measure(elements=elements)


def parse_element(buff: TextBuffer) -> ast.Element:
    told = buff.tell()
    try:
        return parse_timed_note(buff)
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_braced(buff)
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_angled(buff)
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_rated(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected element")


def parse_timed_note(buff: TextBuffer) -> ast.TimedNote:
    note = parse_note(buff)
    time = parse_time(buff)
    return ast.TimedNote(note=note, time=time)


def parse_braced(buff: TextBuffer) -> ast.Braced:
    parse_ch(buff, "{")
    elements = list[ast.Element]()
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, "}")
    return ast.Braced(inners=elements)


def parse_angled(buff: TextBuffer) -> ast.Angled:
    parse_ch(buff, "<")
    elements = list[ast.Element]()
    while True:
        told = buff.tell()
        try:
            elements.append(parse_element(buff))
        except ParserError:
            buff.seek(told)
            break
    parse_ch(buff, ">")
    return ast.Angled(inners=elements)


def parse_rated(buff: TextBuffer) -> ast.Rated:
    rat = parse_rat(buff)
    inner = parse_element(buff)
    return ast.Rated(ratio=rat, inner=inner)


def parse_rat(buff: TextBuffer) -> ast.Ratio:
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
    return ast.Ratio(n=n, d=d)


def parse_note(buff: TextBuffer) -> ast.Note:
    told = buff.tell()
    try:
        return parse_sao(buff)
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_rest(buff)
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_tied(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected note")


def parse_sao(buff: TextBuffer) -> ast.SAO:
    accid = parse_accid(buff)
    solfa = parse_solfa(buff)
    octav = parse_octav(buff)
    return ast.SAO(solfa=solfa, accid=accid, octav=octav)


def parse_rest(buff: TextBuffer) -> ast.Rest:
    parse_ch(buff, "0")
    return ast.Rest()


def parse_tied(buff: TextBuffer) -> ast.Tied:
    parse_ch(buff, "-")
    return ast.Tied()


def parse_aao(buff: TextBuffer) -> ast.AAO:
    alpha = parse_alpha(buff)
    accid = parse_accid(buff)
    octav = parse_octav(buff)
    return ast.AAO(alpha=alpha, accid=accid, octav=octav)


def parse_mod(buff: TextBuffer) -> ast.Mode:
    sao = parse_sao(buff)
    parse_ch(buff, "=")
    aao = parse_aao(buff)
    return ast.Mode(sao=sao, aao=aao)


def parse_mtr(buff: TextBuffer) -> ast.Metre:
    n = parse_positive(buff)
    parse_ch(buff, "/")
    d = parse_positive(buff)
    return ast.Metre(n=n, d=d)


def parse_bmp(buff: TextBuffer) -> int:
    return parse_positive(buff)


def parse_accid(buff: TextBuffer) -> int | None:
    told = buff.tell()
    try:
        parse_ch(buff, "@")
        return 0
    except ParserError:
        buff.seek(told)
    told = buff.tell()
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
    told = buff.tell()
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


def parse_octav(buff: TextBuffer) -> int:
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
    told = buff.tell()
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


def parse_time(buff: TextBuffer) -> ast.Time:
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
    return ast.Time(und=und, dot=dot)


def parse_final(buff: TextBuffer) -> list[int] | None:
    told = buff.tell()
    try:
        return parse_ch(buff, "|")
    except ParserError:
        buff.seek(told)
    told = buff.tell()
    try:
        return parse_order(buff)
    except ParserError:
        buff.seek(told)
    raise ParserError(buff, "Expected order")


def parse_order(buff: TextBuffer) -> list[int]:
    parse_ch(buff, ":")
    nums = list[int]()
    while True:
        told = buff.tell()
        try:
            nums.append(parse_positive(buff))
        except ParserError:
            buff.seek(told)
            break
    return nums


def parse_positive(buff: TextBuffer) -> int:
    parse_ws(buff)
    char = buff.peek(1)
    if char not in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
        buff.move(1)
        raise ParserError(buff, "Expected a positive integer")
    num = char
    while True:
        char = buff.peek(1)
        if char not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            break
        buff.move(1)
        num += char
    return int(num)


def parse_alpha(buff: TextBuffer) -> ast.Alpha:
    parse_ws(buff)
    read = buff.peek(1)
    if read not in ("C", "D", "E", "F", "G", "A", "B"):
        raise ParserError(buff, "Expected A-G")
    buff.move(1)
    return read


def parse_solfa(buff: TextBuffer) -> ast.Solfa:
    parse_ws(buff)
    read = buff.peek(1)
    if read not in ("1", "2", "3", "4", "5", "6", "7"):
        raise ParserError(buff, "Expected 1-7")
    buff.move(1)
    return read


def parse_ch(buff: TextBuffer, char: str) -> None:
    parse_ws(buff)
    read = buff.peek(1)
    if read != char:
        raise ParserError(buff, f"Expected {char}")
    buff.move(1)


def parse_eof(buff: TextBuffer) -> None:
    parse_ws(buff)
    read = buff.peek()
    if read:
        raise ParserError(buff, "Expected end of file")


def parse_ws(buff: TextBuffer) -> None:
    while True:
        char = buff.peek(1)
        if not char.isspace():
            break
        buff.move(1)
