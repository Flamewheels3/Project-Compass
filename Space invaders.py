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
    class Projectile:
        def __init__(self):
            self.color = (200,100,100)
            self.speed = 5
            self.size = 10
            self.x = None
            self.y = None

    class Evil:
        def __init__(self):
            self.x = None
            self.y = None

            self.speed = 1

            self.ship = './Cybersikerhet/Space invaders assets/Evil-plane.png'
            self.ship = pygame.image.load(self.ship).convert_alpha()
            self.ship = pygame.transform.scale(self.ship, (50, 50))
            self.ship = pygame.transform.flip(self.ship, False, True)

            self.fire_rate = 5
            self.fire_state = 0


    def __init__(self):
        #window sizes
        self.height = 600
        self.width = 800

        #pygame logic
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.running = True
        self.FPS = 60
        self.show_hit_boxes = False

        self.ship = './Cybersikerhet/Space invaders assets/airplane-scaled.png'
        self.ship = pygame.image.load(self.ship).convert_alpha()
        self.ship = pygame.transform.scale(self.ship, (50, 50)) 

        self.bk = './Cybersikerhet/Space invaders assets/rainbow.png'
        self.bk = pygame.image.load(self.bk).convert_alpha()
        self.bk = pygame.transform.scale(self.bk, (self.width, 5000))
        self.background_scrolling_speed = 1
        self.background_location = -5000+self.height

        self.player_shot_proj = []
        self.projectile_locations = []
        self.evil_fellows = []

        self.waves = {
            -4000:[100,300,500,700],
            -2000:[100,200,300,400,500,600,700]
        }

    def shoot_player_projectile(self):
        x=self.Projectile()
        x.x = self.mouseX
        x.y = self.mouseY
        self.player_shot_proj.append(x)

    def summon_evil(self,x,y):
        temp = self.Evil()
        temp.x = x
        temp.y = y
        self.evil_fellows.append(temp)


    def Handle_mouse(self,event):
        pass

    def Start_Game(self):
        while self.running:

            self.screen.blit(self.bk,(0,self.background_location))
            self.background_location+=self.background_scrolling_speed

            if self.background_location in self.waves:
                for i in self.waves[self.background_location]:
                    self.summon_evil(i,-100)

            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        pass
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.shoot_player_projectile()
                elif event.type == pygame.MOUSEMOTION:
                    pass

            self.projectile_locations = []

            for i in self.player_shot_proj:
                pygame.draw.circle(self.screen, i.color,(i.x,i.y),i.size)
                if self.show_hit_boxes:
                    pygame.draw.rect(self.screen, (50,255,50), pygame.Rect(i.x-i.size,i.y-i.size,i.size*2,i.size*2))
                self.projectile_locations.append([pygame.Rect(i.x-i.size,i.y-i.size,i.size*2,i.size*2),i])
                i.y -= i.speed
                

            for i in self.evil_fellows:
                if self.show_hit_boxes:
                    pygame.draw.rect(self.screen,(50,255,50),pygame.Rect(i.x,i.y,50,50))

                self.screen.blit(i.ship,(i.x,i.y))
                i.y += i.speed

                #if i.fire_state == i.fire_rate

                for j in self.projectile_locations:
                    if j[0].colliderect(pygame.Rect(i.x,i.y,50,50)):
                        self.evil_fellows.remove(i)
                        self.player_shot_proj.remove(j[1])
            
            self.screen.blit(self.ship,(self.mouseX-25,self.mouseY-10))

            pygame.display.update()
            self.clock.tick(self.FPS)
            
        pygame.quit()

if __name__ == '__main__':
    EscaperoomGame = main()
    EscaperoomGame.Start_Game()