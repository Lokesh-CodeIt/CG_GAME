# EmberVault: The Crystal Maze - Comprehensive Viva Preparation Guide

*A complete, student-friendly guide designed to help you confidently understand the project, explain your code, and ace your Computer Graphics viva examination.*

---

## Part A: 2-Minute Project Introduction

*(Memorize this natural explanation to give when your professor says: "Tell me about your project.")*

> "Good morning/afternoon, Professor. My project is titled **EmberVault: The Crystal Maze**. It is a 2D computer graphics cave-exploration maze game and an interactive academic graphics laboratory built from scratch in Python using Pygame for pixel display and event polling.
>
> What makes this project unique as a Computer Graphics submission is that **I did not use high-level game engines or pre-built rendering functions** for game objects. Instead, every visual element you see—from the cave wall edges to the torch light and character sprites—is calculated mathematically from fundamental algorithms:
>
> 1. We implemented **Bresenham's and DDA Line Algorithms** for rasterizing wall boundaries.
> 2. We implemented the **Midpoint Circle Algorithm** for outer key halos, light rings, and filled scanline discs.
> 3. We implemented **Cohen-Sutherland and Liang-Barsky Line Clipping** to dynamically clip maze wall lines against the player's moving rectangular torch light window.
> 4. We implemented **2D Homogeneous Matrix Transformations** ($3 \times 3$ matrices) for composite translation, rotation, scaling, reflection, and shear.
>
> Gameplay features 5 progressively challenging procedural caverns, circle-versus-wall pushout collision detection, dynamic fog of war, and intelligent enemy wraiths using Breadth-First Search (BFS) corridor pathfinding.
>
> In addition, we built an interactive **Computer Graphics Laboratory mode** directly into the game menu, allowing you to interactively test Bresenham, DDA, Midpoint Circle 8-way symmetry, and Cohen-Sutherland 4-bit region outcodes with live coordinate calculations.
>
> The entire game follows a strict **zero-timer design**, where abilities like the directional dash and energy shield recharge through player actions rather than artificial countdowns. All 16 automated verification test cases pass with a 100% success rate."

---

## Part B: 30-Second Elevator Pitch

*(Use this when the examiner wants a very quick summary: "In 30 seconds, what have you done?")*

> "**EmberVault** is a 2D cave exploration game and interactive Computer Graphics laboratory built from scratch in Python and Pygame. Instead of using pre-built graphics APIs, we implemented core CG algorithms from mathematical scratch: **Bresenham and DDA Line Drawing**, **Midpoint Circle Drawing**, **Cohen-Sutherland Line Clipping**, **2D $3 \times 3$ Affine Matrix Transformations**, and **BFS Grid Pathfinding**. The torch acts as an active clipping window revealing the maze. It includes 5 levels, intelligent AI, action-based abilities, and a dedicated CG Lab mode demonstrating the algorithms interactively."

---

## Part C: Complete Game Explanation (Step-by-Step)

Here is how the game works from the moment you open it to completing a level:

1. **Launch**: You run `python main.py`. An $800 \times 600$ window opens showing a deep navy title screen with drifting stardust particles and a spinning crystal diamond showcase.
2. **Title Options**: You can select Level 1 to 5 using keys `1-5` or `TAB`, press `L` to open the Computer Graphics Laboratory, or press `ENTER` to play.
3. **Entering the Cavern**: Pressing `ENTER` spawns the player at a runic teleport shrine in the cavern's starting chamber.
4. **Torch & Fog of War**: The cave is dark. The player's crystal torch casts a radiant cyan light. The torch acts as a rectangular clipping window—geometry outside is clipped away. Corridors you explore remain recorded in a persistent discovery grid so you don't get lost.
5. **Moving & Colliding**: You navigate using `WASD` or Arrow keys. Circle-versus-cell pushout collision detection prevents you from walking into walls and lets you slide smoothly along corridor faces.
6. **Enemies**: Shadow Wraiths with purple bodies and neon-green wings inhabit the cave. In higher levels, Stalker Wraiths use Breadth-First Search (BFS) pathfinding to pursue you along corridors.
7. **Shooting**: Pressing `SPACE` fires crystal arrows. Arrows hit and destroy wraiths (+150 pts), shattering them into neon-green and purple shards.
8. **Action Abilities**:
   - **Dash (`LSHIFT` / `X`)**: Bursts the player forward instantly. Recharges after taking 35 walking steps.
   - **Energy Shield (`E`)**: Deploys a rotating hexagonal shield that absorbs an enemy hit completely without losing a life.
   - **Cyan Surge Crystal**: Grants 5 shots of 3-way spread arrows (Tri-Shot) using 2D rotation matrices.
   - **Violet Aegis Crystal**: Restores 1 lost life and recharges your shield.
