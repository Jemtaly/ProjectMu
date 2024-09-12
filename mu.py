#!/usr/bin/env python3


import argparse
import sys
import wave
from fractions import Fraction
from parser import parse_music

import numpy as np
import pyaudio
from piano import Piano


Solfa = {
    "1":  0,
    "2":  2,
    "3":  4,
    "4":  5,
    "5":  7,
    "6":  9,
    "7": 11,
}
Alpha = {
    "A":  9,
    "B": 11,
    "C": 12,
    "D": 14,
    "E": 16,
    "F": 17,
    "G": 19,
}


def flatten(music, output=sys.stdout):
    unordered = {}
    i = 0
    for group in music["groups"]:
        mod = group["mod"]
        lft = mod["lft"]
        lft = Solfa[lft["solfa"]] + (lft["accid"] if lft.get("accid") is not None else 0) + lft["octav"] * 12
        rgt = mod["rgt"]
        rgt = Alpha[rgt["alpha"]] + (rgt["accid"] if rgt.get("accid") is not None else 0) + rgt["octav"] * 12
        mod = rgt - lft
        bmp = group["bmp"]
        bmp = int(bmp)
        mtr = group["mtr"]
        mtn = int(mtr["n"])
        mtd = int(mtr["d"])
        mtr = Fraction(mtn, mtd)
        for passage in group["passages"]:
            i += 1
            unordered[i] = []
            j = 0
            for measure in passage["measures"]:
                j += 1
                Accid = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
                ctr = Fraction(0)

                def visit(element, base=Fraction(1, 4)):
                    nonlocal ctr
                    if element.get("note") is not None:
                        note = element["note"]
                        if note.get("solfa") is not None:
                            if note.get("accid") is not None:
                                Accid[note["solfa"]] = note["accid"]
                            note = Solfa[note["solfa"]] + Accid[note["solfa"]] + note["octav"] * 12
                            unordered[i].append([mod + note, 0])
                        elif note.get("rest") is not None:
                            unordered[i].append([-np.inf, 0])
                        elif len(unordered[i]) == 0:
                            output.write(f"Warning: A tied note is found at the beginning of Passage {i}, which is considered as a rest\n")
                            unordered[i].append([-np.inf, 0])
                        time = element["time"]
                        time = Fraction(1, 2 ** time["und"]) * (2 - Fraction(1, 2 ** time["dot"]))
                        time = time * base
                        unordered[i][-1][1] += time * 60 * mtd / bmp
                        ctr += time
                    else:
                        if element.get("rat") is not None:
                            rat = element["rat"]
                            rtn = int(rat["n"])
                            rtd = int(rat["d"]) if rat.get("d") is not None else 2 ** (rtn.bit_length() - 1)
                            rat = Fraction(rtn, rtd)
                            base /= rat
                        if element.get("angled") is not None:
                            base /= 2
                            braced = element["angled"]
                        else:
                            braced = element["braced"]
                        for element in braced["elements"]:
                            visit(element, base)

                for element in measure["elements"]:
                    visit(element)
                if ctr != mtr:
                    output.write(f"Warning: Passage {i}, Measure {j} has wrong time signature, expected {mtr}, got {ctr}\n")
    if music.get("order") is not None:
        nums = [int(num) for num in music["order"]]
    else:
        nums = unordered.keys()
    tones = []
    for num in nums:
        if num not in unordered:
            output.write(f"Warning: Passage {num} not found, skipping\n")
        else:
            tones.extend(unordered[num])
    return tones


funcs = {
    "sn": lambda t, freq: np.sin(2 * np.pi * freq * t),
    "pl": lambda t, freq, delta=5.0: np.sin(2 * np.pi * (freq - delta / 2) * t) / 3 - np.sin(2 * np.pi * (freq + delta / 2) * t) / 3 * 2,
    "sq": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) for i in range(n)], 0) * 4 / np.pi,
    "tr": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) ** 2 * (-1) ** i for i in range(n)], 0) * 8 / np.pi**2,
    "st": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (i + 1) * freq * t) / (i + 1) for i in range(n)], 0) * 2 / np.pi,
    # 'sq': lambda t, freq: np.sign(np.sin(2 * np.pi * freq * t)),
    # 'tr': lambda t, freq: np.fabs(np.fmod(freq * t + 0.75, 1.0) * 4.0 - 2.0) - 1.0,
    # 'st': lambda t, freq: np.fabs(np.fmod(freq * t + 0.50, 1.0) * 2.0 - 0.0) - 1.0,
}


def gen_wave(h, d, func, attack, decay, volume, sr, sw):
    fw = np.linspace(0, d, int(sr * d))
    bw = np.linspace(d, 0, int(sr * d))
    data = func(fw, 440 * 2 ** ((h - 9) / 12)) * np.fmin(np.fmin(fw / attack, bw / decay), 1.0) * volume
    return np.int16(data * 32767) if sw == 2 else np.uint8(data * 127 + 128)


def save(tones, func, sr, sw, attack, decay, volume, output):
    with wave.open(output, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(sw)
        file.setframerate(sr)
        for h, d in tones:
            file.writeframes(gen_wave(h, d, func, attack, decay, volume, sr, sw).tobytes())


def play(tones, func, sr, sw, attack, decay, volume, output=sys.stdout):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(sw), channels=1, rate=sr, output=True)
    with Piano(output) as gui:
        for h, d in tones:
            gui.show(h)
            stream.write(gen_wave(h, d, func, attack, decay, volume, sr, sw).tobytes())
            gui.show(-np.inf)
    stream.stop_stream()
    stream.close()
    pa.terminate()


def main():
    parser = argparse.ArgumentParser(description="ProjectMu - A Numbered Notation Score Compiler")
    parser.add_argument("filename", type=str, help="path to the input numbered notation score file")
    parser.add_argument("-o", "--output", type=str, default=None, help="output wav file path, if not specified, play the sound instead")
    parser.add_argument("-t", "--timbre", type=str, choices=funcs.keys(), default=next(iter(funcs)), help="timbre of the output sound")
    parser.add_argument("-r", "--sample-rate", type=int, default=44100, help="sample rate of the output sound")
    parser.add_argument("-w", "--sample-width", type=int, default=2, choices=[1, 2], help="sample width of the output sound")
    parser.add_argument("-a", "--attack", type=float, default=0.02, help="attack time of the output sound")
    parser.add_argument("-d", "--decay", type=float, default=0.02, help="decay time of the output sound")
    parser.add_argument("-v", "--volume", type=float, default=0.8, help="volume of the output sound")
    args = parser.parse_args()
    with open(args.filename, "r") as file:
        music = parse_music(file)
    tones = flatten(music)
    if args.output is None:
        play(tones, funcs[args.timbre], args.sample_rate, args.sample_width, args.attack, args.decay, args.volume)
    else:
        save(tones, funcs[args.timbre], args.sample_rate, args.sample_width, args.attack, args.decay, args.volume, args.output)


if __name__ == "__main__":
    main()
