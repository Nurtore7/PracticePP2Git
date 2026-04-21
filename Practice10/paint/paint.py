import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()

# Цвета
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

color = BLACK
brush_size = 5
drawing = False
mode = "brush"   # brush / rect / circle / eraser

start_pos = None

screen.fill(WHITE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Нажатие мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos

        # Отпускание мыши
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            if mode == "rect":
                pygame.draw.rect(screen, color, (*start_pos, end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]), 2)

            if mode == "circle":
                radius = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
                pygame.draw.circle(screen, color, start_pos, radius, 2)

        # Движение мыши
        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == "brush":
                pygame.draw.circle(screen, color, event.pos, brush_size)
            if mode == "eraser":
                pygame.draw.circle(screen, WHITE, event.pos, brush_size)

        # Клавиши
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                color = RED
            if event.key == pygame.K_g:
                color = GREEN
            if event.key == pygame.K_b:
                color = BLUE
            if event.key == pygame.K_k:
                color = BLACK

            if event.key == pygame.K_1:
                mode = "brush"
            if event.key == pygame.K_2:
                mode = "rect"
            if event.key == pygame.K_3:
                mode = "circle"
            if event.key == pygame.K_4:
                mode = "eraser"

    pygame.display.update()
    clock.tick(60)