9. **Objective**: Find all spinning amber vault keys scattered in the cavern. Once all keys are collected, the exit portal unseals.
10. **Level Completion**: Walking into the portal completes the level (+500 pts). If you took no damage, you earn an extra +300 pts and the `UNTOUCHED` badge. Completing all 5 levels conquers EmberVault with the `CHAMPION` badge!

---

## Part D: Technical Concepts in Simple Language

- **Rasterization**: Turning a mathematical formula (like $y = mx + c$) into real square colored pixels on a screen grid.
- **Why Bresenham is faster than DDA**: DDA uses floating-point division (`dx / steps`) and rounds numbers on every step. Bresenham uses only integer additions and subtractions with a decision variable ($p_k$), making it faster and free of floating-point inaccuracies.
- **Clipping**: Determining which parts of a shape fall inside a visible window and throwing away the parts outside.
- **Cohen-Sutherland Outcodes**: Dividing the 2D plane into 9 zones using 4 binary bits: Top, Bottom, Right, Left. If both endpoints have code `0000`, the line is completely inside. If the bitwise AND (`c0 & c1`) is not zero, the line is completely outside.
- **Homogeneous Coordinates**: Adding a 3rd dimension ($z = 1$) to 2D points: $[x, y, 1]^T$. This allows translation (addition) to be multiplied as a matrix, meaning we can combine Translation, Rotation, and Scaling into one single $3 \times 3$ matrix.
- **Double Buffering**: Having two screens in memory. The computer draws everything on the invisible "back buffer." Once the frame is finished, it instantly swaps it with the visible "front buffer." This prevents flickering and screen tearing.

---

## Part E: 68 Viva Questions & Answers

### Category 1: Basic Project Introduction and Objectives
**Q1: What is the title and objective of your project?**
> **A:** The project is titled *EmberVault: The Crystal Maze*. The objective is to build a 2D cave-exploration game and an academic graphics laboratory demonstrating core Computer Graphics algorithms (line drawing, circle generation, line clipping, 2D matrix transformations, and pathfinding) implemented from scratch.

**Q2: What problem does this project solve?**
> **A:** Most student game projects rely on high-level black-box engines (like Unity or Unreal) where computer graphics algorithms are hidden. This project implements rasterization, clipping, and geometric transformations from fundamental mathematics to demonstrate how computer graphics actually works under the hood.

**Q3: What are the main features of your game?**
> **A:** 5 procedural cavern levels, dynamic fog of war, torch illumination clipping, circle-versus-cell pushout collision detection, arrow shooting, action-based abilities (dash, energy shield, tri-shot), BFS enemy pathfinding, local high-score persistence, and an interactive Computer Graphics Lab.

**Q4: Who are the intended users of this application?**
> **A:** Computer science and engineering students, educators, and viva examiners studying or demonstrating 2D computer graphics algorithms, affine transformations, and rasterization mathematics.

**Q5: What is the significance of the "Zero-Timer Design"?**
> **A:** In traditional games, abilities use artificial countdown clocks. In EmberVault, all abilities and recharges are tied to discrete gameplay actions (walking 35 steps recharges dash, picking up Aegis crystals restores shield), making the mechanics deterministic and skill-focused.

