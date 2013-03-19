import pygame
import sys
import traceback
import math
import time
import threading
import random


class Wall:
    '''a class for wall that grows until it hits something'''
    sprite=None
    UP_DOWN=1
    LEFT_RIGHT=0
    
    

    def __init__(self, pos, dir, width, height):
        '''dir is 1 (up/down) 0 (left/right)'''
        self.height=height
        self.width=width
        self.dir=dir
        if Wall.sprite ==None:
            Wall.sprite=pygame.image.load('BrickWall.jpg').convert()
        self.sprite=Wall.sprite
        self.pos = pygame.Rect ( pos[0], pos[1], 10 , 10 )
        self.v=10
        self.growing=[True,True] #for the 2 ends L/R or Up/Down


    def grow(self):
        '''grow the wall until hits an edge''' 
        if self.dir==Wall.UP_DOWN:
            if self.growing[0]==True:
                self.pos.top-=self.v
                self.pos.height+=self.v
                if self.pos.top < 0:
                    self.growing[0]=False                
            if self.growing[1]==True:
                self.pos.height+=self.v
                if self.pos.bottom > self.height:
                    self.growing[1]=False
        elif self.dir==Wall.LEFT_RIGHT:
             if self.growing[0]==True:
                self.pos.left-=self.v
                self.pos.width+=self.v
                if self.pos.left < 0:
                    self.growing[0]=False                
             if self.growing[1]==True:
                self.pos.width+=self.v
                if self.pos.right > self.width:
                    self.growing[1]=False
        else:
            #shouldn't get here
            e=Exception()
            e.message="self.dir (direction) should be 0 or 1"
            raise e
 

    def test_collide(self, wall):
        if self.growing.count(True)>0:
            if self.dir==Wall.LEFT_RIGHT and wall.dir==Wall.UP_DOWN:
                if self.pos.right  > wall.pos.right:
                    growing[1]=False
                if self.pos.left < wall.pos.left:
                    growing[0]=False
            elif self.dir==Wall.UP_DOWN and wall.dir==Wall.LEFT_RIGHT:
                if self.pos.top< wall.pos.top:
                    growing[0]=False
                if self.pos.bottom > wall.pos.bottom :
                    growing[1]=False
            
                
            print "self.pos", self.pos
            print "wall.pos", wall.pos
            if wall.pos.colliderect(self.pos):
                self.growing=False   
    
class Ball:
    '''a class for ball'''
    def __init__(self, velocity):
        self.sprite=pygame.image.load('ball.gif').convert()
        self.pos = self.sprite.get_rect().move(0, 0)
        self.v=velocity #velocity [x, y]

    def move(self):
        a=[0,0]
        v=self.v
        v[0]+=a[0]
        v[1]+=a[1]
        self.pos = self.pos.move(self.v[0], self.v[1])

    # test for a collision with the
    # edge and bounce is needed
    def edge_collide(self, x, y):
        if self.pos.top < 0 :
            self.pos.top=0
            self.v[1] *= -1
        elif self.pos.bottom > y :
            self.pos.bottom=y
            self.v[1] *= -1
        if self.pos.left < 0 :
            self.pos.left=0
            self.v[0] *= -1
        elif self.pos.right > x :
            self.pos.right=x
            self.v[0] *= -1

    def test_collide(self, wall):
        if wall.pos.colliderect(self.pos):
            print self.pos
            if wall.dir==Wall.UP_DOWN:
                if self.v[0] > 0:
                    self.pos.right=wall.pos.left
                else:
                    self.pos.left=wall.pos.right
                self.v[0] *= -1
            elif wall.dir==Wall.LEFT_RIGHT:
                if self.v[1] > 0:
                    self.pos.bottom=wall.pos.top
                else:
                    self.pos.top=wall.pos.bottom
                self.v[1] *= -1
                 

            

class Background:
    ''''a class for a background'''
    def __init__(self, x, y):
        self.background = pygame.Surface((x,y))
        # crate a background the same size as the window
        self.background = self.background.convert()
        # convert the background format to an appropriate one
        self.background.fill((0,0,0))

    
def main():
    # parameters
    win_width = 512+1
    win_height = 512+1
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("Project Balls")  

    background=Background(win_height, win_width)
    # Used for detecting double-clicks.
    #            (time,            (x, y), button)
    clock=pygame.time.Clock ()
    last_click = (time.clock(),    (0, 0), -1    )
    drag=False
    running=True
    balls=[Ball([3,4]), Ball([4,3]), Ball([5,2])]
    walls=[]#[Wall((100,100) , Wall.LEFT_RIGHT  , win_height, win_width), \
           #Wall((400,300) , Wall.UP_DOWN , win_height, win_width) ]

    # Main loop
    single_click=False
    dir=Wall.UP_DOWN
    while running:
        #delete all the balls
        for o in balls:
            screen.blit(background.background, o.pos, o.pos)
        #move and render the balls
        for o in balls:
            o.move()
            o.edge_collide(win_width, win_height)
            for w in walls:
                o.test_collide(w)
            screen.blit(o.sprite, o.pos )      
        pygame.time.delay(33)
        #update all the walls
        for w in walls:
            for w1 in walls:
                if w1!=w:
                    w.test_collide(w1)
            screen.blit(o.sprite, o.pos ) 
            screen.blit(w.sprite, w.pos, w.pos )
            
        pygame.display.update()

        
        
        
        #single click
        now=time.clock()
        #print "dir:", dir, "single_click:", single_click
        if single_click==True and now -last_click[0] >= 0.5:
            single_click=False
            print "dir", dir
            if dir==Wall.LEFT_RIGHT :
                dir=Wall.UP_DOWN
            else:
                dir=Wall.LEFT_RIGHT
            print "dir", dir
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 running = False
            elif event.type == pygame.MOUSEMOTION:
                coords=event.dict['pos']
                #print "cursor->", my_mandle.scale_coords((coords))
                dx, dy=event.dict['rel']
                if event.dict['buttons'][0]==1:
                    drag=True
            elif event.type == pygame.MOUSEBUTTONUP:
                coords=event.dict['pos']
                if drag:
                    #dragging must have finished
                    drag=False
                elif now -last_click[0] < 0.5:
                    # Double click!
                    walls.append(Wall((coords), dir, win_width, win_height))
                    single_click=False
                else :
                    #single click
                    print "single_click:", single_click
                    single_click=True
                last_click = ( now, (0, 0), 0)
        



try:
    main()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)
pygame.quit()
