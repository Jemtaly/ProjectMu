import io
import re
class ParserError(Exception):
    def __init__(self, input: io.StringIO, message: str):
        told = input.tell()
        input.seek(0)
        prev = input.read(told)
        prev = prev.split('\n')
        last = prev.pop()
        self.lineno = len(prev) + 1
        self.colno = len(last) + 1
        self.message = message
    def __str__(self):
        return f'{self.message} at line {self.lineno} column {self.colno}'
def parse_music(input):
    music = {}
    music['groups'] = [parse_group(input)]
    while True:
        told = input.tell()
        try:
            parse(input, r';')
            music['groups'].append(parse_group(input))
        except ParserError:
            input.seek(told)
            break
    music['order'] = parse_order(input)
    parse(input, r'\Z')
    return music
def parse_order(input):
    told = input.tell()
    try:
        parse(input, r'\|')
        return None
    except ParserError:
        input.seek(told)
    try:
        parse(input, r':')
        nums = []
        while True:
            told = input.tell()
            try:
                nums.append(parse_num(input))
            except ParserError:
                input.seek(told)
                break
        return nums
    except ParserError:
        input.seek(told)
    raise ParserError(input, 'Expected final')
def parse_group(input):
    group = {}
    group['mod'] = parse_mod(input)
    group['mtr'] = parse_mtr(input)
    group['bmp'] = parse_bmp(input)
    group['passages'] = [parse_passage(input)]
    while True:
        told = input.tell()
        try:
            parse(input, r',')
            group['passages'].append(parse_passage(input))
        except ParserError:
            input.seek(told)
            break
    return group
def parse_passage(input):
    passage = {}
    passage['measures'] = [parse_measure(input)]
    while True:
        told = input.tell()
        try:
            passage['measures'].append(parse_measure(input))
        except ParserError:
            input.seek(told)
            break
    return passage
def parse_measure(input):
    measure = {}
    measure['elements'] = [parse_element(input)]
    while True:
        told = input.tell()
        try:
            measure['elements'].append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse(input, r'\|')
    return measure
def parse_element(input):
    told = input.tell()
    try:
        note = parse_note(input)
        time = parse_time(input)
        return {'note': note, 'time': time}
    except ParserError:
        input.seek(told)
    try:
        rat = parse_rat(input)
        angled = parse_angled(input)
        return {'rat': rat, 'angled': angled}
    except ParserError:
        input.seek(told)
    try:
        rat = parse_rat(input)
        braced = parse_braced(input)
        return {'rat': rat, 'braced': braced}
    except ParserError:
        input.seek(told)
    try:
        angled = parse_angled(input)
        return {'angled': angled}
    except ParserError:
        input.seek(told)
    raise ParserError(input, 'Expected element')
def parse_rat(input):
    parse(input, r'\[')
    rat = {}
    rat['n'] = parse_num(input)
    told = input.tell()
    try:
        parse(input, r':')
        rat['d'] = parse_num(input)
    except ParserError:
        input.seek(told)
    parse(input, r'\]')
    return rat
def parse_angled(input):
    parse(input, r'<')
    angled = {}
    angled['elements'] = []
    while True:
        told = input.tell()
        try:
            angled['elements'].append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse(input, r'>')
    return angled
def parse_braced(input):
    parse(input, r'\{')
    braced = {}
    braced['elements'] = []
    while True:
        told = input.tell()
        try:
            braced['elements'].append(parse_element(input))
        except ParserError:
            input.seek(told)
            break
    parse(input, r'\}')
    return braced
def parse_note(input):
    told = input.tell()
    try:
        return parse_sao(input)
    except ParserError:
        input.seek(told)
    try:
        rest = parse(input, r'0')
        return {'rest': rest}
    except ParserError:
        input.seek(told)
    try:
        tied = parse(input, r'-')
        return {'tied': tied}
    except ParserError:
        input.seek(told)
    raise ParserError(input, 'Expected note')
def parse_sao(input):
    accid = parse_accid(input)
    solfa = parse_solfa(input)
    octav = parse_octav(input)
    return {'accid': accid, 'solfa': solfa, 'octav': octav}
def parse_aao(input):
    alpha = parse_alpha(input)
    accid = parse_accid(input)
    octav = parse_octav(input)
    return {'alpha': alpha, 'accid': accid, 'octav': octav}
def parse_mod(input):
    lft = parse_sao(input)
    parse(input, r'=')
    rgt = parse_aao(input)
    return {'lft': lft, 'rgt': rgt}
def parse_mtr(input):
    n = parse_num(input)
    parse(input, r'/')
    d = parse_num(input)
    return {'n': n, 'd': d}
def parse_bmp(input):
    return parse_num(input)
def parse_accid(input):
    told = input.tell()
    try:
        parse(input, r'@')
        return 0
    except ParserError:
        input.seek(told)
    try:
        parse(input, r'#')
        i = +1
        while True:
            told = input.tell()
            try:
                parse(input, r'#')
                i += 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    try:
        parse(input, r'b')
        i = -1
        while True:
            told = input.tell()
            try:
                parse(input, r'b')
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
        parse(input, r"'")
        i = +1
        while True:
            told = input.tell()
            try:
                parse(input, r"'")
                i += 1
            except ParserError:
                input.seek(told)
                break
        return i
    except ParserError:
        input.seek(told)
    try:
        parse(input, r',')
        i = -1
        while True:
            told = input.tell()
            try:
                parse(input, r',')
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
            parse(input, r'/')
            und += 1
        except ParserError:
            input.seek(told)
            break
    dot = 0
    while True:
        told = input.tell()
        try:
            parse(input, r'\.')
            dot += 1
        except ParserError:
            input.seek(told)
            break
    return {'und': und, 'dot': dot}
def parse_num(input):
    return parse(input, r'[1-9][0-9]*')
def parse_alpha(input):
    return parse(input, r'[A-G]')
def parse_solfa(input):
    return parse(input, r'[1-7]')
def parse(input, pattern):
    while True:
        told = input.tell()
        char = input.read(1)
        if not char.isspace():
            input.seek(told)
            break
    told = input.tell()
    match = re.match(pattern, input.read())
    if match is None:
        raise ParserError(input, f'Expected {pattern}')
    input.seek(told + match.end())
    return match.group()
