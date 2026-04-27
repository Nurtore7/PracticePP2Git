import pygame
import sys
import random

# Initialize pygame
pygame.init()

# FPS means how many frames per second the game will run
FPS = 60
clock = pygame.time.Clock()

# Colors in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Screen size
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Practice 11 Racer")

# Initial enemy speed
enemy_speed = 5

# Coin speed
coin_speed = 5


score = 0
coins = 0


N_COINS = 5


last_speed_level = 0


font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)

# Load images
background = pygame.image.load("Practice10/racer/AnimatedStreet.png")
player_img = pygame.image.load("Practice10/racer/Player.png")
enemy_img = pygame.image.load("Practice10/racer/Enemy.png")


crash_sound = pygame.mixer.Sound("Practice10/racer/crash.wav")

# Game Over text
game_over_text = font.render("Game Over", True, BLACK)

# Player position
player_rect = player_img.get_rect()
player_rect.center = (160, 520)

# Enemy position
enemy_rect = enemy_img.get_rect()
enemy_rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Coin settings
coin_size = 20
coin_rect = pygame.Rect(0, 0, coin_size, coin_size)

# Coin weight means how many points this coin gives
coin_weight = 1

# This variable shows whether the game is over or not
game_over = False


# Function for choosing coin color by weight
def get_coin_color(weight):
    # Weight 1 coin is yellow
    if weight == 1:
        return YELLOW

    # Weight 2 coin is orange
    if weight == 2:
        return ORANGE

    # Weight 3 coin is green
    return GREEN


# Function for choosing coin size by weight
def get_coin_size(weight):
    # Bigger weight means bigger coin
    if weight == 1:
        return 18

    if weight == 2:
        return 24

    return 30


# Function for resetting enemy position
def reset_enemy():
    global enemy_rect

    # Move enemy back to the top
    enemy_rect.top = 0

    # Choose random x position on the road
    enemy_rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# Function for resetting coin position and weight
def reset_coin():
    global coin_rect, coin_weight, coin_size

    # Randomly choose coin weight
    coin_weight = random.choice([1, 2, 3])

    # Coin size depends on weight
    coin_size = get_coin_size(coin_weight)

    # Create new rectangle for coin
    coin_rect = pygame.Rect(0, 0, coin_size, coin_size)

    # Put coin above the screen in random x position
    coin_rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)


# Function for restarting the whole game
def reset_game():
    global enemy_speed, coin_speed, score, coins, game_over, last_speed_level

    # Reset speed
    enemy_speed = 5
    coin_speed = 5

   
    score = 0
    coins = 0

    
    last_speed_level = 0

   
    game_over = False

    # Reset player position
    player_rect.center = (160, 520)

    # Reset enemy and coin positions
    reset_enemy()
    reset_coin()


# Generate first coin
reset_coin()

# Main game loop
while True:

    # Check all events
    for event in pygame.event.get():

        # If player closes the window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

    # Draw background
    screen.blit(background, (0, 0))

    
    if not game_over:

        # Get pressed keys
        keys = pygame.key.get_pressed()

        # Move player left
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.move_ip(-5, 0)

        # Move player right
        if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
            player_rect.move_ip(5, 0)

        # Move enemy down
        enemy_rect.move_ip(0, enemy_speed)

       
        if enemy_rect.bottom > SCREEN_HEIGHT:
            score += 1
            reset_enemy()

        # Move coin down
        coin_rect.move_ip(0, coin_speed)

        # If coin goes below the screen, reset it
        if coin_rect.top > SCREEN_HEIGHT:
            reset_coin()

        # Check collision between player and enemy
        if player_rect.colliderect(enemy_rect):
            crash_sound.play()
            game_over = True

        
        if player_rect.colliderect(coin_rect):

            
            coins += coin_weight

            # Generate new coin
            reset_coin()

            # Calculate current speed level
            current_speed_level = coins // N_COINS

            
            if current_speed_level > last_speed_level:
                enemy_speed += 1
                last_speed_level = current_speed_level

        # Draw player car
        screen.blit(player_img, player_rect)

        # Draw enemy car
        screen.blit(enemy_img, enemy_rect)

        # Draw coin with color and size depending on weight
        pygame.draw.circle(
            screen,
            get_coin_color(coin_weight),
            coin_rect.center,
            coin_size // 2
        )

        # Draw coin weight inside the coin
        weight_text = font_small.render(str(coin_weight), True, BLACK)
        weight_rect = weight_text.get_rect(center=coin_rect.center)
        screen.blit(weight_text, weight_rect)

    # If game is over
    else:
        
        screen.fill(RED)

        
        screen.blit(game_over_text, (30, 250))

       
        restart_text = font_small.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (100, 320))

   
    score_text = font_small.render("Score: " + str(score), True, BLACK)

    
    coin_text = font_small.render("Coins: " + str(coins), True, BLACK)

    
    speed_text = font_small.render("Speed: " + str(enemy_speed), True, BLACK)

    
    screen.blit(score_text, (10, 10))

    
    screen.blit(coin_text, (260, 10))


    screen.blit(speed_text, (10, 35))

    
    pygame.display.update()

    # Limit game speed to 60 FPS
    clock.tick(FPS)