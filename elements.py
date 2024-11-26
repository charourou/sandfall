# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 09:26:32 2024

@author: gatou
"""
import pygame, math
import random as rd
from typing import Tuple, List, Type, Iterable, Callable
from copy import copy, deepcopy
from enum import Enum

from settings import *

class Dir:
    """ Defines all the possible directions """
    UP =    -1, 0
    DOWN =  1, 0
    LEFT =  0, -1
    RIGHT = 0, 1
    UP_LEFT = -1, -1
    UP_RIGHT = -1, 1
    DOWN_LEFT = 1, -1
    DOWN_RIGHT = 1, 1
    STILL = 0, 0     

class Tile(pygame.sprite.Sprite):
    name : str
    
    def __init__(self, x: int, y: int,
                 color: Tuple[int, int, int] 
                 ):

        pygame.sprite.Sprite.__init__(self)
        # position
        self.x, self.y = x, y
        
        self.color = color
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        
        # control flags
        self.next_move = None
        # self.last_update: int = 0

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
        try:
            self.image.fill(self.color)
        except:
            print(self.image)
            print(self.color)
        self.next_move = None
        
    def move(self, direction: Dir):
        self.y += direction[0]
        self.x += direction[1]

class SandTile(Tile):
    name = 'Sand'
    dry = True
    sequence = ()
    
    def __init__(self, x , y ):
        t = 120 + rd.randint(0,20)
        super().__init__(x, y,
                         (t + rd.randint(0,20), t , 0) 
                         )
    def get_wet(self):
        self.color = BROWN
        self.dry = False

class AcidTile(Tile):
    name = 'Acid'
    def __init__(self, x , y ):
        super().__init__(x, y,
                         (0, 235 + rd.randint(0,20), 0) 
                         )

class ConcreteTile(Tile):
    name = 'Concrete'
    def __init__(self, x , y ):
        t = rd.randint(0,15)
        super().__init__(x, y, (90 + t, 90 + t, 90 +t) )
        
class WaterTile(Tile):
    name = 'Water'
    def __init__(self, x , y ):
        super().__init__(x, y, (0, 0, 200 + rd.randint(0,50)) )
    
    def move(self, direction):
         super().move(direction)
         if direction == Dir.STILL:
             old_color = self.color
             self.color = (0, 0, max(150, old_color[2]-1))
         else:
             self.color = (0, 0, 200 + rd.randint(0,50))


class Sandbox:
    empty_matrix = []
    for _ in range(GRIDHEIGHT):
        empty_matrix.append([None for _ in range(GRIDWIDTH)])
    elements = {'s': SandTile, 'c': ConcreteTile, 
                'a' : AcidTile ,'w': WaterTile}
    toggle = 's'    
    
    def __init__(self, width, height):
        self.sm = deepcopy(Sandbox.empty_matrix)
        self.sprites = pygame.sprite.Group()
        
    def add_tile(self, x: int, y: int, TileType):
            if self.sm[y][x] is None: 
                particle = TileType(x, y )
                self.sm[y][x] = particle
                self.sm[y][x].add(self.sprites)
                
    def del_tile(self, x: int, y: int ):
        self.sprites.remove(self.sm[y][x])
        self.sm[y][x] = None
        
    def check_hanging(self, j , i):
        # gravity
        if j == GRIDHEIGHT -1:
            return None
        elif self.sm[j+1][i] is None:
            return Dir.DOWN
        
        # border control -> quick exit
        if i == 0 or i == GRIDWIDTH -1:
            return None
        
        belowAB = [Dir.DOWN_LEFT, Dir.DOWN_RIGHT]
        if self.sm[j+1][i]:
            rd.shuffle(belowAB)
            belowA, belowB = belowAB[0], belowAB[1]
            if self.sm[j+1][i+belowA[1]] is None:
                return belowA
            elif self.sm[j+1][i-belowA[1]] is None:
                return belowB
            else:
                return None
                
    
    def check_sliding(self, j, i) :
        '''Water particle behavior'''
        if j == GRIDHEIGHT -1:
            return None
        # border control -> quick exit
        if i == 0 or i == GRIDWIDTH -1:
            return None
        
        sideAB = [Dir.LEFT, Dir.RIGHT]
        if self.sm[j+1][i]:
            rd.shuffle(sideAB)
            sideA, sideB = sideAB[0], sideAB[1]
            if self.sm[j][i+sideA[1]] is None:
                return sideA
            elif self.sm[j][i-sideA[1]] is None:
                return sideB
            else:
                return Dir.STILL  # Output STILL ! for Water coloration
    
    def check_reaction(self,j,i):
        if j == GRIDHEIGHT - 1:
            self.del_tile(i,j)
            return True
        
        if type(self.sm[j+1][i]) in {ConcreteTile, SandTile}:
            self.del_tile(i,j)
            self.del_tile(i,j+1)
            return True
        
        if type(self.sm[j+1][i]) in {WaterTile}:
            pass
    
    def check_swapping(self,j,i):
        ''' For Sand on top of water'''
        if j == GRIDHEIGHT -1:
            return None
        
        particle = self.sm[j][i]
        overpart = self.sm[j-1][i]  
        underpart = self.sm[j+1][i]
        if type(overpart) == WaterTile and particle.dry:
            particle.get_wet()

        if type(underpart) == WaterTile:
            underpart.next_move = Dir.UP
            self.sm[j][i].get_wet()
            return Dir.DOWN
        
    
    def check_valid_move(self, new_matrix, mov, j, i):
        pass
    
    def update(self):
        new_matrix = deepcopy(Sandbox.empty_matrix)
        # for _ in range(GRIDHEIGHT):
        #     new_matrix.append([None for _ in range(GRIDWIDTH)])
        
        for j in range(GRIDHEIGHT):
            for i in hor_scan(GRIDWIDTH):
                particle = self.sm[j][i]
                if particle is None:
                    continue

                #• Where to put Acid behavior ?  
                if type(particle) == AcidTile:
                    pschit = self.check_reaction(j, i)
                    if pschit:
                        continue

                if particle.next_move: # bypass if There is an existing move.
                    mov = particle.next_move
                elif type(particle) == ConcreteTile: # Concrete doesnot fall
                    mov = None
                else: # Gravity if self.sm[j][i] exists
                    mov = self.check_hanging(j,i)
                                            
                # Water behavior -> Dir STILL is a possible outcome
                if mov is None and type(particle) == WaterTile :
                    mov = self.check_sliding(j,i)
                    
                # Sand Swapping 
                if mov is None and type(particle) == SandTile :
                    mov = self.check_swapping(j,i)
                    
                    
                if mov is None:
                    new_matrix[j][i] = particle
                        
                else: # check target destination is valid
                    if new_matrix[j+mov[0]][i+mov[1]] is None:
                        particle.move(mov)
                        new_matrix[j+mov[0]][i+mov[1]] = particle
                    else:
                        new_matrix[j][i] = particle
                 
                      
                        
        
        self.sm = new_matrix
        self.sprites.update()
    
    # def check_valid_move(self):
    #     new_matrix[j][i] = self.sm[j][i]
    
    def pencil(self, x, y):
        
        r = math.ceil(PENSIZE/2)
        for i in range(1-r,r):
            for j in range(1-r,r):
                if check_col(x+i):
                    self.add_tile(x+j, y+i, self.elements[self.toggle])
                
    


def check_col(i):
    if 0 < i < GRIDWIDTH - 1:
        return True
    else:
        return False

def hor_scan(n):
    alea = rd.randint(0,1)
    if alea:
        return range(n)
    else:
        return reversed(range(n))
    

class Arlist:
    def __init__(self, n = 0):
        self.n = n
        if n == 0:
            self.seq = [1]
        else:
            self.seq = Arlist(n-1).generate()
    
    def __repr__(self):
        str_out = ''
        for turtle in self.seq:
            str_out += str(turtle)
        return str_out
        
    def generate(self):
        vec_out = []
        vec = self.seq
        
        value, n_seq = vec[0], 0
        
        for turtle in range(len(vec)):
            if vec[turtle] == value:
                n_seq += 1
            else:
                vec_out.append(n_seq)
                vec_out.append(value)
                n_seq = 1
                value = vec[turtle]
                
        vec_out.append(n_seq)
        vec_out.append(value)
        return vec_out

# test
# print(Arlist(5))

A = Tile( 0, 0, (100,100,100))
