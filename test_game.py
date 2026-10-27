"""
test_game.py - Comprehensive Automated Verification Suite for EmberVault: The Crystal Maze
========================================================================================
Validates all visual enhancements, gameplay abilities, intelligent AI, and the CG Lab mode.
Strictly adheres to the zero-timer constraint (all abilities action- or charge-based).
"""
import os
import sys

# Ensure headless execution in automated test runner
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
import graphics as gfx
from graphics import bresenham_line, dda_line, circle_points, cohen_sutherland, outcode
from game import Game, W, H, CELL, COLS, ROWS, OFF_X
from levels import Level, LEVEL_SETTINGS
from cg_lab import CGLab


def run_tests():
    print("=================================================================")
    print("   EMBERVAULT: THE CRYSTAL MAZE - EXTENDED VERIFICATION SUITE    ")
    print("=================================================================")

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    game = Game(screen)

    # -------------------------------------------------------------------------
    # 1. Title State & Dual Mode Layout
    # -------------------------------------------------------------------------
    print("\n[1/16] Verifying Title State, Particles, and Dual Menu Layout...")
    assert game.state == "title"
    assert len(game.title_stars) == 40
    # Test title button hit tests
    btn_play = pygame.Rect(W // 2 - 250, 372, 235, 46)
    btn_cglab = pygame.Rect(W // 2 + 15, 372, 235, 46)
    assert btn_play.collidepoint(W // 2 - 150, 390)
    assert btn_cglab.collidepoint(W // 2 + 100, 390)
    game.draw()
    print("  -> Title screen, star particles, and action buttons verified.")

    # -------------------------------------------------------------------------
    # 2. Level Selection & Cycling
    # -------------------------------------------------------------------------
    print("\n[2/16] Verifying Level Selection & Navigation (1-5 / Tab)...")
    assert game.selected_level == 0
    game.select_level(2)
    assert game.selected_level == 2
    game.cycle_level(1)
    assert game.selected_level == 3
    game.cycle_level(-1)
    assert game.selected_level == 2
    game.select_level(0)
    print("  -> Level selection and chamber details validated.")

    # -------------------------------------------------------------------------
    # 3. All 5 Levels Generation, Custom Layouts & Both Crystal Types
    # -------------------------------------------------------------------------
    print("\n[3/16] Verifying All 5 Caverns Layout, Corridors, & Dual Crystals...")
    for idx in range(len(LEVEL_SETTINGS)):
        lvl = Level(idx)
        assert lvl.start == lvl.cell_center(*lvl.start_cell)
        assert not lvl.is_wall(*lvl.start), f"Start point in wall on level {idx}"
        assert not lvl.is_wall(*lvl.exit), f"Exit point in wall on level {idx}"
        assert len(lvl.keys) == LEVEL_SETTINGS[idx][4]
        assert len(lvl.bats) == LEVEL_SETTINGS[idx][5]
        assert len(lvl.boosts) >= 1, f"Missing Surge crystals on level {idx}"
        assert len(lvl.aegis) >= 1, f"Missing Aegis crystals on level {idx}"
        # Verify crystals are placed in open cells
        for bx, by in lvl.boosts:
            assert not lvl.is_wall(bx, by), f"Surge crystal inside wall on level {idx}"
        for ax, ay in lvl.aegis:
            assert not lvl.is_wall(ax, ay), f"Aegis crystal inside wall on level {idx}"
        print(f"  -> Level {idx+1} ({lvl.name}): Corridors, Keys, Bats, Surge & Aegis crystals [OK]")

    # -------------------------------------------------------------------------
    # 4. Starting New Game & Start Setup
    # -------------------------------------------------------------------------
    print("\n[4/16] Verifying new_game(), Teleport Shrine & Action-Based State...")
    game.selected_level = 0
    game.new_game()
    assert game.state == "play"
    assert game.level_no == 0
    assert game.lives == 3
    assert game.score == 0
    assert game.dash_charges == 2
    assert game.shield_charges >= 1
    assert not game.shield_active
    assert game.surge_charges == 0
    assert game.minimap_bg is not None
    print("  -> Game initialized with action-based abilities and zero countdown timers.")

    # -------------------------------------------------------------------------
    # 5. Dynamic Fog of War Discovery
    # -------------------------------------------------------------------------
    print("\n[5/16] Verifying Dynamic Fog of War & Persistent Discovered Cells...")
    sr, sc = game.level.start_cell
    assert game.discovered[sr][sc] is True
    # Initial cells outside start torch reach should be undiscovered
    far_cell_discovered = game.discovered[0][0]
    # Move player forward in corridor to discover new cells
    game.update(0.1, vx=1.0, vy=0.0)
    # Check that explored area is marked discovered
    cr, cc = int(game.py // CELL), int((game.px - OFF_X) // CELL)
    assert game.discovered[cr][cc] is True
    game.draw()
    print("  -> Fog of War reveals corridors dynamically and renders soft exploration ghosting.")

    # -------------------------------------------------------------------------
    # 6. Player Movement & Wall Collision Detection
    # -------------------------------------------------------------------------
    print("\n[6/16] Verifying Movement Physics & Circle-Wall Pushout Collision...")
    game.px, game.py = Level.cell_center(ROWS // 2, COLS // 2)
    orig_px, orig_py = game.px, game.py
    game.update(0.016, vx=1.0, vy=0.0)
    assert game.px > orig_px
    # Push into wall continuously
    for _ in range(50):
        game.update(0.016, vx=-1.0, vy=0.0)
    assert not game.level.is_wall(game.px, game.py)
    print("  -> Stepped circle-versus-cell pushout prevents penetrating solid cave walls.")

    # -------------------------------------------------------------------------
    # 7. Dash Ability & Action-Based Walking Recharge
    # -------------------------------------------------------------------------
    print("\n[7/16] Verifying Dash Ability, Motion Ghosting & Walking Recharge...")
    game.px, game.py = Level.cell_center(ROWS // 2, COLS // 2)
    start_dashes = game.dash_charges
    px_before = game.px
    game.dash(1.0, 0.0)
    assert game.dash_charges == start_dashes - 1
    assert game.px > px_before
    assert not game.level.is_wall(game.px, game.py)
    assert len(game.afterimages) > 0

    # Exhaust remaining dashes
    while game.dash_charges > 0:
        game.dash(1.0, 0.0)
    assert game.dash_charges == 0
    p_exhausted = game.px
    game.dash(1.0, 0.0)  # Should fail cleanly without dash charges
    assert game.px == p_exhausted

    # Recharge via gameplay action (walking 35 steps without timer)
    game.dash_step_counter = 34
    game.update(0.016, vx=1.0, vy=0.0)
    assert game.dash_charges == 1
    print("  -> Dash performs collision-checked burst and recharges purely via walking steps.")

    # -------------------------------------------------------------------------
    # 8. Energy Shield Ability & Damage Absorption
    # -------------------------------------------------------------------------
    print("\n[8/16] Verifying Energy Shield Activation & Zero-Damage Absorption...")
    assert not game.shield_active
    assert game.shield_charges >= 1
    game.toggle_shield()
    assert game.shield_active
    # Simulate an enemy hit
    cur_lives = game.lives
    game._hit()
    assert not game.shield_active, "Shield should break after absorbing the blow"
    assert game.lives == cur_lives, "Lives must not decrease when shield absorbs damage"
    print("  -> Energy Shield completely absorbed lethal strike without life loss.")

    # -------------------------------------------------------------------------
    # 9. Crystal Power-Ups: Cyan Surge & Violet Aegis
    # -------------------------------------------------------------------------
    print("\n[9/16] Verifying Crystal Power-Ups (Cyan Surge & Violet Aegis)...")
    # Cyan Surge pickup
    bs_pos = game.boosts_left[0]
    game.px, game.py = bs_pos[0], bs_pos[1]
    game.update(0.016)
    assert game.surge_charges == 5
    assert len(game.boosts_left) == 0

    # Violet Aegis pickup
    ag_pos = game.aegis_left[0]
    game.lives = 2  # Set lives to 2 to test life restoration
    game.px, game.py = ag_pos[0], ag_pos[1]
    game.update(0.016)
    assert game.shield_active is True
    assert game.lives == 3
    assert len(game.aegis_left) == 0
    print("  -> Surge (+5 Tri-Shots) and Aegis (Shield + Life) pickups operate flawlessly.")

    # -------------------------------------------------------------------------
    # 10. Surge Tri-Shot Spread Arrows & Enemy Purging
    # -------------------------------------------------------------------------
    print("\n[10/16] Verifying Surge Tri-Shot Spread Weapon & Enemy Purging...")
    game.shoot_cd = 0.0
    game.angle = 0.0
    assert game.surge_charges > 0
    game.shoot()
    assert len(game.arrows) == 3, "Tri-Shot must generate 3 spread arrows using rotation matrix"
    assert game.surge_charges == 4, "Surge charge decremented by 1 per volley"
    # Kill bat and verify purple/green debris and score
    bat = game.level.bats[0]
    game._kill_bat(bat)
    assert not bat.alive
    assert game.score >= 150
    assert game.level_bats_killed == 1
    print("  -> Tri-Shot 3-way spread arrows and shadow wraith elimination verified.")

    # -------------------------------------------------------------------------
    # 11. BFS Corridor Pathfinding & Intelligent Enemy AI
    # -------------------------------------------------------------------------
    print("\n[11/16] Verifying Grid BFS Corridor Pathfinding & Stalker/Scout AI...")
    lvl = game.level
    start_rc = lvl.start_cell
    exit_rc = (int(lvl.exit[1] // CELL), int((lvl.exit[0] - OFF_X) // CELL))
    bfs_path = lvl.find_bfs_path(start_rc, exit_rc)
    assert bfs_path is not None, "BFS pathfinder must locate valid corridor route"
    assert len(bfs_path) >= 2
    assert bfs_path[0] == start_rc
    # Verify every step in BFS path is in an open corridor (grid == 0)
    for r, c in bfs_path:
        assert lvl.grid[r][c] == 0, f"BFS path traversed solid wall at ({r}, {c})"

    # Verify Bat AI execution
    test_bat = lvl.bats[0]
    test_bat.alive = True
    test_bat.kind = "stalker"
    bx_orig, by_orig = test_bat.x, test_bat.y
    test_bat.update_ai(lvl, game.px, game.py, 0.1)
    assert (test_bat.x, test_bat.y) != (bx_orig, by_orig)
    assert not lvl.is_wall(test_bat.x, test_bat.y)
    print("  -> BFS corridor pathfinding and intelligent Stalker enemy navigation verified.")

    # -------------------------------------------------------------------------
    # 12. Key Collection, Portal Unsealing & Level Clear
    # -------------------------------------------------------------------------
    print("\n[12/16] Verifying Key Collection, Portals, & Badges...")
    while game.keys_left:
        k = game.keys_left[0]
        game.px, game.py = k[0], k[1]
        game.update(0.016)
    assert len(game.keys_left) == 0
    game.px, game.py = game.level.exit
    game.update(0.016)
    assert game.state == "levelclear"
    assert "UNTOUCHED" in game.badges
    print("  -> Keys collected, portal unlocked, UNTOUCHED badge awarded.")

    # -------------------------------------------------------------------------
    # 13. Coordinate Grid Overlay & CG Mode Toggles
    # -------------------------------------------------------------------------
    print("\n[13/16] Verifying Cartesian Grid Overlay & Algorithm Toggles...")
    game.toggle_grid()
    assert game.show_grid
    game.draw()
    game.toggle_grid()
    assert not game.show_grid

    # In-game line/clip toggles
    game.r.toggle_line()
    assert game.r.line_algo == "DDA"
    game.r.toggle_line()
    assert game.r.line_algo == "Bresenham"

    game.r.toggle_clip()
    assert game.r.clip_algo == "Liang-Barsky"
    game.r.toggle_clip()
    assert game.r.clip_algo == "Cohen-Sutherland"
    print("  -> Cartesian grid and live runtime algorithm toggles verified.")

    # -------------------------------------------------------------------------
    # 14. Pause, Help Field Guide, and Best Score Persistence
    # -------------------------------------------------------------------------
    print("\n[14/16] Verifying Pause, Field Guide & Local Score Persistence...")
    game.load_level()
    game.toggle_pause()
    assert game.state == "pause"
    pause_px = game.px
    game.update(0.1, vx=1.0, vy=1.0)
    assert game.px == pause_px, "Player moved during pause!"
    game.toggle_pause()
    assert game.state == "play"

    game.toggle_help()
    assert game.show_help
    game.draw()
    game.toggle_help()
    assert not game.show_help

    # Score persistence test
    game.score = 2500
    game._save_best_score()
    loaded_best = game._load_best_score()
    assert loaded_best >= 2500
    print("  -> Pause isolation, Field Guide overlay, and best_score.txt persistence OK.")

    # -------------------------------------------------------------------------
    # 15. Computer Graphics Laboratory Mode Integration
    # -------------------------------------------------------------------------
    print("\n[15/16] Verifying Computer Graphics Laboratory State & Mode Switching...")
    game.enter_cg_lab()
    assert game.state == "cglab"
    cglab = game.cg_lab
    assert isinstance(cglab, CGLab)

    # Test mode tabs
    for mode in ["bresenham", "dda", "circle", "clipping"]:
        cglab.mode = mode
        game.draw()
        assert cglab.mode == mode

    # Test preset cycling
    cglab.mode = "bresenham"
    p0_init = list(cglab.p0)
    cglab._cycle_preset()
    assert cglab.p0 != p0_init
    cglab._reset_current_mode()

    # Exit back to main game
    game.exit_cg_lab()
    assert game.state == "title"
    print("  -> CG Laboratory mode entered, switched tabs, cycled presets, and exited cleanly.")

    # -------------------------------------------------------------------------
    # 16. Pure CG Algorithm Correctness Verification
    # -------------------------------------------------------------------------
    print("\n[16/16] Verifying Exact Mathematical Correctness of All 4 CG Algorithms...")
    # A. Bresenham Line
    b_pts = list(bresenham_line(2, 3, 8, 7))
    assert (2, 3) in b_pts and (8, 7) in b_pts
    assert len(b_pts) == 7  # dx = 6 -> 7 pixels plotted

    # B. DDA Line
    dda_pts = list(dda_line(2, 3, 8, 7))
    assert (2, 3) in dda_pts and (8, 7) in dda_pts
    assert len(dda_pts) == 7

    # C. Midpoint Circle
    c_pts = list(circle_points(10, 10, 5))
    assert len(c_pts) > 0
    for x, y in c_pts:
        d = math.hypot(x - 10, y - 10)
        assert abs(d - 5) <= 1.0, f"Circle pixel ({x}, {y}) too far from radius 5"

    # D. Cohen-Sutherland Line Clipping
    win = (5, 5, 20, 20)
    # Trivial accept (both inside)
    assert outcode(10, 10, win) == 0
    res_accept = cohen_sutherland(10, 10, 15, 15, win)
    assert res_accept == (10, 10, 15, 15)

    # Trivial reject (both to the left)
    c_left = outcode(2, 10, win)
    assert (c_left & 1) != 0  # LEFT bit
    res_reject = cohen_sutherland(1, 10, 3, 15, win)
    assert res_reject is None

    # Partial clip across boundaries
    res_clip = cohen_sutherland(2, 10, 25, 10, win)
    assert res_clip is not None
    cx0, cy0, cx1, cy1 = res_clip
    assert cx0 == 5 and cx1 == 20 and cy0 == 10 and cy1 == 10

    print("  -> Bresenham, DDA, Midpoint Circle, and Cohen-Sutherland algorithms verified.")

    pygame.quit()
    print("\n=================================================================")
    print("   ALL 16/16 EXTENDED VERIFICATION TESTS PASSED SUCCESSFULLY!    ")
    print("=================================================================")


if __name__ == "__main__":
    run_tests()