**Q6: What is the Computer Graphics Lab mode?**
> **A:** It is a standalone mode accessed from the title menu (`L` key) where students can interactively test Bresenham's line, DDA line, Midpoint Circle 8-way symmetry, and Cohen-Sutherland clipping on a live coordinate grid.

---

### Category 2: Programming Language and Technologies
**Q7: Which programming language is used and why?**
> **A:** Python 3 (3.10+). Python was chosen for its clean syntax, readability, strong mathematical support, and rapid prototyping capabilities.

**Q8: What is Pygame's role in this project?**
> **A:** Pygame is used strictly as a lightweight wrapper for opening the OS window, capturing keyboard/mouse events, and drawing raw pixels or 1-pixel scanline spans (`Surface.fill`). We did not use Pygame's built-in vector collision or geometry drawing modules for game entities.

**Q9: Did you use any external game engines or frameworks?**
> **A:** No. No engines like Unity, Godot, or Unreal, and no external physics or rendering engines were used.

**Q10: How are high scores saved?**
> **A:** Locally in a text file named `best_score.txt` using standard Python file I/O with automatic fallback to in-memory tracking if file permissions fail.

**Q11: What dependencies are required to run the project?**
> **A:** Only Python and the `pygame` library (`pip install pygame`).

---

### Category 3: Computer Graphics Fundamentals
**Q12: What is the difference between raster graphics and vector graphics?**
> **A:** Vector graphics represent shapes using mathematical equations (points, lines, curves). Raster graphics represent images as a 2D grid of discrete color pixels. Our project converts mathematical vector models into raster pixels on screen.

**Q13: What is the screen resolution and coordinate system used?**
> **A:** The window is $800 \times 600$ pixels. The coordinate system places the origin $(0, 0)$ at the top-left corner, with the X-axis increasing to the right and the Y-axis increasing downward.

**Q14: What is double buffering and why is it necessary?**
> **A:** Double buffering uses an off-screen surface to compose the entire scene before presenting it to the monitor in a single step using `pygame.display.flip()`. This prevents visual tearing and screen flickering.

**Q15: What is scanline polygon filling?**
> **A:** It is an algorithm that draws solid polygons by scanning horizontal rows of pixels, calculating intersection coordinates with polygon edges, sorting them left-to-right, and drawing spans between odd-even pairs of intersections.

**Q16: How do you achieve color gradients without shaders?**
> **A:** By computing linear interpolation between color tuples based on radius or normalized distance: `color = start * (1 - p) + end * p`.

**Q17: What is frame rate independent movement?**
> **A:** Updating physics positions using delta time: $\text{position} += \text{velocity} \times \Delta t$, ensuring movement speed remains constant regardless of whether the computer runs at 30 FPS or 60 FPS.

---

### Category 4: Actual Graphics Algorithms Implemented
**Q18: How does the DDA line algorithm work?**
> **A:** DDA calculates $\Delta x$ and $\Delta y$, determines the number of steps as $\max(|\Delta x|, |\Delta y|)$, computes floating-point increments $x_{\text{inc}} = \Delta x/\text{steps}$ and $y_{\text{inc}} = \Delta y/\text{steps}$, and rounds $(x, y)$ to the nearest integer pixel at each step.

**Q19: How does Bresenham's line algorithm work?**
> **A:** Bresenham's algorithm uses an integer decision parameter $p_k$. For shallow slopes ($|\Delta x| > |\Delta y|$), $p_0 = 2\Delta y - \Delta x$. If $p_k < 0$, it selects the Eastern pixel $(x+1, y)$ and adds $2\Delta y$; if $p_k \ge 0$, it selects the North-Eastern pixel $(x+1, y+1)$ and adds $2(\Delta y - \Delta x)$.

**Q20: Why is Bresenham preferred over DDA in production systems?**
> **A:** Bresenham uses exclusively integer additions, subtractions, and bit-shifts ($2\Delta y = \Delta y \ll 1$). DDA requires floating-point division and rounding operations, which are computationally more expensive and subject to cumulative precision errors.

