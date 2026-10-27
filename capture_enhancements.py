"""
capture_enhancements.py - Generates visual verification images for:
1. Title screen with dual Game & CG Lab modes.
2. In-game action showing energy shield barrier, dash ghost trails, Fog of War, and intelligent wraiths.
3. CG Lab Bresenham line algorithm interactive grid & step table.
4. CG Lab Midpoint circle algorithm 8-way symmetry octant color coding.
5. CG Lab Cohen-Sutherland line clipping with 4-bit region outcodes.
"""
import os
import sys

# Headless video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from game import Game, W, H, CELL, OFF_X, ROWS, COLS
from levels import Level

def capture():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    game = Game(screen)

    out_dir = r"C:\Users\NILESH MARATHE\.gemini\antigravity-ide\brain\e19d0f3a-913e-4861-b6a5-3e776a77bef9"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Title Screen
    game.state = "title"
    game.t = 1.8
    game.draw()
    title_path = os.path.join(out_dir, "title_menu_enhanced.png")
    pygame.image.save(screen, title_path)
    print("Saved title:", title_path)

    # 2. In-Game Play with Shield, Dash trail, and Fog of War
    game.selected_level = 0
    game.new_game()
    # Move to central nexus plaza
    game.px, game.py = Level.cell_center(ROWS // 2, COLS // 2)
    # Engage shield
    game.shield_active = True
    # Fire surge tri-shot
    game.surge_charges = 4
    game.shoot()
    # Perform dash to generate ghost trails
    game.dash(1.0, 0.0)
    game.t = 3.5
    game.update(0.016)
    game.draw()
    gameplay_path = os.path.join(out_dir, "gameplay_abilities_enhanced.png")
    pygame.image.save(screen, gameplay_path)
    print("Saved gameplay:", gameplay_path)

    # 3. CG Lab - Bresenham Line
    game.enter_cg_lab()
    game.cg_lab.mode = "bresenham"
    game.draw()
    cglab_b_path = os.path.join(out_dir, "cglab_bresenham.png")
    pygame.image.save(screen, cglab_b_path)
    print("Saved CG Lab Bresenham:", cglab_b_path)

    # 4. CG Lab - Midpoint Circle
    game.cg_lab.mode = "circle"
    game.cg_lab.circle_center = [12, 9]
    game.cg_lab.circle_radius = 6
    game.draw()
    cglab_c_path = os.path.join(out_dir, "cglab_circle.png")
    pygame.image.save(screen, cglab_c_path)
    print("Saved CG Lab Circle:", cglab_c_path)

    # 5. CG Lab - Cohen-Sutherland Clipping
    game.cg_lab.mode = "clipping"
    game.cg_lab.clip_p0 = [2, 15]
    game.cg_lab.clip_p1 = [21, 2]
    game.draw()
    cglab_clip_path = os.path.join(out_dir, "cglab_clipping.png")
    pygame.image.save(screen, cglab_clip_path)
    print("Saved CG Lab Clipping:", cglab_clip_path)

    pygame.quit()
    print("All captures completed successfully!")

if __name__ == "__main__":
    capture()
