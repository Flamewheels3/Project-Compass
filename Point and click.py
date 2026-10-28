'''
Have a compass in the bottom right corner of the screen
Have the text in a diffrent file to offer language options

Have a website witch they download the game from, they must first loggin to the website
We will give them a username and passwrod, the website will warn them not to give the password to games
The website will be designed as a place where you buy games, but it's just setdressing
When the game is run, it will ask you for your username and password
The goal of the game is to go throught the escape room, and delete the password

A person is helping you though the game, telling you what to do
At one point the game closes, and the person is swaped out, (the text changes colour)
At the end, it will ask you to sign into you google acount to reset the password
If you do, you get the bad end as the new person mocks you for making the same mistake twice

The gamplay will be posters, and riddles, the riddles will be based on cybersicruty
The main threats are:
    “Gratis”
    Last ned denne lenken
    Fremmede på nett - folk utgir seg ikke alltid for å være dem de egentlig er
    Aldri gjenta passord - 2 faktorisering
    Hvem vil stjele fra barn
One room per threat, where you go through diffrent puzzles
'''

'''
gameplay ideas:
Escape room:
Issue, is boring

Thoes autoflying plane games:
Issue, hard to tech players
Solutions: have gates for the player to fly through, which one is the coorect answer
'''

import pygame


class main:

    class Puzzel:
        pass

    class Info:
        pass

    class Wall:
        def __init__(self):
            self.image = None

    class Room:
        def __init__(self):
            self.north = None
            self.west = None
            self.up = None
            self.down = None
            self.east = None
            self.south = None

    def __init__(self):
        #window sizes
        self.height = 600
        self.width = 800

        #pygame logic
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.mouse.set_visible(False)

        self.running = True

        #starting room
        self.sr = self.Room()
        self.sr.north = self.Wall()
        self.sr.north.image = 'out-image-0-FormXob.b2d626284468d0d6ce6acbf00d82f712.png'

        #Charicter position
        self.current_room = self.sr
        self.direction = 'N'


    def Handle_mouse(self,event):
        pass

    def Start_Game(self):
        while self.running:

            if self.direction == 'N':
                self.screen.blit(pygame.image.load(self.current_room.north.image),(0,0))
            elif self.direction == 'E':
                self.screen.blit(pygame.image.load(self.current_room.east.image),(0,0))
            elif self.direction == 'S':
                self.screen.blit(pygame.image.load(self.current_room.south.image),(0,0))
            elif self.direction == 'W':
                self.screen.blit(pygame.image.load(self.current_room.west.image),(0,0))
            elif self.direction == 'U':
                self.screen.blit(pygame.image.load(self.current_room.up.image),(0,0))
            elif self.direction == 'P':
                self.screen.blit(pygame.image.load(self.current_room.down.image),(0,0))

            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.Handle_mouse(event)
                elif event.type == pygame.MOUSEMOTION:
                    pass
            self.screen.blit(pygame.image.load('space.gif'),(self.mouseX,self.mouseY))

                    
            
            pygame.display.update()
            
        pygame.quit()

if __name__ == '__main__':
    EscaperoomGame = main()
    EscaperoomGame.Start_Game()