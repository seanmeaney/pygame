import random
import sys

import pygame
from pygame.draw import circle
from pygame.locals import *

from entities import Cacher, Enemy, Laser, Player, ResetException, ANIMATIONFINISHED, LEVELUP

class Game():

    def __init__(self, width = 800, height = 600):
        self.width = width
        self.height = height
        self.screen,self.font = self.init_pygame()
        self.sr = self.screen.get_rect()
        self.p, self.l, self.c, self.d = self.init_data()
        self.background = pygame.image.load("./assets/background.png").convert()
        self.difficulty = 1
        self.movement = [0,0]
        self.score = 0
        self.game_over = False

    def init_pygame(self):
        pygame.init()
        pygame.key.set_repeat(1, 1)
        pygame.display.set_caption("Fried Chicken")
        pygame.mixer.Channel(0).play(pygame.mixer.Sound("./assets/unreal.xm"), loops = 4)
        return pygame.display.set_mode((self.width, self.height), pygame.SRCALPHA),pygame.font.SysFont('arial', 30)

    def init_data(self):
        c = self.cache((32,int(self.height*1.8)),(self.width - 16,0))
        p = Player((64,64),(self.height//2-64,self.width//2-64))
        l = Laser((32,int(self.height*1.8)),(self.width - 16,0))
        return p,l,c,[]

    def render(self):
        self.screen.blit(self.background,(0,0))
        self.l.render(self.screen)
        [dog.render(self.screen) for dog in self.d]
        self.dying_screen()
        self.p.render(self.screen)
        self.screen.blit(self.font.render(f"Score: {int(self.score)}", True, (255, 255, 255)),(0,0))
        pygame.display.flip()

    def dying_screen(self):
        if self.game_over:
            circle_surf = pygame.Surface((self.width,self.height))
            circle_surf.set_colorkey((248,34,217))
            circle_surf.fill((0,0,0))
            pygame.draw.circle(circle_surf,(248,34,217),self.p.rect.center,300 - (self.p.since_death*2))
            self.screen.blit(circle_surf, (0,0))

    def update(self, fps):
        pygame.display.set_caption(f"Fried Chicken - {int(fps)}fps")
        if not self.game_over:
            self.score += (1/6)*self.difficulty
            self.p.update(self.sr,(self.movement[0]*0.5*self.difficulty, self.movement[1]*0.5*self.difficulty))
            self.l.update(self.sr, self.c,0.25 * self.difficulty)
            [dog.update(self.sr,self.difficulty) for dog in self.d]
            self.collisions()
            self.movement = [0,0]
        else:
            self.p.death()

    def collisions(self):
        for ent in (self.d + [self.l]):
            relative = ((ent.rect.left - self.p.rect.left),(ent.rect.top - self.p.rect.top))
            if (self.p.mask.overlap(ent.mask, relative)):
                self.game_over = True
                pygame.time.set_timer(ANIMATIONFINISHED, 4000)
        
    #Masks are calculated pixel by pixel, calculating at runtime slows game significantally so 
    #they are cached to speed this up. Masks also have a bitdepth of 1 so they dont take much memory
    def cache(self, size, pos, img_name = "laser_basic.png"):
        cache = {}
        scale = (size[1]//128)-1
        for x in range(1,scale):
            c = Cacher(size, pos, img_name, r=x)
            self.screen.fill((0,0,0))
            count = 0
            while True:
                try: 
                    c.rects_are_dumb()
                    self.screen.blit(self.font.render(f"Caching({x}/{scale})" + '.'*(count//4), False, (255, 255, 255)),(0,0))
                    pygame.display.flip()
                except(ResetException):
                    cache[x] = c.cache; break 
                count+=1
        return cache

    def input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit(self.score)
            elif event.type == pygame.USEREVENT:
                self.difficulty +=1
                self.d.append(Enemy((48,48),(self.width-65,1)))
            elif event.type == ANIMATIONFINISHED:
                exit(self.score)
            elif event.type == LEVELUP:     #warning before speed increases
                pygame.time.set_timer(pygame.USEREVENT, 3000, True)
                pygame.mixer.Channel(1).play(pygame.mixer.Sound("./assets/level_up.wav"))
            elif event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    self.movement[1] -= 1
                if event.key == K_a:
                    self.movement[0] -= 1
                if event.key == K_s:
                    self.movement[1] += 1
                if event.key == K_d:
                    self.movement[0] += 1

def exit(score):
    print(int(score))
    pygame.quit()
    sys.exit()

def main():
    game = Game()
    clock = pygame.time.Clock()
    pygame.time.set_timer(LEVELUP, random.randint(30000, 45000))
    while True:
        game.input()
        game.update(clock.get_fps())
        game.render()
        clock.tick(60)

if __name__ == "__main__":
    main()
