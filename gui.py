class GUI:
    P = {0: 1, 2: 3, 4: 5, 5: 7, 7: 9, 9: 11, 11: 13}
    Q = {1: 2, 3: 4, 6: 8, 8: 10, 10: 12}
    def __init__(self, output, H = 12, W = 4, Y = 9, X = 2, T = 2, L = 2):
        self.H = H
        self.W = W
        self.Y = Y
        self.X = X
        self.T = T
        self.L = L
        self.output = output
    def __enter__(self):
        self.output.write('\033[?1049h')
        self.output.write('\033[?25l')
        self.output.flush()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.output.write('\033[?1049l')
        self.output.write('\033[?25h')
        self.output.flush()
    def show(self, h):
        H = self.H
        W = self.W
        Y = self.Y
        X = self.X
        T = self.T
        L = self.L
        self.output.write('\033[2J')
        for i in range(0, 8):
            top, bot = ('┌', '└') if i == 0 else ('┐', '┘') if i == 7 else ('┬', '┴')
            self.output.write(f'\033[{T + 0};{L + i * W * 2}H' + top)
            self.output.write(f'\033[{T + H};{L + i * W * 2}H' + bot)
            for j in range(1, H):
                self.output.write(f'\033[{T + j};{L + i * W * 2}H' + '│')
        for i in GUI.P.values():
            self.output.write(f'\033[{T + 0};{L + i * W - (W - 1)}H' + '─' * (W * 2 - 1))
            self.output.write(f'\033[{T + H};{L + i * W - (W - 1)}H' + '─' * (W * 2 - 1))
        for i in GUI.Q.values():
            self.output.write(f'\033[{T + 0};{L + i * W - X}H' + '▄' * (X * 2 + 1))
            for j in range(1, Y):
                self.output.write(f'\033[{T + j};{L + i * W - X}H' + '█' * (X * 2 + 1))
        self.output.flush()
        if h % 12 in GUI.P:
            self.output.write(f'\033[{T + H - 2};{L + GUI.P[h % 12] * W}H' + '▄')
        if h % 12 in GUI.Q:
            self.output.write(f'\033[{T + Y - 2};{L + GUI.Q[h % 12] * W}H' + '▀')
        self.output.flush()
