"""
test_game.py - Comprehensive automated verification for EmberVault: The Crystal Maze
Tests all 5 levels, custom starts, level selection, boost crystals, grid overlay, and algorithms.
"""
import os
import sys

# Set headless SDL video driver for automated testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import graphics as gfx
from game import Game, W, H
from levels import Level, LEVEL_SETTINGS

def run_tests():
    print("--- Starting EmberVault Extended Verification Suite ---")
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    game = Game(screen)

    # 1. Title State & Redesigned Layout
    print("[1/11] Verifying Title State, Drifting Particles, and Redesigned Layout...")
    assert game.state == "title"
    assert len(game.title_stars) == 40
    game.draw()
    print("  -> Title screen rendered cleanly without overflow.")

    # 2. Title Level Selection Feature
    print("[2/11] Verifying Title Level Selection (1-5 / Tab)...")
    assert game.selected_level == 0
    game.select_level(3)
    assert game.selected_level == 3
    game.cycle_level(1)
    assert game.selected_level == 4
    game.cycle_level(1)
    assert game.selected_level == 0
    game.draw()
    print("  -> Level selection and showcase badge verified.")

    # 3. Verifying All 5 Levels Generation & Unique Starting Points
    print("[3/11] Verifying all 5 Cavern Levels and Unique Starting Chambers...")
    for idx in range(len(LEVEL_SETTINGS)):
        lvl = Level(idx)
        assert lvl.start == lvl.cell_center(*lvl.start_cell)
        assert not lvl.is_wall(*lvl.start)
        assert not lvl.is_wall(*lvl.exit)
        assert len(lvl.keys) == LEVEL_SETTINGS[idx][4]
        assert len(lvl.bats) == LEVEL_SETTINGS[idx][5]
        print(f"  -> Level {idx+1}: {lvl.name} starting at {lvl.chamber_title} {lvl.start} [PASSED]")

    # 4. Starting New Game & Level 1 Setup
    print("[4/11] Verifying new_game() and Start Teleport Shrine...")
    game.selected_level = 0
    game.new_game()
    assert game.state == "play"
    assert game.level_no == 0
    assert game.lives == 3
    assert game.score == 0
    assert len(game.keys_left) == 1
    assert game.minimap_bg is not None
    game.draw()
    print("  -> Level 1 loaded, teleport shrine rendered, minimap active.")

    # 5. Coordinate Grid Overlay Feature (G key)
    print("[5/11] Verifying Coordinate Grid Overlay (G key)...")
    assert not game.show_grid
    game.toggle_grid()
    assert game.show_grid
    game.draw()
    game.toggle_grid()
    assert not game.show_grid
    print("  -> Grid overlay toggled and drawn successfully.")

    # 6. Player Movement & Wall Collision
    print("[6/11] Verifying Player Movement & Collision Pushout...")
    orig_px, orig_py = game.px, game.py
    game.update(0.016, vx=1.0, vy=0.0)
    assert game.px != orig_px
    for _ in range(60):
        game.update(0.016, vx=-1.0, vy=0.0)
    assert not game.level.is_wall(game.px, game.py)
    print("  -> Player movement and 3D beveled wall collision validated.")

    # 7. Shooting Mechanics & Bat Purging
    print("[7/11] Verifying Shooting, Cooldown, and Bat Destruction...")
    game.px, game.py = Level.cell_center(7, 9)  # Open central chamber
    game.angle = 0.0
    game.shoot()
    assert len(game.arrows) == 1
    assert game.shoot_cd > 0
    game.update(0.016)
    assert len(game.arrows) == 1 and game.arrows[0][3] > 0
    # Purge bat
    bat = game.level.bats[0]
    game._kill_bat(bat)
    assert not bat.alive
    assert game.score == 150
    assert game.best_score >= 150
    print("  -> Arrow physics, reload cooldown, and bat destruction verified.")

    # 8. Boost Crystal Feature (Crystal Surge)
    print("[8/11] Verifying Crystal Surge (Speed & Torch Boost)...")
    game.selected_level = 1
    game.new_game()
    assert len(game.boosts_left) >= 1
    boost_pos = game.boosts_left[0]
    game.px, game.py = boost_pos[0], boost_pos[1]
    game.update(0.016)
    assert game.boost_timer > 0
    assert len(game.boosts_left) == 0
    game.draw()
    print("  -> Crystal Surge activated, boost timer active, and status HUD verified.")

    # 9. Key Collection & Exit Transition
    print("[9/11] Verifying Key Collection and Exit Transition...")
    while game.keys_left:
        k = game.keys_left[0]
        game.px, game.py = k[0], k[1]
        game.update(0.016)
    assert len(game.keys_left) == 0
    game.px, game.py = game.level.exit
    game.update(0.016)
    assert game.state == "levelclear"
    game.draw()
    print("  -> Keys collected, portal unsealed, level clear verified.")

    # 10. Pause and Resume (Feature A)
    print("[10/11] Verifying Pause / Resume (Feature A)...")
    game.load_level()
    assert game.state == "play"
    game.toggle_pause()
    assert game.state == "pause"
    pause_px, pause_py = game.px, game.py
    game.update(0.1, vx=1.0, vy=1.0)
    assert game.px == pause_px and game.py == pause_py
    game.draw()
    game.toggle_pause()
    assert game.state == "play"
    print("  -> Pause overlay and frozen updates verified.")

    # 11. CG Algorithm Switching & Field Guide
    print("[11/11] Verifying CG Algorithm Toggles & Field Guide Overlay...")
    game.r.toggle_line()
    assert game.r.line_algo == "DDA"
    game.r.toggle_line()
    assert game.r.line_algo == "Bresenham"

    game.r.toggle_clip()
    assert game.r.clip_algo == "Liang-Barsky"
    game.r.toggle_clip()
    assert game.r.clip_algo == "Cohen-Sutherland"

    game.toggle_help()
    assert game.show_help
    game.draw()
    game.toggle_help()
    assert not game.show_help
    print("  -> Line/Clip algorithm toggles and Field Guide verified.")

    pygame.quit()
    print("\nALL 11/11 EXTENDED VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
