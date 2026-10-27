"""
game.py  -  game logic + drawing (uses graphics.py and matrix.py)
"""
import math
import random
import pygame

import graphics as gfx
from graphics import Renderer
from matrix import compose, translate, rotate, scale, shear, apply, reflect_y
from levels import Level, CELL, COLS, ROWS, OFF_X, LEVEL_SETTINGS

W, H = 800, 600
PLAYER_R = 8
PLAYER_SPEED = 165
ARROW_SPEED = 430          # pixels / second
SHOOT_COOLDOWN = 0.35      # seconds between two arrows
BLAST_TIME = 0.6           # life of the explosion
BAT_RESPAWN = 10.0         # seconds before a killed bat comes back
BG = (5, 5, 10)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.r = Renderer(screen)
        self.font = pygame.font.SysFont(None, 26)
        self.big = pygame.font.SysFont(None, 64)
        self.mid = pygame.font.SysFont(None, 34)
        self.glow_cache = {}
        self.t = 0.0
        self.state = "title"
        self.score = 0
        self.embers, self.ripples = [], []
        self.arrows, self.blasts, self.debris = [], [], []
        self.shoot_cd = 0.0

    # ------------------------------------------------------------ setup
    def new_game(self):
        self.score, self.lives, self.level_no = 0, 3, 0
        self.load_level()

    def load_level(self):
        self.level = Level(self.level_no)
        self.px, self.py = self.level.start
        self.angle = 0.0
        self.keys_left = list(self.level.keys)
        self.keys_total = len(self.keys_left)
        self.level_time = 0.0
        self.invuln = 1.5
        self.msg, self.msg_t = "", 0.0
        self.embers, self.ripples = [], []
        self.arrows, self.blasts, self.debris = [], [], []
        self.shoot_cd = 0.0
        self.state = "play"

    def reset_level(self):
        self.load_level()

    # ------------------------------------------------------------ update
    def update(self, dt, vx=0.0, vy=0.0):
        self.t += dt
        if self.state != "play":
            return
        L = self.level
        self.level_time += dt
        self.invuln = max(0.0, self.invuln - dt)
        self.msg_t = max(0.0, self.msg_t - dt)
        self.shoot_cd = max(0.0, self.shoot_cd - dt)

        # --- translation: move the player (axis by axis so we can slide on walls)
        if vx or vy:
            mag = math.hypot(vx, vy)
            vx, vy = vx / mag, vy / mag
            target = math.atan2(vy, vx)
            diff = (target - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * min(1.0, dt * 14)
        self.px += vx * PLAYER_SPEED * dt
        self._collide()
        self.py += vy * PLAYER_SPEED * dt
        self._collide()

        # --- bats patrol and bounce back from walls
        for b in L.bats:
            if not b.alive:                              # dead: wait, then respawn
                b.respawn -= dt
                if b.respawn <= 0:
                    if math.hypot(b.home[0] - self.px, b.home[1] - self.py) < 90:
                        b.respawn = 0.5                  # player too close, wait a bit
                    else:
                        b.revive()
                continue
            b.spawn_age += dt
            b.x += b.dx * b.speed * dt
            b.y += b.dy * b.speed * dt
            if L.is_wall(b.x + b.dx * 14, b.y + b.dy * 14):
                b.dx, b.dy = -b.dx, -b.dy
            if (self.invuln <= 0 and b.spawn_age >= 0.5
                    and math.hypot(b.x - self.px, b.y - self.py) < 17):
                self._hit()

        # --- arrows: TRANSLATION along the aim direction
        for a in self.arrows[:]:
            a[3] += dt                                   # age
            ca, sa = math.cos(a[2]), math.sin(a[2])
            a[0] += ca * ARROW_SPEED * dt
            a[1] += sa * ARROW_SPEED * dt
            tx, ty = a[0] + ca * 10, a[1] + sa * 10      # arrow tip
            if L.is_wall(tx, ty) or a[3] > 1.6:
                self.arrows.remove(a)
                self._spawn_sparks(tx, ty)
                continue
            for b in L.bats:
                if b.alive and b.spawn_age >= 0.3 and math.hypot(b.x - tx, b.y - ty) < 17:
                    self._kill_bat(b)
                    self.arrows.remove(a)
                    break

        # --- explosions (age -> scaling), debris shards (translate + rotate + scale)
        for bl in self.blasts[:]:
            bl[2] += dt
            if bl[2] > BLAST_TIME:
                self.blasts.remove(bl)
        for d in self.debris[:]:
            d[0] += d[2] * dt; d[1] += d[3] * dt
            d[4] += d[5] * dt                            # spin
            d[6] += dt
            if d[6] >= d[7]:
                self.debris.remove(d)

        # --- keys
        for k in self.keys_left[:]:
            if math.hypot(k[0] - self.px, k[1] - self.py) < 18:
                self.keys_left.remove(k)
                self.ripples.append([k[0], k[1], 0.0])
                self.score += 250
                self._say("Key collected!")

        # --- exit
        if math.hypot(L.exit[0] - self.px, L.exit[1] - self.py) < 20:
            if self.keys_left:
                self._say("The portal is sealed - find all keys!")
            else:
                self.score += max(100, 1000 - int(self.level_time) * 10)
                self.level_no += 1
                self.state = "win" if self.level_no >= len(LEVEL_SETTINGS) else "levelclear"

        # --- particles
        self._spawn_embers(dt)
        for e in self.embers[:]:
            e[0] += e[2] * dt; e[1] += e[3] * dt; e[4] -= dt
            if e[4] <= 0:
                self.embers.remove(e)
        for rp in self.ripples[:]:
            rp[2] += dt
            if rp[2] > 0.7:
                self.ripples.remove(rp)

    # ------------------------------------------------------------ shooting
    def shoot(self):
        """Fire an arrow in the direction the player is facing."""
        if self.state != "play" or self.shoot_cd > 0:
            return
        self.shoot_cd = SHOOT_COOLDOWN
        x = self.px + math.cos(self.angle) * 12
        y = self.py + math.sin(self.angle) * 12
        self.arrows.append([x, y, self.angle, 0.0])      # [x, y, angle, age]

    def _kill_bat(self, b):
        b.alive = False
        b.respawn = BAT_RESPAWN
        self.blasts.append([b.x, b.y, 0.0])
        for i in range(9):                               # shards fly out in all directions
            ang = i * 2 * math.pi / 9 + random.uniform(-0.3, 0.3)
            sp = random.uniform(70, 150)
            self.debris.append([b.x, b.y, math.cos(ang) * sp, math.sin(ang) * sp,
                                random.uniform(0, 6.28), random.uniform(-14, 14),
                                0.0, random.uniform(0.45, 0.8), (200, 60, 120)])
        self.score += 150
        self._say("Bat destroyed!  +150")

    def _spawn_sparks(self, x, y):
        for i in range(5):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(30, 90)
            self.debris.append([x, y, math.cos(ang) * sp, math.sin(ang) * sp,
                                random.uniform(0, 6.28), random.uniform(-10, 10),
                                0.0, random.uniform(0.2, 0.4), (255, 200, 110)])

    def _say(self, text):
        self.msg, self.msg_t = text, 1.6

    def _hit(self):
        self.lives -= 1
        self.ripples.append([self.px, self.py, 0.0])
        if self.lives <= 0:
            self.state = "gameover"
            return
        self.px, self.py = self.level.start
        self.invuln = 2.0
        self._say("Ouch! A bat got you.")

    def _collide(self):
        """Circle-vs-wall-cell collision: push the player out of any wall."""
        L = self.level
        cx, cy = int((self.px - OFF_X) // CELL), int(self.py // CELL)
        for rr in range(cy - 1, cy + 2):
            for cc in range(cx - 1, cx + 2):
                if not (0 <= rr < ROWS and 0 <= cc < COLS) or L.grid[rr][cc] == 0:
                    continue
                left, top = OFF_X + cc * CELL, rr * CELL
                nx = min(max(self.px, left), left + CELL)
                ny = min(max(self.py, top), top + CELL)
                dx, dy = self.px - nx, self.py - ny
                d2 = dx * dx + dy * dy
                if 1e-9 < d2 < PLAYER_R ** 2:
                    d = math.sqrt(d2)
                    self.px += dx / d * (PLAYER_R - d)
                    self.py += dy / d * (PLAYER_R - d)

    def _flame_world(self):
        m = compose(translate(self.px, self.py), rotate(self.angle), translate(-2, -14))
        return apply(m, [(0, 0)])[0]

    def _spawn_embers(self, dt):
        if random.random() < dt * 28:
            fx, fy = self._flame_world()
            self.embers.append([fx, fy - 4, random.uniform(-14, 14), random.uniform(-40, -12),
                                random.uniform(0.4, 0.9)])

    # ------------------------------------------------------------ drawing
    def _glow(self, R):
        """Pre-render the warm torch glow with the MIDPOINT CIRCLE algorithm."""
        if R not in self.glow_cache:
            s = pygame.Surface((2 * R + 1, 2 * R + 1), pygame.SRCALPHA)
            for r in range(R, 0, -1):                    # big disc first, small last
                a = int(120 * (1 - r / R) ** 2)
                for y, xl, xr in gfx.circle_spans(R, R, r):
                    s.fill((255, 150, 50, a), (xl, y, xr - xl + 1, 1))
            self.glow_cache[R] = s
        return self.glow_cache[R]

    def draw(self):
        if self.state == "title":
            return self.draw_title()
        L, r, surf = self.level, self.r, self.screen
        surf.fill(BG)

        # the torch flickers -> window size changes a little every frame
        half = L.torch + 4 * math.sin(self.t * 7) + 2.5 * math.sin(self.t * 13.1)
        r.set_window(int(self.px), int(self.py), int(half))
        xmin, ymin, xmax, ymax = r.win
        win_rect = pygame.Rect(xmin, ymin, xmax - xmin, ymax - ymin)

        self._draw_cells(win_rect)

        # warm glow, limited to the clip window
        R = int(L.torch * 1.3)
        surf.set_clip(win_rect)
        surf.blit(self._glow(R), (int(self.px) - R, int(self.py) - R))
        surf.set_clip(None)

        # wall faces: every segment is CLIPPED against the torch window
        for p0, p1 in L.segments:
            r.line(p0, p1, (205, 170, 120), thick=2)

        self._draw_exit()
        for k in self.keys_left:
            self._draw_key(k)
        for b in L.bats:
            self._draw_bat(b)
        self._draw_arrows()
        self._draw_player()
        self._draw_blasts()
        self._draw_effects()
        self._draw_window_frame(xmin, ymin, xmax, ymax)
        self._draw_hud()
        if self.state != "play":
            self._draw_overlay()

    # floor + rock cells, clipped by rectangle intersection
    def _draw_cells(self, win_rect):
        L, r = self.level, self.r
        xmin, ymin, xmax, ymax = r.win
        c0 = max(0, int((xmin - OFF_X) // CELL)); c1 = min(COLS - 1, int((xmax - OFF_X) // CELL))
        r0 = max(0, int(ymin // CELL));            r1 = min(ROWS - 1, int(ymax // CELL))
        for row in range(r0, r1 + 1):
            for col in range(c0, c1 + 1):
                rect = pygame.Rect(OFF_X + col * CELL, row * CELL, CELL, CELL)
                vis = rect.clip(win_rect)                # rectangle clipping
                if vis.w <= 0 or vis.h <= 0:
                    continue
                f = r.fade(*rect.center)
                if L.grid[row][col] == 1:
                    v = ((row * 7 + col * 13) % 5) * 4
                    base = (30 + v, 22 + v, 22 + v)
                else:
                    v = ((row * 5 + col * 11) % 3) * 3
                    base = (78 + v, 68 + v, 78 + v)
                self.screen.fill((int(base[0] * f), int(base[1] * f), int(base[2] * f)), vis)
                if L.grid[row][col] == 0:                # a few pebbles on the floor
                    for i in range(3):
                        px = rect.x + (row * 17 + col * 29 + i * 13) % (CELL - 4) + 2
                        py = rect.y + (row * 31 + col * 7 + i * 19) % (CELL - 4) + 2
                        if r.in_window(px, py):
                            c = int(70 * f)
                            self.screen.fill((c, c, c + 8), (px, py, 2, 2))

    def _draw_player(self):
        r = self.r
        blink = self.invuln > 0 and int(self.t * 14) % 2 == 0
        # body (midpoint circle, filled)
        r.disc(self.px, self.py, PLAYER_R, (40, 190, 200) if not blink else (255, 255, 255), use_fade=False)
        # direction arrow  -> ROTATION + TRANSLATION
        arrow = [(10, 0), (-5, -6), (-2, 0), (-5, 6)]
        pts = apply(compose(translate(self.px, self.py), rotate(self.angle)), arrow)
        r.fill_polygon(pts, (235, 250, 255))
        # torch stick + flame  -> TRANSLATION + ROTATION + SHEAR + SCALING
        fx, fy = self._flame_world()
        r.line((self.px, self.py), (fx, fy + 1), (120, 80, 40), thick=2, use_fade=False)
        flicker = 0.85 + 0.25 * math.sin(self.t * 21)
        wob = 0.35 * math.sin(self.t * 13)
        flame = [(0, -11), (4, -4), (3, 2), (0, 4), (-3, 2), (-4, -4)]
        m = compose(translate(fx, fy), shear(wob, 0), scale(flicker, flicker + 0.1))
        r.fill_polygon(apply(m, flame), (255, 120, 30))
        m2 = compose(translate(fx, fy), shear(wob, 0), scale(0.55 * flicker, 0.6 * flicker))
        r.fill_polygon(apply(m2, flame), (255, 230, 120))

    def _draw_key(self, k):
        r = self.r
        bob = 3 * math.sin(self.t * 3 + k[0])
        spin = math.cos(self.t * 3.5)                    # x-scale -> looks like a spinning gem
        pulse = 1 + 0.12 * math.sin(self.t * 6)
        gem = [(0, -11), (8, 0), (0, 11), (-8, 0)]
        m = compose(translate(k[0], k[1] + bob), scale(spin * pulse, pulse))
        r.fill_polygon(apply(m, gem), (255, 215, 60))
        r.polyline(apply(m, gem), (255, 250, 190), 1, use_fade=False)
        r.circle(k[0], k[1] + bob, int(15 + 3 * math.sin(self.t * 5)), (150, 120, 30), 1)

    def _draw_bat(self, b):
        r = self.r
        if not b.alive:
            return
        # respawn animation: SCALING from 0 up to full size (with a little overshoot)
        k = min(1.0, b.spawn_age / 0.5)
        grow = 1.0 if k >= 1 else math.sin(k * math.pi / 2) * (1 + 0.25 * math.sin(k * math.pi))
        flap = 0.2 + 0.8 * abs(math.sin(self.t * 11 + b.phase))
        sx = 1 if (b.dx + b.dy) >= 0 else -1             # REFLECTION when flying the other way
        base = compose(translate(b.x, b.y + 2 * math.sin(self.t * 4 + b.phase)), scale(1.3 * sx * grow, 1.3 * grow))
        wing = [(-1, -2), (-5, -15), (-12, -13), (-15, -4), (-8, -5)]
        for sy in (1, -1):                               # upper wing + mirrored lower wing
            m = compose(base, scale(1, sy * flap))
            r.fill_polygon(apply(m, wing), (190, 50, 110))
        r.fill_polygon(apply(base, [(7, 0), (2, -5), (-6, -3), (-6, 3), (2, 5)]), (90, 20, 50))
        r.disc(b.x + 3 * sx, b.y - 1, 1, (255, 60, 60), use_fade=False)

    def _draw_arrows(self):
        """Arrow = polygons moved with  M = T(x, y) x R(angle) x S(stretch, 1)."""
        r = self.r
        head = [(10, 0), (3, -4), (3, 4)]
        shaft = [(3, -1), (-14, -1), (-14, 1), (3, 1)]
        fletch1 = [(-9, 0), (-15, -5), (-12, -5), (-6, 0)]
        fletch2 = [(-9, 0), (-15, 5), (-12, 5), (-6, 0)]
        for x, y, ang, age in self.arrows:
            stretch = 1 + 0.6 * max(0.0, 1 - age * 9)     # SCALING: stretched at launch
            m = compose(translate(x, y), rotate(ang), scale(stretch, 1))   # TRANSLATE . ROTATE . SCALE
            r.fill_polygon(apply(m, shaft), (170, 125, 70))
            r.fill_polygon(apply(m, fletch1), (230, 230, 240))
            r.fill_polygon(apply(m, fletch2), (230, 230, 240))
            r.fill_polygon(apply(m, head), (235, 240, 255))

    def _draw_blasts(self):
        """Explosion: a star that is SCALED up (and rotated) while it fades out."""
        r = self.r
        star = []
        for i in range(16):                               # 8-point star
            rad = 10 if i % 2 == 0 else 4.5
            a = i * math.pi / 8
            star.append((rad * math.cos(a), rad * math.sin(a)))
        for x, y, age in self.blasts:
            p = age / BLAST_TIME                          # 0 -> 1
            s = 0.3 + 3.4 * math.sin(p * math.pi / 2)     # scale factor grows fast, then slows
            fade = (1 - p) ** 0.6
            m = compose(translate(x, y), rotate(p * 2.0), scale(s, s))
            r.fill_polygon(apply(m, star), (int(255 * fade), int(110 * fade), int(30 * fade)))
            m2 = compose(translate(x, y), rotate(-p * 2.5), scale(s * 0.55, s * 0.55))
            r.fill_polygon(apply(m2, star), (int(255 * fade), int(235 * fade), int(140 * fade)))
            r.circle(x, y, int(s * 13), (int(255 * fade), int(180 * fade), int(90 * fade)), 2)
        for x, y, vx, vy, rot, vrot, age, life, col in self.debris:
            k = 1 - age / life                            # shard SHRINKS as it ages
            m = compose(translate(x, y), rotate(rot), scale(k, k))
            r.fill_polygon(apply(m, [(5, 0), (-3, -3), (-3, 3)]), col)

    def _draw_exit(self):
        r, L = self.r, self.level
        ex, ey = L.exit
        open_ = not self.keys_left
        pulse = 1 + 0.15 * math.sin(self.t * 5)
        star = []
        for i in range(10):                              # 5-point star
            rad = 15 if i % 2 == 0 else 7
            a = i * math.pi / 5 - math.pi / 2
            star.append((rad * math.cos(a), rad * math.sin(a)))
        m = compose(translate(ex, ey), rotate(self.t * (2.0 if open_ else 0.5)), scale(pulse, pulse))
        col = (70, 255, 170) if open_ else (150, 55, 60)
        r.fill_polygon(apply(m, star), col)
        r.circle(ex, ey, int(19 + 2 * math.sin(self.t * 4)), col, 1)

    def _draw_effects(self):
        r = self.r
        for e in self.embers:
            if r.in_window(e[0], e[1]):
                a = max(0.0, e[4] / 0.9)
                self.screen.fill((int(255 * a), int(150 * a), int(40 * a)), (int(e[0]), int(e[1]), 2, 2))
        for x, y, age in self.ripples:                   # expanding midpoint circles
            a = 1 - age / 0.7
            r.circle(x, y, int(age * 110) + 2, (int(255 * a), int(220 * a), int(100 * a)), 2)

    def _draw_window_frame(self, xmin, ymin, xmax, ymax):
        c = (255, 190, 90)
        n = 18
        for (x, y, sx, sy) in ((xmin, ymin, 1, 1), (xmax, ymin, -1, 1),
                               (xmin, ymax, 1, -1), (xmax, ymax, -1, -1)):
            self.r.line((x, y), (x + sx * n, y), c, 3, use_fade=False)
            self.r.line((x, y), (x, y + sy * n), c, 3, use_fade=False)

    # ------------------------------------------------------------ HUD & screens
    def _text(self, txt, font, color, pos, center=False):
        img = font.render(txt, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, rect)

    def _draw_hud(self):
        self.screen.fill((0, 0, 0), (0, 0, W, 30))
        self._text(f"Level {self.level_no + 1}/3 - {self.level.name}", self.font, (230, 200, 140), (10, 6))
        self._text(f"Keys {self.keys_total - len(self.keys_left)}/{self.keys_total}", self.font, (255, 215, 60), (330, 6))
        self._text(f"Score {self.score}", self.font, (200, 230, 255), (440, 6))
        self._text("Lives", self.font, (230, 120, 130), (580, 6))
        for i in range(self.lives):                       # lives drawn with midpoint circles
            self.r.set_window(0, 0, 10000, 10000)
            self.r.disc(650 + i * 24, 15, 8, (230, 70, 90), use_fade=False)
        self.screen.fill((0, 0, 0), (0, H - 24, W, 24))
        self._text(f"[SPACE] Shoot   [L] Line: {self.r.line_algo}   [C] Clip: {self.r.clip_algo}   [R] Restart   [ESC] Quit",
                   pygame.font.SysFont(None, 22), (150, 150, 170), (10, H - 18))
        ready = 1 - self.shoot_cd / SHOOT_COOLDOWN        # arrow reload bar
        self.screen.fill((50, 50, 60), (W - 90, H - 17, 80, 10))
        self.screen.fill((110, 230, 160) if ready >= 1 else (230, 170, 80), (W - 90, H - 17, int(80 * ready), 10))
        if self.msg_t > 0:
            self._text(self.msg, self.mid, (255, 235, 170), (W // 2, 60), center=True)

    def _draw_overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 170))
        self.screen.blit(s, (0, 0))
        if self.state == "levelclear":
            self._text("LEVEL COMPLETE!", self.big, (110, 255, 180), (W // 2, 230), True)
            self._text(f"Score: {self.score}", self.mid, (230, 230, 255), (W // 2, 290), True)
            self._text("Press ENTER for the next cave", self.mid, (255, 215, 120), (W // 2, 350), True)
        elif self.state == "gameover":
            self._text("YOU WERE LOST IN THE DARK", self.big, (255, 100, 110), (W // 2, 230), True)
            self._text(f"Final score: {self.score}", self.mid, (230, 230, 255), (W // 2, 290), True)
            self._text("Press ENTER to try again", self.mid, (255, 215, 120), (W // 2, 350), True)
        elif self.state == "win":
            self._text("YOU ESCAPED THE CAVE!", self.big, (110, 255, 180), (W // 2, 230), True)
            self._text(f"Final score: {self.score}", self.mid, (230, 230, 255), (W // 2, 290), True)
            self._text("Press ENTER to play again", self.mid, (255, 215, 120), (W // 2, 350), True)

    def draw_title(self):
        r, surf = self.r, self.screen
        surf.fill(BG)
        r.set_window(W // 2, H // 2, 10000, fade_radius=10000)
        # animated background: rotating + scaling squares (composite transformations)
        for i in range(14):
            s = 40 + i * 28
            a = self.t * 0.25 * (1 if i % 2 else -1) + i * 0.2
            sq = [(-s / 2, -s / 2), (s / 2, -s / 2), (s / 2, s / 2), (-s / 2, s / 2)]
            m = compose(translate(W // 2, H // 2), rotate(a), scale(1 + 0.06 * math.sin(self.t + i), 1))
            col = (int(30 + 12 * i), int(20 + 7 * i), int(15 + 3 * i))
            r.polyline(apply(m, sq), col, 1, use_fade=False)
        for i in range(8):                                # glowing midpoint rings
            r.circle(W // 2, H // 2, 20 + i * 9 + int(4 * math.sin(self.t * 2 + i)), (255, 150 - i * 12, 40), 1)
        self._text("DARK CAVE EXPLORER", self.big, (255, 205, 120), (W // 2, 90), True)
        self._text("A Computer Graphics Project", self.mid, (170, 170, 200), (W // 2, 135), True)
        lines = ["Arrow keys / WASD  -  move        SPACE  -  shoot an arrow at the bats",
                 "Collect every key, then enter the glowing portal",
                 "Your torch is a CLIP WINDOW - you only see what is inside it!",
                 "Shoot or avoid the bats   -   3 caves, 3 lives",
                 "[L] switch DDA / Bresenham     [C] switch Cohen-Sutherland / Liang-Barsky"]
        for i, t in enumerate(lines):
            self._text(t, self.font, (210, 210, 230), (W // 2, 440 + i * 26), True)
        if int(self.t * 2) % 2 == 0:
            self._text("Press ENTER to start", self.mid, (255, 235, 150), (W // 2, 395), True)
