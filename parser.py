import io


class ParserError(Exception):
    def __init__(self, input: io.StringIO, message: str):
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


def parse_music(input):
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
    return {"groups": groups, "order": order}


def parse_order(input):
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


def parse_group(input):
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
    return {"mod": mod, "mtr": mtr, "bmp": bmp, "passages": passages}


def parse_passage(input):
    measures = [parse_measure(input)]
    while True:
        told = input.tell()
        try:
            measures.append(parse_measure(input))
        except ParserError:
            input.seek(told)
            break
    return {"measures": measures}


def parse_measure(input):
    elements = [parse_element(input)]
    while True:
        told = input.tell()
        try:
            elements.append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse_ch(input, "|")
    return {"elements": elements}


def parse_element(input):
    told = input.tell()
    try:
        note = parse_note(input)
        time = parse_time(input)
        return {"note": note, "time": time}
    except ParserError:
        input.seek(told)
    try:
        angled = parse_angled(input)
        return {"angled": angled}
    except ParserError:
        input.seek(told)
    try:
        rat = parse_rat(input)
        braced = parse_braced(input)
        return {"rat": rat, "braced": braced}
    except ParserError:
        input.seek(told)
    try:
        rat = parse_rat(input)
        angled = parse_angled(input)
        return {"rat": rat, "angled": angled}
    except ParserError:
        input.seek(told)
    raise ParserError(input, "Expected element")


def parse_rat(input):
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
    return {"n": n, "d": d}


def parse_angled(input):
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
    return {"elements": elements}


def parse_braced(input):
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
    return {"elements": elements}


def parse_note(input):
    told = input.tell()
    try:
        return parse_sao(input)
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, "0")
        return {"rest": "0"}
    except ParserError:
        input.seek(told)
    try:
        parse_ch(input, "-")
        return {"tied": "-"}
    except ParserError:
        input.seek(told)
    raise ParserError(input, "Expected note")


def parse_sao(input):
    accid = parse_accid(input)
    solfa = parse_solfa(input)
    octav = parse_octav(input)
    return {"accid": accid, "solfa": solfa, "octav": octav}


def parse_aao(input):
    alpha = parse_alpha(input)
    accid = parse_accid(input)
    octav = parse_octav(input)
    return {"alpha": alpha, "accid": accid, "octav": octav}


def parse_mod(input):
    lft = parse_sao(input)
    parse_ch(input, "=")
    rgt = parse_aao(input)
    return {"lft": lft, "rgt": rgt}


def parse_mtr(input):
    n = parse_positive(input)
    parse_ch(input, "/")
    d = parse_positive(input)
    return {"n": n, "d": d}


def parse_bmp(input):
    return parse_positive(input)


def parse_accid(input):
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


def parse_octav(input):
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


def parse_time(input):
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
    return {"und": und, "dot": dot}


def parse_positive(input):
    parse_ws(input)
    char = input.read(1)
    if char not in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
        raise ParserError(input, "Expected a positive integer")
    num = char
    while True:
        told = input.tell()
        char = input.read(1)
        if char not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            input.seek(told)
            break
        num += char
    return num


def parse_alpha(input):
    parse_ws(input)
    char = input.read(1)
    if char not in {"C", "D", "E", "F", "G", "A", "B"}:
        raise ParserError(input, "Expected A-G")
    return char


def parse_solfa(input):
    parse_ws(input)
    char = input.read(1)
    if char not in {"1", "2", "3", "4", "5", "6", "7"}:
        raise ParserError(input, "Expected 1-7")
    return char


def parse_eof(input):
    parse_ws(input)
    if input.read(1):
        raise ParserError(input, "Expected end of file")


def parse_ch(input, char):
    parse_ws(input)
    if input.read(1) != char:
        raise ParserError(input, f"Expected {char}")


def parse_ws(input):
    while True:
        told = input.tell()
        char = input.read(1)
        if not char.isspace():
            input.seek(told)
            break
