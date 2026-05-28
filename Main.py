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