**Q21: How does the Midpoint Circle algorithm work?**
> **A:** It evaluates the circle equation $f(x, y) = x^2 + y^2 - r^2$ at the midpoint between candidate pixels. Starting at $(0, r)$ with initial decision parameter $p_0 = 1 - r$, if $p_k < 0$, it picks Eastern pixel $(x+1, y)$ and increments $p$ by $2x + 1$; if $p_k \ge 0$, it picks South-Eastern pixel $(x+1, y-1)$ and increments $p$ by $2(x - y) + 1$.

**Q22: What is 8-way symmetry in circle generation?**
> **A:** A circle has 8-fold reflective symmetry across the axes and diagonals. The Midpoint algorithm calculates pixels for only one octant ($0 \le x \le y$), and simply mirrors coordinates to generate the remaining 7 octants: $(\pm x, \pm y)$ and $(\pm y, \pm x)$.

**Q23: How does Cohen-Sutherland line clipping work?**
> **A:** It divides 2D space into 9 regions using 4-bit codes: $[T, B, R, L]$. It evaluates endpoints:
> - If $c_0 \mid c_1 == 0$: Trivial Accept (line is completely inside).
> - If $c_0 \ \& \ c_1 \ne 0$: Trivial Reject (both points are outside on the same side).
> - Otherwise, it finds the intersection with the window boundary and re-tests.

**Q24: How does Liang-Barsky clipping differ from Cohen-Sutherland?**
> **A:** Cohen-Sutherland uses repeated geometric edge intersections in Cartesian space. Liang-Barsky uses a parametric line formulation ($x = x_0 + u \Delta x$) and tests 4 inequalities ($u \cdot p_k \le q_k$) to find clipping parameters $u_1, u_2 \in [0, 1]$, making it computationally faster with fewer divisions.

**Q25: Where is line clipping used in the actual game?**
> **A:** In `graphics.py:Renderer.set_window()`. Every wall line segment in the cavern is clipped against the rectangular bounding box of the player's torch light before rasterization.

**Q26: Can you switch between clipping algorithms while playing?**
> **A:** Yes! Pressing the `C` key toggles the active clipping algorithm between Cohen-Sutherland and Liang-Barsky in real time.

**Q27: Can you switch line drawing algorithms during gameplay?**
> **A:** Yes! Pressing the `L` key toggles between Bresenham's algorithm and the DDA algorithm in real time.

---

### Category 5: Game Loop and Rendering
**Q28: What is a game loop?**
> **A:** A continuous loop that runs every frame, consisting of three core steps: (1) Process Inputs, (2) Update Game State and Physics, and (3) Render Graphics to the Screen.

**Q29: How does your game enforce a smooth 60 FPS?**
> **A:** Using `clock = pygame.time.Clock()` and `dt = min(clock.tick(60) / 1000.0, 0.05)`. This caps execution to 60 frames per second and clamps delta time to prevent physics tunneling on lag spikes.

**Q30: What happens in `game.update(dt)`?**
> **A:** Player positions are updated by velocity, collision pushout is applied, fog of war updates the discovered grid, bat AI executes pathfinding, arrows move forward, and particle lifespans are updated.

**Q31: What happens in `game.draw()`?**
> **A:** The screen is cleared with the dark navy background, the torch window is set on the renderer, visible cells and wall bevels are clipped and drawn, characters and items are drawn via affine matrix transforms, and the HUD is overlaid.

**Q32: How is pausing implemented?**
> **A:** When `state == "pause"`, `game.update()` returns early, skipping physics, timers, and AI movement, while `game.draw()` continues rendering the frozen scene with a semi-transparent pause card.

**Q33: How does the Cartesian grid overlay (`G` key) work?**
> **A:** When enabled, it draws coordinate grid lines clipped to the torch window and renders $(x, y)$ coordinate labels on cell intersections.

---

