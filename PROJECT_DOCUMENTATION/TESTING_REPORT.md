# EmberVault: The Crystal Maze - Formal Testing & Verification Report

This report documents the rigorous verification process conducted on **EmberVault: The Crystal Maze**. All tests documented herein have been executed against the live Python source code and verified using both automated test harnesses and headless render capture verifications.

---

## 1. Testing Methodology

The verification suite evaluates three primary system tiers:
1. **Low-Level Mathematical Algorithms**: Pure numerical testing of rasterization (Bresenham, DDA, Midpoint Circle), 2D homogeneous matrix transformations, and geometric clipping against ground-truth mathematical coordinates.
2. **Game Simulation Physics & Logic**: Testing movement vector integration, stepped circle-versus-cell pushout collision detection, action-based recharge counters, damage absorption, and BFS grid pathfinding.
3. **State Machine & Rendering Pipeline**: Validating transition flows between Title, Gameplay, Pause, Level Clear, Victory, Game Over, and the standalone Computer Graphics Laboratory mode.

The testing harness is implemented in [test_game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/test_game.py), executed using Python 3.13.5 and Pygame 2.6.1 under a headless SDL dummy video driver (`SDL_VIDEODRIVER=dummy`) to guarantee reproducible, deterministic testing.

---

## 2. Comprehensive Test-Case Verification Matrix

| Test ID | System Feature | Preconditions | Execution Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| **TC-01** | Application Startup & Title Menu | Pygame initialized, default window size $800 \times 600$ | Initialize `Game(screen)`, render title frame | State is `"title"`, 40 drifting stars initialized, crystal showcase and buttons rendered without text clipping | All title elements aligned, dual action buttons rendered cleanly | **PASSED** |
| **TC-02** | Title Level Selection & Cycling | Application in Title state | Press keys `1` to `5`, press `TAB` or arrow keys | `selected_level` updates from 0 to 4 and wraps cleanly on modulo arithmetic | Selection indices 0..4 update correctly and wrap cyclically | **PASSED** |
| **TC-03** | 5 Cavern Mazes & Geometry Integrity | `LEVEL_SETTINGS` loaded for indices 0 to 4 | Instantiate `Level(i)` for $i \in [0, 4]$, check start/exit coordinates and crystal placements | Starts and exits never spawn in walls (`grid == 0`), keys match count ($1..5$), Surge and Aegis crystals spawn in open cells | All 5 caverns generated without wall collisions on key entities | **PASSED** |
| **TC-04** | New Game Initialization & Zero-Timer State | Title state, Level 1 selected | Call `game.new_game()` | State transitions to `"play"`, lives set to 3, score to 0, dash charges to 2, shield charges $\ge 1$, zero countdown timers | Initialized with discrete action charges and empty timer values | **PASSED** |
| **TC-05** | Dynamic Fog of War & Discovery Grid | Game in `"play"` state at start chamber | Sample `discovered` grid at start, advance player forward, re-sample | Starting chamber cells marked `True`, unvisited distant cells marked `False`, visited corridors persist in `discovered` | Start chamber lit, discovered corridors persist across movement | **PASSED** |
| **TC-06** | Player Movement & Wall Pushout Collision | Player at open corridor coordinate | Update position with $v_x = 1.0$, push into solid wall for 50 frames with $v_x = -1.0$ | Player translates smoothly in open corridor; collision pushout stops player from penetrating solid wall cells | Player moved forward, then pushout prevented penetrating wall | **PASSED** |
| **TC-07** | Dash Ability & Walking Recharge | Player has 2 dash charges | Execute `game.dash(1.0, 0.0)`, exhaust charges, walk 35 paces | Dash bursts forward instantly leaving motion afterimages, charge drops to 0; walking 35 paces restores +1 charge without any timer | Dash triggered with ghost trails, charges exhausted and recharged via walking | **PASSED** |
| **TC-08** | Energy Shield Damage Absorption | Player has shield charge, lives = 3 | Call `game.toggle_shield()`, simulate enemy collision via `game._hit()` | Shield barrier activates; upon hit, shield breaks and absorbs strike completely, lives remain at 3 | Shield absorbed impact completely; lives remained at 3 | **PASSED** |
| **TC-09** | Crystal Power-Ups (Surge & Aegis) | Surge and Aegis crystals present in level | Move player over Cyan Surge crystal, then over Violet Aegis crystal | Surge awards +5 Tri-Shot charges & dash recharge; Aegis restores +1 lost life & engages Energy Shield barrier | Crystals picked up, status HUD updated, charges awarded accurately | **PASSED** |
| **TC-10** | Surge Tri-Shot Spread Arrows & Wraith Purge | Surge charges = 4, Wraith alive in chamber | Call `game.shoot()`, call `game._kill_bat(bat)` | 3 arrows spawned with angular offsets using 2D rotation matrix; bat shatters into purple/green debris (+150 PTS) | 3 spread arrows generated, wraith destroyed, +150 score added | **PASSED** |
| **TC-11** | Grid BFS Pathfinding & Enemy Navigation | Level generated, Stalker bat alive | Query `level.find_bfs_path(start, exit)`, execute `test_bat.update_ai(...)` | BFS finds shortest corridor sequence (all cells open); Stalker bat navigates along corridor waypoints toward player | Shortest path found; Stalker pursued along valid corridor without entering walls | **PASSED** |
| **TC-12** | Key Collection, Portal Unsealing & Level Clear | Level 1 active, 1 key uncollected | Collect all keys, walk onto exit portal cell | Exit portal unseals only after all keys collected; level transitions to `"levelclear"`; `UNTOUCHED` badge awarded if no damage | Portal unsealed, level clear triggered, flawless badge awarded | **PASSED** |
| **TC-13** | Coordinate Grid Overlay & Live CG Toggles | Game in `"play"` state | Press `G` (grid), `L` (line toggle), `C` (clip toggle) | Cartesian grid renders with coordinate marks; line toggles DDA $\leftrightarrow$ Bresenham; clip toggles Cohen-Sutherland $\leftrightarrow$ Liang-Barsky | Grid toggled cleanly; algorithms swapped dynamically at runtime | **PASSED** |
| **TC-14** | Pause Isolation & Score Persistence | Game in `"play"` state | Call `toggle_pause()`, update physics, write score, load score | Physics, timers, and movement freeze during pause; score saved and read from `best_score.txt` | Coordinates remained frozen during pause; high score persisted to disk | **PASSED** |
| **TC-15** | Interactive CG Lab Mode & Navigation | Main Title state active | Call `enter_cg_lab()`, cycle tabs 1..4, cycle presets (`P`), exit | State becomes `"cglab"`, tabs switch modes, presets update points, ESC returns to `"title"` | CG Lab entered, modes cycled, math panels rendered, exited to menu | **PASSED** |
| **TC-16** | Mathematical Algorithm Correctness | Standalone mathematical functions in `graphics.py` | Compute Bresenham line $(2,3)\to(8,7)$, DDA line, Midpoint circle $(r=5)$, Cohen-Sutherland clipping | Bresenham plots exact 7 integer pixels; DDA matches; circle points satisfy $|d - r| \le 1.0$; clipping computes exact trivial accept, trivial reject, and partial cuts | All 4 algorithms produced mathematically exact pixel/clipping coordinates | **PASSED** |

