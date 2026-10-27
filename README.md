# Dark Cave Explorer  -  Computer Graphics Mini Project (Python + pygame)

## Run
```
pip install pygame
python main.py
```
Controls: Arrow keys / WASD = move | **SPACE (or F) = shoot arrow** | L = switch DDA <-> Bresenham | C = switch Cohen-Sutherland <-> Liang-Barsky | R = restart level | ENTER = continue | ESC = quit

## Story
You explore a pitch-black cave. Your torch is a **clipping window** - everything outside it is not drawn.
Collect all keys, avoid or **shoot the bats with arrows (SPACE)**, and enter the glowing portal. 3 levels, 3 lives.
A destroyed bat explodes (+150 points) and comes back after 10 seconds.

| Level | Torch size | Keys | Bats |
|-------|-----------|------|------|
| 1 - The Entrance | large | 1 | 1 (slow) |
| 2 - The Crystal Tunnels | medium | 2 | 3 |
| 3 - The Abyss | small | 3 | 5 (faster) |

## Files
| File | What is inside |
|------|----------------|
| `graphics.py` | DDA, Bresenham, Midpoint circle, Cohen-Sutherland, Liang-Barsky, Scan-line fill, Renderer (clip window) |
| `matrix.py`   | 3x3 homogeneous matrices: translate, rotate, scale, shear, reflect, compose |
| `levels.py`   | Cave generation + wall segments |
| `game.py`     | Game logic and all drawing |
| `main.py`     | Window + input loop |

pygame is used ONLY for the window, keyboard and putting pixels / 1-pixel-high strips on screen.

## Where each CG concept is used
| Concept | Where in the game | File / function |
|---|---|---|
| DDA line | Wall edges (press L to switch) | `graphics.dda_line` |
| Bresenham line | Wall edges, torch frame, torch stick | `graphics.bresenham_line` |
| Midpoint circle (outline) | Key halo, portal ring, pickup ripple, title rings | `graphics.circle_points` |
| Midpoint circle (filled) | Player body, lives, torch glow, bat eyes | `graphics.circle_spans` |
| Cohen-Sutherland clipping | Every wall line is clipped to the torch window | `graphics.cohen_sutherland` |
| Liang-Barsky clipping | Same, press C to switch | `graphics.liang_barsky` |
| Rectangle clipping | Rock/floor cells cut by the torch window | `Game._draw_cells` |
| Polygon fill (scan-line) | Player arrow, flame, keys, bats, portal star | `graphics.scanline_spans` |
| Translation | Player & bat movement, bobbing keys, **arrow flying forward, debris shards** | `matrix.translate` |
| Rotation | Player arrow turns, portal star spins, title squares, **shot arrow points where you aim, blast star & shards spin** | `matrix.rotate` |
| Scaling | Pulsing key/portal, bat wing flap, flickering flame, **explosion grows, shards shrink, arrow stretches on launch, bat grows in when it respawns** | `matrix.scale` |
| Reflection | Bat is mirrored when flying the other way | `matrix.reflect_y` / `scale(-1,1)` |
| Shear | Wobbling torch flame | `matrix.shear` |
| Composite transformation | `compose(translate, rotate, scale)` everywhere, e.g. **`Game._draw_arrows`, `Game._draw_blasts`** | `matrix.compose` |
| Animation / double buffering | 60 FPS loop, flicker, particles | `main.py` |
| Light falloff (shading) | Colour fades with distance from torch | `Renderer.fade` |

## Likely viva questions
**Q1. What is the difference between DDA and Bresenham?**
DDA uses floating-point increments (dx/steps, dy/steps) and rounds every point. Bresenham uses only integer additions with a decision parameter, so it is faster and more accurate.

**Q2. Explain the midpoint circle algorithm.**
Start at (0, r) with p = 1 - r. If p < 0 the next pixel is (x+1, y) and p += 2x + 1; otherwise it is (x+1, y-1) and p += 2(x - y) + 1. Only one octant is computed; the other 7 points come from 8-way symmetry.

**Q3. Where is clipping used in your game?**
The torch is a rectangular clip window. Each wall segment is clipped to it; the part outside is rejected, so only the lit part is drawn. Bats, keys and portal are drawn through the same window.

**Q4. How does Cohen-Sutherland work?**
Each endpoint gets a 4-bit region code (left, right, top, bottom). If both codes are 0000 the line is accepted; if the AND of the codes is non-zero it is rejected; otherwise the line is cut at a window edge and the test repeats.

**Q5. How is Liang-Barsky different?**
It uses the parametric form of the line and computes entry/exit parameters u1, u2 against the four edges (p, q values). It needs fewer intersection calculations, so it is generally faster.

**Q6. What are homogeneous coordinates and why use them?**
Points are written (x, y, 1) so translation can also be a matrix. Then translation, rotation and scaling can be combined into ONE matrix by multiplication (composite transformation).

**Q7. Show a composite transformation in your game.**
The player's arrow: `compose(translate(px,py), rotate(angle))` - the arrow is first rotated about the origin, then moved to the player's position. Order matters: the matrix on the right is applied first.

**Q8. Where do you use reflection and shear?**
Reflection: `scale(-1, 1)` flips the bat sprite when it moves left. Shear: the torch flame is sheared by a sine value each frame to make it wobble.

**Q9. How does the scan-line fill work?**
For every horizontal line we find where it intersects the polygon edges, sort the x values, and fill between pairs (even-odd rule).

**Q10. How is the torch light effect made?**
Pixel colour is multiplied by a factor that decreases with distance from the player, and a warm glow made of concentric filled midpoint circles with decreasing transparency is drawn over the window.

**Q11. Which transformations are used when you shoot an arrow and kill a bat?**
Arrow: `compose(translate(x, y), rotate(angle), scale(stretch, 1))`. The arrow shape is stretched (scaling), turned to the aim direction (rotation) and then moved to its current position (translation); the position changes every frame along (cos a, sin a). Explosion: a star polygon is drawn with `compose(translate(bx, by), rotate(p), scale(s, s))` where s grows with time (scaling about the bat's centre), and the shards use `scale(k, k)` with k shrinking from 1 to 0 while they rotate and translate outwards.

**Q12. Why do you translate to the origin first / why is the order important?**
Rotation and scaling work about the ORIGIN. So the shape is defined around (0, 0), scaled/rotated there, and only then translated to the bat's position. If translation were applied first, the shape would rotate/scale about the screen origin and fly away instead of exploding in place (matrix multiplication is not commutative).
