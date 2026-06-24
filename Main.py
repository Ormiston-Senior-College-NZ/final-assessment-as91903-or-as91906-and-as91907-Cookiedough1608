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
ROAD = (45, 45, 45)

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
    pygame.draw.ellipse(screen, (230,230,230), (cloud[0], cloud[1], 120, 50,))x
    cloud[0] -= 1 

