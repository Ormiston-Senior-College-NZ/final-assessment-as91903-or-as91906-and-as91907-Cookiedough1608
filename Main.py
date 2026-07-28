import pygame
import random
import math

# Initialize
pygame.init()

# Screen
WIDTH = 1000
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Party Run")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("arial", 40, bold=True)
big_font = pygame.font.SysFont("arial", 80, bold=True)

# Colours
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

BLUE = (50, 120, 255)
RED = (220, 60, 60)
GREEN = (50, 220, 100)
YELLOW = (255, 230, 80)

PURPLE = (170, 100, 255)

# Brighter colours
SKY_TOP = (70, 180, 255)
SKY_BOTTOM = (180, 230, 255)

ROAD = (70, 70, 70)

BUILDING = (90, 100, 130)
WINDOW = (255, 240, 120)

GRASS = (70, 180, 70)
SUN = (255, 220, 70)

# Player
player = pygame.Rect(120, 320, 60, 60)
player_vel_y = 0
gravity = 1
jump_power = -18
on_ground = True

# Game variables
scroll_speed = 8
score = 0
game_over = False

# Obstacles
obstacles = []

# Bad choices
bad_items = []

# Good choices
good_items = []

# Stars
stars = []
for i in range(80):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT)])

# Clouds
clouds = []
for i in range(6):
    clouds.append([random.randint(0, WIDTH), random.randint(20, 150)])

# Impairment system
impaired = False
impair_timer = 0


# Functions
def draw_background():
    # Sky gradient
    for y in range(HEIGHT):
        r = SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * y // HEIGHT
        g = SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * y // HEIGHT
        b = SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * y // HEIGHT
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Sun
    pygame.draw.circle(screen, SUN, (850, 90), 45)

    # Stars (only at top)
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 2)

    # Clouds
    for cloud in clouds:
        pygame.draw.ellipse(screen, (250, 250, 250), (cloud[0], cloud[1], 120, 50))
        pygame.draw.ellipse(screen, (250, 250, 250), (cloud[0] + 20, cloud[1] - 10, 70, 40))

        cloud[0] -= 1
        if cloud[0] < -140:
            cloud[0] = WIDTH + random.randint(50, 300)
            cloud[1] = random.randint(20, 140)

    # Buildings
    random.seed(1)
    for i in range(12):
        x = i * 100
        building_height = random.randint(120, 260)

        pygame.draw.rect(screen, BUILDING, (x, HEIGHT - 120 - building_height, 80, building_height))

        # Windows
        for row in range(8):
            for col in range(3):
                wx = x + 12 + col * 22
                wy = HEIGHT - 105 - building_height + row * 28
                pygame.draw.rect(screen, WINDOW, (wx, wy, 10, 14))

    # Grass
    pygame.draw.rect(screen, GRASS, (0, 360, WIDTH, 20))

    # Road
    pygame.draw.rect(screen, ROAD, (0, 380, WIDTH, 120))

    # Road lines
    for i in range(18):
        pygame.draw.rect(screen, WHITE, (i * 80 - (score % 80), 435, 45, 8))


def spawn_obstacles():
    if random.randint(1, 70) == 1:
        obstacle = pygame.Rect(WIDTH, 330, 50, 50)
        obstacles.append(obstacle)

    if random.randint(1, 200) == 1:
        bad = pygame.Rect(WIDTH, 300, 40, 40)
        bad_items.append(bad)

    if random.randint(1, 250) == 1:
        good = pygame.Rect(WIDTH, 300, 40, 40)
        good_items.append(good)


# Main loop
running = True

while running:

    clock.tick(FPS)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE and on_ground:
                if impaired:
                    player_vel_y = jump_power + 5
                else:
                    player_vel_y = jump_power
                on_ground = False

            if event.key == pygame.K_r and game_over:
                game_over = False
                score = 0
                obstacles.clear()
                bad_items.clear()
                good_items.clear()
                player.x = 120
                player.y = 320
                player_vel_y = 0
                on_ground = True
                impaired = False
                impair_timer = 0

    if not game_over:

        # Background
        draw_background()

        # Gravity
        player_vel_y += gravity
        player.y += player_vel_y

        # Ground collision
        if player.y >= 320:
            player.y = 320
            player_vel_y = 0
            on_ground = True

        # Spawn items
        spawn_obstacles()

        # Move obstacles
        for obstacle in obstacles:
            obstacle.x -= scroll_speed

        for bad in bad_items:
            bad.x -= scroll_speed

        for good in good_items:
            good.x -= scroll_speed

        # Remove offscreen
        obstacles = [o for o in obstacles if o.x > -100]
        bad_items = [b for b in bad_items if b.x > -100]
        good_items = [g for g in good_items if g.x > -100]

        # Collisions
        for obstacle in obstacles:
            if player.colliderect(obstacle):
                game_over = True

        # Bad items collision
        for bad in bad_items[:]:
            if player.colliderect(bad):
                impaired = True
                impair_timer = 400
                bad_items.remove(bad)

        # Good item collision
        for good in good_items[:]:
            if player.colliderect(good):
                impaired = False
                impair_timer = 0
                good_items.remove(good)

        # Impairment timer
        if impaired:
            impair_timer -= 1
            # Screen shake
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
        else:
            offset_x = 0
            offset_y = 0

        if impair_timer <= 0:
            impaired = False

        # Draw player
        player_draw = pygame.Rect(
            player.x + offset_x,
            player.y + offset_y,
            player.width,
            player.height
        )

        pygame.draw.rect(screen, BLUE, player_draw, border_radius=15)

        # Head
        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (player_draw.centerx, player_draw.y + 18),
            14
        )

        # Body
        pygame.draw.rect(
            screen,
            BLUE,
            (player_draw.x + 15, player_draw.y + 30, 30, 25),
            border_radius=8
        )

        # Eyes (whites)
        pygame.draw.circle(screen, WHITE, (player_draw.x + 18, player_draw.y + 18), 6)
        pygame.draw.circle(screen, WHITE, (player_draw.x + 42, player_draw.y + 18), 6)

        # Eyes (pupils)
        pygame.draw.circle(screen, BLACK, (player_draw.centerx - 5, player_draw.y + 16), 2)
        pygame.draw.circle(screen, BLACK, (player_draw.centerx + 5, player_draw.y + 16), 2)

          # Obstacles
        for obstacle in obstacles:
            pygame.draw.rect(screen, RED, obstacle, border_radius=10)
 
        # Bad items
        for bad in bad_items:
            pygame.draw.circle(screen, PURPLE, bad.center, 20)
            pygame.draw.circle(screen, WHITE, bad.center, 6)
 
        # Good items
        for good in good_items:
            pygame.draw.circle(screen, GREEN, good.center, 20)
            pygame.draw.circle(screen, WHITE, good.center, 6)
 
        # Score
        score += 1
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
 
        if impaired:
            impaired_text = font.render("IMPAIRED!", True, PURPLE)
            screen.blit(impaired_text, (WIDTH // 2 - 100, 20))

        else:
        # Game over screen
        screen.fill(BLACK)
 
        over_text = big_font.render("GAME OVER", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 100))
 
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
 
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
 
    pygame.display.flip()
 
pygame.quit()
 


 