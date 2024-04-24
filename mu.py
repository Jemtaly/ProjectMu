import wave
import argparse
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
def flatten(music):
    passages = {}
    i = 0
    for group in music.group():
        mod = group.mod()
        bmp = group.bmp()
        mtr = group.mtr()
        alpha = mod.alpha().getText()
        accid = mod.accid().getText()
        octav = mod.octav().getText()
        accid = accid.count('#') - accid.count('b')
        octav = octav.count("^") - octav.count("v")
        alpha = Alpha[alpha] + accid + octav * 12
        mod = mod.getText()
        bmp = int(bmp.num().getText())
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
                ctr = 0
                def visit(element, base = Fraction(1, 4)):
                    nonlocal ctr
                    if element.note():
                        note = element.note()
                        if note.solfa():
                            solfa = note.solfa().getText()
                            accid = note.accid().getText()
                            octav = note.octav().getText()
                            if len(accid) > 0:
                                Accid[solfa] = accid.count('#') - accid.count('b')
                            accid = Accid[solfa]
                            octav = octav.count("^") - octav.count("v")
                            solfa = Solfa[solfa] + accid + octav * 12
                            passages[i].append([440 * 2 ** ((solfa + alpha) / 12), 0])
                        elif note.rest():
                            passages[i].append([0, 0])
                        time = element.time().getText()
                        exts = time.count('-')
                        unds = time.count('/')
                        dots = time.count('.')
                        time = Fraction(exts + 1) if exts else Fraction(2 ** (dots + 1) - 1, 2 ** (dots + unds))
                        time = time * base
                        passages[i][-1][1] += time * 60 * mtd / bmp
                        ctr += time
                        return
                    if element.rat():
                        rat = element.rat()
                        rtn = int(rat.num(0).getText())
                        rtd = int(rat.num(1).getText())
                        rat = Fraction(rtn, rtd)
                        base /= rat
                    else:
                        base /= 2
                    for elem in element.element():
                        visit(elem, base)
                for element in measure.element():
                    visit(element)
                if ctr != mtr:
                    print(f'Warning: Passage {i}, Measure {j} has wrong time signature, expected {mtr}, got {ctr}')
    order = [int(num.getText()) for num in music.final().num()] or passages.keys()
    tones = []
    for num in order:
        if num not in passages:
            print(f'Warning: Passage {num} not found, skipping')
            continue
        tones.extend(passages[num])
    return tones
funcs = {
    'sine': lambda t, freq: np.sin(2 * np.pi * freq * t),
    'poly': lambda t, freq, delta = 2.0: np.sin(2 * np.pi * (freq - delta) * t) * 0.4 - np.sin(2 * np.pi * (freq + delta) * t) * 0.6,
    'triangle': lambda t, freq: np.fabs(np.fmod(freq * t + 0.75, 1.0) * 4.0 - 2.0) - 1.0,
    'sawtooth': lambda t, freq: np.fabs(np.fmod(freq * t + 0.50, 1.0) * 2.0 - 0.0) - 1.0,
    'square': lambda t, freq: np.sign(np.sin(2 * np.pi * freq * t)),
}
def main():
    parser = argparse.ArgumentParser(description = 'ProjectMu - Numbered Notation Score Compiler')
    parser.add_argument('filename', type = str, help = 'path to the input numbered notation score file')
    parser.add_argument('-o', '--output', type = str, default = 'output.wav', help = 'output wav file path')
    parser.add_argument('-t', '--timbre', type = str, choices = funcs.keys(), default = 'sine', help = 'timbre of the output sound')
    args = parser.parse_args()
    input = FileStream(args.filename)
    lexer = muLexer(input)
    stream = CommonTokenStream(lexer)
    parser = muParser(stream)
    music = parser.music()
    tones = flatten(music)
    func = funcs[args.timbre]
    data = np.concatenate([func(np.linspace(0, dura, int(44100 * dura)), freq) * np.fmin(np.fmin(np.linspace(0, dura, int(44100 * dura)) / 0.02, np.linspace(dura, 0, int(44100 * dura)) / 0.02), 1.0) for freq, dura in tones])
    data = np.int16(data * 32767)
    with wave.open(args.output, 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(44100)
        file.writeframes(data)
if __name__ == '__main__':
    main()
