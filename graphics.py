"""
graphics.py  -  ALL the computer-graphics algorithms, written from scratch
---------------------------------------------------------------------------
pygame is ONLY used to open a window, read the keyboard and put one
pixel / one horizontal strip on the screen.  Every shape you see is
produced by the algorithms below:

  1. DDA line algorithm
  2. Bresenham line algorithm
  3. Midpoint circle algorithm  (outline + filled disc)
  4. Cohen-Sutherland line clipping
  5. Liang-Barsky line clipping
  6. Scan-line polygon fill
  7. Rectangle clipping (cells vs torch window)
"""
import math
import pygame

# ----------------------------------------------------------------------
# 1. DDA  (Digital Differential Analyzer) line algorithm
# ----------------------------------------------------------------------
def dda_line(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    steps = int(max(abs(dx), abs(dy)))          # number of steps = larger delta
    if steps == 0:
        yield int(round(x0)), int(round(y0))
        return
    x_inc, y_inc = dx / steps, dy / steps       # increment per step
    x, y = x0, y0
    for _ in range(steps + 1):
        yield int(round(x)), int(round(y))
        x += x_inc
        y += y_inc


# ----------------------------------------------------------------------
# 2. Bresenham line algorithm  (integer only, all octants)
# ----------------------------------------------------------------------
def bresenham_line(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy                               # decision parameter
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


# ----------------------------------------------------------------------
# 3. Midpoint circle algorithm (8-way symmetry)
# ----------------------------------------------------------------------
def _octant(r):
    x, y = 0, r
    p = 1 - r                                   # initial decision parameter
    while x <= y:
        yield x, y
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1


def circle_points(cx, cy, r):
    """Outline of a circle: each octant point is mirrored 8 times."""
    for x, y in _octant(r):
        yield cx + x, cy + y
        yield cx - x, cy + y
        yield cx + x, cy - y
        yield cx - x, cy - y
        yield cx + y, cy + x
        yield cx - y, cy + x
        yield cx + y, cy - x
        yield cx - y, cy - x


def circle_spans(cx, cy, r):
    """Filled disc = horizontal spans between mirrored midpoint points."""
    for x, y in _octant(r):
        yield cy + y, cx - x, cx + x
        yield cy - y, cx - x, cx + x
        yield cy + x, cx - y, cx + y
        yield cy - x, cx - y, cx + y


# ----------------------------------------------------------------------
# 4. Cohen-Sutherland line clipping
# ----------------------------------------------------------------------
INSIDE, LEFT, RIGHT, TOP, BOTTOM = 0, 1, 2, 4, 8      # 4-bit region code


def outcode(x, y, win):
    xmin, ymin, xmax, ymax = win
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= TOP
    elif y > ymax:
        code |= BOTTOM
    return code


def cohen_sutherland(x0, y0, x1, y1, win):
    xmin, ymin, xmax, ymax = win
    c0, c1 = outcode(x0, y0, win), outcode(x1, y1, win)
    while True:
        if not (c0 | c1):            # both codes 0000 -> trivially ACCEPT
            return x0, y0, x1, y1
        if c0 & c1:                  # share an outside region -> trivially REJECT
            return None
        c = c0 if c0 else c1         # pick an endpoint that is outside
        if c & TOP:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0); y = ymin
        elif c & BOTTOM:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0); y = ymax
        elif c & RIGHT:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0); x = xmax
        else:                        # LEFT
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0); x = xmin
        if c == c0:
            x0, y0 = x, y
            c0 = outcode(x0, y0, win)
        else:
            x1, y1 = x, y
            c1 = outcode(x1, y1, win)


# ----------------------------------------------------------------------
# 5. Liang-Barsky line clipping (parametric)
# ----------------------------------------------------------------------
def liang_barsky(x0, y0, x1, y1, win):
    xmin, ymin, xmax, ymax = win
    dx, dy = x1 - x0, y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - xmin, xmax - x0, y0 - ymin, ymax - y0)
    u1, u2 = 0.0, 1.0
    for pk, qk in zip(p, q):
        if pk == 0:                  # line parallel to this boundary
            if qk < 0:
                return None          # and outside it
        else:
            t = qk / pk
            if pk < 0:               # entering
                if t > u2:
                    return None
                u1 = max(u1, t)
            else:                    # leaving
                if t < u1:
                    return None
                u2 = min(u2, t)
    return x0 + u1 * dx, y0 + u1 * dy, x0 + u2 * dx, y0 + u2 * dy


