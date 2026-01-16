import argparse

from .parser import TextBuffer, parse_music
from .converter import flatten
from .audio import AudioSettings, FUNCS


def main():
    parser = argparse.ArgumentParser(description="ProjectMu - A Numbered Musical Notation Tool")
    parser.add_argument("filename", type=str, help="path to the input numbered notation score file")
    parser.add_argument("-o", "--output", type=str, default=None, help="output wav file path, if not specified, play the sound instead")
    parser.add_argument("-t", "--timbre", type=str, choices=FUNCS, default=next(iter(FUNCS)), help="timbre of the output sound")
    parser.add_argument("-r", "--sample-rate", type=int, default=44100, help="sample rate of the output sound")
    parser.add_argument("-w", "--sample-width", type=int, default=2, choices=[1, 2], help="sample width of the output sound")
    parser.add_argument("-a", "--attack", type=float, default=0.02, help="attack time of the output sound")
    parser.add_argument("-d", "--decay", type=float, default=0.02, help="decay time of the output sound")
    parser.add_argument("-v", "--volume", type=float, default=0.8, help="volume of the output sound")
    args = parser.parse_args()
    with open(args.filename, "r") as file:
        music = parse_music(TextBuffer(file.read()))
    tones = flatten(music)
    settings = AudioSettings(
        func=FUNCS[args.timbre],
        attack=args.attack,
        decay=args.decay,
        volume=args.volume,
        sr=args.sample_rate,
        sw=args.sample_width,
    )
    if args.output is None:
        settings.play(tones)
    else:
        settings.save(tones, args.output)

if __name__ == "__main__":
    main()
