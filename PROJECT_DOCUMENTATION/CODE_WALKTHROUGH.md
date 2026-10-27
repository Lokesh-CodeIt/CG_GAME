# EmberVault: The Crystal Maze - Step-by-Step Code Walkthrough

This document traces the complete codebase of **EmberVault: The Crystal Maze**, explaining every module, class, and function step-by-step with real code references, mathematical explanations, and gameplay logic.

---

## 1. Project Directory & File Map

```text
DarkCaveExplorer/
│
├── main.py                 # Application startup, window creation, and 60 FPS input/event loop
├── graphics.py             # Pure Computer Graphics algorithms library (DDA, Bresenham, Midpoint, Clipping)
├── matrix.py               # 2D Homogeneous 3x3 transformation matrix pipeline
├── levels.py               # Seeded DFS maze generator, corridor loop injection, BFS AI pathfinding
├── game.py                 # Core game engine: player physics, abilities, fog of war, rendering, HUD
├── cg_lab.py               # Interactive academic Computer Graphics Laboratory mode
├── test_game.py            # Automated 16-test headless verification suite
├── best_score.txt          # Persistent local storage for all-time record score
└── README.md               # Quick-start instructions, control references, and overview
```

---

## 2. Low-Level Computer Graphics Library: `graphics.py`

[graphics.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py) contains all foundational rasterization, clipping, and scanning algorithms implemented from scratch. Pygame is used solely to blit individual pixels and 1-pixel scanline spans.

### 2.1 Digital Differential Analyzer (DDA) Line Algorithm
- **Location**: [graphics.py: Lines 22-35](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L22-L35)
- **Function**: `dda_line(x0, y0, x1, y1)`
- **Mathematical Logic**:
  1. Calculates coordinate differences: $dx = x_1 - x_0$, $dy = y_1 - y_0$.
  2. Determines required steps: $\text{steps} = \max(|dx|, |dy|)$.
  3. Computes floating-point increments per step:
     $$x_{\text{inc}} = \frac{dx}{\text{steps}}, \quad y_{\text{inc}} = \frac{dy}{\text{steps}}$$
  4. Increments $x$ and $y$ on each iteration and rounds each coordinate to integer pixels:
     $$\text{yield } (\text{round}(x), \text{round}(y))$$
- **Usage in Game**: Used for drawing wall boundaries when toggled with key `L`, and in the CG Lab DDA mode.

### 2.2 Bresenham's Integer Line Algorithm
- **Location**: [graphics.py: Lines 38-70](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L38-L70)
- **Function**: `bresenham_line(x0, y0, x1, y1)`
- **Mathematical Logic**:
  - Avoids floating-point divisions by using integer arithmetic and an incremental decision parameter $p_k$.
  - For shallow slopes ($dx > dy$):
    - Initial decision parameter: $p_0 = 2dy - dx$.
    - If $p_k < 0$: $p_{k+1} = p_k + 2dy$, next pixel is $(x + s_x, y)$.
    - If $p_k \ge 0$: $p_{k+1} = p_k + 2(dy - dx)$, next pixel is $(x + s_x, y + s_y)$.
  - Symmetrical logic is implemented for steep slopes ($dy \ge dx$).
- **Usage in Game**: Default algorithm for drawing glowing cave wall edges, torch clipping boundaries, and the CG Lab Bresenham demonstration.

### 2.3 Midpoint Circle Algorithm (Outline & Filled Spans)
- **Location**: [graphics.py: Lines 73-122](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L73-L122)
- **Functions**: `circle_points(cx, cy, r)`, `circle_spans(cx, cy, r)`
- **Mathematical Logic**:
  - Evaluates circle function $f(x, y) = x^2 + y^2 - r^2$ at midpoint between Eastern candidate $(x+1, y)$ and South-Eastern candidate $(x+1, y-1)$.
  - Initial decision parameter at $(0, r)$: $p_0 = 1 - r$.
  - In each step:
    - If $p_k < 0$: next point is $(x+1, y)$ and $p_{k+1} = p_k + 2x + 1$.
    - If $p_k \ge 0$: next point is $(x+1, y-1)$ and $p_{k+1} = p_k + 2(x - y) + 1$.
  - Generates 8-way symmetry points across all 8 octants.
  - `circle_spans()` collects horizontal scanline spans $(y, x_{\text{left}}, x_{\text{right}})$ to draw filled circles (used for player body, torch glow, and shield barriers).

