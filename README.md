# EmberVault: The Crystal Maze  -  Computer Graphics Mini-Project (Python + Pygame)

A 2D computer graphics cave-exploration maze game and academic graphics laboratory built from scratch using foundational rasterization, 2D homogeneous matrix transformations, and clipping algorithms.

---

## Quick Start

### Prerequisites
Python 3.10+ and `pygame`:
```bash
pip install pygame
```

### Run the Game
```bash
python main.py
```

### Run the Automated Verification Suite
```bash
python test_game.py
```

---

## Controls Reference

| Action | Primary Key | Secondary Key | Context |
|---|---|---|---|
| **Move Explorer** | `W`, `A`, `S`, `D` | `Up`, `Left`, `Down`, `Right` | In-Game |
| **Shoot Crystal Arrow** | `SPACE` | `F` | In-Game |
| **Dash Ability** | `LSHIFT` | `X` | In-Game |
| **Energy Shield Barrier** | `E` | - | In-Game |
| **Enter CG Laboratory** | `L` | Mouse Click `[L] CG LABORATORY` | Title Menu |
| **Select Level (1 - 5)** | `1`, `2`, `3`, `4`, `5` | `TAB` / `Arrow Keys` | Title Menu |
| **Start Game / Confirm** | `ENTER` | Mouse Click `[ENTER] PLAY GAME` | Title / Overlays |
| **Toggle Cartesian Grid** | `G` | - | In-Game |
| **Pause / Resume** | `P` | - | In-Game |
| **Field Guide & Theory** | `H` | - | In-Game / Title |
| **Cycle Line Algorithm** | `L` | (*DDA* $\leftrightarrow$ *Bresenham*) | In-Game |
| **Cycle Line Clipping** | `C` | (*Cohen-Sutherland* $\leftrightarrow$ *Liang-Barsky*) | In-Game |
| **Restart Level** | `R` | - | In-Game |
| **Exit / Return / Quit** | `ESC` | `M` (CG Lab only) | Everywhere |

---

## Visual & Aesthetic Enhancements

1. **Futuristic Cave Atmosphere**: Deep midnight navy-black base (`#080c14`, `#0e1420`) with cool steel-cyan bevels and luminous electric cyan wall boundaries (`#00dcf5`). Zero brown or muddy yellow tints.
2. **Dynamic Flashlight & Fog of War**:
   - Radiant electric cyan/blue gradient torch glow around the player (`#00e1ff` to `#0037af`).
   - Real-time persistent discovery grid: explored chambers and corridors remain softly visible with subtle ghosting when distant from the torch light.
   - Nearby walls, crystals, keys, and enemies remain clearly visible.
3. **Redesigned Shadow Wraiths**:
   - Distinctive purple carapace (`#6e23af`) and neon-green plasma wings/antennae (`#39ff14`).
   - Shaders, damage vignette flash, and particle bursts upon defeat.
4. **Distinctive Crystal Collectibles**:
   - **Vault Keys**: Spinning multifaceted amber-gold gems with radiant golden halo rings (`#ffcd2d`).
   - **Cyan Surge Crystals**: Electric cyan shards granting **Tri-Shot spread arrows** and dash charges.
   - **Violet Aegis Crystals**: Deep violet crystals providing an **Energy Shield barrier** and restoring life.
5. **Polished Minimap (Vault Radar)**:
   - Live radar in the upper right displaying discovered corridors, crystals, keys, and the player.
6. **Clean Title Screen & Overlays**:
   - Aligned dual action buttons: `[ ENTER ] PLAY GAME` and `[ L ] CG LABORATORY`.
   - Crystal showcase with rotating wireframe diamonds.
   - Local high-score record badge (`best_score.txt`).

---

## Gameplay Enhancements (Zero-Timer Design)

> **Important**: In strict adherence to design requirements, EmberVault contains **zero countdown timers, time limits, or timed challenges**. All ability activations, durations, and recharges are entirely **action- and charge-based**.

1. **Energy Shield (`E`)**:
   - Deploys a rotating hexagonal energy barrier with orbiting runic particles.
   - Completely absorbs lethal damage from a Shadow Wraith without losing a life.
   - Recharged through gameplay actions: picking up Violet Aegis crystals, unsealing keys, or purging wraiths.
2. **Directional Dash (`LSHIFT` / `X`)**:
   - Instantly bursts the player forward in the movement direction with motion-trail afterimages.
   - Full stepped collision detection prevents dashing through solid cave walls.
   - Recharged by gameplay action: walking 35 paces through the cavern recharges 1 dash charge.
3. **Crystal Power-Ups**:
   - **Cyan Surge**: Awards 5 charges of **Tri-Shot Spread Arrows** (fires 3 arrows in a $30^\circ$ fan using 2D rotation matrices) and replenishes dash charges.
   - **Violet Aegis**: Restores 1 lost life and activates the Energy Shield barrier.
4. **Intelligent Enemy AI**:
   - **Corridor Breadth-First Search (BFS)**: Stalker wraiths navigate along valid grid corridors directly toward the player.
   - **Patrol & Chase**: Scout wraiths patrol corridors and intelligently switch to pursuit when the player enters their sector.
