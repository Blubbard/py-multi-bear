import pygame
import sys
import traceback
import math
import time
import threading
import random

# global constants


class Cursor(object):
    '''A class for a custom animated cursor'''
    sprite=None
    UP_DOWN=1
    LEFT_RIGHT=0
    _width=30
    _height=10

    def __init__(self, pos, dir):
        '''dir is 1 (up/down) 0 (left/right)'''
        self.dir=dir
        self._rect=self._get_rect(dir, pos) 
        if Cursor.sprite==None:
            Cursor.sprite=pygame.image.load('BrickWall.jpg').convert()

    def on_click(self, pos):
        '''Define a click action'''
        # rotate the cursor 90 degrees
        if self.dir==self.UP_DOWN :
            self.dir=self.LEFT_RIGHT
        else:
            self.dir=self.UP_DOWN
        self._rect = self._get_rect(self.dir, pos)
        print "on_click rect=", self._rect

    def on_move(self, pos):
        '''define a mouse move action'''
        self._rect = self._get_rect(self.dir, pos)
        #print "on_move() rect=" , self._rect

    def get_rect(self):
        return self._rect

# Private:
    def _get_rect(self, dir, pos):
        '''return a rectangle enclosing the sprite'''
        if dir==Cursor.LEFT_RIGHT:
            rect = pygame.Rect(pos[0], pos[1], Cursor._width, Cursor._height )
        else:
            rect = pygame.Rect(pos[0], pos[1], Cursor._height, Cursor._width )
        return rect
        
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
        self.pos = pygame.Rect( pos[0], pos[1], 10 , 10 )
        self.v=10
        self.growing=[True,True] #for the 2 ends L/R or Up/Down
        print "Wall() pos=", pos


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
                    self.growing[1]=False
                if self.pos.left < wall.pos.left:
                    self.growing[0]=False
            elif self.dir==Wall.UP_DOWN and wall.dir==Wall.LEFT_RIGHT:
                if self.pos.top< wall.pos.top:
                    self.growing[0]=False
                if self.pos.bottom > wall.pos.bottom :
                    self.growing[1]=False

            if wall.pos.colliderect(self.pos):
                self.growing=[False, False]   
    
class Ball:
    '''a class for a ball'''
    def __init__(self, velocity):
        self.sprite=pygame.image.load('ball.gif').convert()
        self.pos = self.sprite.get_rect().move(0, 0)
        self.v=velocity #velocity [x, y]
        print "Ball() pos=", self.pos

    def move(self):
        a=[0,0]
        v=self.v
        v[0]+=a[0]
        v[1]+=a[1]
        self.pos = self.pos.move(self.v[0], self.v[1])

    # test for a collision with the
    # edge and bounce if needed
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

class PygameEventHandler(object)
    '''Base class for handling pygame events'''

    def __init__(self):
        #location of the last click
        self._coords=None
    
    def handle_events():
        now=time.clock()
        # detect a single click
        single_click=false
        if now -last_click[0] >= 0.5:
            if cursor!=None:
                cursor.on_click(coords)
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 event_handler.on_quit()
            elif event.type == pygame.MOUSEMOTION:
                self.on_move(pos)
                #coords=event.dict['pos']
                #print "cursor->", coords
                #if cursor!=None:
                #    cursor.on_move(coords)
                #dx, dy=event.dict['rel']
                #if event.dict['buttons'][0]==1:
                #    drag=True
            elif event.type == pygame.MOUSEBUTTONUP:
                self._coords=event.dict['pos']
                if drag:
                    #dragging must have finished
                    drag=False
                elif now-last_click[0] < 0.5:
                    # Double click!
                    #walls.append(Wall((coords), cursor.get_dir(), win_width, win_height))
                    self.on_dbl_click()
                else :
                    #just record it and wait
                    print "single_click"
                last_click = ( now, (0, 0), 0)    
    
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
    balls=[Ball([3,4])] #, Ball([4,3]), Ball([5,2])]
    walls=[Wall((100,100) , Wall.LEFT_RIGHT  , win_height, win_width) ] #, \
           #Wall((400,300) , Wall.UP_DOWN , win_height, win_width) ]

    # Create a cursor
    cursor=Cursor((100,100), Cursor.LEFT_RIGHT )

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
            # grow any of the walls if necessary
            w.grow()
            for w1 in walls:
                if w1!=w:
                    w.test_collide(w1)
            # re-draw balls
            #screen.blit(o.sprite, o.pos )
            #re-draw walls
            screen.blit(w.sprite, w.pos, w.pos )
        #delete the cursor
        if cursor!=None:
            rect=cursor.get_rect()
            screen.blit(background.background, rect, rect)     
      
        # handle mouse, keyboard and other events
        handle_events(cursor, walls, last_click, running)

        #draw the cursor
        if cursor!=None:
            rect=cursor.get_rect()
            screen.blit(cursor.sprite, rect, rect)

        # we are done so ...
        pygame.display.update()
try:
    main()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)
pygame.quit()