### Category 6: Coordinate Systems and Drawing
**Q34: How are 2D homogeneous matrices structured?**
> **A:** Points are represented as 3-element column vectors $[x, y, 1]^T$. Transformations are $3 \times 3$ matrices:
> $$\text{Translate} = \begin{bmatrix} 1 & 0 & tx \\ 0 & 1 & ty \\ 0 & 0 & 1 \end{bmatrix}, \quad \text{Rotate} = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}, \quad \text{Scale} = \begin{bmatrix} sx & 0 & 0 \\ 0 & sy & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**Q35: What is matrix composition and why is it useful?**
> **A:** Matrix composition multiplies multiple transformation matrices together: $\mathbf{M} = \mathbf{T} \times \mathbf{R} \times \mathbf{S}$. This allows translation, rotation, and scaling to be combined into a single matrix, transforming hundreds of points with a single matrix multiplication.

**Q36: How does the player character rotate to face movement?**
> **A:** `self.angle = math.atan2(vy, vx)`. In rendering, `matrix.rotate(self.angle)` rotates the arrow sprite around the player's center.

**Q37: How is the torch flame animated?**
> **A:** Using `matrix.shear(kx, ky)` with a sinusoidal parameter $\sin(t \times 12)$, which shears the flame geometry sideways to produce an organic flickering effect.

**Q38: How are bat wings animated?**
> **A:** Using `matrix.scale(1.0, math.sin(t * 14))`, which rapidly scales the wing polygons along the Y-axis to simulate flapping.

---

### Category 7: Movement and Collision Detection
**Q39: How does the game detect wall collisions?**
> **A:** Using circle-versus-cell pushout collision detection in `Game._collide()`. The player is modeled as a bounding circle of radius $R = 8$. The game samples the 9 adjacent grid tiles around the player.

**Q40: How does the pushout algorithm prevent getting stuck in walls?**
> **A:** For any solid wall tile, it finds the closest point $(nx, ny)$ on the tile boundary to the player center $(px, py)$. If distance $d < R$, it displaces the player along the normal vector by the penetration depth $(R - d)$.

**Q41: Why does movement update the X and Y axes separately?**
> **A:** We update $px += vx \cdot dt$ and collide, then update $py += vy \cdot dt$ and collide. This axis separation allows wall sliding—if you run diagonally into a horizontal wall, horizontal motion continues while vertical motion is absorbed.

**Q42: How does the Dash ability prevent dashing through walls?**
> **A:** The dash is divided into 4 discrete sub-steps of 12 pixels each. After each sub-step, `Game._collide()` is executed. If a wall is hit, the player immediately stops at the wall surface.

**Q43: What is the radius of the player's bounding circle?**
> **A:** `PLAYER_R = 8` pixels.

**Q44: How are arrow projectile collisions detected?**
> **A:** The arrow tip coordinate $(tx, ty)$ is checked against `Level.is_wall()`. If it hits a wall, the arrow is deleted with impact sparks. If the distance to a bat is less than 18 pixels, the bat is killed.

---

### Category 8: Enemy Behavior and Pathfinding
**Q45: What types of enemies exist in the game?**
> **A:** Shadow Wraiths with two distinct AI behaviors: (1) **Scouts**, which patrol corridors and chase when close, and (2) **Stalkers**, which actively hunt the player across the maze using BFS.

**Q46: What algorithm is used for Stalker pathfinding?**
> **A:** Breadth-First Search (BFS) over the cavern maze grid.

**Q47: Why is BFS guaranteed to find the shortest path?**
> **A:** Because all grid corridor steps have an equal edge weight of 1. BFS explores nodes in order of increasing distance from the start node, guaranteeing that the first time the target node is visited, it has traveled the minimal number of steps.

**Q48: How does the Stalker follow the BFS path?**
> **A:** The BFS returns a list of grid cells $[(r_0, c_0), (r_1, c_1), \dots]$. The wraith sets its velocity towards the center of waypoint $(r_1, c_1)$. When distance is less than 4 pixels, it pops that waypoint and aims for the next.

**Q49: What happens when an enemy is defeated?**
> **A:** The wraith dies, grants +150 points, shatters into 9 spinning purple and neon-green debris shards, and respawns at its home chamber after 10 seconds.

---

