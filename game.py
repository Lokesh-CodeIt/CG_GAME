"""
game.py  -  EmberVault: The Crystal Maze
Game logic and computer graphics rendering (uses graphics.py and matrix.py)
"""
import os
import math
import random
import pygame

import graphics as gfx
from graphics import Renderer
from matrix import compose, translate, rotate, scale, shear, apply, reflect_y
from levels import Level, CELL, COLS, ROWS, OFF_X, LEVEL_SETTINGS
from cg_lab import CGLab

W, H = 800, 600
PLAYER_R = 8
BASE_PLAYER_SPEED = 165
BOOST_PLAYER_SPEED = 222
ARROW_SPEED = 430          # pixels / second
SHOOT_COOLDOWN = 0.35      # seconds between two arrows
BLAST_TIME = 0.6           # life of the explosion
BAT_RESPAWN = 10.0         # seconds before a killed bat comes back

# --- Visual Identity: Cool Dark Navy, Black, and Cyan Theme (No Brown/Yellow) ---
BG = (8, 12, 20)                  # Deep midnight navy-black
WALL_DARK = (14, 20, 32)          # Obsidian navy wall base
WALL_LIGHT = (22, 32, 50)         # Cool navy wall facet
WALL_BEVEL = (34, 50, 76)         # Cool steel-cyan bevel
WALL_EDGE = (0, 220, 245)         # Luminous electric cyan wall boundary line
FLOOR_BASE = (26, 40, 60)         # Cool navy-slate walkable path
FLOOR_ALT = (30, 46, 68)          # Floor paver variation
PEBBLE_COLOR = (25, 160, 215)     # Bioluminescent cyan dust specks