---

## 3. Detailed Results Analysis

### 3.1 Collision Pushout Robustness
The collision detection algorithm uses a continuous circle-versus-cell pushout approach in `Game._collide()`. Rather than a simple boolean flag that halts movement, it samples the 9 adjacent grid tiles surrounding the player, determines the closest point on each solid wall tile to the player's center, calculates the penetration depth $d = \sqrt{\Delta x^2 + \Delta y^2}$, and normalizes the displacement vector:

$$\vec{p}_{\text{corrected}} = \vec{p} + \frac{\Delta \vec{p}}{d} \cdot (R_{\text{player}} - d)$$

Because this correction is executed independently after both the horizontal ($v_x \cdot \Delta t$) and vertical ($v_y \cdot \Delta t$) movement steps, the player can smoothly slide along vertical or horizontal wall faces without snagging on cell corners. In Test TC-06, pushing the player into a corner wall for 50 continuous frames verified that the player coordinate never entered solid wall boundaries.

### 3.2 Zero-Timer Ability Verification
In compliance with the project specifications, no timer-based cooldowns or durations govern the new abilities:
- **Dash**: The dash count decreases upon activation and only recharges when the step counter `dash_step_counter` increments to 35 steps taken through player movement.
- **Energy Shield**: The shield does not wear off after a fixed number of seconds. It remains active indefinitely until an impact occurs, absorbing the blow and breaking upon contact.
- **Crystal Surge**: Grants exactly 5 discrete shots of 3-way Tri-Shot arrows rather than a temporary time window.

### 3.3 Enemy AI Pathfinding Verification
In Test TC-11, the Breadth-First Search algorithm `Level.find_bfs_path()` was tested between the level start chamber and the exit portal. The generated path was iterated through to verify that every coordinate $(r, c)$ in the returned sequence satisfied `Level.grid[r][c] == 0`. The test confirmed that Stalker wraiths follow this path step-by-step rather than walking through diagonal or solid block barriers.

---

## 4. Known Edge Cases and Limitations

1. **Sub-Pixel Rounding on Extreme Clipping Angles**:
   - In `graphics.cohen_sutherland()`, when a line segment is almost horizontal or vertical, the division $\frac{\Delta x}{\Delta y}$ or $\frac{\Delta y}{\Delta x}$ involves floating-point arithmetic before rounding to integer pixel coordinates. In rare situations with slopes $|\Delta y| < 10^{-6}$, floating-point epsilon is used to prevent zero-division errors (`dx != 0`).
2. **Minimap Scale Resolution**:
   - The Vault Radar minimap renders cells at $5 \times 5$ pixels. On high-resolution displays, the minimap remains fixed at $95 \times 75$ pixels in the upper-right corner. This is intentional to ensure zero performance degradation on standard hardware.
3. **Audio Output**:
   - The project does not include audio sound effects or music files (`.wav` / `.ogg`), maintaining lightweight portability and eliminating audio driver dependencies across different platforms. Visual feedback (flashes, floating text, ripples, particles) provides clear state indications.

---

## 5. Verification Sign-Off

- **Total Test Cases Executed**: 16
- **Passed**: 16 (100%)
- **Failed**: 0 (0%)
- **Exit Code**: `0` (Success)
- **Automated Test Script**: [test_game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/test_game.py)
