import random

import pygame
from pygame.locals import *

ANIMATIONFINISHED = USEREVENT + 1
LEVELUP = USEREVENT + 2

class ResetException(Exception):
    """90 degrees, reset me"""

class Entity():

    def __init__(self, size, pos, img_name):
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.img = pygame.image.load("./assets/" + img_name).convert_alpha()
        self.surf.blit(self.img, (0,0))
        self.size = size
        self.transformed_surface = self.surf
        self.rect = Rect(pos,size)
        self.mask = pygame.mask.from_surface(self.transformed_surface)

    def render(self, screen):
        screen.blit(self.transformed_surface, self.rect)

    def update(self, scr_rect):
        raise Exception("Overload me!")

class Player(Entity):
    def __init__(self, size, pos, img_name = "chicken.png"):
        super().__init__(size, pos, img_name)
        self.since_death = 0
        self.fried = pygame.image.load("./assets/fried_chicken.png").convert_alpha()

    def death(self):
        self.rect = self.transformed_surface.get_rect(center = self.rect.center)
        if self.since_death <= 120:
            self.transformed_surface = pygame.transform.rotate(self.surf, -self.since_death*3)
            self.rect = self.transformed_surface.get_rect(center = self.rect.center)
        elif self.since_death >= 140:
            self.transformed_surface = self.fried
            self.rect.move_ip([0,(self.since_death-160)]) #negative for 20 (jump up then down)
        self.since_death+=1

    def update(self, scr_rect, move):
        self.rect.move_ip(move)
        self.rect.clamp_ip(scr_rect)

class Laser(Entity):
    def __init__(self, size, pos, img_name = "laser.png", r = None):
        super().__init__(size, pos, img_name)
        self.r = self.fill_surface(r)
        self.angle = 0

    def fill_surface(self, r = None):
        self.angle = 0      #reset relevent attributes so new sweep starts with clean surface
        self.surf = pygame.Surface(self.size, pygame.SRCALPHA) 
        scale = self.size[1]//128
        if not r: r = random.randint(1,scale-2)
        for x in range(scale):
            if x != r: self.surf.blit(self.img, (0,scale+ x*128))
        return r

    def update(self, scr_rect, cache,inc = 0):
        self.angle -= inc
        if self.angle <= -90:
            self.r = self.fill_surface()
        self.transformed_surface = pygame.transform.rotate(self.surf,self.angle)
        tr = scr_rect.topright
        self.rect = self.transformed_surface.get_rect(topright = (tr[0]+20,tr[1]-20))
        self.mask = cache[self.r][self.angle]

class Enemy(Entity):
    def __init__(self, size, pos, img_name = "dog.png"):
        super().__init__(size, pos, img_name)
        self.velocity = [random.randint(-3,-1) ,random.randint(1,4)]
        self.boost = 2

    def update(self, scr_rect, boost):
        if self.boost != boost: 
            self.velocity[0] += (boost-2); self.velocity[1]+= (boost-2)
            self.boost = boost
        self.rect.move_ip(self.velocity)
        if self.rect.top <= 0 or self.rect.bottom >= scr_rect.bottom:
            self.velocity[1] = -self.velocity[1]
        if self.rect.left <= 0 or self.rect.right >= scr_rect.right:
            self.velocity[0] = -self.velocity[0]

class Cacher(Laser):
    def __init__(self, size, pos, img_name, r):
        super().__init__(size, pos, img_name, r=r)
        self.cache = {}
        self.angle = 0.25

    def rects_are_dumb(self):
        self.angle -= 0.25
        if self.angle <= -90:
            raise ResetException()
        self.transformed_surface = pygame.transform.rotate(self.surf,self.angle)
        self.cache[self.angle] = pygame.mask.from_surface(self.transformed_surface)