# Interactive & Accent Colors
CYAN_ELECTRIC = (0, 235, 255)     # Electric cyan torch glow & player core
CYAN_GLOW = (20, 200, 245)        # Secondary cyan
CYAN_ACCENT = (20, 190, 230)      # Vivid cyan accent
CYAN_BOOST = (80, 240, 255)       # Speed boost crystal
PURPLE_VOID = (110, 35, 175)      # Enemy carapace purple
PURPLE_DARK = (65, 15, 105)       # Enemy shadow body
NEON_GREEN = (57, 255, 20)        # Enemy plasma wings & glowing eyes
NEON_GREEN_BRIGHT = (140, 255, 100) # Specular eye highlight
AMBER_GOLD = (255, 205, 45)       # Vault keys & score
GOLD_BRIGHT = (255, 245, 160)     # Key sparkle / star highlight
CORAL_RED = (235, 72, 84)         # Damage indicators & life hearts
VIOLET_ACCENT = (165, 95, 235)    # Portal aura ring & level victory banner
TEXT_WHITE = (244, 248, 252)      # High-contrast white text
TEXT_MUTED = (155, 175, 195)      # Soft grey
HUD_BG = (10, 15, 24)             # Deep navy HUD bar
HUD_BORDER = (25, 55, 80)         # HUD divider line


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.r = Renderer(screen)
        self.cg_lab = CGLab(screen)

        # Standardized, robust fonts with graceful fallbacks
        self.font_title = pygame.font.SysFont("segoe ui", 36, bold=True) or pygame.font.SysFont(None, 40)
        self.font_subtitle = pygame.font.SysFont("segoe ui", 22, bold=True) or pygame.font.SysFont(None, 24)
        self.font_btn = pygame.font.SysFont("segoe ui", 20, bold=True) or pygame.font.SysFont(None, 22)
        self.font = pygame.font.SysFont("segoe ui", 18, bold=True) or pygame.font.SysFont(None, 20)
        self.font_body = pygame.font.SysFont("segoe ui", 16) or pygame.font.SysFont(None, 18)
        self.font_sm = pygame.font.SysFont("segoe ui", 14) or pygame.font.SysFont(None, 16)
        self.big = pygame.font.SysFont("segoe ui", 38, bold=True) or pygame.font.SysFont(None, 42)
        self.mid = pygame.font.SysFont("segoe ui", 22, bold=True) or pygame.font.SysFont(None, 24)

        self.glow_cache = {}
        self.t = 0.0
        self.state = "title"
        self.selected_level = 0
        self.score = 0
        self.best_score = self._load_best_score()
        self.badges = set()
        self.show_help = False
        self.show_grid = False
        self.dmg_flash = 0.0
        self.boost_timer = 0.0

        # Action-based Abilities & Status (No countdown timers!)
        self.dash_charges = 2
        self.dash_step_counter = 0
        self.shield_charges = 1
        self.shield_active = False
        self.surge_charges = 0
        self.afterimages = []
        self.discovered = [[False] * COLS for _ in range(ROWS)]
        self.level_bats_killed = 0
        self.level_dashes_used = 0
        self.level_start_lives = 3

        self.float_texts = []
        self.embers, self.ripples = [], []
        self.title_stars = [[random.uniform(0, W), random.uniform(0, H), random.uniform(15, 45), random.uniform(0.3, 1.0)] for _ in range(40)]
        self.arrows, self.blasts, self.debris = [], [], []
        self.shoot_cd = 0.0
        self.minimap_bg = None

    # ------------------------------------------------------------ Persistence
    def _score_file_path(self):
        return os.path.join(os.path.dirname(__file__), "best_score.txt")

    def _load_best_score(self):
        try:
            p = self._score_file_path()
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 0

    def _save_best_score(self):
        if self.score > self.best_score:
            self.best_score = self.score
            try:
                p = self._score_file_path()
                with open(p, "w", encoding="utf-8") as f:
                    f.write(str(self.best_score))
            except Exception:
                pass

    # ------------------------------------------------------------ State & Level Select
    def toggle_pause(self):
        if self.state == "play":
            self.state = "pause"
        elif self.state == "pause":
            self.state = "play"

    def toggle_help(self):
        self.show_help = not self.show_help

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self._say("Grid overlay: " + ("ENABLED" if self.show_grid else "DISABLED"))

    def enter_cg_lab(self):
        self.state = "cglab"

    def exit_cg_lab(self):
        self.state = "title"

    def handle_mouse_click(self, pos):
        if self.state == "title":
            btn1_rect = pygame.Rect(W // 2 - 250, 372, 235, 46)
            btn2_rect = pygame.Rect(W // 2 + 15, 372, 235, 46)
            if btn1_rect.collidepoint(pos):
                self.new_game()
                return True
            elif btn2_rect.collidepoint(pos):
                self.enter_cg_lab()
                return True
        return False

    def select_level(self, idx):
        if 0 <= idx < len(LEVEL_SETTINGS):
            self.selected_level = idx

    def cycle_level(self, delta):
        n = len(LEVEL_SETTINGS)
        self.selected_level = (self.selected_level + delta) % n

    # ------------------------------------------------------------ Setup
    def new_game(self):
        self.score, self.lives = 0, 3
        self.level_no = self.selected_level
        self.load_level()

    def load_level(self):
        self.level = Level(self.level_no)
        self.px, self.py = self.level.start
        self.angle = 0.0
        self.keys_left = list(self.level.keys)
        self.keys_total = len(self.keys_left)
        self.boosts_left = list(self.level.boosts)
        self.aegis_left = list(getattr(self.level, "aegis", []))
        self.level_time = 0.0
        self.invuln = 1.5
        self.boost_timer = 0.0
        self.surge_charges = 0
        self.shield_active = False
        self.shield_charges = max(1, self.shield_charges)
        self.dash_charges = max(2, self.dash_charges)
        self.dash_step_counter = 0
        self.level_bats_killed = 0
        self.level_dashes_used = 0
        self.level_start_lives = self.lives
        self.afterimages = []

        # Initialize and reveal starting chamber in Fog of War
        self.discovered = [[False] * COLS for _ in range(ROWS)]
        sr, sc = self.level.start_cell
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if 0 <= sr + dr < ROWS and 0 <= sc + dc < COLS:
                    self.discovered[sr + dr][sc + dc] = True

        self.msg, self.msg_t = "", 0.0
        self.embers, self.ripples = [], []
        self.arrows, self.blasts, self.debris = [], [], []
        self.float_texts = []
        self.dmg_flash = 0.0
        self.shoot_cd = 0.0
        self.show_help = False
        self._build_minimap()
        self.state = "play"

    def reset_level(self):
        self.load_level()

    # ------------------------------------------------------------ Mini-map Cache
    def _build_minimap(self):
        surf = pygame.Surface((COLS * 5, ROWS * 5))
        surf.fill((10, 16, 26))
        for r in range(ROWS):
            for c in range(COLS):
                if self.level.grid[r][c] == 1:
                    pygame.draw.rect(surf, (22, 34, 52), (c * 5, r * 5, 5, 5))
                else:
                    pygame.draw.rect(surf, (14, 22, 34), (c * 5, r * 5, 5, 5))
        self.minimap_bg = surf

    # ------------------------------------------------------------ Update
    def update(self, dt, vx=0.0, vy=0.0):
        self.t += dt
        self.dmg_flash = max(0.0, self.dmg_flash - dt)

        # Update drifting title stars
        for st in self.title_stars:
            st[1] -= st[2] * dt
            if st[1] < -10:
                st[1] = H + 10
                st[0] = random.uniform(0, W)

        # Update floating feedback texts regardless of pause
        for ft in self.float_texts[:]:
            ft[1] += ft[3] * dt
            ft[5] += dt
            if ft[5] >= ft[6]:
                self.float_texts.remove(ft)

        # Pause or Help stops all world physics, animations, and game timers
        if self.state != "play" or self.show_help:
            return

        L = self.level
        self.level_time += dt
        self.invuln = max(0.0, self.invuln - dt)
        self.msg_t = max(0.0, self.msg_t - dt)
        self.shoot_cd = max(0.0, self.shoot_cd - dt)

        # Dynamic speed with Crystal Surge charges (Action-based, zero timer!)
        speed = BOOST_PLAYER_SPEED if self.surge_charges > 0 else BASE_PLAYER_SPEED

        # --- translation: move the player (axis by axis for wall sliding)
        if vx or vy:
            mag = math.hypot(vx, vy)
            vx, vy = vx / mag, vy / mag
            target = math.atan2(vy, vx)
            diff = (target - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * min(1.0, dt * 14)
            # Recharging dash by walking (action-based, zero timer!)
            self.dash_step_counter += 1
            if self.dash_step_counter >= 35:
                self.dash_step_counter = 0
                if self.dash_charges < 3:
                    self.dash_charges += 1
                    self.float_texts.append(["DASH READY +1", self.px, self.py - 14, -35, CYAN_ACCENT, 0.0, 0.9])

        self.px += vx * speed * dt
        self._collide()
        self.py += vy * speed * dt
        self._collide()

        # Reveal Fog of War around player's torch
        cr, cc = int(self.py // CELL), int((self.px - OFF_X) // CELL)
        reach = int(math.ceil(self.level.torch / CELL)) + 1
        for dr in range(-reach, reach + 1):
            for dc in range(-reach, reach + 1):
                rr, cc_cell = cr + dr, cc + dc
                if 0 <= rr < ROWS and 0 <= cc_cell < COLS:
                    cx_w, cy_w = Level.cell_center(rr, cc_cell)
                    if math.hypot(cx_w - self.px, cy_w - self.py) <= self.level.torch + 15:
                        self.discovered[rr][cc_cell] = True

        # Update dash motion trail afterimages
        for img in self.afterimages[:]:
            img[3] += dt
            if img[3] >= img[4]:
                self.afterimages.remove(img)

        # Emit cyan boost particles if Crystal Surge active
        if self.surge_charges > 0 and random.random() < dt * 25:
            self.debris.append([self.px, self.py, random.uniform(-20, 20), random.uniform(-20, 20),
                                0.0, 0.0, 0.0, random.uniform(0.2, 0.4), CYAN_BOOST])

        # --- creatures: Intelligent corridor AI with BFS pathfinding
        for b in L.bats:
            if not b.alive:                              # dead: wait, then respawn
                b.respawn -= dt
                if b.respawn <= 0:
                    if math.hypot(b.home[0] - self.px, b.home[1] - self.py) < 90:
                        b.respawn = 0.5                  # player too close, delay
                    else:
                        b.revive()
                continue
            b.spawn_age += dt
            b.update_ai(L, self.px, self.py, dt)
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
                if not self.keys_left:
                    self.badges.add("KEYMASTER")
                if self.shield_charges < 2:
                    self.shield_charges += 1
                self.ripples.append([k[0], k[1], 0.0])
                self.score += 250
                self._save_best_score()
                self._say("Vault Key Recovered! +250")
                self.float_texts.append(["+250 KEY RECOVERED", k[0], k[1] - 8, -42, AMBER_GOLD, 0.0, 1.2])

        # --- boost crystals (Cyan: Surge Tri-Shot charges & Dash recharge)
        for bs in self.boosts_left[:]:
            if math.hypot(bs[0] - self.px, bs[1] - self.py) < 18:
                self.boosts_left.remove(bs)
                self.surge_charges += 5
                if self.dash_charges < 3:
                    self.dash_charges += 1
                self.ripples.append([bs[0], bs[1], 0.0])
                self.score += 150
                self._save_best_score()
                self._say("[ CRYSTAL SURGE ] +5 Tri-Shot Spreads & Dash Recharged")
                self.float_texts.append(["[ +5 TRI-SHOTS ]", bs[0], bs[1] - 10, -42, CYAN_BOOST, 0.0, 1.4])

        # --- aegis crystals (Violet: Shield Barrier & Life Restoration)
        for ag in self.aegis_left[:]:
            if math.hypot(ag[0] - self.px, ag[1] - self.py) < 18:
                self.aegis_left.remove(ag)
                if self.shield_charges < 2:
                    self.shield_charges += 1
                self.shield_active = True
                if self.lives < 3:
                    self.lives += 1
                self.ripples.append([ag[0], ag[1], 0.0])
                self.score += 150
                self._save_best_score()
                self._say("[ AEGIS CRYSTAL ] Energy Shield Engaged & Life Restored")
                self.float_texts.append(["[ SHIELD ENGAGED ]", ag[0], ag[1] - 10, -42, VIOLET_ACCENT, 0.0, 1.4])

        # --- exit
        if math.hypot(L.exit[0] - self.px, L.exit[1] - self.py) < 20:
            if self.keys_left:
                self._say("Vault portal sealed - collect all keys!")
            else:
                # Action-based completion and flawless bonuses (zero time penalty!)
                bonus = 500
                if self.lives == self.level_start_lives:
                    bonus += 300
                    self.badges.add("UNTOUCHED")
                self.score += bonus
                self._save_best_score()
                self.level_no += 1
                if self.level_no >= len(LEVEL_SETTINGS):
                    self.badges.add("CHAMPION")
                    self.state = "win"
                else:
                    self.state = "levelclear"

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

    # ------------------------------------------------------------ Combat & Feedback
    def dash(self, vx=0.0, vy=0.0):
        """Short directional dash: checks wall collisions step-by-step; leaves motion trails."""
        if self.state != "play" or self.show_help:
            return
        if self.dash_charges <= 0:
            self._say("Dash depleted! Walk or collect crystals to recharge.")
            return

        self.dash_charges -= 1
        self.level_dashes_used += 1
        if self.level_dashes_used >= 3:
            self.badges.add("PHANTOM")

        if vx == 0.0 and vy == 0.0:
            dx = math.cos(self.angle)
            dy = math.sin(self.angle)
        else:
            mag = math.hypot(vx, vy)
            dx, dy = vx / mag, vy / mag

        # Dash distance 44px evaluated in 4 small steps with collision checking
        dash_dist = 44.0
        steps = 4
        step_len = dash_dist / steps

        self.afterimages.append([self.px, self.py, self.angle, 0.0, 0.35])

        for s in range(steps):
            self.px += dx * step_len
            self._collide()
            self.py += dy * step_len
            self._collide()
            if s % 2 == 0:
                self.afterimages.append([self.px, self.py, self.angle, 0.0, 0.28 - s * 0.05])
                self._spawn_sparks(self.px, self.py)

        self.ripples.append([self.px, self.py, 0.0])
        self.float_texts.append(["[ DASH! ]", self.px, self.py - 10, -45, CYAN_ELECTRIC, 0.0, 0.9])

    def toggle_shield(self):
        """Activates the Energy Shield barrier if charges are ready."""
        if self.state != "play" or self.show_help:
            return
        if self.shield_active:
            self._say("Energy Shield is already active!")
            return
        if self.shield_charges <= 0:
            self._say("Shield energy depleted! Collect Aegis crystals or keys to recharge.")
            return
        self.shield_charges -= 1
        self.shield_active = True
        self.ripples.append([self.px, self.py, 0.0])
        self.float_texts.append(["[ SHIELD ACTIVE ]", self.px, self.py - 12, -45, VIOLET_ACCENT, 0.0, 1.3])
        self._say("[ ENERGY SHIELD ENGAGED - Absorbs damage ]")

    def shoot(self):
        """Fire an arrow in the direction the player is facing (Tri-Shot if Surge charges available)."""
        if self.state != "play" or self.shoot_cd > 0:
            return
        self.shoot_cd = SHOOT_COOLDOWN

        if self.surge_charges > 0:
            self.surge_charges -= 1
            # 3-way spread using 2D rotation matrices
            angles = [self.angle - 0.26, self.angle, self.angle + 0.26]
            for ang in angles:
                x = self.px + math.cos(ang) * 12
                y = self.py + math.sin(ang) * 12
                self.arrows.append([x, y, ang, 0.0])
            self.float_texts.append([f"TRI-SHOT ({self.surge_charges} left)", self.px, self.py - 12, -35, CYAN_BOOST, 0.0, 0.8])
        else:
            x = self.px + math.cos(self.angle) * 12
            y = self.py + math.sin(self.angle) * 12
            self.arrows.append([x, y, self.angle, 0.0])

    def _kill_bat(self, b):
        b.alive = False
        b.respawn = BAT_RESPAWN
        self.blasts.append([b.x, b.y, 0.0])
        for i in range(9):                               # shards fly out in purple & neon green
            ang = i * 2 * math.pi / 9 + random.uniform(-0.3, 0.3)
            sp = random.uniform(70, 150)
            col = NEON_GREEN if i % 2 == 0 else PURPLE_VOID
            self.debris.append([b.x, b.y, math.cos(ang) * sp, math.sin(ang) * sp,
                                random.uniform(0, 6.28), random.uniform(-14, 14),
                                0.0, random.uniform(0.45, 0.8), col])
        self.score += 150
        self.level_bats_killed += 1
        if self.level_bats_killed >= 3:
            self.badges.add("PURGER")
        if self.level_bats_killed % 2 == 0 and self.shield_charges < 2:
            self.shield_charges += 1
            self.float_texts.append(["SHIELD RECHARGED +1", b.x, b.y - 22, -35, CYAN_ACCENT, 0.0, 1.2])
        self._save_best_score()
        self._say("Shadow Wraith Purged! +150")
        self.float_texts.append(["+150 PURGED", b.x, b.y - 8, -40, NEON_GREEN, 0.0, 1.0])

    def _spawn_sparks(self, x, y):
        for i in range(5):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(30, 90)
            col = CYAN_ELECTRIC if i % 2 == 0 else VIOLET_ACCENT
            self.debris.append([x, y, math.cos(ang) * sp, math.sin(ang) * sp,
                                random.uniform(0, 6.28), random.uniform(-10, 10),
                                0.0, random.uniform(0.2, 0.4), col])

    def _say(self, text):
        self.msg, self.msg_t = text, 1.6

    def _hit(self):
        if self.shield_active:
            # Shield absorbs the impact completely!
            self.shield_active = False
            self.invuln = 1.0
            self.dmg_flash = 0.2
            self.ripples.append([self.px, self.py, 0.0])
            self._spawn_sparks(self.px, self.py)
            self._say("[ SHIELD BROKE! Impact Absorbed ]")
            self.float_texts.append(["SHIELD ABSORBED!", self.px, self.py - 14, -45, CYAN_ELECTRIC, 0.0, 1.4])
            return

        self.lives -= 1
        self.dmg_flash = 0.4
        self.ripples.append([self.px, self.py, 0.0])
        self.float_texts.append(["-1 LIFE!", self.px, self.py - 12, -45, CORAL_RED, 0.0, 1.2])
        if self.lives <= 0:
            self._save_best_score()
            self.state = "gameover"
            return
        self.px, self.py = self.level.start
        self.invuln = 2.0
        self._say("Hit by shadow wraith! Retreat to cover.")

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

    # ------------------------------------------------------------ Rendering
    def _glow(self, R):
        """Cool electric cyan/blue torch glow with radiant luminous falloff (no brown/yellow)."""
        if R not in self.glow_cache:
            s = pygame.Surface((2 * R + 1, 2 * R + 1), pygame.SRCALPHA)
            for r in range(R, 0, -1):
                p = 1 - r / R
                a = int(140 * (p ** 2))
                # Gradient: Radiant cyan in center (10, 225, 255) to deep electric blue (0, 55, 175)
                red = int(10 * p)
                green = int(225 * p + 50 * (1 - p))
                blue = int(255 * p + 175 * (1 - p))
                for y, xl, xr in gfx.circle_spans(R, R, r):
                    s.fill((red, green, blue, a), (xl, y, xr - xl + 1, 1))
            self.glow_cache[R] = s
        return self.glow_cache[R]

    def draw(self):
        if self.state == "title":
            return self.draw_title()
        if self.state == "cglab":
            return self.cg_lab.draw()

        L, r, surf = self.level, self.r, self.screen
        surf.fill(BG)

        # Torch flickers -> window size changes subtly every frame (+ Surge bonus)
        extra = 25.0 if self.surge_charges > 0 else 0.0
        half = L.torch + extra + 4 * math.sin(self.t * 7) + 2.5 * math.sin(self.t * 13.1)
        r.set_window(int(self.px), int(self.py), int(half))
        xmin, ymin, xmax, ymax = r.win
        win_rect = pygame.Rect(xmin, ymin, xmax - xmin, ymax - ymin)

        self._draw_cells(win_rect)

        # Optional CG Cartesian coordinate grid
        if self.show_grid:
            self._draw_coordinate_grid(win_rect)

        # Cool cyan/blue torch glow clipped to viewing frustum
        R = int((L.torch + extra) * 1.3)
        surf.set_clip(win_rect)
        surf.blit(self._glow(R), (int(self.px) - R, int(self.py) - R))
        surf.set_clip(None)

        # Wall faces: line segments clipped against the torch window (electric cyan)
        for p0, p1 in L.segments:
            r.line(p0, p1, WALL_EDGE, thick=2)

        self._draw_start_shrine()
        self._draw_exit()
        for k in self.keys_left:
            self._draw_key(k)
        for bs in self.boosts_left:
            self._draw_boost(bs)
        for ag in self.aegis_left:
            self._draw_aegis(ag)
        for b in L.bats:
            self._draw_bat(b)
        self._draw_arrows()
        self._draw_player()
        self._draw_blasts()
        self._draw_effects()
        self._draw_window_frame(xmin, ymin, xmax, ymax)
        self._draw_minimap()
        self._draw_hud()

        if self.state == "pause":
            self._draw_pause_overlay()
        elif self.state in ("levelclear", "gameover", "win"):
            self._draw_overlay()

        if self.show_help:
            self._draw_help_overlay()

    # Floor + rock cells: Cool Dark Navy, Black, and Cyan palette with Dynamic Fog of War
    def _draw_cells(self, win_rect):
        L, r = self.level, self.r
        xmin, ymin, xmax, ymax = r.win
        c0 = max(0, int((xmin - OFF_X) // CELL))
        c1 = min(COLS - 1, int((xmax - OFF_X) // CELL))
        r0 = max(0, int(ymin // CELL))
        r1 = min(ROWS - 1, int(ymax // CELL))
        for row in range(r0, r1 + 1):
            for col in range(c0, c1 + 1):
                self.discovered[row][col] = True

        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(OFF_X + col * CELL, row * CELL, CELL, CELL)
                is_in_torch = rect.colliderect(win_rect)
                was_discovered = self.discovered[row][col]

                if not is_in_torch and not was_discovered:
                    continue  # Unexplored and outside torch -> pitch dark

                if is_in_torch:
                    vis = rect.clip(win_rect)
                    if vis.w <= 0 or vis.h <= 0:
                        continue
                    f = r.fade(*rect.center)
                else:
                    # Explored fog-of-war ghosting (soft dim navy)
                    vis = rect
                    f = 0.20

                if L.grid[row][col] == 1:
                    v = ((row * 7 + col * 13) % 4) * 3
                    base = (WALL_DARK[0] + v, WALL_DARK[1] + v, WALL_DARK[2] + v)
                    self.screen.fill((int(base[0] * f), int(base[1] * f), int(base[2] * f)), vis)
                    if is_in_torch and vis.w == CELL and vis.h == CELL:
                        top_col = (int(WALL_BEVEL[0] * f), int(WALL_BEVEL[1] * f), int(WALL_BEVEL[2] * f))
                        pygame.draw.line(self.screen, top_col, (rect.x, rect.y), (rect.x + CELL, rect.y), 1)
                        pygame.draw.line(self.screen, top_col, (rect.x, rect.y), (rect.x, rect.y + CELL), 1)
                else:
                    v = ((row * 5 + col * 11) % 3) * 3
                    base = (FLOOR_BASE[0] + v, FLOOR_BASE[1] + v, FLOOR_BASE[2] + v)
                    self.screen.fill((int(base[0] * f), int(base[1] * f), int(base[2] * f)), vis)
                    if vis.w == CELL and vis.h == CELL:
                        p_col = (int(18 * f), int(28 * f), int(44 * f))
                        pygame.draw.rect(self.screen, p_col, rect, 1)
                    if is_in_torch:
                        for i in range(2):
                            px = rect.x + (row * 17 + col * 29 + i * 13) % (CELL - 4) + 2
                            py = rect.y + (row * 31 + col * 7 + i * 19) % (CELL - 4) + 2
                            if r.in_window(px, py):
                                c_blue = int(PEBBLE_COLOR[2] * f)
                                c_green = int(PEBBLE_COLOR[1] * f)
                                self.screen.fill((int(20 * f), c_green, c_blue), (px, py, 2, 2))

    def _draw_coordinate_grid(self, win_rect):
        """Draw CG coordinate grid lines clipped to viewing window."""
        L, r = self.level, self.r
        xmin, ymin, xmax, ymax = r.win
        c0 = max(0, int((xmin - OFF_X) // CELL))
        c1 = min(COLS - 1, int((xmax - OFF_X) // CELL))
        r0 = max(0, int(ymin // CELL))
        r1 = min(ROWS - 1, int(ymax // CELL))
        for col in range(c0, c1 + 2):
            x = OFF_X + col * CELL
            if xmin <= x <= xmax:
                p0 = (x, max(ymin, 0))
                p1 = (x, min(ymax, ROWS * CELL))
                r.line(p0, p1, (0, 110, 150), 1, use_fade=True)
        for row in range(r0, r1 + 2):
            y = row * CELL
            if ymin <= y <= ymax:
                p0 = (max(xmin, OFF_X), y)
                p1 = (min(xmax, OFF_X + COLS * CELL), y)
                r.line(p0, p1, (0, 110, 150), 1, use_fade=True)

    def _draw_start_shrine(self):
        """Draw starting chamber rune platform at level.start in luminous cyan."""
        r, L = self.r, self.level
        sx, sy = L.start
        if r.in_window(sx, sy):
            pulse = 1 + 0.08 * math.sin(self.t * 4)
            # Outer cyan runic circle platform
            r.circle(sx, sy, int(15 * pulse), (0, 180, 220), 1)
            # Rotating inner celestial glyph
            m = compose(translate(sx, sy), rotate(self.t * 0.8), scale(pulse, pulse))
            cross = [(-8, -1), (8, -1), (8, 1), (-8, 1)]
            cross2 = [(-1, -8), (1, -8), (1, 8), (-1, 8)]
            r.fill_polygon(apply(m, cross), (0, 140, 185))
            r.fill_polygon(apply(m, cross2), (0, 140, 185))

    def _draw_player(self):
        r = self.r
        blink = self.invuln > 0 and int(self.t * 14) % 2 == 0
        # Body: radiant cyan core with white specular star
        body_col = (CYAN_BOOST if self.surge_charges > 0 else CYAN_ELECTRIC) if not blink else (255, 255, 255)
        r.disc(self.px, self.py, PLAYER_R, body_col, use_fade=False)
        r.disc(self.px - 2, self.py - 2, 2, (255, 255, 255), use_fade=False)
        # Direction arrow -> ROTATION + TRANSLATION
        arrow = [(11, 0), (-5, -6), (-2, 0), (-5, 6)]
        pts = apply(compose(translate(self.px, self.py), rotate(self.angle)), arrow)
        r.fill_polygon(pts, (245, 252, 255))
        # Crystal Scepter (titanium silver) + Arcane Plasma flame (electric cyan + white)
        fx, fy = self._flame_world()
        r.line((self.px, self.py), (fx, fy + 1), (150, 185, 215), thick=2, use_fade=False)
        flicker = 0.85 + 0.25 * math.sin(self.t * 21)
        wob = 0.35 * math.sin(self.t * 13)
        flame = [(0, -11), (4, -4), (3, 2), (0, 4), (-3, 2), (-4, -4)]
        m = compose(translate(fx, fy), shear(wob, 0), scale(flicker, flicker + 0.1))
        r.fill_polygon(apply(m, flame), CYAN_ELECTRIC)
        m2 = compose(translate(fx, fy), shear(wob, 0), scale(0.55 * flicker, 0.6 * flicker))
        r.fill_polygon(apply(m2, flame), (210, 250, 255))

        # Energy Shield Barrier: Rotating Hexagonal Shield & Orbiting Runes (if shield_active)
        if self.shield_active:
            shield_pulse = 1.0 + 0.08 * math.sin(self.t * 6)
            hex_pts = []
            for i in range(6):
                ang = i * math.pi / 3
                hex_pts.append((17 * shield_pulse * math.cos(ang), 17 * shield_pulse * math.sin(ang)))
            m_shield = compose(translate(self.px, self.py), rotate(self.t * 1.5))
            r.polyline(apply(m_shield, hex_pts + [hex_pts[0]]), CYAN_ELECTRIC, thick=2, use_fade=False)
            m_shield2 = compose(translate(self.px, self.py), rotate(-self.t * 2.0))
            r.polyline(apply(m_shield2, hex_pts + [hex_pts[0]]), VIOLET_ACCENT, thick=1, use_fade=False)
            for i in range(3):
                o_ang = self.t * 3.0 + i * (2 * math.pi / 3)
                ox = self.px + math.cos(o_ang) * 19
                oy = self.py + math.sin(o_ang) * 19
                r.disc(ox, oy, 3, CYAN_ELECTRIC, use_fade=False)

    def _draw_key(self, k):
        r = self.r
        bob = 3 * math.sin(self.t * 3 + k[0])
        spin = math.cos(self.t * 3.5)                    # x-scale -> spinning gem
        pulse = 1 + 0.12 * math.sin(self.t * 6)
        gem = [(0, -11), (8, 0), (0, 11), (-8, 0)]
        m = compose(translate(k[0], k[1] + bob), scale(spin * pulse, pulse))
        r.fill_polygon(apply(m, gem), AMBER_GOLD)
        r.polyline(apply(m, gem), GOLD_BRIGHT, 1, use_fade=False)
        r.circle(k[0], k[1] + bob, int(15 + 3 * math.sin(self.t * 5)), (215, 165, 40), 1)

    def _draw_boost(self, bs):
        r = self.r
        bob = 3 * math.sin(self.t * 4 + bs[0])
        spin = math.sin(self.t * 3.0)
        pulse = 1 + 0.15 * math.sin(self.t * 7)
        shard = [(0, -12), (6, -3), (3, 10), (-3, 10), (-6, -3)]
        m = compose(translate(bs[0], bs[1] + bob), scale(spin * pulse, pulse))
        r.fill_polygon(apply(m, shard), CYAN_BOOST)
        r.polyline(apply(m, shard), (255, 255, 255), 1, use_fade=False)
        r.circle(bs[0], bs[1] + bob, int(16 + 2 * math.sin(self.t * 6)), (0, 220, 255), 1)

    def _draw_aegis(self, ag):
        r = self.r
        bob = 3 * math.sin(self.t * 3.5 + ag[0])
        spin = math.sin(self.t * 2.8)
        pulse = 1 + 0.12 * math.sin(self.t * 5.5)
        shield_poly = [(0, -13), (9, -4), (6, 9), (0, 14), (-6, 9), (-9, -4)]
        m = compose(translate(ag[0], ag[1] + bob), scale(spin * pulse, pulse))
        r.fill_polygon(apply(m, shield_poly), VIOLET_ACCENT)
        r.polyline(apply(m, shield_poly), (255, 200, 255), 1, use_fade=False)
        r.circle(ag[0], ag[1] + bob, int(16 + 2 * math.sin(self.t * 6)), (180, 80, 240), 1)

    def _draw_bat(self, b):
        """Redesigned pixel-art creature: Deep Purple Carapace with vibrant Neon Green Plasma Wings & Eyes."""
        r = self.r
        if not b.alive:
            return
        # Respawn animation: SCALING from 0 up to full size
        k = min(1.0, b.spawn_age / 0.5)
        grow = 1.0 if k >= 1 else math.sin(k * math.pi / 2) * (1 + 0.25 * math.sin(k * math.pi))
        flap = 0.2 + 0.8 * abs(math.sin(self.t * (15 if b.bat_type == "stalker" else 11) + b.phase))
        sx = 1 if (b.dx + b.dy) >= 0 else -1             # REFLECTION when flying opposite direction

        base = compose(translate(b.x, b.y + 2.5 * math.sin(self.t * 5 + b.phase)), scale(1.3 * sx * grow, 1.3 * grow))

        # --- 1. Neon Green Plasma Wings (segmented scythes) ---
        wing_plasma = [(-2, -3), (-8, -14), (-16, -11), (-14, -2), (-6, -4)]
        wing_core = [(-3, -3), (-8, -11), (-13, -9), (-10, -3)]
        wing_color = NEON_GREEN if b.bat_type == "scout" else (100, 255, 60)
        wing_inner = (160, 255, 120)

        for sy in (1, -1):                               # Upper + mirrored lower wing
            m_wing = compose(base, scale(1, sy * flap))
            r.fill_polygon(apply(m_wing, wing_plasma), wing_color)
            r.fill_polygon(apply(m_wing, wing_core), wing_inner)
            r.polyline(apply(m_wing, wing_plasma), (180, 50, 240), 1, use_fade=False)

        # --- 2. Deep Purple Carapace & Abdomen ---
        carapace = [(7, 0), (3, -6), (-4, -5), (-9, 0), (-4, 5), (3, 6)]
        r.fill_polygon(apply(base, carapace), (85, 20, 135))
        crest = [(3, 0), (-1, -3), (-5, -2), (-6, 0), (-5, 2), (-1, 3)]
        r.fill_polygon(apply(base, crest), (145, 45, 215))

        # --- 3. Neon Green Razor Mandibles ---
        mandibles = [(7, -3), (12, -4), (10, 0), (12, 4), (7, 3)]
        r.fill_polygon(apply(base, mandibles), NEON_GREEN)

        # --- 4. Glowing Neon Green Eyes ---
        r.disc(b.x + 4 * sx, b.y - 2, 2, NEON_GREEN, use_fade=False)
        r.disc(b.x + 5 * sx, b.y - 2, 1, NEON_GREEN_BRIGHT, use_fade=False)

    def _draw_arrows(self):
        """Arrow = polygons moved with M = T(x, y) x R(angle) x S(stretch, 1)."""
        r = self.r
        head = [(10, 0), (3, -4), (3, 4)]
        shaft = [(3, -1), (-14, -1), (-14, 1), (3, 1)]
        fletch1 = [(-9, 0), (-15, -5), (-12, -5), (-6, 0)]
        fletch2 = [(-9, 0), (-15, 5), (-12, 5), (-6, 0)]
        for x, y, ang, age in self.arrows:
            stretch = 1 + 0.6 * max(0.0, 1 - age * 9)     # SCALING: stretched at launch
            m = compose(translate(x, y), rotate(ang), scale(stretch, 1))
            r.fill_polygon(apply(m, shaft), (150, 175, 200))
            r.fill_polygon(apply(m, fletch1), CYAN_ELECTRIC)
            r.fill_polygon(apply(m, fletch2), CYAN_ELECTRIC)
            r.fill_polygon(apply(m, head), (245, 252, 255))

    def _draw_blasts(self):
        """Explosion: star scaled up and rotated in Neon Green & Purple."""
        r = self.r
        star = []
        for i in range(16):
            rad = 10 if i % 2 == 0 else 4.5
            a = i * math.pi / 8
            star.append((rad * math.cos(a), rad * math.sin(a)))
        for x, y, age in self.blasts:
            p = age / BLAST_TIME
            s = 0.3 + 3.4 * math.sin(p * math.pi / 2)
            fade = (1 - p) ** 0.6
            m = compose(translate(x, y), rotate(p * 2.0), scale(s, s))
            r.fill_polygon(apply(m, star), (int(NEON_GREEN[0] * fade), int(NEON_GREEN[1] * fade), int(NEON_GREEN[2] * fade)))
            m2 = compose(translate(x, y), rotate(-p * 2.5), scale(s * 0.55, s * 0.55))
            r.fill_polygon(apply(m2, star), (int(PURPLE_VOID[0] * fade), int(PURPLE_VOID[1] * fade), int(PURPLE_VOID[2] * fade)))
            r.circle(x, y, int(s * 13), (int(CYAN_ELECTRIC[0] * fade), int(CYAN_ELECTRIC[1] * fade), int(CYAN_ELECTRIC[2] * fade)), 2)
        for x, y, vx, vy, rot, vrot, age, life, col in self.debris:
            k = 1 - age / life                            # shard shrinks as it ages
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
        col = CYAN_ELECTRIC if open_ else (160, 30, 60)
        r.fill_polygon(apply(m, star), col)
        ring_col = VIOLET_ACCENT if open_ else (120, 20, 45)
        r.circle(ex, ey, int(19 + 2 * math.sin(self.t * 4)), ring_col, 2)

    def _draw_effects(self):
        r = self.r
        # Dash afterimages: fading motion ghost trails
        for img in self.afterimages:
            ix, iy, iang, iage, ilife = img
            alpha = max(0.0, 1.0 - iage / ilife)
            ghost_col = (int(CYAN_ELECTRIC[0] * alpha), int(CYAN_ELECTRIC[1] * alpha), int(CYAN_ELECTRIC[2] * alpha))
            r.circle(ix, iy, PLAYER_R, ghost_col, 1)

        # Ethereal cyan embers rising from the torch
        for e in self.embers:
            if r.in_window(e[0], e[1]):
                a = max(0.0, e[4] / 0.9)
                self.screen.fill((int(0 * a), int(225 * a), int(255 * a)), (int(e[0]), int(e[1]), 2, 2))
        for x, y, age in self.ripples:
            a = 1 - age / 0.7
            r.circle(x, y, int(age * 110) + 2, (int(0 * a), int(210 * a), int(245 * a)), 2)

        # Floating score/feedback texts
        for ft in self.float_texts:
            text, fx, fy, vy, col, age, dur = ft
            alpha = max(0.0, 1.0 - age / dur)
            scaled_col = (int(col[0] * alpha), int(col[1] * alpha), int(col[2] * alpha))
            self._text(text, self.font_sm, scaled_col, (int(fx), int(fy)), center=True)

        # Damage vignette flash
        if self.dmg_flash > 0:
            df = min(1.0, self.dmg_flash / 0.4)
            flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (CORAL_RED[0], CORAL_RED[1], CORAL_RED[2], int(105 * df)), (0, 0, W, H), 8)
            self.screen.blit(flash_surf, (0, 0))

    def _draw_window_frame(self, xmin, ymin, xmax, ymax):
        c = (0, 225, 245)  # Electric cyan corner brackets (no yellow)
        n = 18
        for (x, y, sx, sy) in ((xmin, ymin, 1, 1), (xmax, ymin, -1, 1),
                               (xmin, ymax, 1, -1), (xmax, ymax, -1, -1)):
            self.r.line((x, y), (x + sx * n, y), c, 3, use_fade=False)
            self.r.line((x, y), (x, y + sy * n), c, 3, use_fade=False)

    # ------------------------------------------------------------ Mini-map with Dynamic Fog of War
    def _draw_minimap(self):
        x0, y0 = W - 114, 50
        w_map, h_map = COLS * 5, ROWS * 5
        # Frame panel
        panel = pygame.Surface((w_map + 10, h_map + 22), pygame.SRCALPHA)
        panel.fill((10, 16, 26, 220))
        self.screen.blit(panel, (x0 - 5, y0 - 16))
        pygame.draw.rect(self.screen, HUD_BORDER, (x0 - 5, y0 - 16, w_map + 10, h_map + 22), 1)
        self._text("VAULT RADAR", self.font_sm, TEXT_MUTED, (x0 + 1, y0 - 15))

        # Dynamic Fog of War Radar: undiscovered cells are shadowed
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                cx_p = x0 + c_idx * 5
                cy_p = y0 + r_idx * 5
                if not self.discovered[r_idx][c_idx]:
                    self.screen.fill((8, 12, 18), (cx_p, cy_p, 5, 5))
                elif self.level.grid[r_idx][c_idx] == 1:
                    self.screen.fill((22, 34, 52), (cx_p, cy_p, 5, 5))
                else:
                    self.screen.fill((14, 28, 44), (cx_p, cy_p, 5, 5))

        # Start shrine marker
        sx = x0 + int((self.level.start[0] - OFF_X) / CELL * 5)
        sy = y0 + int(self.level.start[1] / CELL * 5)
        pygame.draw.rect(self.screen, (0, 160, 200), (sx - 1, sy - 1, 3, 3))

        # Exit / Portal marker
        L = self.level
        ex = x0 + int((L.exit[0] - OFF_X) / CELL * 5)
        ey = y0 + int(L.exit[1] / CELL * 5)
        ecol = CYAN_ELECTRIC if not self.keys_left else VIOLET_ACCENT
        pygame.draw.circle(self.screen, ecol, (ex, ey), 3)

        # Boost crystals markers (only if discovered)
        for bs in self.boosts_left:
            bc_r, bc_c = int(bs[1] // CELL), int((bs[0] - OFF_X) // CELL)
            if self.discovered[bc_r][bc_c]:
                bx = x0 + int((bs[0] - OFF_X) / CELL * 5)
                by = y0 + int(bs[1] / CELL * 5)
                pygame.draw.circle(self.screen, CYAN_BOOST, (bx, by), 2)

        # Aegis crystals markers (only if discovered)
        for ag in self.aegis_left:
            ac_r, ac_c = int(ag[1] // CELL), int((ag[0] - OFF_X) // CELL)
            if self.discovered[ac_r][ac_c]:
                ax = x0 + int((ag[0] - OFF_X) / CELL * 5)
                ay = y0 + int(ag[1] / CELL * 5)
                pygame.draw.circle(self.screen, VIOLET_ACCENT, (ax, ay), 2)

        # Uncollected keys markers (only if discovered)
        for k in self.keys_left:
            kc_r, kc_c = int(k[1] // CELL), int((k[0] - OFF_X) // CELL)
            if self.discovered[kc_r][kc_c]:
                kx = x0 + int((k[0] - OFF_X) / CELL * 5)
                ky = y0 + int(k[1] / CELL * 5)
                pygame.draw.rect(self.screen, AMBER_GOLD, (kx - 1, ky - 1, 3, 3))

        # Player marker with subtle pulse
        px = x0 + int((self.px - OFF_X) / CELL * 5)
        py = y0 + int(self.py / CELL * 5)
        p_pulse = int(self.t * 8) % 2 == 0
        pygame.draw.circle(self.screen, (255, 255, 255) if p_pulse else CYAN_ELECTRIC, (px, py), 2)

    # ------------------------------------------------------------ HUD & Screens
    def _text(self, txt, font, color, pos, center=False):
        img = font.render(txt, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, rect)

    def _draw_hud(self):
        # Top HUD bar
        self.screen.fill(HUD_BG, (0, 0, W, 32))
        pygame.draw.line(self.screen, HUD_BORDER, (0, 32), (W, 32), 1)
        self._text(f"Lvl {self.level_no + 1}: {self.level.name}", self.font_body, TEXT_WHITE, (10, 7))
        self._text(f"Keys: {self.keys_total - len(self.keys_left)}/{self.keys_total}", self.font_body, AMBER_GOLD, (215, 7))
        self._text(f"Score: {self.score}", self.font_body, CYAN_ELECTRIC, (310, 7))

        # Shield status (Action charges, zero timer)
        shield_txt = "SHIELD: [ACTIVE]" if self.shield_active else f"SHIELD: [{self.shield_charges}]"
        shield_col = CYAN_ELECTRIC if self.shield_active else (VIOLET_ACCENT if self.shield_charges > 0 else TEXT_MUTED)
        self._text(shield_txt, self.font_sm, shield_col, (405, 9))

        # Dash status (Action charges, zero timer)
        dash_pips = "*" * self.dash_charges + "-" * (3 - self.dash_charges)
        self._text(f"DASH: [{dash_pips}]", self.font_sm, CYAN_ACCENT, (515, 9))

        # Lives drawn with midpoint circles
        for i in range(self.lives):
            self.r.set_window(0, 0, 10000, 10000)
            self.r.disc(605 + i * 18, 16, 6, CORAL_RED, use_fade=False)
            self.screen.fill((255, 175, 185), (603 + i * 18, 14, 2, 2))

        # Surge tri-shot charges if active
        if self.surge_charges > 0:
            self._text(f"TRI-SHOT: {self.surge_charges}", self.font_sm, CYAN_BOOST, (670, 9))

        # Bottom Bar
        self.screen.fill(HUD_BG, (0, H - 26, W, 26))
        pygame.draw.line(self.screen, HUD_BORDER, (0, H - 26), (W, H - 26), 1)
        grid_status = "ON" if self.show_grid else "OFF"
        self._text(f"[SPACE] Shoot  [LSHIFT/X] Dash  [E] Shield  [L] {self.r.line_algo}  [C] {self.r.clip_algo}  [G] Grid:{grid_status}  [P] Pause  [H] Guide",
                   self.font_sm, TEXT_MUTED, (10, H - 19))

        # Arrow reload bar
        ready = 1 - self.shoot_cd / SHOOT_COOLDOWN
        self.screen.fill((22, 34, 52), (W - 88, H - 18, 78, 10))
        bar_col = CYAN_ELECTRIC if ready >= 1 else (0, 140, 220)
        self.screen.fill(bar_col, (W - 88, H - 18, int(78 * ready), 10))
        pygame.draw.rect(self.screen, HUD_BORDER, (W - 88, H - 18, 78, 10), 1)

        # Message notification banner
        if self.msg_t > 0:
            msg_surf = self.font_body.render(self.msg, True, (240, 250, 255))
            msg_rect = msg_surf.get_rect(center=(W // 2, 58))
            bg_rect = msg_rect.inflate(24, 10)
            panel = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            panel.fill((10, 18, 30, 235))
            self.screen.blit(panel, bg_rect.topleft)
            pygame.draw.rect(self.screen, CYAN_ELECTRIC, bg_rect, 1)
            self.screen.blit(msg_surf, msg_rect)

    def _draw_pause_overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((6, 9, 15, 205))
        self.screen.blit(s, (0, 0))

        card_w, card_h = 460, 290
        cx, cy = W // 2, H // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((12, 18, 28, 245))
        self.screen.blit(card_surf, card_rect.topleft)
        pygame.draw.rect(self.screen, CYAN_ELECTRIC, card_rect, 2)
        pygame.draw.rect(self.screen, HUD_BORDER, card_rect.inflate(6, 6), 1)

        self._text("GAME PAUSED", self.big, CYAN_ELECTRIC, (cx, cy - 95), center=True)
        self._text(f"Current Cave: {self.level.name}", self.font, TEXT_WHITE, (cx, cy - 50), center=True)
        self._text(f"Vault Score: {self.score}   |   Best Score: {self.best_score}", self.font, AMBER_GOLD, (cx, cy - 24), center=True)

        # Unlocked achievements badges
        if self.badges:
            badge_str = "Badges: " + " ".join(f"[{b}]" for b in sorted(self.badges))
            self._text(badge_str, self.font_sm, (57, 255, 20), (cx, cy), center=True)

        self._text("Press [P] to Resume Game", self.mid, TEXT_WHITE, (cx, cy + 34), center=True)
        self._text("[R] Restart Cave Level       [H] Field Guide", self.font, TEXT_MUTED, (cx, cy + 74), center=True)
        self._text("[ESC] Quit to Desktop", self.font_sm, (215, 80, 90), (cx, cy + 106), center=True)

    def _draw_help_overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((6, 9, 15, 230))
        self.screen.blit(s, (0, 0))

        card_w, card_h = 740, 530
        cx, cy = W // 2, H // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((12, 18, 28, 245))
        self.screen.blit(card_surf, card_rect.topleft)
        pygame.draw.rect(self.screen, VIOLET_ACCENT, card_rect, 2)
        pygame.draw.rect(self.screen, HUD_BORDER, card_rect.inflate(6, 6), 1)

        self._text("EMBERVAULT: FIELD GUIDE & CG ACADEMIC LAB", self.mid, CYAN_ELECTRIC, (cx, cy - 235), center=True)

        guide = [
            ("EXPEDITION OBJECTIVES & CRYSTAL POWERS", (0, 225, 255)),
            ("Explore 5 labyrinthine caves. Your torch acts as an active rectangular clipping window.", TEXT_WHITE),
            ("Collect all amber keys to unseal the portal. Fog of War reveals explored corridors.", TEXT_WHITE),
            ("Cyan Surge Crystals: +5 Tri-Shot spread arrow charges & recharges Dash.", (80, 240, 255)),
            ("Violet Aegis Crystals: Engages Energy Shield (absorbs damage) & restores life.", (180, 110, 255)),
            ("", TEXT_WHITE),
            ("CONTROLS & SHORTCUTS", (0, 225, 255)),
            ("Move: [Arrow Keys / WASD]  |  Combat: [SPACE / F] Shoot (Tri-Shot with Surge)", TEXT_WHITE),
            ("Dash Ability: [LSHIFT / X]  |  Energy Shield: [E] Activate Barrier", TEXT_WHITE),
            ("Title Mode: [ENTER] Start Game  |  [L] CG Laboratory Mode  |  [1-5/TAB] Level", TEXT_WHITE),
            ("In-Game Shortcuts: [G] Grid Overlay  |  [P] Pause  |  [R] Restart Level", TEXT_WHITE),
            ("", TEXT_WHITE),
            ("COMPUTER GRAPHICS ALGORITHMS (Interactive Lab & Live Demos)", (0, 225, 255)),
            ("1. Line Drawing: [L] Toggle DDA (differential) <-> Bresenham (integer-only rasterization)", TEXT_WHITE),
            ("2. Line Clipping: [C] Toggle Cohen-Sutherland (outcodes) <-> Liang-Barsky (parametric)", TEXT_WHITE),
            ("3. Midpoint Circle: Player disc, life orbs, teleporter platform, and ripple waves", TEXT_WHITE),
            ("4. Scan-line Polygon Fill: Arrow head/fletching, wraith wings, scepter flame & portal stars", TEXT_WHITE),
            ("5. 2D 3x3 Homogeneous Matrices: Translation, Rotation, Scaling & Shear compositions", TEXT_WHITE),
        ]

        start_y = cy - 200
        for text, col in guide:
            if not text:
                start_y += 6
                continue
            is_hdr = col in ((0, 225, 255), (57, 255, 20))
            fnt = self.font if is_hdr else self.font_sm
            self._text(text, fnt, col, (cx, start_y), center=True)
            start_y += 21 if is_hdr else 17

        self._text("Press [H] or [ENTER] to return", self.mid, AMBER_GOLD, (cx, cy + 235), center=True)

    def _draw_overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((6, 9, 15, 215))
        self.screen.blit(s, (0, 0))

        card_w, card_h = 520, 310
        cx, cy = W // 2, H // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((12, 18, 28, 245))
        self.screen.blit(card_surf, card_rect.topleft)

        if self.state == "levelclear":
            pygame.draw.rect(self.screen, CYAN_ELECTRIC, card_rect, 2)
            pygame.draw.rect(self.screen, VIOLET_ACCENT, card_rect.inflate(6, 6), 1)
            self._text("CAVE LEVEL COMPLETE!", self.big, CYAN_ELECTRIC, (cx, cy - 100), True)
            self._text(f"Cave {self.level_no} Cleared: {self.level.name}", self.font, VIOLET_ACCENT, (cx, cy - 50), True)
            self._text(f"Current Vault Score: {self.score}", self.mid, TEXT_WHITE, (cx, cy - 10), True)
            if self.badges:
                b_str = "Badges: " + " ".join(f"[{b}]" for b in sorted(self.badges))
                self._text(b_str, self.font_sm, (57, 255, 20), (cx, cy + 20), True)
            else:
                self._text(f"All-Time Best: {self.best_score}", self.font, AMBER_GOLD, (cx, cy + 20), True)
            self._text("Press ENTER for the next cave", self.mid, (0, 235, 255), (cx, cy + 85), True)
        elif self.state == "gameover":
            pygame.draw.rect(self.screen, CORAL_RED, card_rect, 2)
            pygame.draw.rect(self.screen, HUD_BORDER, card_rect.inflate(6, 6), 1)
            self._text("LOST IN THE SHADOWS", self.big, CORAL_RED, (cx, cy - 100), True)
            self._text("Your crystal torch has burned out.", self.font, TEXT_MUTED, (cx, cy - 50), True)
            self._text(f"Final Score: {self.score}", self.mid, TEXT_WHITE, (cx, cy - 10), True)
            self._text(f"All-Time Best: {self.best_score}", self.font, AMBER_GOLD, (cx, cy + 25), True)
            self._text("Press ENTER to rekindle the torch", self.mid, (0, 235, 255), (cx, cy + 85), True)
        elif self.state == "win":
            pygame.draw.rect(self.screen, GOLD_BRIGHT, card_rect, 2)
            pygame.draw.rect(self.screen, CYAN_ELECTRIC, card_rect.inflate(6, 6), 1)
            self._text("EMBERVAULT CONQUERED!", self.big, GOLD_BRIGHT, (cx, cy - 100), True)
            self._text("You have conquered all 5 Caverns of the Crystal Sanctum!", self.font, CYAN_ELECTRIC, (cx, cy - 50), True)
            self._text(f"Grand Vault Score: {self.score}", self.mid, TEXT_WHITE, (cx, cy - 10), True)
            if self.badges:
                b_str = "Badges: " + " ".join(f"[{b}]" for b in sorted(self.badges))
                self._text(b_str, self.font_sm, (57, 255, 20), (cx, cy + 20), True)
            else:
                self._text(f"All-Time Best: {self.best_score}", self.font, AMBER_GOLD, (cx, cy + 20), True)
            self._text("Press ENTER to play again", self.mid, (0, 235, 255), (cx, cy + 85), True)

    def draw_title(self):
        """Clean, modern, professionally aligned main menu with dual game & CG Lab modes."""
        r, surf = self.r, self.screen
        surf.fill(BG)

        # 1. Background: Gentle drifting crystal stardust in cyan/azure
        for st in self.title_stars:
            a = max(0.1, min(1.0, st[3]))
            c = int(110 * a)
            surf.fill((int(10 * a), c, int(180 * a)), (int(st[0]), int(st[1]), 2, 2))

        # 2. Header Section: Title & Subtitle (centered, high-contrast)
        self._text("COMPUTER GRAPHICS LAB", self.font_sm, (0, 210, 240), (W // 2, 26), center=True)
        self._text("EMBERVAULT", self.font_title, GOLD_BRIGHT, (W // 2, 58), center=True)
        self._text("THE CRYSTAL MAZE", self.font_subtitle, CYAN_ELECTRIC, (W // 2, 90), center=True)

        # 3. Crystal Showcase (centered at (400, 185))
        cx, cy = W // 2, 182
        r.set_window(cx, cy, 10000, fade_radius=10000)

        # Subtle outer midpoint circles
        r.circle(cx, cy, 54, (0, 70, 100), 1)
        r.circle(cx, cy, 40, (0, 120, 160), 1)

        # Concentric rotating wireframe diamonds in electric cyan
        for i in range(4):
            s = 18 + i * 12
            a = self.t * 0.4 * (1 if i % 2 else -1) + i * 0.4
            sq = [(-s / 2, -s / 2), (s / 2, -s / 2), (s / 2, s / 2), (-s / 2, s / 2)]
            m = compose(translate(cx, cy), rotate(a))
            col = (0, int(90 + 35 * i), int(140 + 30 * i))
            r.polyline(apply(m, sq), col, 1, use_fade=False)

        # Multifaceted glowing amber crystal gem in the center
        gem_spin = math.sin(self.t * 2.5)
        gem = [(0, -11), (8, 0), (0, 11), (-8, 0)]
        m_gem = compose(translate(cx, cy), scale(gem_spin, 1.0))
        r.fill_polygon(apply(m_gem, gem), AMBER_GOLD)
        r.polyline(apply(m_gem, gem), GOLD_BRIGHT, 1, use_fade=False)

        # All-time record pill badge below crystal
        rec_rect = pygame.Rect(W // 2 - 130, 252, 260, 24)
        rec_surf = pygame.Surface(rec_rect.size, pygame.SRCALPHA)
        rec_surf.fill((12, 18, 28, 215))
        surf.blit(rec_surf, rec_rect.topleft)
        pygame.draw.rect(surf, (30, 65, 95), rec_rect, 1)
        self._text(f"BEST RECORD: {self.best_score} PTS", self.font_sm, (255, 215, 80), (W // 2, 263), center=True)

        # 4. Level Details Card (Neat section at y = 286..356)
        lvl_data = LEVEL_SETTINGS[self.selected_level]
        card_rect = pygame.Rect(140, 286, 520, 70)
        card_surf = pygame.Surface(card_rect.size, pygame.SRCALPHA)
        card_surf.fill((12, 18, 28, 230))
        surf.blit(card_surf, card_rect.topleft)
        pygame.draw.rect(surf, HUD_BORDER, card_rect, 1)

        # Level header line
        self._text(f"< LEVEL {self.selected_level + 1} OF {len(LEVEL_SETTINGS)}: {lvl_data[0].upper()} >",
                   self.font, TEXT_WHITE, (W // 2, 304), center=True)
        # Level details line
        self._text(f"Chamber: {lvl_data[8]}   |   Keys: {lvl_data[4]}   |   Wraiths: {lvl_data[5]}   |   Torch: {lvl_data[3]}px",
                   self.font_sm, TEXT_MUTED, (W // 2, 332), center=True)

        # 5. Dual Action Buttons: [ENTER] PLAY GAME  and  [L] CG LABORATORY at y = 372..418
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        btn1_col = (int(0 * pulse + 0 * (1 - pulse)), int(225 * pulse + 255 * (1 - pulse)), int(255 * pulse + 235 * (1 - pulse)))
        
        # Primary Game Button
        btn1_rect = pygame.Rect(W // 2 - 250, 372, 235, 46)
        btn1_surf = pygame.Surface(btn1_rect.size, pygame.SRCALPHA)
        btn1_surf.fill((16, 26, 42, 240))
        surf.blit(btn1_surf, btn1_rect.topleft)
        pygame.draw.rect(surf, btn1_col, btn1_rect, 2)
        self._text("[ ENTER ] PLAY GAME", self.font_btn, TEXT_WHITE, (btn1_rect.centerx, btn1_rect.centery), center=True)

        # Secondary CG Lab Button
        btn2_rect = pygame.Rect(W // 2 + 15, 372, 235, 46)
        btn2_surf = pygame.Surface(btn2_rect.size, pygame.SRCALPHA)
        btn2_surf.fill((16, 26, 42, 240))
        surf.blit(btn2_surf, btn2_rect.topleft)
        pygame.draw.rect(surf, VIOLET_ACCENT, btn2_rect, 2)
        self._text("[ L ] CG LABORATORY", self.font_btn, (215, 175, 255), (btn2_rect.centerx, btn2_rect.centery), center=True)

        # 6. Keyboard Controls & Shortcuts (Neatly organized at y = 434..534)
        row1_y = 438
        self._text("[ 1 - 5 / TAB ] Change Level", self.font_body, (220, 240, 255), (130, row1_y))
        self._text("[ G ] Toggle Grid Overlay", self.font_body, (0, 220, 245), (370, row1_y))
        self._text("[ H ] Field Guide & Theory", self.font_body, (255, 215, 80), (570, row1_y))

        row2_y = 472
        self._text("[ WASD / Arrows ] Move", self.font_body, TEXT_MUTED, (130, row2_y))
        self._text("[ SPACE / F ] Shoot", self.font_body, TEXT_MUTED, (370, row2_y))
        self._text("[ LSHIFT / X ] Dash Ability", self.font_body, CYAN_ACCENT, (570, row2_y))

        row3_y = 506
        self._text("[ E ] Energy Shield Barrier", self.font_body, VIOLET_ACCENT, (130, row3_y))
        self._text("[ P ] Pause / Resume", self.font_body, TEXT_MUTED, (370, row3_y))
        self._text("[ ESC ] Quit to Desktop", self.font_body, (215, 90, 100), (570, row3_y))

        # 7. Status Footer at Bottom
        self.screen.fill(HUD_BG, (0, H - 24, W, 24))
        pygame.draw.line(self.screen, HUD_BORDER, (0, H - 24), (W, H - 24), 1)
        self._text("Computer Graphics Mini-Project  |  DDA & Bresenham Line  |  Cohen-Sutherland Clipping  |  Midpoint Circle",
                   self.font_sm, TEXT_MUTED, (W // 2, H - 13), center=True)

        if self.show_help:
            self._draw_help_overlay()
