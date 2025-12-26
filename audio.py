import sys
import wave
from dataclasses import dataclass
from typing import Callable, TextIO

import numpy as np
import pyaudio

from .core import *
from .tones import Tone
from .piano import Piano


Func = Callable[[np.ndarray, float], np.ndarray]


FUNCS: dict[str, Func] = {
    "sn": lambda t, freq: np.sin(2 * np.pi * freq * t),
    "pl": lambda t, freq, delta=5.0: np.sin(2 * np.pi * (freq - delta / 2) * t) / 3 - np.sin(2 * np.pi * (freq + delta / 2) * t) / 3 * 2,
    "sq": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) for i in range(n)], 0) * 4 / np.pi,
    "tr": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (2 * i + 1) * freq * t) / (2 * i + 1) ** 2 * (-1) ** i for i in range(n)], 0) * 8 / np.pi**2,
    "st": lambda t, freq, n=8: np.sum([np.sin(2 * np.pi * (i + 1) * freq * t) / (i + 1) for i in range(n)], 0) * 2 / np.pi,
    # 'sq': lambda t, freq: np.sign(np.sin(2 * np.pi * freq * t)),
    # 'tr': lambda t, freq: np.fabs(np.fmod(freq * t + 0.75, 1.0) * 4.0 - 2.0) - 1.0,
    # 'st': lambda t, freq: np.fabs(np.fmod(freq * t + 0.50, 1.0) * 2.0 - 0.0) - 1.0,
}


@dataclass
class AudioSettings:
    func: Func
    attack: float
    decay: float
    volume: float
    sr: int
    sw: int

    def gen_wave(self, tone: Tone) -> bytes:
        fw = np.linspace(0, tone.secs, int(self.sr * tone.secs))
        bw = np.linspace(tone.secs, 0, int(self.sr * tone.secs))
        data = self.func(fw, 440 * 2 ** ((tone.pitch - 9) / 12)) * np.fmin(np.fmin(fw / self.attack, bw / self.decay), 1.0) * self.volume
        return (np.int16(data * 32767) if self.sw == 2 else np.uint8(data * 127 + 128)).tobytes()

    def save(self, tones: list[Tone], output: str) -> None:
        with wave.open(output, "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(self.sw)
            file.setframerate(self.sr)
            for tone in tones:
                file.writeframes(self.gen_wave(tone))

    def play(self, tones: list[Tone], output: TextIO = sys.stdout):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pa.get_format_from_width(self.sw), channels=1, rate=self.sr, output=True)
        with Piano(output) as gui:
            for tone in tones:
                gui.show(tone.pitch)
                stream.write(self.gen_wave(tone))
                gui.show(-np.inf)
        stream.stop_stream()
        stream.close()
        pa.terminate()
