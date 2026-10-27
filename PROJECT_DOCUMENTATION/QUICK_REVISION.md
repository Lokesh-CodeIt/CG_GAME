# EmberVault: The Crystal Maze - Quick Revision Sheet

*A concise, high-yield summary for last-minute viva preparation and project review.*

---

## 1. Essential Computer Graphics Definitions

| Term | One-Line Academic Definition | Everyday Analogy |
|---|---|---|
| **Pixel** | The smallest individual addressable unit of color on a raster display grid. | A single colored tile in a mosaic picture. |
| **Rasterization** | The process of converting continuous mathematical vector shapes (lines, circles, polygons) into discrete screen pixels. | Coloring squares on graph paper to draw a smooth curve. |
| **Clipping** | The computational geometric technique of discarding parts of primitives that lie outside a defined view volume or window. | Looking through an open window; the wall cuts off the view outside the frame. |
| **Homogeneous Coordinates** | A 3D coordinate representation $[x, y, 1]^T$ for 2D points allowing translation, rotation, and scaling to be multiplied as uniform $3 \times 3$ matrices. | Putting multiple gear transformations into a single unified gearbox. |
| **Double Buffering** | Drawing the next frame onto an off-screen surface (back buffer) before instantly flipping it to the display (front buffer) to eliminate visual screen tearing. | Preparing the next chalkboard presentation behind a curtain before opening it. |
| **Scan-Line Filling** | Rasterizing solid polygons by finding intersection spans along horizontal raster rows and filling between pairs of edges. | Coloring a shape row-by-row with a horizontal highlighter pen. |

---

## 2. Core Algorithms Quick Reference