# ----------------------------------------------------------------------
# 6. Scan-line polygon fill (even-odd rule)
# ----------------------------------------------------------------------
def scanline_spans(pts):
    n = len(pts)
    ys = [p[1] for p in pts]
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        yc = y + 0.5                              # scan-line height
        xs = []
        for i in range(n):                        # find edge intersections
            xa, ya = pts[i]
            xb, yb = pts[(i + 1) % n]
            if ya == yb:
                continue                          # ignore horizontal edges
            if (ya <= yc < yb) or (yb <= yc < ya):
                xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):        # fill between pairs
            yield y, int(round(xs[i])), int(round(xs[i + 1]))


# ----------------------------------------------------------------------
# Renderer: wraps the algorithms and applies the TORCH CLIP WINDOW
# ----------------------------------------------------------------------
class Renderer:
    def __init__(self, surface):
        self.surf = surface
        self.line_algo = "Bresenham"              # or "DDA"
        self.clip_algo = "Cohen-Sutherland"       # or "Liang-Barsky"
        self.set_window(400, 300, 10000, 10000)

    # the clip window is a square centred on the player
    def set_window(self, cx, cy, half, fade_radius=None):
        self.center = (cx, cy)
        self.win = (cx - half, cy - half, cx + half, cy + half)
        self.fade_radius = fade_radius if fade_radius else half * 1.25

    def toggle_line(self):
        self.line_algo = "DDA" if self.line_algo == "Bresenham" else "Bresenham"

    def toggle_clip(self):
        self.clip_algo = ("Liang-Barsky" if self.clip_algo == "Cohen-Sutherland"
                          else "Cohen-Sutherland")

    def in_window(self, x, y):
        return outcode(x, y, self.win) == INSIDE

    def fade(self, x, y):
        """Light falls off with distance from the torch (1.0 bright .. 0.15 dim)."""
        d = math.hypot(x - self.center[0], y - self.center[1])
        return max(0.15, 1.0 - 0.85 * min(1.0, d / self.fade_radius))

    def _shade(self, color, f):
        return (int(color[0] * f), int(color[1] * f), int(color[2] * f))

    # ---- lines --------------------------------------------------------
    def line(self, p0, p1, color, thick=1, use_fade=True):
        clip = cohen_sutherland if self.clip_algo == "Cohen-Sutherland" else liang_barsky
        seg = clip(p0[0], p0[1], p1[0], p1[1], self.win)
        if seg is None:
            return                                  # completely outside torch
        gen = bresenham_line if self.line_algo == "Bresenham" else dda_line
        off = thick // 2
        fill = self.surf.fill
        for x, y in gen(*seg):
            col = self._shade(color, self.fade(x, y)) if use_fade else color
            fill(col, (x - off, y - off, thick, thick))

    def polyline(self, pts, color, thick=1, closed=True, use_fade=True):
        n = len(pts)
        last = n if closed else n - 1
        for i in range(last):
            self.line(pts[i], pts[(i + 1) % n], color, thick, use_fade)

    # ---- polygon fill (spans clipped to the window) -------------------
    def fill_polygon(self, pts, color):
        xmin, ymin, xmax, ymax = self.win
        for y, xl, xr in scanline_spans(pts):
            if y < ymin or y > ymax:
                continue
            xl, xr = max(xl, xmin), min(xr, xmax)
            if xr < xl:
                continue
            f = self.fade((xl + xr) / 2, y)
            self.surf.fill(self._shade(color, f), (xl, y, xr - xl + 1, 1))

    # ---- circles ------------------------------------------------------
    def disc(self, cx, cy, r, color, use_fade=True):
        xmin, ymin, xmax, ymax = self.win
        for y, xl, xr in circle_spans(int(cx), int(cy), int(r)):
            if y < ymin or y > ymax:
                continue
            xl, xr = max(xl, xmin), min(xr, xmax)
            if xr < xl:
                continue
            col = self._shade(color, self.fade(cx, cy)) if use_fade else color
            self.surf.fill(col, (xl, y, xr - xl + 1, 1))

    def circle(self, cx, cy, r, color, thick=2):
        for x, y in circle_points(int(cx), int(cy), int(r)):
            if self.in_window(x, y):
                self.surf.fill(color, (x, y, thick, thick))
