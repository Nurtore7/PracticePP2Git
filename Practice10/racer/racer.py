import pygame, sys
from pygame.locals import *
import random, time

# Initialize pygame
pygame.init()

# FPS means how many frames per second the game will run
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors in RGB format
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Screen size
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Initial speed of enemies and coins
SPEED = 5

# Score and collected coins
SCORE = 0
COINS = 0

# Fonts for text
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

# Load background image
background = pygame.image.load("pp2/Practice10/images/AnimatedStreet.png")

# Create game window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

# Create Game Over text
game_over_text = font.render("Game Over", True, BLACK)


# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent Sprite constructor
        super().__init__()

        # Load enemy image
        self.image = pygame.image.load("pp2/Practice10/images/Enemy.png")

        # Get rectangle of the image
        # Rect is used for position, movement and collision
        self.rect = self.image.get_rect()

        # Place enemy at random X position at the top of the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        # SCORE is global because we change it inside this method
        global SCORE

        # Move enemy down
        self.rect.move_ip(0, SPEED)

        # If enemy goes below the screen
        if self.rect.bottom > SCREEN_HEIGHT:
            # Add 1 point
            SCORE += 1

            # Move enemy back to the top
            self.rect.top = 0

            # Give enemy a new random X position
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent Sprite constructor
        super().__init__()

        # Create a simple yellow coin surface with size 20x20
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)

        # Get rectangle of the coin
        self.rect = self.image.get_rect()

        # Place coin above the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    def move(self):
        # Move coin down
        self.rect.move_ip(0, SPEED)

        # If coin goes below the screen
        if self.rect.top > SCREEN_HEIGHT:
            # Move coin back above the screen
            self.rect.top = -20

            # Give coin a new random X position
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent Sprite constructor
        super().__init__()

        # Load player image
        self.image = pygame.image.load("pp2/Practice10/images/Player.png")

        # Get rectangle of the player image
        self.rect = self.image.get_rect()

        # Set player's start position
        self.rect.center = (160, 520)

    def move(self):
        # Get all currently pressed keys
        pressed_keys = pygame.key.get_pressed()

        # Move left only if player is not outside the left border
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)

        # Move right only if player is not outside the right border
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)


# Function to restart the game
def reset_game():
    # These variables are global because they are used in the main game loop
    global SPEED, SCORE, COINS, P1, enemies, coins, all_sprites

    # Reset values to the beginning
    SPEED = 5
    SCORE = 0
    COINS = 0

    # Create player
    P1 = Player()

    # Create two enemies
    E1 = Enemy()
    E2 = Enemy()

    # Create one coin
    C1 = Coin()

    # Group for enemies
    enemies = pygame.sprite.Group(E1, E2)

    # Group for coins
    coins = pygame.sprite.Group(C1)

    # Group for all sprites
    # It helps us move and draw all objects using one loop
    all_sprites = pygame.sprite.Group(P1, E1, E2, C1)


# Start the first game
reset_game()

# Create custom event for increasing speed
INC_SPEED = pygame.USEREVENT + 1

# This event will happen every 1000 milliseconds, so every 1 second
pygame.time.set_timer(INC_SPEED, 1000)

# This variable shows whether the game is over or not
game_over = False


# Main infinite game loop
while True:

    # Check all events
    for event in pygame.event.get():

        # If the player closes the window
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # If game is not over, increase speed every second
        if not game_over:
            if event.type == INC_SPEED:
                SPEED += 0.5

        # If game is over, wait for R key to restart
        if game_over:
            if event.type == KEYDOWN:
                if event.key == K_r:
                    reset_game()
                    game_over = False

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # If game is still running
    if not game_over:

        # Move and draw every object
        for entity in all_sprites:
            entity.move()
            DISPLAYSURF.blit(entity.image, entity.rect)

        # Check collision between player and enemies
        if pygame.sprite.spritecollideany(P1, enemies):
            # Play crash sound
            pygame.mixer.Sound("pp2/Practice10/images/crash.wav").play()

            # Stop the game and show Game Over screen
            game_over = True

        # Check collision between player and coins
        if pygame.sprite.spritecollideany(P1, coins):
            # Increase coin counter
            COINS += 1

            # Move collected coin back above the screen
            for coin in coins:
                coin.rect.top = -20
                coin.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    # If game is over
    else:
        # Fill screen with red color
        DISPLAYSURF.fill(RED)

        # Draw Game Over text
        DISPLAYSURF.blit(game_over_text, (30, 250))

        # Draw restart instruction
        restart_text = font_small.render("Press R to Restart", True, WHITE)
        DISPLAYSURF.blit(restart_text, (100, 320))

    # Create score text
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)

    # Create coin text
    coin_text = font_small.render("Coins: " + str(COINS), True, BLACK)

    # Draw score in the top-left corner
    DISPLAYSURF.blit(score_text, (10, 10))

    # Draw coins in the top-right corner
    DISPLAYSURF.blit(coin_text, (280, 10))

    # Update the display
    pygame.display.update()

    # Limit game speed to 60 FPS
    FramePerSec.tick(FPS)