### Category 9: Gameplay Mechanics and Zero-Timer Design
**Q50: How does the Energy Shield work?**
> **A:** Pressing `E` engages a rotating hexagonal energy barrier with orbiting runes. When hit by an enemy, the shield breaks and absorbs the damage completely; your lives do not decrease.

**Q51: How does the shield recharge without a timer?**
> **A:** Through gameplay actions: collecting a Violet Aegis crystal, or purging 2 Shadow Wraiths awards +1 shield charge.

**Q52: How does the Dash ability recharge without a timer?**
> **A:** Through walking steps: every 35 paces the player takes through the cavern recharges 1 dash charge (up to 3 max).

**Q53: What does the Cyan Surge crystal do?**
> **A:** It grants 5 charges of **Tri-Shot Spread Arrows** (fires 3 arrows in a $30^\circ$ fan using 2D rotation matrices) and recharges 1 dash charge.

**Q54: What does the Violet Aegis crystal do?**
> **A:** It restores 1 lost life (up to 3 max) and engages the Energy Shield.

---

### Category 10: Code Structure and Implementation
**Q55: What is the purpose of `levels.py`?**
> **A:** It procedural generates the 5 caverns using seeded DFS maze carving, knocks out walls to create loops, places keys and exits, and implements BFS pathfinding and enemy AI.

**Q56: What is the purpose of `cg_lab.py`?**
> **A:** It houses the interactive Computer Graphics Laboratory class `CGLab`, rendering pixel grids, interactive endpoints, step tables, and theory panels for Bresenham, DDA, Midpoint Circle, and Cohen-Sutherland algorithms.

**Q57: What is the purpose of `matrix.py`?**
> **A:** It provides $3 \times 3$ homogeneous affine transformation functions (`translate`, `rotate`, `scale`, `shear`, `reflect_y`, `compose`, `apply`).

**Q58: How is the dynamic Fog of War represented in memory?**
> **A:** As a 2D boolean grid `self.discovered = [[False] * COLS for _ in range(ROWS)]`. Cells within the player's torch radius are set to `True`.

**Q59: How does `Renderer.fade` create lighting falloff?**
> **A:** It calculates the Euclidean distance from the torch center to a primitive. If distance exceeds the torch radius, intensity decreases quadratically: $\text{factor} = 1 - (d / \text{radius})^2$, tinting the color toward dark navy.

---

### Category 11: Testing and Debugging
**Q60: How was the project tested?**
> **A:** Using an automated test suite [test_game.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/test_game.py) containing 16 unit and integration test cases covering math, physics, abilities, pathfinding, and graphics modes.

**Q61: How can tests run without opening a physical display window?**
> **A:** By setting the environment variable `os.environ["SDL_VIDEODRIVER"] = "dummy"`, which directs Pygame to use a headless memory surface without opening an OS desktop window.

**Q62: Did all 16 test cases pass?**
> **A:** Yes, all 16 automated tests passed with exit code 0.