5. **Score & Badges**:
   - Action rewards for collecting keys (+250), purging wraiths (+150), and unsealing portals (+500).
   - Flawless completion awards bonus points and badges:
     - `UNTOUCHED`: Complete a cavern without taking any damage.
     - `PURGER`: Defeat 3 or more Shadow Wraiths in a single cavern.
     - `CHAMPION`: Conquer all 5 caverns of the Crystal Sanctum.
   - High scores are saved to `best_score.txt`.

---

## Interactive Computer Graphics Laboratory Mode

A dedicated, standalone academic demonstration environment accessible directly from the main menu (`[ L ] CG LABORATORY`). It demonstrates real-time computer graphics algorithms interactively with live parameter adjustments and step-by-step mathematical theory panels:

1. **Bresenham's Line Algorithm**:
   - Integer-only incremental rasterization.
   - Displays plotted discrete pixel cells alongside continuous ideal vector line.
   - Live step-by-step table showing step $k$, coordinates $(x, y)$, and decision parameter $p_k$.
2. **DDA Line Algorithm (Digital Differential Analyzer)**:
   - Floating-point differential increment rasterization ($dx/\text{steps}$, $dy/\text{steps}$).
   - Displays real-time step calculations and float roundings.
3. **Midpoint Circle Algorithm**:
   - 8-way symmetry rasterization from a single octant.
   - Each of the 8 symmetric octants is rendered in a **distinct color** on the pixel grid.
   - Displays initial decision parameter $p_0 = 1 - r$ and Eastern ($E$) vs South-Eastern ($SE$) pixel decisions.
4. **Cohen-Sutherland Line Clipping**:
   - Interactive clipping rectangle and draggable endpoint segments.
   - Computes and displays 4-bit region outcodes ($\text{Top}, \text{Bottom}, \text{Right}, \text{Left}$).
   - Visualizes bitwise acceptance/rejection tests and boundary edge intersection points.

**CG Lab Controls**:
- `1`, `2`, `3`, `4`: Switch between Bresenham, DDA, Circle, and Clipping modes.
- `Left-Click & Drag`: Move endpoints, circle radius, or clipping lines on the grid.
- `P`: Cycle presets (steep slopes, horizontal, vertical, partial clip, full reject).
- `R`: Reset to default demonstration parameters.
- `ESC` / `M`: Return to EmberVault main menu.

---

## 5 Caverns Overview

| Level | Cavern Name | Starting Chamber | Torch Radius | Keys | Wraiths | Power-Ups |
|---|---|---|---|---|---|---|
| **1** | The Cobalt Gateway | Azure Archway `(1, 1)` | 155px | 1 | 1 Scout | Surge & Aegis |
| **2** | The Cyan Chasm | Cobalt Sanctuary `(13, 1)` | 125px | 2 | 2 Wraiths | Surge & Aegis |
| **3** | The Obsidian Labyrinth | Obsidian Outpost `(7, 1)` | 105px | 3 | 3 Wraiths (Stalker) | Surge & Aegis |
| **4** | The Abyssal Depths | Abyss Caldera `(1, 17)` | 92px | 4 | 4 Wraiths | Surge & Aegis |
| **5** | The Sanctum Core | Sanctum Nexus `(13, 17)` | 80px | 5 | 5 Wraiths (Elite) | Surge & Aegis |

---

## Where Each Computer Graphics Concept Is Implemented

| Computer Graphics Concept | Implementation in EmberVault | Primary Source File / Function |
|---|---|---|
| **Bresenham's Line Algorithm** | Wall boundaries, torch frame, CG Lab line demo | `graphics.py:bresenham_line`, `cg_lab.py` |
| **DDA Line Algorithm** | Alternate wall boundary mode (`L` toggle), CG Lab DDA demo | `graphics.py:dda_line`, `cg_lab.py` |
| **Midpoint Circle Algorithm** | Outer halos, ripple effects, CG Lab 8-way symmetry | `graphics.py:circle_points`, `cg_lab.py` |
| **Midpoint Circle Spans** | Torch gradient glow, player body, shield barrier, eyes | `graphics.py:circle_spans` |
| **Cohen-Sutherland Clipping** | Dynamic torch rectangular clipping window, CG Lab clipping demo | `graphics.py:cohen_sutherland`, `cg_lab.py` |
| **Liang-Barsky Clipping** | Alternate line clipping mode (`C` toggle) | `graphics.py:liang_barsky` |
| **Scan-Line Polygon Fill** | Player ship, wraith carapaces, crystals, portal star | `graphics.py:scanline_spans` |
| **2D Matrix Translation** | Player motion, wraith navigation, arrow flight, particles | `matrix.py:translate` |
| **2D Matrix Rotation** | Player aiming, Tri-Shot fan spread, portal star spin, shield runes | `matrix.py:rotate` |
| **2D Matrix Scaling** | Shield pulsation, wraith wing flaps, crystal gem heartbeat | `matrix.py:scale` |
| **2D Matrix Shear** | Wobbling plasma torch flare | `matrix.py:shear` |
| **2D Matrix Reflection** | Mirroring wraith sprites based on movement direction | `matrix.py:reflect_y` |
| **Composite Transformations** | Multi-matrix composition (`translate * rotate * scale`) | `matrix.py:compose`, `matrix.py:apply` |
| **Breadth-First Search (BFS)** | Grid corridor navigation for intelligent Stalker enemies | `levels.py:Level.find_bfs_path` |
| **Fog of War Persistent Visibility** | Grid discovery rasterization and torch illumination falloff | `game.py:Game._draw_cells` |
