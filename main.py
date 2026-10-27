"""
EMBERVAULT: THE CRYSTAL MAZE  -  Computer Graphics Mini-Project
Run:   python main.py
"""
import sys
import pygame
from game import Game, W, H


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("EmberVault: The Crystal Maze")
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if game.show_help:
                        game.show_help = False
                    else:
                        pygame.quit()
                        sys.exit()
                if e.key == pygame.K_p:
                    game.toggle_pause()
                if e.key == pygame.K_h:
                    game.toggle_help()
                if e.key == pygame.K_l:
                    game.r.toggle_line()
                if e.key == pygame.K_c:
                    game.r.toggle_clip()
                if e.key == pygame.K_g:
                    game.toggle_grid()
                if game.state == "title" and not game.show_help:
                    if e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                        game.select_level(e.key - pygame.K_1)
                    elif e.key in (pygame.K_TAB, pygame.K_RIGHT):
                        game.cycle_level(1)
                    elif e.key == pygame.K_LEFT:
                        game.cycle_level(-1)
                if e.key == pygame.K_RETURN:
                    if game.show_help:
                        game.show_help = False
                    elif game.state == "pause":
                        game.toggle_pause()
                    elif game.state in ("title", "gameover", "win"):
                        game.new_game()
                    elif game.state == "levelclear":
                        game.load_level()
                if e.key in (pygame.K_SPACE, pygame.K_f) and game.state == "play" and not game.show_help:
                    game.shoot()
                if e.key == pygame.K_r and game.state in ("play", "pause"):
                    game.reset_level()

        vx, vy = 0.0, 0.0
        if game.state == "play" and not game.show_help:
            k = pygame.key.get_pressed()
            vx = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
            vy = (k[pygame.K_DOWN] or k[pygame.K_s]) - (k[pygame.K_UP] or k[pygame.K_w])

        game.update(dt, vx, vy)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()

