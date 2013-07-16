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

    def __init__(self, pos, dir ):
        '''dir is 1 (up/down) 0 (left/right)'''
        self.dir=dir
        if dir==Cursor.UP_DOWN:
            self._height=30
            self._width=10
        else:
            self._height=10
            self._width=30
        self._rect = pygame.Rect ( pos[0], pos[1], self._width , self._height )
        if Cursor.sprite==None:
            Cursor.sprite=pygame.image.load('BrickWall.jpg').convert()

    def get_rect(self):
        '''Returns the pygame rectangle enclosing the shape'''
        return self._rect

    def on_click(self, pos):
        '''Define a click action'''
        if self.dir==Cursor.UP_DOWN :
            self.dir=Cursor.LEFT_RIGHT
        else:
            self.dir=Cursor.UP_DOWN
        # swap height and width to rotate cursor
        temp = self._width
        self._width = self._height
        self._height = temp
        #update the rectangle in which it lives
        self._rect = pygame.Rect( pos[0], pos[1], self._width, self._height )
        print "on_click() _rect=", self._rect

    def on_move(self, pos):
        '''define a mouse move action'''
        self._rect = pygame.Rect( pos[0], pos[1], self._width, self._height )
        print "on_move() _rect=" , self._rect
        
        
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
            
                
            print "self.pos", self.pos
            print "wall.pos", wall.pos
            if wall.pos.colliderect(self.pos):
                self.growing=[False , False]  
    
class Ball(object):
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
    cursor=Cursor((100,100), Cursor.LEFT_RIGHT)

    # Main loop
    single_click=False
    dir=Wall.UP_DOWN
    while running:
        pygame.time.delay(33)
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

        #delete the cursor
        if cursor!=None:
            screen.blit(background.background, cursor.get_rect(),cursor.get_rect())

            
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 running = False
            elif event.type == pygame.MOUSEMOTION:
                coords=event.dict['pos']
                #print "cursor->", coords
                if cursor!=None:
                    cursor.on_move(coords)
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
                    if cursor!=None:
                        cursor.on_click(coords)
                    single_click=True
                last_click = ( now, (0, 0), 0)
                
        #reposition the cursor
        if cursor!=None:
            screen.blit(cursor.sprite, cursor.get_rect(), cursor.get_rect() )

        # we are done so ...
        pygame.display.update()

try:
    main()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)
pygame.quit()
