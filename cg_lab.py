"""
cg_lab.py - Interactive Computer Graphics Laboratory for EmberVault
===================================================================
A self-contained, real-time academic laboratory demonstrating core CG algorithms:
  1. Bresenham's Line Algorithm (Integer-only incremental rasterization)
  2. DDA Line Algorithm (Digital Differential Analyzer)
  3. Midpoint Circle Algorithm (8-way symmetry rasterization)
  4. Cohen-Sutherland Line Clipping (4-bit region outcodes and edge intersections)

All demonstrations compute actual mathematical coordinates and steps in real time.
"""
import math
import pygame
from graphics import (
    bresenham_line, dda_line, _octant, circle_points,
    cohen_sutherland, outcode, INSIDE, LEFT, RIGHT, TOP, BOTTOM
)

# Colors matching the EmberVault cool dark navy, black, and cyan palette
BG = (8, 12, 20)
PANEL_BG = (12, 18, 30)
PANEL_BORDER = (25, 55, 80)
GRID_LINE = (20, 32, 48)
GRID_AXIS = (0, 180, 220)
GRID_HOVER = (15, 45, 68)

CYAN_ELECTRIC = (0, 235, 255)
CYAN_ACCENT = (20, 190, 230)
NEON_GREEN = (57, 255, 20)
PURPLE_VOID = (145, 45, 215)
AMBER_GOLD = (255, 205, 45)
CORAL_RED = (235, 72, 84)
TEXT_WHITE = (244, 248, 252)
TEXT_MUTED = (155, 175, 195)
TEXT_DIM = (95, 115, 135)

# Distinct 8 octant colors for Midpoint Circle symmetry visualization
OCTANT_COLORS = [
    (57, 255, 20),    # Octant 1: Neon Green
    (0, 235, 255),    # Octant 2: Electric Cyan
    (145, 45, 215),   # Octant 3: Purple
    (255, 205, 45),   # Octant 4: Gold
    (235, 72, 84),    # Octant 5: Coral Red
    (80, 240, 255),   # Octant 6: Light Cyan
    (210, 120, 255),  # Octant 7: Lavender
    (120, 255, 160),  # Octant 8: Mint
]