### 2.4 Cohen-Sutherland Line Clipping Algorithm
- **Location**: [graphics.py: Lines 125-165](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L125-L165)
- **Functions**: `outcode(x, y, win)`, `cohen_sutherland(x0, y0, x1, y1, win)`
- **Mathematical Logic**:
  - Encodes point positions using a 4-bit region code:
    - Bit 0 (`LEFT`): $x < x_{\text{min}}$
    - Bit 1 (`RIGHT`): $x > x_{\text{max}}$
    - Bit 2 (`BOTTOM`): $y < y_{\text{min}}$
    - Bit 3 (`TOP`): $y > y_{\text{max}}$
  - Bitwise Trivial Accept: `if not (c0 | c1)` $\implies$ segment is completely inside window.
  - Bitwise Trivial Reject: `if (c0 & c1)` $\implies$ both points share an outside half-plane; segment is completely invisible.
  - Boundary Edge Intersection: Solves parametric line equation to clip against window edge and recalculates the outcode.
- **Usage in Game**: Used by `Renderer` to clip every maze wall line segment to the torch light window.

### 2.5 Liang-Barsky Parametric Line Clipping Algorithm
- **Location**: [graphics.py: Lines 168-200](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L168-L200)
- **Function**: `liang_barsky(x0, y0, x1, y1, win)`
- **Mathematical Logic**:
  - Uses the parametric representation: $x = x_0 + u \cdot dx$, $y = y_0 + u \cdot dy$ where $u \in [0, 1]$.
  - Solves 4 boundary inequalities $u \cdot p_k \le q_k$ for left, right, bottom, and top edges.
  - Updates parameter interval $[u_1, u_2]$. If $u_1 > u_2$, the line is completely rejected.
- **Usage in Game**: Alternate clipping algorithm toggled with key `C`.

### 2.6 Scan-Line Concave Polygon Filling
- **Location**: [graphics.py: Lines 203-238](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L203-L238)
- **Function**: `scanline_spans(pts)`
- **Mathematical Logic**:
  - Computes bounding box $[y_{\text{min}}, y_{\text{max}}]$ for arbitrary polygon vertices.
  - For each horizontal raster line $y$: finds all edge intersections using linear interpolation:
    $$x_{\text{int}} = x_a + (y - y_a) \cdot \frac{x_b - x_a}{y_b - y_a}$$
  - Sorts intersection points by $x$ ascending and pairs them: $[(x_0, x_1), (x_2, x_3), \dots]$ to fill solid horizontal interior pixel rows.
- **Usage in Game**: Renders player ship body, arrow tips, wraith carapaces, and spinning portal star.

---

## 3. Matrix Transformation Pipeline: `matrix.py`

[matrix.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/matrix.py) implements affine transformations using $3 \times 3$ homogeneous matrices:

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \mathbf{M} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

- `translate(tx, ty)`: Translates points by vector $(\Delta x, \Delta y)$.
- `rotate(angle)`: Rotates points counter-clockwise by $\theta$ radians.
- `scale(sx, sy)`: Scales coordinates relative to the origin.
- `reflect_y()`: Mirrors points horizontally across the y-axis (`scale(-1, 1)`).
- `shear(kx, ky)`: Shears geometry sideways (used for wobbling torch flame).
- `compose(*matrices)`: Multiplies multiple $3 \times 3$ matrices sequentially to form a single composite transformation matrix:
  $$\mathbf{M}_{\text{composite}} = \mathbf{M}_n \times \mathbf{M}_{n-1} \times \dots \times \mathbf{M}_1$$
- `apply(matrix, points)`: Multiplies a list of $(x, y)$ coordinate tuples by the transformation matrix, returning transformed screen coordinates.

---

## 4. Maze Generation & Enemy AI: `levels.py`

[levels.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/levels.py) creates the procedural caverns, coordinates, and AI entities.

### 4.1 Maze Carving & Topology
- **Seeded Depth-First Search (`_carve`)**:
  - Operates on a $19 \times 15$ grid of odd coordinates with outer boundary walls.
  - Carves paths 2 steps at a time to maintain grid walls.
  - Carves a $3 \times 3$ open central chamber (Grand Nexus Plaza) at the maze center.
  - Knocks down selected interior walls to introduce tactical loops.
