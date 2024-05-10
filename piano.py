class Piano:
    white = {0: 3, 1: 5, 2: 7, 3: 8, 4: 10, 5: 0, 6: 2}
    black = {1: 4, 2: 6, 4: 9, 5: 11, 6: 1}
    def __init__(self, output, W = 3, B = 2, U = 6, D = 9, T = 0, L = 0):
        self.args = W, B, U, D, T, L
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
        W, B, U, D, T, L = self.args
        self.output.write('\033[2J')
        Us, Ds, Um, Dm = [9] * 2 * (W * 7 + 1), [9] * 2 * (W * 7 + 1), [False] * (W * 7 + 1), [False] * (W * 7 + 1)
        for i, v in Piano.white.items():
            Um[i * W] = Um[i * W + W] = Dm[i * W] = Dm[i * W + W] = True
            cl = 3 if h % 12 == v else 7
            for j in range(1, W * 2 + 1):
                Us[i * 2 * W + j] = Ds[i * 2 * W + j] = cl
        for i, v in Piano.black.items():
            Um[i * W] = False
            cl = 4 if h % 12 == v else 0
            for j in range(1 - B, 1 + B):
                Us[i * 2 * W + j] = cl
        Ucs = [(l, 0, '│' if m else ' ') if l == r else (9, r, '▐') if l == 9 else (r, l, '▌') for l, m, r in zip(Us[0::2], Um, Us[1::2])]
        Dcs = [(l, 0, '│' if m else ' ') if l == r else (9, r, '▐') if l == 9 else (r, l, '▌') for l, m, r in zip(Ds[0::2], Dm, Ds[1::2])]
        for i in range(0, U):
            self.output.write('\033[{};{}H'.format(T + i + 1, L + 1))
            for bg, fg, ch in Ucs:
                self.output.write('\033[{};{}m{}'.format(30 + fg, 40 + bg, ch))
            self.output.write('\033[0m')
        for i in range(U, D):
            self.output.write('\033[{};{}H'.format(T + i + 1, L + 1))
            for bg, fg, ch in Dcs:
                self.output.write('\033[{};{}m{}'.format(30 + fg, 40 + bg, ch))
            self.output.write('\033[0m')
        self.output.flush()
