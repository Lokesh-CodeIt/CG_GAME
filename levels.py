"""
levels.py  -  builds the 3 cave levels
--------------------------------------
Each cave is generated from a fixed seed (so the levels are always the same):
  1. A random maze is carved with depth-first search.
  2. A few extra walls are knocked out so the cave has loops.
  3. Keys, exit and bats are placed automatically.
The wall FACES are converted into line segments that the graphics
module draws with DDA / Bresenham and clips with the torch window.
"""
import random
from collections import deque

CELL = 40
COLS, ROWS = 19, 15          # odd numbers -> perfect maze layout
OFF_X = 20                   # centre the 19 columns inside the 800px window

LEVEL_SETTINGS = [
    # name,                     seed, loops, torch, keys, bats, bat speed, start_rc,               chamber_title
    ("The Cobalt Gateway",       101,  18,   155,     1,    1,    55,      (1, 1),                 "Azure Archway"),
    ("The Cyan Chasm",           202,  22,   125,     2,    2,    70,      (ROWS - 2, 1),          "Cobalt Sanctuary"),
    ("The Obsidian Labyrinth",   303,  26,   105,     3,    3,    85,      (ROWS // 2, 1),         "Obsidian Outpost"),
    ("The Abyssal Depths",       404,  28,    92,     4,    4,    95,      (1, COLS - 2),          "Abyss Caldera"),
    ("The Sanctum Core",         505,  32,    80,     5,    5,   110,      (ROWS - 2, COLS - 2),   "Sanctum Nexus"),
]


class Bat:
    def __init__(self, x, y, horizontal, speed, phase, bat_type="scout"):
        self.x, self.y = x, y
        self.dx, self.dy = (1, 0) if horizontal else (0, 1)
        self.speed = speed
        self.phase = phase
        self.bat_type = bat_type    # "scout" or "stalker"
        # --- shooting support: a bat can be killed and later respawns at home
        self.home = (x, y, self.dx, self.dy)
        self.alive = True
        self.respawn = 0.0          # countdown until it comes back
        self.spawn_age = 1.0        # < 0.5 while it is "growing in" (scaling)

    def revive(self):
        self.x, self.y, self.dx, self.dy = self.home
        self.alive = True
        self.spawn_age = 0.0


class Level:
    def __init__(self, index):
        name, seed, loops, torch, nkeys, nbats, bspeed, start_rc, chamber = LEVEL_SETTINGS[index]
        self.name, self.torch = name, torch
        self.chamber_title = chamber
        self.start_cell = start_rc
        rng = random.Random(seed)
        self.grid = self._carve(rng, loops)
        self.dist = self._bfs(start_rc)
        self.start = self.cell_center(*start_rc)
        far = sorted(self.dist, key=self.dist.get, reverse=True)
        self.exit = self.cell_center(*far[0])
        self.keys = [self.cell_center(r, c) for r, c in self._pick_keys(rng, nkeys, far[0])]
        self.boosts = [self.cell_center(r, c) for r, c in self._pick_boosts(rng, far[0])] if index >= 1 else []
        self.bats = self._pick_bats(rng, nbats, bspeed, index)
        self.segments = self._wall_segments()

    # ---------------- helpers ----------------
    @staticmethod
    def cell_center(r, c):
        return (OFF_X + c * CELL + CELL // 2, r * CELL + CELL // 2)

    def is_wall(self, px, py):
        c, r = int((px - OFF_X) // CELL), int(py // CELL)
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return True
        return self.grid[r][c] == 1

    # ---------------- generation with architectural chambers & loops ----------------
    def _carve(self, rng, loops):
        g = [[1] * COLS for _ in range(ROWS)]
        g[1][1] = 0
        stack = [(1, 1)]
        while stack:
            r, c = stack[-1]
            opts = [(r + dr, c + dc, dr, dc) for dr, dc in ((2, 0), (-2, 0), (0, 2), (0, -2))
                    if 0 < r + dr < ROWS - 1 and 0 < c + dc < COLS - 1 and g[r + dr][c + dc] == 1]
            if opts:
                nr, nc, dr, dc = rng.choice(opts)
                g[r + dr // 2][c + dc // 2] = 0
                g[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        # Architectural Central Chamber (Grand Nexus Plaza)
        cr, cc = ROWS // 2, COLS // 2
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if 0 < cr + dr < ROWS - 1 and 0 < cc + dc < COLS - 1:
                    g[cr + dr][cc + dc] = 0

        # Tactical loop paths for varied routing & dodging
        walls = []
        for r in range(1, ROWS - 1):
            for c in range(1, COLS - 1):
                if g[r][c] == 1:
                    if r % 2 == 1 and c % 2 == 0 and g[r][c - 1] == 0 and g[r][c + 1] == 0:
                        walls.append((r, c))
                    elif r % 2 == 0 and c % 2 == 1 and g[r - 1][c] == 0 and g[r + 1][c] == 0:
                        walls.append((r, c))
        rng.shuffle(walls)
        for r, c in walls[:loops]:
            g[r][c] = 0
        return g

    def _neighbours(self, r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= r + dr < ROWS and 0 <= c + dc < COLS and self.grid[r + dr][c + dc] == 0:
                yield r + dr, c + dc

    def _bfs(self, start):
        dist, q = {start: 0}, deque([start])
        while q:
            cur = q.popleft()
            for n in self._neighbours(*cur):
                if n not in dist:
                    dist[n] = dist[cur] + 1
                    q.append(n)
        return dist

    def _pick_keys(self, rng, n, exit_cell):
        start_cell = getattr(self, "start_cell", (1, 1))
        dead_ends = [cell for cell in self.dist
                     if len(list(self._neighbours(*cell))) == 1 and cell not in (start_cell, exit_cell)]
        rng.shuffle(dead_ends)
        chosen = []
        for cell in dead_ends:
            if self.dist[cell] < 5:
                continue
            if all(abs(cell[0] - o[0]) + abs(cell[1] - o[1]) >= 6 for o in chosen):
                chosen.append(cell)
            if len(chosen) == n:
                break
        others = [c for c in self.dist if c not in chosen and c != exit_cell and c != start_cell and self.dist[c] > 4]
        rng.shuffle(others)
        while len(chosen) < n and others:
            chosen.append(others.pop())
        return chosen

    def _pick_boosts(self, rng, exit_cell):
        start_cell = getattr(self, "start_cell", (1, 1))
        candidates = [c for c, d in self.dist.items() if d > 6 and c != exit_cell and c != start_cell]
        if candidates:
            rng.shuffle(candidates)
            return [candidates[0]]
        return []

    def _pick_bats(self, rng, n, speed, level_index=0):
        if n == 0:
            return []
        cands = []
        for (r, c), d in self.dist.items():
            if d < 7:
                continue
            h = (not self.is_wall(*self.cell_center(r, c - 1)) and not self.is_wall(*self.cell_center(r, c + 1))
                 and not self.is_wall(*self.cell_center(r, c - 2)))
            v = (not self.is_wall(*self.cell_center(r - 1, c)) and not self.is_wall(*self.cell_center(r + 1, c))
                 and not self.is_wall(*self.cell_center(r - 2, c)))
            if h:
                cands.append((r, c, True))
            elif v:
                cands.append((r, c, False))
        rng.shuffle(cands)
        bats, used = [], []
        for idx, (r, c, horiz) in enumerate(cands):
            if all(abs(r - a) + abs(c - b) >= 4 for a, b in used):
                x, y = self.cell_center(r, c)
                is_stalker = (level_index >= 2 and idx == 0)
                bat_type = "stalker" if is_stalker else "scout"
                bat_speed = int(speed * 1.25) if is_stalker else speed
                bats.append(Bat(x, y, horiz, bat_speed, rng.random() * 6, bat_type))
                used.append((r, c))
            if len(bats) == n:
                break
        return bats

    # ---------------- wall faces -> merged line segments ----------------
    def _wall_segments(self):
        segs = []
        g = self.grid

        def floor(r, c):
            return 0 <= r < ROWS and 0 <= c < COLS and g[r][c] == 0

        for dr, dc, horizontal in ((-1, 0, True), (1, 0, True), (0, -1, False), (0, 1, False)):
            outer = ROWS if horizontal else COLS
            inner = COLS if horizontal else ROWS
            for a in range(outer):
                run = None
                for b in range(inner + 1):
                    r, c = (a, b) if horizontal else (b, a)
                    face = b < inner and g[r][c] == 1 and floor(r + dr, c + dc)
                    if face and run is None:
                        run = b
                    if not face and run is not None:
                        if horizontal:
                            y = a * CELL + (CELL if dr == 1 else 0)
                            segs.append(((OFF_X + run * CELL, y), (OFF_X + b * CELL, y)))
                        else:
                            x = OFF_X + a * CELL + (CELL if dc == 1 else 0)
                            segs.append(((x, run * CELL), (x, b * CELL)))
                        run = None
        return segs