| Algorithm | Primary Purpose | Mathematical Core / Decision Variable | Time Complexity | Implementation in Project |
|---|---|---|---|---|
| **Bresenham's Line** | Integer-only incremental line rasterization | $p_0 = 2\Delta y - \Delta x$<br>$p_{k+1} = p_k + 2\Delta y$ if $p_k < 0$<br>$p_{k+1} = p_k + 2(\Delta y - \Delta x)$ if $p_k \ge 0$ | $O(\max(\Delta x, \Delta y))$ | [graphics.py:bresenham_line](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L38-L70), [cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py) |
| **DDA Line** | Differential line rasterization with float steps | $\text{steps} = \max(\|\Delta x\|, \|\Delta y\|)$<br>$x_{\text{inc}} = \Delta x/\text{steps}, y_{\text{inc}} = \Delta y/\text{steps}$<br>$x = x + x_{\text{inc}}, y = y + y_{\text{inc}}$ | $O(\text{steps})$ | [graphics.py:dda_line](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L22-L35), [cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py) |
| **Midpoint Circle** | 8-way symmetric circle rasterization | $p_0 = 1 - r$<br>$p_{k+1} = p_k + 2x + 1$ (if $E$ chosen)<br>$p_{k+1} = p_k + 2(x - y) + 1$ (if $SE$ chosen) | $O(r)$ | [graphics.py:circle_points](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L73-L95), [cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py) |
| **Cohen-Sutherland Clipping** | Line clipping against a rectangular window | 4-bit Outcodes $[T, B, R, L]$<br>Accept if $c_0 \mid c_1 == 0$<br>Reject if $c_0 \ \& \ c_1 \ne 0$<br>Else intersect boundary edge | $O(1)$ | [graphics.py:cohen_sutherland](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L125-L165), [cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py) |
| **Liang-Barsky Clipping** | Parametric line clipping using inequalities | $u \cdot p_k \le q_k$ where $p_k, q_k$ represent directional deltas; updates $u_1, u_2 \in [0, 1]$ | $O(1)$ | [graphics.py:liang_barsky](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py#L168-L200) |
| **Breadth-First Search (BFS)** | Shortest corridor grid pathfinding | Queue traversal over grid neighbor cells $(r \pm 1, c)$ and $(r, c \pm 1)$ where `grid == 0` | $O(V + E) = O(\text{ROWS} \times \text{COLS})$ | [levels.py:Level.find_bfs_path](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/levels.py#L190-L215) |

---

## 3. Important Source Files & Responsibilities

1. [main.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/main.py): Application entry point, Pygame window creation, event dispatch loop, and 60 FPS clock timing.
2. [graphics.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/graphics.py): Low-level computer graphics algorithms implemented from mathematical scratch (DDA, Bresenham, Midpoint Circle, Cohen-Sutherland, Liang-Barsky, Scan-line fill, Renderer).
3. [matrix.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/matrix.py): 2D homogeneous transformation pipeline using $3 \times 3$ matrices (`translate`, `rotate`, `scale`, `shear`, `reflect_y`, `compose`, `apply`).
4. [levels.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/levels.py): Procedural maze carving using seeded DFS, loop injection, BFS topological distance mapping, BFS corridor pathfinding, and Bat enemy AI.
5. [game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/game.py): Game logic engine, player physics, wall pushout collision, action-based abilities (dash, energy shield, surge tri-shot), persistent fog of war, HUD, and menu rendering.
6. [cg_lab.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/cg_lab.py): Interactive Computer Graphics Laboratory mode demonstrating Bresenham, DDA, Midpoint Circle, and Cohen-Sutherland algorithms on a live pixel grid.
7. [test_game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/test_game.py): Automated test suite containing 16 unit and integration test cases executed under headless video.
8. [best_score.txt](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/best_score.txt): Local text file storing all-time high score.

---

## 4. Key Controls Cheat Sheet

- **Move Explorer**: `W`, `A`, `S`, `D` or Arrow Keys
- **Shoot Crystal Arrow**: `SPACE` or `F`
- **Directional Dash**: `LSHIFT` or `X` (Recharges every 35 paces walked)
- **Energy Shield Barrier**: `E` (Recharges on Aegis pickup or purging 2 wraiths)
- **Computer Graphics Lab**: `L` (on Title) or click `[ L ] CG LABORATORY`
- **Select Level (1 - 5)**: `1`, `2`, `3`, `4`, `5` or `TAB` (on Title)
- **Toggle Cartesian Grid**: `G` (In-Game)
- **Cycle Line Algorithm**: `L` (*DDA* $\leftrightarrow$ *Bresenham* in-game)
- **Cycle Line Clipping**: `C` (*Cohen-Sutherland* $\leftrightarrow$ *Liang-Barsky* in-game)
- **Pause / Resume**: `P`
- **Field Guide & Theory**: `H`
- **Restart Level**: `R`
- **Start / Confirm**: `ENTER`
- **Return / Exit**: `ESC` (or `M` in CG Lab)

---

## 5. Main Execution Flow Summary

1. **Initialization**: `main.py` initializes Pygame, creates an $800 \times 600$ pixel window, instantiates the `Game` class, and starts `pygame.time.Clock()`.
2. **Title State**: The user sees the title screen with floating stardust, rotating crystal showcase, level selection, and dual buttons (`[ENTER] PLAY GAME` and `[L] CG LABORATORY`).
3. **Gameplay Startup**: Pressing `ENTER` calls `game.new_game()`, which loads Level 1 from `levels.py`, calculates start/exit positions, caches the minimap, and initializes action abilities.
4. **Game Loop (60 FPS)**:
   - **Event Polling**: Reads keyboard/mouse events and triggers actions (shooting, dash, shield, toggles).
   - **Physics & AI Update (`game.update`)**: Updates player velocity, runs stepped collision detection to slide along walls, discovers cells in fog of war, and runs enemy BFS pathfinding.
   - **Rendering (`game.draw`)**: Sets the torch clip window on `Renderer`, draws cells clipped to the light, draws entities via 3x3 homogeneous matrix transformations, and blits the HUD.
   - **Flip**: `pygame.display.flip()` presents the completed frame to the screen via double buffering.

---

## 6. Project Strengths, Limitations, and Future Work

### 5 Key Strengths
1. **Algorithmic Authenticity**: Implements core computer graphics algorithms (Bresenham, DDA, Midpoint Circle, Cohen-Sutherland, Liang-Barsky, Matrix Transformations) from raw mathematical principles without high-level black-box graphics engines.
2. **Zero-Timer Philosophy**: Eliminates artificial time pressures, countdowns, and timers, replacing them with action-based mechanics (walking steps, pickups, wraith purges).
3. **Interactive Computer Graphics Lab**: Standalone educational laboratory mode demonstrating live algorithm calculations, discrete pixel grids, step-by-step tables, and 8-way symmetry color-coding.
4. **Intelligent Pathfinding AI**: Stalker wraiths utilize real-time Breadth-First Search over the maze corridor topology to hunt the player smoothly through corners.
5. **Robust Architecture & Verification**: Fully tested with a 16-test headless verification suite passing with 100% success.

### 5 Limitations
1. **CPU Software Rasterization**: Primitives are computed in Python software loops rather than being rendered on dedicated GPU shaders, keeping the game lightweight for 2D but unsuited for 3D polygonal geometry.
2. **Fixed Window Resolution**: Screen size is fixed at $800 \times 600$ pixels; no dynamic window scaling or multi-monitor fullscreen resolution switching is implemented.
3. **Absence of Sound Effects**: Visual feedback is rich (ripples, sparks, vignette flashes, text floaters), but there is no audio synthesizer or soundtrack.
4. **Discrete Grid Coordinate Snapping in CG Lab**: The CG Lab operates on a $24 \times 18$ grid for educational visual clarity, rather than high-density sub-pixel grids.
5. **Local Text File Storage**: High scores and achievements are stored locally in `best_score.txt` without cloud sync or online leaderboards.

### 5 Possible Future Improvements
1. **Hardware Acceleration**: Implement OpenGL/WebGL shaders using PyOpenGL or ModernGL to demonstrate vertex and fragment shaders.
2. **Dynamic 2D Raycasted Shadows**: Expand the current circular torch clipping window into raycasted 2D shadow casting using polygon edge intersection rays.
3. **A* Heuristic Pathfinding**: Enhance BFS enemy pathfinding with Manhattan distance heuristics ($f(n) = g(n) + h(n)$) to benchmark $A^*$ performance against BFS.
4. **Procedural Level Editor**: Add an interactive maze drawing tool where students can carve custom walls and place keys.
5. **3D Perspective Projection**: Transform the 2D maze into a 3D raycasting engine (like Wolfenstein 3D) using the same maze grid and matrix projection math.