class CGLab:
    def __init__(self, screen):
        self.screen = screen
        self.mode = "bresenham"  # "bresenham", "dda", "circle", "clipping"
        self.modes = ["bresenham", "dda", "circle", "clipping"]
        self.mode_titles = {
            "bresenham": "1. Bresenham's Line Algorithm",
            "dda": "2. DDA Line Algorithm",
            "circle": "3. Midpoint Circle Algorithm",
            "clipping": "4. Cohen-Sutherland Line Clipping"
        }

        # Fonts with robust fallbacks
        self.font_title = pygame.font.SysFont("segoe ui", 22, bold=True) or pygame.font.SysFont(None, 24)
        self.font_subtitle = pygame.font.SysFont("segoe ui", 16, bold=True) or pygame.font.SysFont(None, 18)
        self.font_body = pygame.font.SysFont("segoe ui", 14) or pygame.font.SysFont(None, 16)
        self.font_code = pygame.font.SysFont("consolas", 12) or pygame.font.SysFont(None, 14)
        self.font_sm = pygame.font.SysFont("segoe ui", 12) or pygame.font.SysFont(None, 14)

        # Raster Grid Dimensions: 24 columns x 18 rows
        self.grid_cols = 24
        self.grid_rows = 18
        self.cell_size = 18
        self.grid_ox = 30
        self.grid_oy = 100

        # Interactive Points (in grid cell coordinates)
        # For lines: p0 and p1
        self.p0 = [3, 4]
        self.p1 = [20, 13]
        self.active_point = 1  # 0 for p0, 1 for p1

        # For circle: center and radius point
        self.circle_center = [12, 9]
        self.circle_radius = 6

        # For clipping: window rectangle and line segment
        self.clip_win = (5, 4, 18, 13)  # xmin, ymin, xmax, ymax in grid cells
        self.clip_p0 = [2, 15]
        self.clip_p1 = [21, 2]

        self.hover_cell = None
        self.dragging = False

        # Presets for quick exploration
        self.line_preset_idx = 0
        self.line_presets = [
            ([3, 4], [20, 13], "Gentle positive slope (0 < m < 1)"),
            ([4, 2], [10, 16], "Steep positive slope (m > 1)"),
            ([3, 14], [20, 4], "Gentle negative slope (-1 < m < 0)"),
            ([5, 16], [12, 2], "Steep negative slope (m < -1)"),
            ([3, 9], [21, 9], "Horizontal line (m = 0)"),
            ([12, 2], [12, 16], "Vertical line (m = undefined)"),
        ]

    # ------------------------------------------------------------ Event Handling
    def handle_event(self, e):
        """Processes mouse clicks, drags, and keyboard shortcuts."""
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                self.mode = "bresenham"
            elif e.key == pygame.K_2:
                self.mode = "dda"
            elif e.key == pygame.K_3:
                self.mode = "circle"
            elif e.key == pygame.K_4:
                self.mode = "clipping"
            elif e.key == pygame.K_TAB:
                curr_idx = self.modes.index(self.mode)
                self.mode = self.modes[(curr_idx + 1) % len(self.modes)]
            elif e.key == pygame.K_p:
                self._cycle_preset()
            elif e.key == pygame.K_r:
                self._reset_current_mode()
            elif e.key == pygame.K_SPACE:
                self.active_point = 1 - self.active_point

        elif e.type == pygame.MOUSEMOTION:
            gx, gy = self._screen_to_grid(e.pos)
            if 0 <= gx < self.grid_cols and 0 <= gy < self.grid_rows:
                self.hover_cell = (gx, gy)
                if self.dragging:
                    self._set_active_point(gx, gy)
            else:
                self.hover_cell = None

        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                gx, gy = self._screen_to_grid(e.pos)
                if 0 <= gx < self.grid_cols and 0 <= gy < self.grid_rows:
                    self.dragging = True
                    self._pick_or_set_point(gx, gy)
                else:
                    # Check mode tabs clicks in header
                    self._check_tab_click(e.pos)

        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                self.dragging = False

    def _screen_to_grid(self, pos):
        x, y = pos
        gx = (x - self.grid_ox) // self.cell_size
        gy = (y - self.grid_oy) // self.cell_size
        return int(gx), int(gy)

    def _pick_or_set_point(self, gx, gy):
        if self.mode in ("bresenham", "dda"):
            d0 = (gx - self.p0[0]) ** 2 + (gy - self.p0[1]) ** 2
            d1 = (gx - self.p1[0]) ** 2 + (gy - self.p1[1]) ** 2
            if d0 <= 2:
                self.active_point = 0
            elif d1 <= 2:
                self.active_point = 1
            else:
                if self.active_point == 0:
                    self.p0 = [gx, gy]
                else:
                    self.p1 = [gx, gy]
        elif self.mode == "circle":
            dc = (gx - self.circle_center[0]) ** 2 + (gy - self.circle_center[1]) ** 2
            if dc <= 2:
                self.circle_center = [gx, gy]
            else:
                # Set radius based on distance from center
                r = int(round(math.hypot(gx - self.circle_center[0], gy - self.circle_center[1])))
                self.circle_radius = max(1, min(r, 11))
        elif self.mode == "clipping":
            d0 = (gx - self.clip_p0[0]) ** 2 + (gy - self.clip_p0[1]) ** 2
            d1 = (gx - self.clip_p1[0]) ** 2 + (gy - self.clip_p1[1]) ** 2
            if d0 <= 2:
                self.active_point = 0
            elif d1 <= 2:
                self.active_point = 1
            else:
                if self.active_point == 0:
                    self.clip_p0 = [gx, gy]
                else:
                    self.clip_p1 = [gx, gy]

    def _set_active_point(self, gx, gy):
        if self.mode in ("bresenham", "dda"):
            if self.active_point == 0:
                self.p0 = [gx, gy]
            else:
                self.p1 = [gx, gy]
        elif self.mode == "circle":
            r = int(round(math.hypot(gx - self.circle_center[0], gy - self.circle_center[1])))
            self.circle_radius = max(1, min(r, 11))
        elif self.mode == "clipping":
            if self.active_point == 0:
                self.clip_p0 = [gx, gy]
            else:
                self.clip_p1 = [gx, gy]

    def _check_tab_click(self, pos):
        x, y = pos
        if 48 <= y <= 76:
            tab_w = 175
            for i, m in enumerate(self.modes):
                tx = 30 + i * (tab_w + 10)
                if tx <= x <= tx + tab_w:
                    self.mode = m
                    break

    def _cycle_preset(self):
        if self.mode in ("bresenham", "dda"):
            self.line_preset_idx = (self.line_preset_idx + 1) % len(self.line_presets)
            p0, p1, _ = self.line_presets[self.line_preset_idx]
            self.p0, self.p1 = list(p0), list(p1)
        elif self.mode == "circle":
            radii = [3, 5, 7, 9, 11]
            idx = (radii.index(self.circle_radius) + 1) % len(radii) if self.circle_radius in radii else 0
            self.circle_radius = radii[idx]
        elif self.mode == "clipping":
            presets = [
                ([2, 15], [21, 2]),
                ([8, 6], [15, 11]),     # Fully inside
                ([1, 1], [4, 3]),       # Fully outside left-top
                ([2, 8], [22, 8]),      # Horizontal cut
                ([10, 1], [10, 17]),    # Vertical cut
            ]
            self.line_preset_idx = (self.line_preset_idx + 1) % len(presets)
            p0, p1 = presets[self.line_preset_idx]
            self.clip_p0, self.clip_p1 = list(p0), list(p1)

    def _reset_current_mode(self):
        if self.mode in ("bresenham", "dda"):
            self.p0 = [3, 4]
            self.p1 = [20, 13]
        elif self.mode == "circle":
            self.circle_center = [12, 9]
            self.circle_radius = 6
        elif self.mode == "clipping":
            self.clip_win = (5, 4, 18, 13)
            self.clip_p0 = [2, 15]
            self.clip_p1 = [21, 2]

    # ------------------------------------------------------------ Main Draw
    def draw(self):
        surf = self.screen
        surf.fill(BG)

        # 1. Header & Navigation Tabs
        self._draw_header()

        # 2. Left: Interactive Raster Grid
        self._draw_grid()

        # 3. Algorithm Plotted Pixels & Highlights
        if self.mode == "bresenham":
            self._draw_bresenham()
        elif self.mode == "dda":
            self._draw_dda()
        elif self.mode == "circle":
            self._draw_circle()
        elif self.mode == "clipping":
            self._draw_clipping()

        # 4. Right: Step-by-Step Mathematical Analysis Panel
        self._draw_analysis_panel()

        # 5. Footer: Instructions & Controls
        self._draw_footer()

    # ------------------------------------------------------------ Sub-renderers
    def _draw_header(self):
        surf = self.screen
        # Top banner
        surf.fill(PANEL_BG, (0, 0, 800, 42))
        pygame.draw.line(surf, PANEL_BORDER, (0, 42), (800, 42), 1)

        t_img = self.font_title.render("EMBERVAULT: COMPUTER GRAPHICS LAB", True, CYAN_ELECTRIC)
        surf.blit(t_img, (30, 8))

        esc_img = self.font_body.render("[ESC / M] Return to Main Menu", True, AMBER_GOLD)
        surf.blit(esc_img, (800 - esc_img.get_width() - 30, 12))

        # Mode Selection Tabs
        tab_w = 175
        for i, m in enumerate(self.modes):
            tx = 30 + i * (tab_w + 10)
            ty = 48
            active = (self.mode == m)
            tab_rect = pygame.Rect(tx, ty, tab_w, 28)
            surf.fill((20, 32, 50) if active else (12, 18, 28), tab_rect)
            border_col = CYAN_ELECTRIC if active else PANEL_BORDER
            pygame.draw.rect(surf, border_col, tab_rect, 1)

            lbl = f"[{i+1}] {m.capitalize()}"
            if m == "clipping":
                lbl = "[4] Clipping"
            lbl_img = self.font_subtitle.render(lbl, True, TEXT_WHITE if active else TEXT_MUTED)
            surf.blit(lbl_img, lbl_img.get_rect(center=tab_rect.center))

    def _draw_grid(self):
        surf = self.screen
        grid_w = self.grid_cols * self.cell_size
        grid_h = self.grid_rows * self.cell_size

        # Grid Background
        panel_rect = pygame.Rect(self.grid_ox - 1, self.grid_oy - 1, grid_w + 2, grid_h + 2)
        surf.fill((10, 16, 26), panel_rect)
        pygame.draw.rect(surf, PANEL_BORDER, panel_rect, 1)

        # Hovered Cell Highlight
        if self.hover_cell:
            hx, hy = self.hover_cell
            r = pygame.Rect(self.grid_ox + hx * self.cell_size, self.grid_oy + hy * self.cell_size,
                            self.cell_size, self.cell_size)
            surf.fill(GRID_HOVER, r)

        # Grid Lines
        for c in range(self.grid_cols + 1):
            x = self.grid_ox + c * self.cell_size
            col = GRID_AXIS if c % 5 == 0 else GRID_LINE
            pygame.draw.line(surf, col, (x, self.grid_oy), (x, self.grid_oy + grid_h), 1)
        for r in range(self.grid_rows + 1):
            y = self.grid_oy + r * self.cell_size
            col = GRID_AXIS if r % 5 == 0 else GRID_LINE
            pygame.draw.line(surf, col, (self.grid_ox, y), (self.grid_ox + grid_w, y), 1)

        # Coordinate Labels
        for c in range(0, self.grid_cols, 5):
            x = self.grid_ox + c * self.cell_size + 2
            surf.blit(self.font_sm.render(str(c), True, TEXT_DIM), (x, self.grid_oy + grid_h + 3))
        for r in range(0, self.grid_rows, 5):
            y = self.grid_oy + r * self.cell_size + 2
            surf.blit(self.font_sm.render(str(r), True, TEXT_DIM), (self.grid_ox - 18, y))

    def _draw_pixel(self, gx, gy, col):
        """Draws a highlighted raster pixel in the grid."""
        if 0 <= gx < self.grid_cols and 0 <= gy < self.grid_rows:
            r = pygame.Rect(self.grid_ox + gx * self.cell_size + 1,
                            self.grid_oy + gy * self.cell_size + 1,
                            self.cell_size - 1, self.cell_size - 1)
            self.screen.fill(col, r)

    def _draw_point_marker(self, gx, gy, label, col, is_active):
        px = self.grid_ox + gx * self.cell_size + self.cell_size // 2
        py = self.grid_oy + gy * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, col, (px, py), 6)
        pygame.draw.circle(self.screen, TEXT_WHITE, (px, py), 3)
        if is_active:
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 9, 1)
        txt = self.font_subtitle.render(label, True, col)
        self.screen.blit(txt, (px + 7, py - 14))

    # ------------------------------------------------------------ Demonstrations
    def _draw_bresenham(self):
        # Compute pixels using actual bresenham_line algorithm
        pixels = list(bresenham_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1]))
        for gx, gy in pixels:
            self._draw_pixel(gx, gy, (0, 180, 240))

        # Draw ideal continuous line underneath for comparison
        x0 = self.grid_ox + self.p0[0] * self.cell_size + self.cell_size // 2
        y0 = self.grid_oy + self.p0[1] * self.cell_size + self.cell_size // 2
        x1 = self.grid_ox + self.p1[0] * self.cell_size + self.cell_size // 2
        y1 = self.grid_oy + self.p1[1] * self.cell_size + self.cell_size // 2
        pygame.draw.line(self.screen, (255, 255, 255, 90), (x0, y0), (x1, y1), 1)

        # Endpoint Markers
        self._draw_point_marker(self.p0[0], self.p0[1], "P0", CYAN_ELECTRIC, self.active_point == 0)
        self._draw_point_marker(self.p1[0], self.p1[1], "P1", NEON_GREEN, self.active_point == 1)

    def _draw_dda(self):
        # Compute pixels using actual dda_line algorithm
        pixels = list(dda_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1]))
        for gx, gy in pixels:
            self._draw_pixel(gx, gy, (57, 220, 100))

        # Ideal line
        x0 = self.grid_ox + self.p0[0] * self.cell_size + self.cell_size // 2
        y0 = self.grid_oy + self.p0[1] * self.cell_size + self.cell_size // 2
        x1 = self.grid_ox + self.p1[0] * self.cell_size + self.cell_size // 2
        y1 = self.grid_oy + self.p1[1] * self.cell_size + self.cell_size // 2
        pygame.draw.line(self.screen, (255, 255, 255, 90), (x0, y0), (x1, y1), 1)

        # Endpoint Markers
        self._draw_point_marker(self.p0[0], self.p0[1], "P0", CYAN_ELECTRIC, self.active_point == 0)
        self._draw_point_marker(self.p1[0], self.p1[1], "P1", NEON_GREEN, self.active_point == 1)

    def _draw_circle(self):
        cx, cy = self.circle_center
        r = self.circle_radius

        # Compute octant points using actual _octant algorithm
        octant_pts = list(_octant(r))

        # Symmetries: 8 points per octant calculation, colored by octant to visualize 8-way symmetry
        for x, y in octant_pts:
            pts_with_colors = [
                (cx + x, cy + y, OCTANT_COLORS[0]),
                (cx + y, cy + x, OCTANT_COLORS[1]),
                (cx - y, cy + x, OCTANT_COLORS[2]),
                (cx - x, cy + y, OCTANT_COLORS[3]),
                (cx - x, cy - y, OCTANT_COLORS[4]),
                (cx - y, cy - x, OCTANT_COLORS[5]),
                (cx + y, cy - x, OCTANT_COLORS[6]),
                (cx + x, cy - y, OCTANT_COLORS[7]),
            ]
            for px, py, col in pts_with_colors:
                self._draw_pixel(px, py, col)

        # Center marker
        self._draw_point_marker(cx, cy, "C", AMBER_GOLD, True)

        # Radius handle on circle perimeter
        self._draw_point_marker(cx + r, cy, f"R={r}", CYAN_ELECTRIC, False)

    def _draw_clipping(self):
        xmin, ymin, xmax, ymax = self.clip_win

        # Draw Clipping Window on Grid
        rx = self.grid_ox + xmin * self.cell_size
        ry = self.grid_oy + ymin * self.cell_size
        rw = (xmax - xmin + 1) * self.cell_size
        rh = (ymax - ymin + 1) * self.cell_size
        clip_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
        clip_surf.fill((0, 220, 255, 28))
        self.screen.blit(clip_surf, (rx, ry))
        pygame.draw.rect(self.screen, CYAN_ELECTRIC, (rx, ry, rw, rh), 2)

        # Label Clip Window
        lbl = self.font_sm.render(f"Clip Window [{xmin},{ymin}]-[{xmax},{ymax}]", True, CYAN_ELECTRIC)
        self.screen.blit(lbl, (rx + 4, ry - 14))

        # Original unclipped line (drawn as dim red/grey dashed line)
        x0 = self.grid_ox + self.clip_p0[0] * self.cell_size + self.cell_size // 2
        y0 = self.grid_oy + self.clip_p0[1] * self.cell_size + self.cell_size // 2
        x1 = self.grid_ox + self.clip_p1[0] * self.cell_size + self.cell_size // 2
        y1 = self.grid_oy + self.clip_p1[1] * self.cell_size + self.cell_size // 2
        pygame.draw.line(self.screen, (180, 70, 80), (x0, y0), (x1, y1), 2)

        # Actual Cohen-Sutherland Algorithm execution
        res = cohen_sutherland(self.clip_p0[0], self.clip_p0[1],
                               self.clip_p1[0], self.clip_p1[1],
                               (xmin, ymin, xmax, ymax))

        if res is not None:
            cx0, cy0, cx1, cy1 = res
            # Plot accepted clipped line in bright neon green
            px0 = self.grid_ox + cx0 * self.cell_size + self.cell_size // 2
            py0 = self.grid_oy + cy0 * self.cell_size + self.cell_size // 2
            px1 = self.grid_ox + cx1 * self.cell_size + self.cell_size // 2
            py1 = self.grid_oy + cy1 * self.cell_size + self.cell_size // 2
            pygame.draw.line(self.screen, NEON_GREEN, (px0, py0), (px1, py1), 4)

            # Draw clipped endpoints
            pygame.draw.circle(self.screen, (255, 255, 255), (int(px0), int(py0)), 4)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(px1), int(py1)), 4)

        # Original endpoints
        self._draw_point_marker(self.clip_p0[0], self.clip_p0[1], "P0", CORAL_RED, self.active_point == 0)
        self._draw_point_marker(self.clip_p1[0], self.clip_p1[1], "P1", AMBER_GOLD, self.active_point == 1)

    # ------------------------------------------------------------ Right Analysis Panel
    def _draw_analysis_panel(self):
        surf = self.screen
        ax, ay = 480, 100
        aw, ah = 295, 428

        panel_rect = pygame.Rect(ax, ay, aw, ah)
        surf.fill(PANEL_BG, panel_rect)
        pygame.draw.rect(surf, PANEL_BORDER, panel_rect, 1)

        # Panel Header
        title = self.mode_titles[self.mode]
        t_img = self.font_subtitle.render(title, True, CYAN_ELECTRIC)
        surf.blit(t_img, (ax + 12, ay + 10))
        pygame.draw.line(surf, PANEL_BORDER, (ax + 10, ay + 32), (ax + aw - 10, ay + 32), 1)

        cur_y = ay + 40

        if self.mode == "bresenham":
            cur_y = self._render_bresenham_theory(ax + 12, cur_y, aw - 24)
        elif self.mode == "dda":
            cur_y = self._render_dda_theory(ax + 12, cur_y, aw - 24)
        elif self.mode == "circle":
            cur_y = self._render_circle_theory(ax + 12, cur_y, aw - 24)
        elif self.mode == "clipping":
            cur_y = self._render_clipping_theory(ax + 12, cur_y, aw - 24)

    def _render_bresenham_theory(self, x, y, max_w):
        surf = self.screen
        dx = self.p1[0] - self.p0[0]
        dy = self.p1[1] - self.p0[1]
        adx, ady = abs(dx), abs(dy)
        slope = (dy / dx) if dx != 0 else float('inf')
        slope_str = f"{slope:.2f}" if dx != 0 else "undefined"

        lines = [
            ("Core Principle:", CYAN_ACCENT),
            ("Integer-only additions with decision parameter.", TEXT_WHITE),
            (f"Endpoints: P0({self.p0[0]},{self.p0[1]}) -> P1({self.p1[0]},{self.p1[1]})", AMBER_GOLD),
            (f"Delta: dx={dx}, dy={dy}  |  Slope: m={slope_str}", TEXT_MUTED),
            (f"Initial Decision Parameter: p0 = 2*dy - dx = {2 * ady - adx}", CYAN_ELECTRIC),
            ("", TEXT_WHITE),
            ("Step-by-Step Rasterization:", CYAN_ACCENT),
        ]
        for txt, col in lines:
            if not txt:
                y += 4
                continue
            surf.blit(self.font_code.render(txt, True, col), (x, y))
            y += 16

        # Step Table (showing first 10 steps)
        pts = list(bresenham_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1]))
        hdr = "  k   ( x ,  y )   Selected Pixel"
        surf.blit(self.font_code.render(hdr, True, (0, 200, 240)), (x, y))
        y += 15

        for k, (px, py) in enumerate(pts[:10]):
            row = f" {k:2d}   ({px:2d}, {py:2d})      Plot ({px},{py})"
            surf.blit(self.font_code.render(row, True, TEXT_WHITE), (x, y))
            y += 14

        if len(pts) > 10:
            surf.blit(self.font_code.render(f" ... +{len(pts)-10} additional pixels plotted", True, TEXT_DIM), (x, y))
        return y

    def _render_dda_theory(self, x, y, max_w):
        surf = self.screen
        dx = self.p1[0] - self.p0[0]
        dy = self.p1[1] - self.p0[1]
        steps = int(max(abs(dx), abs(dy)))
        x_inc = dx / steps if steps != 0 else 0
        y_inc = dy / steps if steps != 0 else 0

        lines = [
            ("Core Principle:", CYAN_ACCENT),
            ("Differential Analyzer: Unit step along major axis.", TEXT_WHITE),
            (f"Endpoints: P0({self.p0[0]},{self.p0[1]}) -> P1({self.p1[0]},{self.p1[1]})", AMBER_GOLD),
            (f"Steps = max(|dx|, |dy|) = {steps}", CYAN_ELECTRIC),
            (f"x_inc = dx/steps = {x_inc:.3f}", TEXT_MUTED),
            (f"y_inc = dy/steps = {y_inc:.3f}", TEXT_MUTED),
            ("", TEXT_WHITE),
            ("Step-by-Step Floating Math -> Integer:", CYAN_ACCENT),
        ]
        for txt, col in lines:
            if not txt:
                y += 4
                continue
            surf.blit(self.font_code.render(txt, True, col), (x, y))
            y += 16

        hdr = "  k   Exact (x, y)     round(x, y)"
        surf.blit(self.font_code.render(hdr, True, NEON_GREEN), (x, y))
        y += 15

        # Recalculate DDA steps for exact float display
        cx, cy = float(self.p0[0]), float(self.p0[1])
        for k in range(min(steps + 1, 9)):
            row = f" {k:2d}  ({cx:5.2f}, {cy:5.2f}) -> ({round(cx):2d}, {round(cy):2d})"
            surf.blit(self.font_code.render(row, True, TEXT_WHITE), (x, y))
            y += 14
            cx += x_inc
            cy += y_inc

        if steps + 1 > 9:
            surf.blit(self.font_code.render(f" ... +{steps + 1 - 9} remaining steps", True, TEXT_DIM), (x, y))
        return y

    def _render_circle_theory(self, x, y, max_w):
        surf = self.screen
        cx, cy = self.circle_center
        r = self.circle_radius
        p0 = 1 - r

        lines = [
            ("Core Principle: 8-Way Symmetry", CYAN_ACCENT),
            ("Compute 1 octant (x <= y) -> mirror to 7 others.", TEXT_WHITE),
            (f"Center: ({cx}, {cy})  |  Radius: {r} cells", AMBER_GOLD),
            (f"Initial Decision Param: p0 = 1 - r = {p0}", CYAN_ELECTRIC),
            ("If p < 0: p += 2x + 1   (E step)", TEXT_MUTED),
            ("If p >= 0: p += 2(x-y) + 1 (SE step)", TEXT_MUTED),
            ("", TEXT_WHITE),
            ("Octant Points & Decision Steps:", CYAN_ACCENT),
        ]
        for txt, col in lines:
            if not txt:
                y += 4
                continue
            surf.blit(self.font_code.render(txt, True, col), (x, y))
            y += 16

        hdr = "  x   y    p_k   Next Step"
        surf.blit(self.font_code.render(hdr, True, (255, 205, 45)), (x, y))
        y += 15

        # Compute octant sequence with decision params
        curr_x, curr_y = 0, r
        p = 1 - r
        step_idx = 0
        while curr_x <= curr_y and step_idx < 8:
            action = "E (x+1)" if p < 0 else "SE (x+1, y-1)"
            row = f" {curr_x:2d}  {curr_y:2d}  {p:3d}    {action}"
            surf.blit(self.font_code.render(row, True, TEXT_WHITE), (x, y))
            y += 14
            if p < 0:
                p += 2 * curr_x + 1
            else:
                curr_y -= 1
                p += 2 * (curr_x - curr_y) + 1
            curr_x += 1
            step_idx += 1

        surf.blit(self.font_sm.render("* Plotted pixels color-coded by octant", True, OCTANT_COLORS[1]), (x, y + 6))
        return y

    def _render_clipping_theory(self, x, y, max_w):
        surf = self.screen
        xmin, ymin, xmax, ymax = self.clip_win
        c0 = outcode(self.clip_p0[0], self.clip_p0[1], self.clip_win)
        c1 = outcode(self.clip_p1[0], self.clip_p1[1], self.clip_win)

        def code_str(c):
            return f"{(c & TOP) >> 2}{(c & BOTTOM) >> 3}{(c & RIGHT) >> 1}{c & LEFT:01b}"

        lines = [
            ("Core Principle: 4-Bit Region Outcodes", CYAN_ACCENT),
            ("Bitwise classification: [Top, Bottom, Right, Left]", TEXT_WHITE),
            (f"Clip Window: [{xmin},{ymin}] to [{xmax},{ymax}]", CYAN_ELECTRIC),
            (f"P0({self.clip_p0[0]},{self.clip_p0[1]}) Code: {code_str(c0)}", CORAL_RED),
            (f"P1({self.clip_p1[0]},{self.clip_p1[1]}) Code: {code_str(c1)}", AMBER_GOLD),
            ("", TEXT_WHITE),
            ("Bitwise Decision Logic:", CYAN_ACCENT),
        ]
        for txt, col in lines:
            if not txt:
                y += 4
                continue
            surf.blit(self.font_code.render(txt, True, col), (x, y))
            y += 16

        # Acceptance/Rejection Status
        if not (c0 | c1):
            status = "TRIVIAL ACCEPT (c0 | c1 == 0000)"
            st_col = NEON_GREEN
        elif c0 & c1:
            status = "TRIVIAL REJECT (c0 & c1 != 0000)"
            st_col = CORAL_RED
        else:
            status = "PARTIAL CLIP (Boundary Intersection)"
            st_col = AMBER_GOLD
        surf.blit(self.font_code.render(f"Result: {status}", True, st_col), (x, y))
        y += 18

        res = cohen_sutherland(self.clip_p0[0], self.clip_p0[1],
                               self.clip_p1[0], self.clip_p1[1],
                               self.clip_win)
        if res is not None:
            cx0, cy0, cx1, cy1 = res
            surf.blit(self.font_code.render("Clipped Segment Coordinates:", True, CYAN_ACCENT), (x, y))
            y += 15
            surf.blit(self.font_code.render(f"P0' = ({cx0:.2f}, {cy0:.2f})", True, NEON_GREEN), (x, y))
            y += 14
            surf.blit(self.font_code.render(f"P1' = ({cx1:.2f}, {cy1:.2f})", True, NEON_GREEN), (x, y))
            y += 16
        else:
            surf.blit(self.font_code.render("Line completely rejected outside window.", True, CORAL_RED), (x, y))
            y += 16

        surf.blit(self.font_sm.render("* Red dashed line = unclipped; Green = clipped", True, TEXT_MUTED), (x, y + 4))
        return y

    def _draw_footer(self):
        surf = self.screen
        surf.fill(PANEL_BG, (0, 560, 800, 40))
        pygame.draw.line(surf, PANEL_BORDER, (0, 560), (800, 560), 1)

        hints = "[1-4] Select Algorithm  |  [L-Click / Drag] Move Points  |  [P] Presets  |  [R] Reset  |  [ESC] Main Menu"
        txt = self.font_body.render(hints, True, TEXT_MUTED)
        surf.blit(txt, txt.get_rect(center=(400, 580)))
