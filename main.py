"""
DARK CAVE EXPLORER  -  Computer Graphics mini-project
Run:   python main.py
"""
import sys
import pygame
from game import Game, W, H


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Dark Cave Explorer - Computer Graphics Project")
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if e.key == pygame.K_l:
                    game.r.toggle_line()
                if e.key == pygame.K_c:
                    game.r.toggle_clip()
                if e.key == pygame.K_RETURN:
                    if game.state in ("title", "gameover", "win"):
                        game.new_game()
                    elif game.state == "levelclear":
                        game.load_level()
                if e.key in (pygame.K_SPACE, pygame.K_f) and game.state == "play":
                    game.shoot()
                if e.key == pygame.K_r and game.state == "play":
                    game.reset_level()

        k = pygame.key.get_pressed()
        vx = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
        vy = (k[pygame.K_DOWN] or k[pygame.K_s]) - (k[pygame.K_UP] or k[pygame.K_w])
        game.update(dt, vx, vy)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
