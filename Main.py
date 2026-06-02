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


