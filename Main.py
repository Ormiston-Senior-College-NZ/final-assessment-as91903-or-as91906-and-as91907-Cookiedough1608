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

# Colors
WHITE =(255, 255, 255)
BLACK =(20, 20, 20)
BLUE = (50, 120, 255)
RED = (220, 60, 60)
GREEN = (50, 220, 100)
YELLOW = (225, 220, 50)
PURPLE = (120, 180, 255)
SKY = (120, 180, 255)
ROAD = (45, 45,  45)

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

# Stars 
stars = []
for i in range(80): 
    stars.append([random.randint(0, WIDTH), random.randint(0,HEIGHT)])

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
        color = ( 
            30, 
            30 + y // 4, 
            70 + y // 3
        ) 
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

# Stars 
for star in stars: 
    pygame.draw.circle(screen, WHITE, star, 2)

# Clouds 
for cloud in clouds: 
    pygame.draw.ellipse(screen, (230,230,230), (cloud[0], cloud[1], 120, 50,))
    cloud[0] -= 1 

    if cloud[0] < -150:
            cloud[0] = WIDTH + random.randint(50, 300)
            cloud[1] = random.randint(20, 150)

    # Buildings
    for i in range(12):
        x = i * 120
        building_height = random.randint(120, 280)

        pygame.draw.rect(
            screen,
            (40, 40, 60),
            (x, HEIGHT - 120 - building_height, 90, building_height)
        )

   # Windows
        for row in range(8):
            for col in range(3):
                wx = x + 15 + col * 25
                wy = HEIGHT - 100 - building_height + row * 30

                pygame.draw.rect(
                    screen,
                    YELLOW,
                    (wx, wy, 10, 15)
                )

 # Road
    pygame.draw.rect(screen, ROAD, (0, 380, WIDTH, 120))

    # Road lines
    for i in range(20):
        pygame.draw.rect(
            screen,
            WHITE,
            (i * 80 - (score % 80), 435, 40, 8)
        )

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

# Bad item collision
        for bad in bad_items:
            if player.colliderect(bad):
                impaired = True
                impair_timer = 400
                bad_items.remove(bad)

# Good item collision
        for good in good_items:
            if player.colliderect(good):
                impaired = False
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

        pygame.draw.rect(screen, BLUE, player_draw, border_radius=12)

# Eyes
        pygame.draw.circle(screen, WHITE, (player_draw.x + 18, player_draw.y + 18), 6)
        pygame.draw.circle(screen, WHITE, (player_draw.x + 42, player_draw.y + 18), 6)

 # Obstacles
        for obstacle in obstacles:
            pygame.draw.rect(screen, RED, obstacle, border_radius=10)

# Bad items
        for bad in bad_items:
            pygame.draw.circle(screen, PURPLE, bad.center, 20)

# Good items
        for good in good_items:
            pygame.draw.circle(screen, GREEN, good.center, 20)
