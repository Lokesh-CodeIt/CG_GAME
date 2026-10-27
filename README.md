# EmberVault: The Crystal Maze  -  Computer Graphics Project (Python + pygame)

## Run
```bash
pip install pygame
python main.py
```
**Controls**:
- **Move**: Arrow keys / `W`, `A`, `S`, `D`
- **Shoot Crystal Arrow**: `SPACE` or `F`
- **Select Level (on Title)**: `1`, `2`, `3`, `4`, `5` or `TAB` / `Arrow Keys`
- **Toggle Coordinate Grid Overlay**: `G`
- **Pause / Resume**: `P`
- **Field Guide & Theory**: `H`
- **Switch Line Algorithm**: `L` (*DDA* $\leftrightarrow$ *Bresenham*)
- **Switch Line Clipping**: `C` (*Cohen-Sutherland* $\leftrightarrow$ *Liang-Barsky*)
- **Restart Level**: `R`
- **Continue / Start**: `ENTER`
- **Quit**: `ESC`

## Story & Visual Theme
You explore the pitch-black crystal caverns of EmberVault. Your torch acts as an **active rectangular clipping window** emitting a cool radiant blue/cyan glow - geometry outside the light is rejected.
Collect all amber vault keys, avoid or **shoot the shadow wraiths with crystal arrows (SPACE)**, and enter the glowing portal. 5 levels, 3 lives.
A destroyed wraith shatters into purple and neon green plasma shards (+150 points) and respawns after 10 seconds.

### Visual Identity & Component Styling
- **Torch Glow**: Cool radiant electric cyan-to-blue gradient falloff (`#00e1ff` to `#0037af`) - zero yellow/orange tint
- **Cave Walls & Floor**: Deep obsidian navy-black bases (`#080c14`, `#0e1420`) with 3D steel-cyan bevels, luminous electric cyan wall boundaries (`#00dcf5`), and bioluminescent cyan dust specks on navy floor pavers
- **Creatures / Enemies**: Redesigned pixel-art Shadow Wraiths featuring deep purple carapaces (`#551487`, `#912dd7`), neon green razor mandibles, and animated neon green plasma wings and glowing eyes (`#39ff14`)
- **Player Character**: Radiant diamond-white/cyan celestial core with titanium-silver crystal scepter and electric cyan plasma flame
- **Collectibles**:
  - **Vault Keys**: Spinning multifaceted amber-gold gems with radiant golden halo rings
  - **Boost Crystals**: Luminous cyan shards granting *Crystal Surge* (+35% speed and +35px torch radius)
  - **Exit Portal**: Celestial spinning star portal with radiant violet and cyan aura rings
- **HUD & Radar**: Sleek dark navy status bar (`#0a0f18`) with crisp typography, heart indicators, score counters, reload gauge, and live Vault Radar mini-map

| Level | Name | Starting Chamber | Torch size | Keys | Shadow Wraiths | Boosts |
|---|---|---|---|---|---|---|
| 1 | The Cobalt Gateway | Azure Archway `(1, 1)` | 155px | 1 | 1 Scout | - |
| 2 | The Cyan Chasm | Cobalt Sanctuary `(13, 1)` | 125px | 2 | 2 Wraiths | 1 Crystal Surge |
| 3 | The Obsidian Labyrinth | Obsidian Outpost `(7, 1)` | 105px | 3 | 3 Wraiths (Stalker) | 1 Crystal Surge |
| 4 | The Abyssal Depths | Abyss Caldera `(1, 17)` | 92px | 4 | 4 Wraiths | 1 Crystal Surge |
| 5 | The Sanctum Core | Sanctum Nexus `(13, 17)` | 80px | 5 | 5 Wraiths (Elite) | 1 Crystal Surge |

## Added Features
1. **Interactive Title Screen Overhaul**: Fixed text scaling with zero overlap, animated crystal gemstone showcase, drifting stardust particles, and instant level selector (`1-5` / `TAB`).
2. **5 Cavern Levels with Distinct Starting Chambers**: Each level features unique entry points with dedicated runic teleport shrines and calibrated difficulties.
3. **Crystal Surge Power-up**: Collectible cyan crystals in levels 2-5 granting $+35\%$ movement speed and $+35\text{px}$ torch illumination for 7 seconds.
4. **Computer Graphics Grid Overlay (`G`)**: Live Cartesian coordinate grid lines clipped to the torch window with cell coordinates.
5. **Pause & Resume (`P`)**: Seamlessly freezes player motion, bat patrols, and world timers with a crystal pause overlay.
6. **Mini-map (Vault Radar)**: Unobtrusive real-time radar in the top-right displaying walls, walkable paths, uncollected amber keys, boost crystals, the portal, and the player.
7. **Visual Feedback & Animations**: Floating score notices (`+250`, `+150`, `✦ SURGE ✦`), red damage vignette flash on hits, arrow impact sparks, and expanding circular ripples.
8. **Best Score Persistence**: Saves and tracks the highest score locally in `best_score.txt` with in-memory fallback, displayed in the HUD and menu screens.
9. **Field Guide / Help Screen (`H`)**: An in-game overlay detailing all active controls, objectives, and verified computer graphics algorithm implementations.

## Files
| File | What is inside |
|------|----------------|
| `graphics.py` | DDA, Bresenham, Midpoint circle, Cohen-Sutherland, Liang-Barsky, Scan-line fill, Renderer (clip window) |
| `matrix.py`   | 3x3 homogeneous matrices: translate, rotate, scale, shear, reflect, compose |
| `levels.py`   | Cave generation + wall segments |
| `game.py`     | Game logic, HUD, minimap, states, and drawing routines |
| `main.py`     | Window + 60 FPS input loop |
| `test_game.py`| Automated test suite verifying mechanics, state transitions, and algorithms |

pygame is used ONLY for the window, keyboard, and putting pixels / 1-pixel-high strips on screen.

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