- **Topological Breadth-First Search Distance Map (`_bfs`)**:
  - Traverses the carved maze from start cell $(1, 1)$ to find the farthest walkable cell, automatically designating it as the exit portal location.

### 4.2 BFS Grid Pathfinding
- **Function**: `find_bfs_path(start_rc, target_rc)`
- **Logic**:
  - Maintains a queue `q = deque([start_rc])` and a `visited` dictionary mapping each cell to its parent: `visited[neighbor] = current`.
  - Expands valid cardinal neighbors (`grid == 0`).
  - Upon reaching `target_rc`, traces parent pointers backward and reverses the list to return the optimal sequence of corridor coordinates $[(r_0, c_0), (r_1, c_1), \dots]$.

### 4.3 Intelligent Enemy AI (`Bat.update_ai`)
- **Stalker Wraiths**:
  - Set `bat_type = "stalker"`.
  - Recalculates `find_bfs_path()` to the player's current grid cell every 0.25 seconds.
  - Follows waypoints along open corridors, smoothly steering toward target waypoints with `math.hypot(wx, wy)`.
- **Scout Wraiths**:
  - Set `bat_type = "scout"`.
  - Executes default corridor patrol, bouncing when wall is reached.
  - If player enters within 5 cells distance, dynamically switches to chase behavior.

---

## 5. Game Engine & Abilities: `game.py`

[game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/game.py) brings together physics, abilities, fog of war, and UI.

### 5.1 Player Physics & Pushout Collision
- Player moves via velocity integration:
  $$\text{px} += v_x \cdot \text{speed} \cdot \Delta t, \quad \text{py} += v_y \cdot \text{speed} \cdot \Delta t$$
- `Game._collide()` samples the 9 grid cells around the player. For each wall tile, it calculates the closest boundary coordinate, measures distance $d$, and pushes the player out by $(R_{\text{player}} - d)$ along the normal vector.

### 5.2 Zero-Timer Ability Implementations
1. **Directional Dash (`dash()`)**:
   - Computes movement direction unit vector.
   - Advances position in 4 sub-steps of 12 pixels each, running collision pushout after each step to prevent wall tunneling.
   - Leaves afterimage coordinates in `self.afterimages` with alpha fading.
   - Recharged through walking: `dash_step_counter` increments on movement; at 35 steps, restores +1 dash charge.
2. **Energy Shield (`toggle_shield()`, `_hit()`)**:
   - Activated via `E` key (`self.shield_active = True`).
   - In `_hit()`, if `shield_active` is true, damage is nullified, the shield breaks, and lives remain untouched.
   - Recharged when picking up an Aegis crystal or purging 2 wraiths.
3. **Tri-Shot Arrow Volleys (`shoot()`)**:
   - If `surge_charges > 0`, decrements 1 charge and fires 3 arrows at angles $[\theta - 0.26, \theta, \theta + 0.26]$ radians.

### 5.3 Dynamic Fog of War & Discovery
- A 2D boolean array `self.discovered[ROWS][COLS]` persists across level play.
- In `update()`, cells within distance $(\text{torch} + 15\text{px})$ from player are marked `True`.
- In `_draw_cells()`, cells that are discovered but outside the current torch radius are drawn with soft dimmed ghosting, keeping explored paths readable.

---

## 6. Interactive CG Laboratory: `cg_lab.py`

[cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py) is the self-contained academic graphics laboratory.

- **Grid Coordinate Mapping**: Converts screen pixel positions to discrete grid cells:
  $$gx = \frac{x - \text{grid\_ox}}{\text{cell\_size}}, \quad gy = \frac{y - \text{grid\_oy}}{\text{cell\_size}}$$
- **Interactive Mouse Handling**: Left-click and drag detects proximity to endpoints $P_0, P_1$ or circle center $C$ and updates coordinates in real time.
- **Algorithm Computation & Step Tables**:
  - Calls `graphics.bresenham_line()` or `graphics.dda_line()` and populates a live mathematical table showing step $k$, coordinate $(x, y)$, decision parameter $p_k$, and chosen pixel.
  - In Midpoint Circle mode, plots octants in 8 distinct colors.
  - In Cohen-Sutherland mode, renders the clip window, evaluates 4-bit region outcodes, and displays boundary intersection calculations.