**Q63: How were visual aesthetics verified?**
> **A:** Using [capture_enhancements.py](file:///C:/Users/NILESH%20MARATHE/.gemini/antigravity-ide/scratch/DarkCaveExplorer/capture_enhancements.py) to render and save PNG images of the title screen, in-game abilities, and all CG Lab modes.

---

### Category 12: Limitations and Future Improvements
**Q64: What is the main computational limitation of the project?**
> **A:** All rasterization (Bresenham, DDA, Midpoint Circle, scanline spans) is executed in Python software loops on the CPU rather than GPU shaders.

**Q65: Why is the screen resolution fixed at $800 \times 600$?**
> **A:** A fixed resolution simplifies the coordinate math for the maze grid and ensures consistent performance across student laptops and lab machines.

**Q66: How could pathfinding be improved beyond BFS?**
> **A:** By implementing the $A^*$ (A-Star) algorithm with a Manhattan distance heuristic ($h = |\Delta r| + |\Delta c|$), which reduces the number of evaluated nodes in larger open spaces.

**Q67: How could the lighting model be extended?**
> **A:** By replacing the circular clipping window with 2D raycasting to compute realistic hard and soft shadows cast by wall corners.

**Q68: What would you do if given another month on this project?**
> **A:** Add audio sound synthesis for crystal chimes, implement GPU-accelerated shaders with PyOpenGL, and convert the maze into a 3D raycaster view like Wolfenstein 3D.

---

## Part F: Tricky Viva Questions (With Honest Professor Responses)

#### Tricky Question 1: "Why did you build this in Pygame instead of a standard graphics API like OpenGL or DirectX?"
> **Model Answer:** "Great question, Professor. Modern APIs like OpenGL and DirectX are hardware-accelerated and hide low-level rasterization inside GPU hardware. The syllabus for our Computer Graphics course focuses on the mathematical foundations—how lines, circles, and clipping are actually calculated at the pixel level. By using Pygame strictly for its pixel buffer, we were able to write Bresenham's, DDA, Midpoint Circle, and Cohen-Sutherland algorithms by hand in code, which directly demonstrates the academic syllabus."

#### Tricky Question 2: "Is your maze randomly generated every time, or are levels fixed?"
> **Model Answer:** "It uses procedural generation with a fixed pseudorandom seed for each level (Seed 101 for Level 1, 202 for Level 2, etc.). This gives the best of both worlds: the maze is generated procedurally using depth-first search, but because the seed is fixed, the level layout is deterministic and repeatable for testing and grading."

#### Tricky Question 3: "Cohen-Sutherland algorithm clips lines. Why didn't you use it for the enemies or player?"
> **Model Answer:** "Because Cohen-Sutherland is specifically designed for 1D line segments against a rectangular window. The player and enemies are 2D polygonal and circular entities. For those, we clip their center coordinates or use bounding box tests, and render their shapes using scanline polygon fills and midpoint circle spans."

#### Tricky Question 4: "What part of this project did you implement yourself?"
> **Model Answer:** "We started with a foundational 2D cave concept and completely enhanced the rendering pipeline and game mechanics: we wrote the interactive Computer Graphics Lab with real-time algorithm tables and 8-way color-coded octants, implemented the action-based abilities (dash, energy shield, tri-shot), upgraded enemy AI with BFS corridor pathfinding, implemented dynamic fog of war, redesigned the visual theme to deep navy/cyan, and wrote the complete automated verification test suite."

---

## Part G: Mock Viva Simulation (20 Questions with Follow-Ups)

1. **Examiner:** "Walk me through how a line is drawn on screen when I look at a cave wall."
   - *Student:* "When a wall is drawn, `Level` provides its endpoints. First, `Renderer` passes those endpoints through the Cohen-Sutherland clipping algorithm against the player's torch window. If accepted, the clipped line is passed to `bresenham_line()`, which generates integer pixel coordinates $(x, y)$ that are written to the screen surface."
   - *Follow-Up:* "What happens if the wall is outside the torch light?"
   - *Student:* "Cohen-Sutherland calculates the 4-bit region outcodes for both endpoints. If they share an outside region (`c0 & c1 != 0`), it is trivially rejected and zero pixels are plotted."

2. **Examiner:** "Why does your midpoint circle algorithm only calculate one octant?"
   - *Student:* "Because a circle has 8-fold reflective symmetry across $x=0$, $y=0$, and the lines $y = \pm x$. Calculating $x \le y$ for Octant 1 and reflecting coordinates to the other 7 octants reduces the number of operations by a factor of 8."
   - *Follow-Up:* "Show me where this symmetry is displayed in your project."
   - *Student:* "In our Computer Graphics Lab under Mode 3 (Circle), each of the 8 symmetric octants is rendered in a distinct color on the pixel grid."

3. **Examiner:** "How do homogeneous coordinates make 2D transformations easier?"
   - *Student:* "In standard 2D coordinates, rotation and scaling are matrix multiplications, but translation is vector addition. By adding a dummy coordinate $w=1$, translation becomes a $3 \times 3$ matrix multiplication, allowing all transformations to be multiplied together into one composite matrix."
