import pygame
import random

# Initialize pygame
pygame.init()

# Screen size
WIDTH, HEIGHT = 600, 600

# Size of one cell in the grid
CELL = 20

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Pro")

# Clock controls the game speed
clock = pygame.time.Clock()

# Font for score and level text
font = pygame.font.SysFont("Verdana", 20)

# Snake starts with one block
snake = [(100, 100)]

# Initial movement direction: right
dx, dy = CELL, 0

# Initial score
score = 0

# Initial level
level = 1

# Initial snake speed
speed = 10

# Every 4 food items, level increases
FOOD_FOR_NEXT_LEVEL = 4

# Time limit for food (in seconds)
FOOD_TIME_LIMIT = 8

# Timer for food
food_timer = 0


# Function to generate food in a random place
def generate_food():
    while True:
        # Generate random x and y position according to the grid
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)

        # Food must not appear inside the snake
        if (x, y) not in snake:
            return (x, y)


# Generate the first food
food = generate_food()

# Main game variable
running = True

# Timer for food (in seconds)
food_timer = 0

# Main game loop
while running:

    # Get delta time (time passed since last frame)
    dt = clock.tick(speed) / 1000.0  # Convert milliseconds to seconds
    
    # Update food timer
    food_timer += dt

    # Check all events
    for event in pygame.event.get():

        # If player closes the window
        if event.type == pygame.QUIT:
            running = False

        # Check keyboard buttons
        if event.type == pygame.KEYDOWN:

            # Move up only if snake is not moving vertically
            if event.key == pygame.K_UP and dy == 0:
                dx, dy = 0, -CELL

            # Move down only if snake is not moving vertically
            if event.key == pygame.K_DOWN and dy == 0:
                dx, dy = 0, CELL

            # Move left only if snake is not moving horizontally
            if event.key == pygame.K_LEFT and dx == 0:
                dx, dy = -CELL, 0

            # Move right only if snake is not moving horizontally
            if event.key == pygame.K_RIGHT and dx == 0:
                dx, dy = CELL, 0

    # Get current snake head
    head = snake[0]

    # Create new head position
    new_head = (head[0] + dx, head[1] + dy)

    # Check wall collision
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
        running = False

    # Check collision with itself
    if new_head in snake:
        running = False

    # Add new head to the beginning of the snake
    snake.insert(0, new_head)

    # Check if snake eats food
    if new_head == food:
        # Reset food timer
        food_timer = 0
        
        # Increase score
        score += 1

        # Generate new food
        food = generate_food()

        # If score is divisible by 4, increase level
        if score % FOOD_FOR_NEXT_LEVEL == 0:
            level += 1

            # Increase speed when level increases
            speed += 2

    else:
        # If snake did not eat food, remove the tail
        snake.pop()
    
    # Check if food timer exceeded the limit
    if food_timer >= FOOD_TIME_LIMIT:
        # Move food to new location
        food = generate_food()
        # Reset timer
        food_timer = 0

    # Fill background
    screen.fill((30, 30, 30))

    # Draw vertical grid lines
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))

    # Draw horizontal grid lines
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

    # Draw snake
    for i, segment in enumerate(snake):
        # Snake becomes a little darker from head to tail
        green_value = max(80, 255 - i * 5)
        color = (0, green_value, 0)

        pygame.draw.rect(
            screen,
            color,
            (segment[0], segment[1], CELL, CELL),
            border_radius=5
        )

    # Draw food - RED color, no timer indicator
    pygame.draw.rect(
        screen,
        (255, 0, 0),  # Solid red color
        (food[0], food[1], CELL, CELL),
        border_radius=5
    )

    # Create score text
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))

    # Create level text
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    
    # Create timer text
    timer_text = font.render(f"Food timer: {FOOD_TIME_LIMIT - int(food_timer)}s", True, (255, 255, 255))

    # Draw score on the screen
    screen.blit(score_text, (10, 10))

    # Draw level on the screen
    screen.blit(level_text, (10, 40))
    
    # Draw timer on the screen
    screen.blit(timer_text, (10, 70))

    # Update display
    pygame.display.flip()

# Quit pygame
pygame.quit()