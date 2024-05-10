block = ' ', '▀', '▄', '█'
frame = ' ', '╵', '╷', '│', '╴', '┘', '┐', '┤', '╶', '└', '┌', '├', '─', '┴', '┬', '┼'
class Piano:
    white = {3: 1, 5: 3, 7: 5, 8: 7, 10: 9, 0: 11, 2: 13}
    black = {4: 2, 6: 4, 9: 8, 11: 10, 1: 12}
    def __init__(self, output, H = 10, W = 4, B = 8, R = 2, T = 1, L = 2, D = 2, U = 3, P = 4, E = 1, V = 2, Q = 3):
        self.args = H, W, B, R, T, L, D, U, P, E, V, Q
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
        H, W, B, R, T, L, D, U, P, E, V, Q = self.args
        self.output.write('\033[2J')
        for i in range(0, 8):
            top, bot = ('┌', '└') if i == 0 else ('┐', '┘') if i == 7 else ('┬', '┴')
            self.output.write(f'\033[{T + 0};{L + i * W * 2}H' + top)
            self.output.write(f'\033[{T + H};{L + i * W * 2}H' + bot)
            for j in range(1, H):
                self.output.write(f'\033[{T + j};{L + i * W * 2}H' + '│')
        for i in Piano.white.values():
            self.output.write(f'\033[{T + 0};{L + i * W - (W - 1)}H' + '─' * (W * 2 - 1))
            self.output.write(f'\033[{T + H};{L + i * W - (W - 1)}H' + '─' * (W * 2 - 1))
        for i in Piano.black.values():
            self.output.write(f'\033[{T + 0};{L + i * W - R}H' + '▄' * (R * 2 + 1))
            for j in range(1, B):
                self.output.write(f'\033[{T + j};{L + i * W - R}H' + '█' * (R * 2 + 1))
        self.output.flush()
        if h == float('-inf'):
            return
        elif h % 12 in Piano.white:
            i = Piano.white[h % 12]
            u = (H * 2 - U + 0) // 2
            d = (H * 2 - D + 1) // 2
            if (H * 2 - U + 1) % 2 == 1:
                self.output.write(f'\033[{T + u};{L + i * W - P // 2}H' + ('▗' + '▄' * (P - 1) + '▖' if P % 2 == 0 else '▄' * P))
            for j in range(u + 1, d):
                self.output.write(f'\033[{T + j};{L + i * W - P // 2}H' + ('▐' + '█' * (P - 1) + '▌' if P % 2 == 0 else '█' * P))
            if (H * 2 - D + 1) % 2 == 1:
                self.output.write(f'\033[{T + d};{L + i * W - P // 2}H' + ('▝' + '▀' * (P - 1) + '▘' if P % 2 == 0 else '▀' * P))
        elif h % 12 in Piano.black:
            i = Piano.black[h % 12]
            u = (B * 2 - V - 1) // 2
            d = (B * 2 - E - 0) // 2
            if (B * 2 - V) % 2 == 1:
                self.output.write(f'\033[{T + u};{L + i * W - Q // 2}H' + ('▛' + '▀' * (Q - 1) + '▜' if Q % 2 == 0 else '▀' * Q))
            for j in range(u + 1, d):
                self.output.write(f'\033[{T + j};{L + i * W - Q // 2}H' + ('▌' + ' ' * (Q - 1) + '▐' if Q % 2 == 0 else ' ' * Q))
            if (B * 2 - E) % 2 == 1:
                self.output.write(f'\033[{T + d};{L + i * W - Q // 2}H' + ('▙' + '▄' * (Q - 1) + '▟' if Q % 2 == 0 else '▄' * Q))
        self.output.flush()
