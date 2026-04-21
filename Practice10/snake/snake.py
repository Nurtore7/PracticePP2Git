import pygame
import random
import sys

pygame.init()

# Размер окна
WIDTH = 600
HEIGHT = 600
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# Цвета
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLACK = (0,0,0)

# Змея
snake = [(100,100), (80,100), (60,100)]
dx = CELL
dy = 0

# Еда
food = (random.randrange(0, WIDTH, CELL), random.randrange(0, HEIGHT, CELL))

score = 0
font = pygame.font.SysFont("Verdana", 20)

def draw_snake():
    for block in snake:
        pygame.draw.rect(screen, GREEN, (*block, CELL, CELL))

def draw_food():
    pygame.draw.rect(screen, RED, (*food, CELL, CELL))

def game_over():
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (250,300))
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()

# Игра
while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and dy == 0:
                dx = 0
                dy = -CELL
            if event.key == pygame.K_DOWN and dy == 0:
                dx = 0
                dy = CELL
            if event.key == pygame.K_LEFT and dx == 0:
                dx = -CELL
                dy = 0
            if event.key == pygame.K_RIGHT and dx == 0:
                dx = CELL
                dy = 0

    # Движение
    head = (snake[0][0] + dx, snake[0][1] + dy)

    # Проверка стены
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        game_over()

    # Проверка на себя
    if head in snake:
        game_over()

    snake.insert(0, head)

    # Еда
    if head == food:
        score += 1
        food = (random.randrange(0, WIDTH, CELL), random.randrange(0, HEIGHT, CELL))
    else:
        snake.pop()

    draw_snake()
    draw_food()

    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10,10))

    pygame.display.update()
    clock.tick(10)