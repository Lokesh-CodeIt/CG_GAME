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
        self.kind = bat_type
        # --- shooting support: a bat can be killed and later respawns at home
        self.home = (x, y, self.dx, self.dy)
        self.alive = True
        self.respawn = 0.0          # countdown until it comes back
        self.spawn_age = 1.0        # < 0.5 while it is "growing in" (scaling)
        self.path = []              # BFS corridor waypoints [(r, c), ...]
        self.repath_tick = 0.0

    def revive(self):
        self.x, self.y, self.dx, self.dy = self.home
        self.alive = True
        self.spawn_age = 0.0
        self.path = []

    def update_ai(self, level, px, py, dt):
        """Intelligent corridor navigation: Stalkers use BFS pathfinding toward player; Scouts patrol."""
        if not self.alive:
            return

        br, bc = int(self.y // CELL), int((self.x - OFF_X) // CELL)
        pr, pc = int(py // CELL), int((px - OFF_X) // CELL)
        dist_cells = abs(br - pr) + abs(bc - pc)

        # Stalkers actively hunt via BFS; Scouts switch to chase only when player is nearby in lit corridor
        should_hunt = (self.bat_type == "stalker") or (dist_cells <= 5)

        self.repath_tick += dt
        if should_hunt and (self.repath_tick >= 0.25 or not self.path):
            self.repath_tick = 0.0
            if 0 <= br < ROWS and 0 <= bc < COLS and 0 <= pr < ROWS and 0 <= pc < COLS:
                self.path = level.find_bfs_path((br, bc), (pr, pc))

        # Follow BFS waypoints if hunting and path exists
        if should_hunt and len(self.path) > 1:
            target_rc = self.path[1]
            tx, ty = level.cell_center(*target_rc)
            wx, wy = tx - self.x, ty - self.y
            dist_to_wp = math.hypot(wx, wy)
            if dist_to_wp < 4:
                self.path.pop(0)
            elif dist_to_wp > 0.01:
                self.dx = wx / dist_to_wp
                self.dy = wy / dist_to_wp
        else:
            # Standard corridor patrol with bounce on walls
            if level.is_wall(self.x + self.dx * 14, self.y + self.dy * 14):
                self.dx, self.dy = -self.dx, -self.dy

        # Move with speed
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt


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
        self.boosts = [self.cell_center(r, c) for r, c in self._pick_boosts(rng, far[0], "surge")]
        self.aegis = [self.cell_center(r, c) for r, c in self._pick_boosts(rng, far[0], "aegis")]
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

    def find_bfs_path(self, start_rc, target_rc):
        """Returns the shortest sequence of (r, c) open corridor cells from start_rc to target_rc."""
        if start_rc == target_rc:
            return [target_rc]
        if not (0 <= target_rc[0] < ROWS and 0 <= target_rc[1] < COLS) or self.grid[target_rc[0]][target_rc[1]] == 1:
            return []
        visited = {start_rc: None}
        q = deque([start_rc])
        while q:
            curr = q.popleft()
            if curr == target_rc:
                break
            for n in self._neighbours(*curr):
                if n not in visited:
                    visited[n] = curr
                    q.append(n)
        if target_rc not in visited:
            return []
        path = []
        curr = target_rc
        while curr is not None:
            path.append(curr)
            curr = visited[curr]
        path.reverse()
        return path

    def _pick_boosts(self, rng, exit_cell, crystal_type="surge"):
        start_cell = getattr(self, "start_cell", (1, 1))
        candidates = [c for c, d in self.dist.items() if d > 5 and c != exit_cell and c != start_cell]
        if not candidates:
            return []
        shuffled = list(candidates)
        rng.shuffle(shuffled)
        if crystal_type == "surge":
            return [shuffled[0]] if shuffled else []
        else:
            return [shuffled[1]] if len(shuffled) > 1 else []

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
