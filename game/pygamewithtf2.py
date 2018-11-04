import pygame
import time
import random
import numpy as np
import math
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter

#MAKE FUNCTIONS OF ENVIRONMENT RESET AN ENV STEP
#THE GAME PART====================================================
#we always have to initialise this
pygame.init()

#setting the size of the screen
display_width = 800
display_height = 600


#this is color definition, RGB ofcourse
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
block_color = (15,122,125)

#then we get to defining the game window
gameDisplay = pygame.display.set_mode((display_width,display_height)) #this is just a tuple as a parameter
#after that we name the game
pygame.display.set_caption('My racey game')
#now we define the games clock
clock = pygame.time.Clock()
#load up the image
carImg = pygame.image.load('racecar.png')

class GameState():

    def __init__(self):
        #car dimensions
        self.car_width= 73
        #game parameters
        self.x = (display_width*0.45)
        self.y = (display_height*0.8)
                
        self.x_change =0
        self.crashed = False
        self.thing_startx = random.randrange(0, display_width)
        self.thing_starty = -600 # the object is gonna spawn off the screen
        self.thing_speed =7
        self.thing_width = 70
        self.thing_height = 70
        self.num_steps = 0
        self.dodged = 0
        self.reward = 0
        
    def __str__(self):
        return(str(self.dodged))
    
    def thing_dodged(count, self):
        font= pygame.font.SysFont(None, 25)
        text = font.render("Dodged : " + str(count), True, black)
        gameDisplay.blit(text, (0,0))

    def things(self, thingx, thingy, thingw, thingh, color):
        pygame.draw.rect(gameDisplay, color, [thingx, thingy,thingw,thingh])
        thingY = int(thingy)
        thingX = int(thingx)
        font1 = pygame.font.SysFont(None, 25)
        text11 = font1.render("block y:" + str(thingY), True, black)
        text12 = font1.render("block x:" + str(thingX), True, black)
        gameDisplay.blit(text11, (100,0))
        gameDisplay.blit(text12, (200,0))
        #this will draw a box on our screen
        
    def car(self, x,y):
        gameDisplay.blit(carImg, (x,y))
        font = pygame.font.SysFont(None, 25)
        text1 =font.render("x :" +str(x), True, black)
        text2 = font.render("y :" +str(y), True, black)
        gameDisplay.blit(text1, (100,25))#this is to get the x coordinate of the car.
        gameDisplay.blit(text2, (200,25))
        #so this blit function is gonna kinda put the image at the tuple (x,y)

    def text_object(self, text, font):
        textsurface = font.render(text, True, black)
        return textsurface, textsurface.get_rect()

    def message_display(self, text):
        largerText = pygame.font.Font('freesansbold.ttf', 115)
        #so the text will be encased by its rectangle which we can use to place it on the screen
        TextSurf, TextRect = self.text_object(text, largerText)
        #now we anna centre it on the screen
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf,TextRect) #kinda like committing it to the screen
        pygame.display.update() #so you always have to use update after blit, its kinda like
        #it computes the thing but we need to update it to the new framw to see it

        #the message will show for 2 seconds
        time.sleep(2)
        #after that time it starts the game again
        #game_loop()

    def reset(self):
        #car dimensions
        self.car_width= 73
        #game parameters
        self.x = (display_width*0.45)
        self.y = (display_height*0.8)
                
        self.x_change =0

        self.thing_startx = random.randrange(0, display_width)
        self.thing_starty = -600 # the object is gonna spawn off the screen
        self.thing_speed =7
        self.thing_width = 70
        self.thing_height = 70

        self.dodged = 0

    def crash(self):
        self.message_display('You Crashed!')
        self.reset()

    def sum_readings(self, readings):
        total = 0
        for i in readings:
            total+=i
        return total

    
    def frame_steps(self, action):
        #EVENT HANDLER
        for event in pygame.event.get():
        #this above creates a list of events that happen
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        if action == 0:
            #move right
            self.x_change = 5
            self.x+=self.x_change
        elif action == 1:
            #move left
            self.x_change = -5
            self.x+=self.x_change
        elif action ==2:
            #do nothing
            self.x_change = 0
            self.x+=self.x_change
            
        #DRAW TO SCREEN
        gameDisplay.fill(white)
        self.things(self.thing_startx, self.thing_starty, self.thing_width, self.thing_height, block_color)
        self.thing_starty+=self.thing_speed
        self.car(self.x, self.y)
        self.thing_dodged(int(self.dodged))

        readings = self.get_readings()
        
        #LOGIC HANDLER
        if self.x>display_width - self.car_width or self.x<0:
            self.crash()
            self.reward = -500

        #repeating the 'things'
        if self.thing_starty>display_height:
            self.thing_starty = -self.thing_height
            self.thing_startx = random.randrange(0, display_width)
            self.dodged+=1
            self.reward = -5 + int(self.sum_readings(readings)/10)
            

        if self.y<self.thing_starty + self.thing_height:
            if self.x>self.thing_startx and self.x<self.thing_startx + self.thing_width or self.x +self.car_width>self.thing_startx and self.x+self.car_width<self.thing_startx+self.thing_width:
                self.crash()
                self.reward = -500


        if self.num_steps % 5 == 0:
            if self.thing_speed < 15:
                self.thing_speed+=0.1

        
        pygame.display.update()
        clock.tick(60)

       # readings=[]
        #NOW HERE GET THE CURRENT CAR POSITION, OBSTACLE POSITIONS, REWARDS ETC
        
        #set the rewards

        self.num_steps+=1

        print("reward ", self.reward)
        state = np.array([readings])
        print(state)

        return self.reward, state

    def get_readings(self):
        readings= []
        car_x = self.x
        car_y = self.y
        obstacle_x = self.thing_startx
        obstacle_y = self.thing_starty
        distance_from_car = math.sqrt((obstacle_x-car_x)**2+(obstacle_y-car_y)**2)
        readings.append(car_x)
        #readings.append(car_y)
        readings.append(obstacle_x)
        readings.append(obstacle_y)
        #readings.append(distance_from_car)
        return readings
    
if __name__=="__main__":
    game_state = GameState()
    while True:
        game_state.frame_steps((random.randint(0, 2)))













        



        
