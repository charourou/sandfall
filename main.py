# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 07:30:59 2024
SandFall
@author: gatou
"""

import pygame

from settings import *
from elements import Tile, Sandbox

def get_mouse_position():
    mouse_pos = pygame.mouse.get_pos()
    mouse_x = int(mouse_pos[0] / TILESIZE) 
    mouse_y = int(mouse_pos[1] / TILESIZE) 
    return mouse_x, mouse_y

def main():
    # Game Setup
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT)) 
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    # Initialize
    Demo = Sandbox(GRIDWIDTH, GRIDHEIGHT)
    
    run = True
    while run:  
        dt = clock.tick(FPS) / 1000
        # events
        mouse_position = get_mouse_position()
        if pygame.mouse.get_pressed()[0]:
            Demo.pencil(mouse_position[0], mouse_position[1])
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    Demo.toggle = 'a'
                if event.key == pygame.K_s:
                    Demo.toggle = 's'
                if event.key == pygame.K_w:
                    Demo.toggle = 'w'   
                if event.key == pygame.K_c:
                    Demo.toggle = 'c' 

        # update
        Demo.update()
        pygame.display.update()
        
        # draw
        WINDOW.fill(DARKGREY)
        Demo.sprites.draw(WINDOW)
        
        
    pygame.quit()
    
main()