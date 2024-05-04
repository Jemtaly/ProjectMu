import wave
import argparse
import sys
from fractions import Fraction
from muLexer import muLexer
from muParser import muParser
from antlr4 import *
import numpy as np
Solfa = {
    '1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11,
}
Alpha = {
    'C': 3, 'D': 5, 'E': 7, 'F': 8, 'G': 10, 'A': 0, 'B': 2,
}
def flatten(music, output = sys.stdout):
    passages = {}
    i = 0
    for group in music.group():
        mod = group.mod()
        aao = mod.aao()
        alpha = aao.alpha().getText()
        accid = aao.accid().getText()
        accid = accid.count('#') - accid.count('b')
        octav = aao.octav().getText()
        octav = octav.count("'") - octav.count(',')
        aao = Alpha[alpha] + accid + octav * 12
        sao = mod.sao()
        solfa = sao.solfa().getText()
        accid = sao.accid().getText()
        accid = accid.count('#') - accid.count('b')
        octav = sao.octav().getText()
        octav = octav.count("'") - octav.count(',')
        sao = Solfa[solfa] + accid + octav * 12
        mod = aao - sao
        bmp = group.bmp()
        bmp = int(bmp.num().getText())
        mtr = group.mtr()
        mtn = int(mtr.num(0).getText())
        mtd = int(mtr.num(1).getText())
        mtr = Fraction(mtn, mtd)
        for passage in group.passage():
            i += 1
            passages[i] = []
            j = 0
            for measure in passage.measure():
                j += 1
                Accid = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0}
                ctr = Fraction(0)
                def visit(element, base = Fraction(1, 4)):
                    nonlocal ctr
                    if element.note():
                        note = element.note()
                        if note.sao():
                            sao = note.sao()
                            solfa = sao.solfa().getText()
                            accid = sao.accid().getText()
                            if len(accid) > 0:
                                Accid[solfa] = accid.count('#') - accid.count('b')
                            accid = Accid[solfa]
                            octav = sao.octav().getText()
                            octav = octav.count("'") - octav.count(',')
                            sao = Solfa[solfa] + accid + octav * 12
                            passages[i].append([440 * 2 ** ((sao + mod) / 12), 0])
                        elif note.rest():
                            passages[i].append([0, 0])
                        elif len(passages[i]) == 0:
                            output.write(f'Warning: A tied note is found at the beginning of Passage {i}, which is considered as a rest\n')
                            passages[i].append([0, 0])
                        time = element.time().getText()
                        time = Fraction(1, 2 ** time.count('/')) * (2 - Fraction(1, 2 ** time.count('.')))
                        time = time * base
                        passages[i][-1][1] += time * 60 * mtd / bmp
                        ctr += time
                        return
                    if element.angled():
                        braced = element.angled()
                        base /= 2
                    else:
                        braced = element.braced()
                    if element.rat():
                        rat = element.rat()
                        rtn = int(rat.num(0).getText())
                        rtd = int(rat.num(1).getText()) if rat.num(1) is not None else 2 ** (rtn.bit_length() - 1)
                        rat = Fraction(rtn, rtd)
                        base /= rat
                    for element in braced.element():
                        visit(element, base)
                for element in measure.element():
                    visit(element)
                if ctr != mtr:
                    output.write(f'Warning: Passage {i}, Measure {j} has wrong time signature, expected {mtr}, got {ctr}\n')
    order = [int(num.getText()) for num in music.final().num()] or passages.keys()
    tones = []
    for num in order:
        if num not in passages:
            output.write(f'Warning: Passage {num} not found, skipping\n')
            continue
        tones.extend(passages[num])
    return tones
funcs = {
    'sn': lambda t, freq: np.sin(2 * np.pi * freq * t),
    'pl': lambda t, freq, delta = 5.0: np.sin(2 * np.pi * (freq - delta / 2) * t) / 3 - np.sin(2 * np.pi * (freq + delta / 2) * t) / 3 * 2,
    'tr': lambda t, freq: np.fabs(np.fmod(freq * t + 0.75, 1.0) * 4.0 - 2.0) - 1.0,
    'st': lambda t, freq: np.fabs(np.fmod(freq * t + 0.50, 1.0) * 2.0 - 0.0) - 1.0,
    'sq': lambda t, freq: np.sign(np.sin(2 * np.pi * freq * t)),
    # 'sq': lambda t, freq, n = 8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) for i in range(n)], 0) * 4 / np.pi,
    # 'tr': lambda t, freq, n = 8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) ** 2 * (-1) ** i for i in range(n)], 0) * 8 / np.pi ** 2,
    # 'st': lambda t, freq, n = 8: np.sum([np.sin(2 * np.pi * (i + 1) * freq * t) / (i + 1) for i in range(n)], 0) * 2 / np.pi,
}
def main():
    parser = argparse.ArgumentParser(description = 'ProjectMu - A Numbered Notation Score Compiler')
    parser.add_argument('filename', type = str, help = 'path to the input numbered notation score file')
    parser.add_argument('-o', '--output', type = str, default = 'output.wav', help = 'output wav file path')
    parser.add_argument('-t', '--timbre', type = str, choices = funcs.keys(), default = 'sine', help = 'timbre of the output sound')
    parser.add_argument('-r', '--sample-rate', type = int, default = 44100, help = 'sample rate of the output sound')
    parser.add_argument('-w', '--sample-width', type = int, default = 2, choices = [1, 2], help = 'sample width of the output sound')
    args = parser.parse_args()
    input = FileStream(args.filename)
    lexer = muLexer(input)
    stream = CommonTokenStream(lexer)
    parser = muParser(stream)
    music = parser.music()
    tones = flatten(music)
    func = funcs[args.timbre]
    sr = args.sample_rate
    sw = args.sample_width
    tin = tout = 0.02
    volume = 0.8
    data = np.concatenate([func(np.linspace(0, dura, int(sr * dura)), freq) * np.fmin(np.fmin(np.linspace(0, dura, int(sr * dura)) / tin, np.linspace(dura, 0, int(sr * dura)) / tout), 1.0) * volume for freq, dura in tones])
    data = np.int16(data * 32767) if sw == 2 else np.uint8(data * 127 + 128)
    with wave.open(args.output, 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(sw)
        file.setframerate(sr)
        file.writeframes(data)
if __name__ == '__main__':
    main()
