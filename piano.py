from typing import TextIO


wdct = {0: 0, 1: 2, 2: 4, 3: 5, 4: 7, 5: 9, 6: 11}
bdct = {0: 1, 1: 3, 3: 6, 4: 8, 5: 10}
wlst = [None if i % 7 not in wdct else wdct[i % 7] + i // 7 * 12 for i in range(-23, 29)]
blst = [None if i % 7 not in bdct else bdct[i % 7] + i // 7 * 12 for i in range(-23, 28)]


class Piano:
    def __init__(self, output: TextIO, W=2, B=1, U=2, D=3, T=0, L=0):
        self.args = W, B, U, D, T, L
        self.output = output

    def __enter__(self):
        self.output.write("\033[?1049h")
        self.output.write("\033[?25l")
        self.output.flush()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.output.write("\033[?1049l")
        self.output.write("\033[?25h")
        self.output.flush()

    def show(self, h):
        W, B, U, D, T, L = self.args
        grid = [[[9, 9] for _ in range(W * 52 * 2)] for _ in range(max(U, D))]
        for i, v in enumerate(wlst):
            if v is None:
                continue
            x = 4 if h == v else 7
            for k in range(D):
                for j in range(0, W * 2 - 1):
                    grid[k][i * 2 * W + j][0] = grid[k][i * 2 * W + j][1] = x
                grid[k][i * 2 * W + W * 2 - 1][0] = x
        for i, v in enumerate(blst):
            if v is None:
                continue
            x = 3 if h == v else 0
            for k in range(U):
                for j in range(2 * W - B, 2 * W + B - 1):
                    grid[k][i * 2 * W + j][0] = grid[k][i * 2 * W + j][1] = x
                grid[k][i * 2 * W + 2 * W + B - 1][0] = x
        self.output.write("\033[2J")
        for i in range(0, max(U, D)):
            self.output.write("\033[{};{}H".format(T + i + 1, L + 1))
            for (a, b), (c, d) in zip(grid[i][0::2], grid[i][1::2]):
                if a == 9:
                    self.output.write("\033[{};{}m".format(30 + d, 40 + a))
                    self.output.write(" " if a == b == c == d else "▕" if a == b == c else "▐" if a == b and c == d else "?")
                else:
                    self.output.write("\033[{};{}m".format(30 + a, 40 + d))
                    self.output.write("█" if a == b == c == d else "▉" if a == b == c else "▌" if a == b and c == d else "▍" if b == c == d else "?")
            self.output.write("\033[0m")
        self.output.flush()
