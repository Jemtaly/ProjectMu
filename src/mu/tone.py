from dataclasses import dataclass


@dataclass
class Tone:
    pitch: int | None
    secs: float = 0.0
