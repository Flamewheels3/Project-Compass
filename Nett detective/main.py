import pygame
import os
import asyncio

'''
saturday
Clock in 15:36
Clock out 17:56
monday
Clock in 22:00
Clock out 23:19
wednessday
Clock in 12:40
Clock out 14:20
'''

#todo list:
#make the resizing direction based, grab the side, resize the side
#make the resizing work on both sides
#make the cursor change when you hover over the side
#pixel world (clicker game with a messanger)
#scroll bar to the email if it's resized too wrong
#rezise the text so that it fits
#makes it so that the notification is gone, not when it's open, but when all mails are marcked as read

import pygame


class main:
    class shortcut:
        def __init__(self,main):
            self.main = main
            self.x = 0
            self.y = 1
            self.width = 50
            self.height = 50
            self.link = None
            self.selected = False
            self.hovered = False
            self.grabbed = False
            self.count_down = 0
            self.grab_offset = (0, 0)

            self.opens = main.window      # which window class this shortcut opens

        def run(self):
            # if its window is already open, bring it to the front instead of making another
            if self.link is not None and not self.link.closed:
                self.main.open_windows.remove(self.link)
                self.main.open_windows.append(self.link)
                return

            self.link = self.opens(self.main)
            self.main.open_windows.append(self.link)

        def draw(self):
            if self.selected == True:
                box = self.get_box()
                # semi-transparent fill
                fill = pygame.Surface(box.size, pygame.SRCALPHA)
                fill.fill((51, 153, 255, 90))
                self.main.screen.blit(fill, box.topleft)
                # solid border
                pygame.draw.rect(self.main.screen, (51, 153, 255), box, 1)
            
            elif self.hovered == True:
                box = self.get_box()   # a few pixels of padding around icon + label
                # semi-transparent fill
                fill = pygame.Surface(box.size, pygame.SRCALPHA)
                fill.fill((51, 153, 255, 10))
                self.main.screen.blit(fill, box.topleft)
                # solid border
                pygame.draw.rect(self.main.screen, (51, 153, 255, 80), box, 1)

            self.text_rect = self.text.get_rect(center=(self.x+self.width/2, self.y+self.height+15))

            self.main.screen.blit(self.image,(self.x,self.y))
            self.main.screen.blit(self.text, self.text_rect)

        def set_name(self,name):
            self.text = self.main.font.render(name, True, (255, 255, 255))
            self.text_rect = self.text.get_rect(center=(self.x+self.width/2, self.y+self.height+15))

        def get_box(self):
            return self.text_rect.union(pygame.Rect(self.x,self.y,self.width,self.height)).inflate(6, 6)

        def get_move_infomation(self):
            return [self.path, self.text]

        def set_icon(self,path):
            self.image = self.main.asset_path + path
            self.path = self.image
            self.image = pygame.image.load(self.image).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

    class window:
        def __init__(self, main):
            self.main = main
            self.title = 'Window'
            self.x = 100
            self.y = 100
            self.width = 300
            self.height = 200
            self.title_height = 25

            self.dragging = False
            self.drag_offset = (0, 0)
            self.closed = False
            self.resizeing = False

            self.resize_start_mouse = (0, 0)
            self.resize_start_size = (0, 0)
            self.min_width = 150
            self.min_height = 80

        def get_rect(self):
            return pygame.Rect(self.x, self.y, self.width, self.height)

        def get_title_rect(self):
            return pygame.Rect(self.x, self.y, self.width, self.title_height)

        def get_close_rect(self):
            return pygame.Rect(self.x + self.width - 22, self.y + 3, 19, 19)

        def get_resize_rect(self):
            size = 5
            return pygame.Rect(self.x+size, self.y+size, self.width-size*2, self.height-size*2)

        def handle_event(self, event):
            """Returns True if the window used the event."""
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.get_rect().collidepoint(event.pos):
                    return False
                if self.get_close_rect().collidepoint(event.pos):
                    self.closed = True
                elif self.get_title_rect().collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = (event.pos[0] - self.x, event.pos[1] - self.y)
                elif not self.get_resize_rect().collidepoint(event.pos):
                    self.resizeing = True
                    self.resize_start_mouse = event.pos
                    self.resize_start_size = (self.width, self.height)
                return True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    self.dragging = False
                    return True
                if self.resizeing:
                    self.resizeing = False
                    return True

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.x = event.pos[0] - self.drag_offset[0]
                    self.y = event.pos[1] - self.drag_offset[1]
                    # keep the title bar reachable (and above the taskbar)
                    self.x = max(-self.width + 60, min(self.x, self.main.width - 60))
                    self.y = max(0, min(self.y, self.main.height - 25 - self.title_height))
                    return True
                if self.resizeing:
                    dx = event.pos[0] - self.resize_start_mouse[0]
                    dy = event.pos[1] - self.resize_start_mouse[1]
                    self.width = max(self.min_width, self.resize_start_size[0] + dx)
                    self.height = max(self.min_height, self.resize_start_size[1] + dy)
                    return True

            return False

        def draw(self):
            screen = self.main.screen
            
            # window body + border
            pygame.draw.rect(screen, (230, 230, 230), self.get_rect())
            pygame.draw.rect(screen, (0, 60, 200), self.get_rect(), 3)
            

            # title bar
            pygame.draw.rect(screen, (0, 84, 227), self.get_title_rect(),
                             border_top_left_radius=6, border_top_right_radius=6)
            title = self.main.font.render(self.title, True, (255, 255, 255))
            screen.blit(title, (self.x + 8, self.y + (self.title_height - title.get_height()) // 2))

            # close button
            close = self.get_close_rect()
            pygame.draw.rect(screen, (200, 70, 50), close, border_radius=3)
            pygame.draw.rect(screen, (255, 255, 255), close, 1, border_radius=3)
            pygame.draw.line(screen, (255, 255, 255), (close.left + 5, close.top + 5), (close.right - 6, close.bottom - 6), 2)
            pygame.draw.line(screen, (255, 255, 255), (close.left + 5, close.bottom - 6), (close.right - 6, close.top + 5), 2)

    class email_app(window):
        def __init__(self, main):
            super().__init__(main)
            self.title = 'E-post'
            self.width = 500
            self.height = 320
            self.min_width = 300
            self.min_height = 150
            self.list_width = 160
            self.row_height = 40
            self.selected_mail = None
            main.notified = False           # opening the app clears the bell

        def get_area(self):
            return pygame.Rect(self.x + 3, self.y + self.title_height,
                               self.width - 6, self.height - self.title_height - 3)

        def get_row_rects(self):
            area = self.get_area()
            return [(mail, pygame.Rect(area.left, area.top + i * self.row_height,
                                       self.list_width, self.row_height))
                    for i, mail in enumerate(self.main.inbox)]

        def handle_event(self, event):
            used = super().handle_event(event)
            if used and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.get_area().collidepoint(event.pos):
                    for mail, rect in self.get_row_rects():
                        if rect.collidepoint(event.pos):
                            self.selected_mail = mail
                            mail['read'] = True
            return used

        def wrap(self, text, max_width):
            font = self.main.small_font
            lines = []
            for paragraph in text.split('\n'):
                line = ''
                for word in paragraph.split(' '):
                    test = (line + ' ' + word).strip()
                    if font.size(test)[0] <= max_width:
                        line = test
                    else:
                        if line:
                            lines.append(line)
                        line = word
                lines.append(line)
            return lines

        def draw_content(self):
            screen = self.main.screen
            font = self.main.small_font
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.list_width, area.height)

            # inbox list
            screen.set_clip(list_rect)
            pygame.draw.rect(screen, (245, 245, 245), list_rect)
            if not self.main.inbox:
                screen.blit(font.render('No emails', True, (120, 120, 120)),
                            (list_rect.left + 10, list_rect.top + 10))
            for mail, rect in self.get_row_rects():
                if mail is self.selected_mail:
                    pygame.draw.rect(screen, (200, 220, 255), rect)
                if not mail['read']:
                    pygame.draw.circle(screen, (51, 153, 255), (rect.left + 10, rect.centery), 4)
                screen.blit(font.render(mail['sender'], True, (0, 0, 0)), (rect.left + 20, rect.top + 4))
                screen.blit(font.render(mail['subject'], True, (90, 90, 90)), (rect.left + 20, rect.top + 21))
                pygame.draw.line(screen, (210, 210, 210), rect.bottomleft, rect.bottomright)

            # reading pane
            screen.set_clip(area)
            pygame.draw.line(screen, (180, 180, 180), list_rect.topright, list_rect.bottomright)
            if self.selected_mail:
                x = list_rect.right + 10
                y = area.top + 10
                for text in ('From: ' + self.selected_mail['sender'],
                             'Subject: ' + self.selected_mail['subject']):
                    screen.blit(font.render(text, True, (0, 0, 0)), (x, y))
                    y += 22
                pygame.draw.line(screen, (180, 180, 180), (x, y + 2), (area.right - 10, y + 2))
                y += 10
                for line in self.wrap(self.selected_mail['body'], area.right - x - 10):
                    screen.blit(font.render(line, True, (0, 0, 0)), (x, y))
                    y += 22
            screen.set_clip(None)
            #pygame.draw.rect(screen, (50,200,50), list_rect)

    class clicker_app(window):
        def __init__(self, main):
            super().__init__(main)
            self.title = 'Pixel world'
            self.width = 500
            self.height = 320
            self.min_width = 300
            self.min_height = 150
            
            self.row_height = 40
            self.selected_mail = None

            self.resize_planet([75,75])
            self.base_clicker_size = [0.15,0.234375]
            self.clicker_shrink_rate = 0.90 #how much prosent it goes down by, so it will be % of the size of the old one
            self.clicker_max_size = [0.4,0.625] #how much prosent of the width and height
            self.clicker_grow_rate = [10**-4 * i for i in [320,500]] #how much it grows by, prosent of width and height

            self.resize()

            self.planet = 0
            self.messages = False
            self.messager_length = self.width*0.25
            self.typing = False

        def get_area(self):
            return pygame.Rect(self.x + 3, self.y + self.title_height,
                               self.width - 6, self.height - self.title_height - 3)

        def get_any_unread_messages(self):
            for i in self.main.friend_list:
                if not i['read']:
                    return True
            return False

        def handle_event(self, event):
            used = super().handle_event(event) #the window.handle_event, runs and checks if it should check for mouse in this one
            if used and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.get_area().collidepoint(event.pos): #if it is clicked in the app
                    if self.selected_mail:
                        if not self.selected_mail['accepted']:
                            if self.get_accsept_button().collidepoint(event.pos):
                                self.selected_mail['accepted'] = True
                            elif self.get_deny_button().collidepoint(event.pos):
                                self.main.friend_list.remove(self.selected_mail)
                                self.selected_mail = None
                                self.resize()
                        else:
                            if self.get_message_bar().collidepoint(event.pos):
                                self.typing = ' '
                    if self.get_clicker_location().collidepoint(event.pos):
                        self.planet+=1
                        self.resize_planet([self.clicker_size[0]+self.clicker_grow_rate[0]*self.width, self.clicker_size[1]+self.clicker_grow_rate[1]*self.height])
                    elif self.get_bell_location().collidepoint(event.pos):
                        if self.messages:
                            self.messages = False
                        else:
                            self.messages = True
                        if self.selected_mail:
                            self.selected_mail = None
                            self.resize()
                    else:
                        for mail, rect in self.get_row_rects():
                            if rect.collidepoint(event.pos):
                                self.selected_mail = mail
                                mail['read'] = True
                                self.resize()
            
            if event.type == pygame.KEYDOWN and self.typing: #will type if unfocused, todo , fix
                if event.key == pygame.K_BACKSPACE:
                    self.typing = self.typing[:-1]
                elif event.key == pygame.K_RETURN:
                    if type(self.selected_mail['accepted']) == list:
                        self.selected_mail['accepted'].append([True,self.typing])
                    else:
                        self.selected_mail['accepted'] = [[True,self.typing]]
                        self.typing = False
                else:
                    self.typing += event.unicode

            return used

        def resize_planet(self, new_size):
            self.clicker_size = new_size
            self.clicker_icon = self.main.asset_path + 'earth_pixel_512.png'
            self.clicker_icon = pygame.image.load(self.clicker_icon).convert_alpha()
            self.clicker_icon = pygame.transform.scale(self.clicker_icon, self.clicker_size)

        def get_clicker_location(self): #todo i want this to be more circle like eventualy, but nor rn
            area = self.get_area()
            return pygame.rect.Rect(area.center[0]-self.clicker_size[0]/2,area.center[1]-self.clicker_size[1]/2, self.clicker_size[0], self.clicker_size[1])

        def get_bell_location(self):
            area = self.get_area()
            return pygame.rect.Rect(area.topleft[0],area.topleft[1], (self.width - 6)*0.08, (self.height-self.title_height - 3)*0.125)

        def resize(self):
            self.msg = self.main.asset_path + 'bell.png'
            if self.selected_mail:
                self.msg = self.main.asset_path + 'Evil-plane.png' #placeholder back arrow
            elif self.get_any_unread_messages(): #if unread messages
                self.msg = self.main.asset_path + 'bell_alerted.png'
            self.msg = pygame.image.load(self.msg).convert_alpha()
            self.msg = pygame.transform.scale(self.msg, ((self.width - 6)*0.08, (self.height-self.title_height - 3)*0.125))

            self.bk = self.main.asset_path + 'bg_pixel_space.png'
            self.bk = pygame.image.load(self.bk).convert_alpha()
            self.bk = pygame.transform.scale(self.bk, (self.width - 6, self.height-self.title_height - 3))
            self.resize_planet([self.width*self.base_clicker_size[0],self.height*self.base_clicker_size[1]])
        
        def wrap(self, text, max_width):
            font = self.main.small_font
            lines = []
            for paragraph in text.split('\n'):
                line = ''
                for word in paragraph.split(' '):
                    test = (line + ' ' + word).strip()
                    if font.size(test)[0] <= max_width:
                        line = test
                    else:
                        if line:
                            lines.append(line)
                        line = word
                lines.append(line)
            return lines

        def get_row_rects(self):
            area = self.get_area()
            return [(mail, pygame.Rect(area.left, area.top + i * self.row_height,
                                       self.messager_length, self.row_height))
                    for i, mail in enumerate(self.main.friend_list)]

        def get_accsept_button(self):
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.messager_length, area.height)
            
            return self.main.small_font.render('Accept', True, (50,200,50)).get_rect(topleft = (list_rect.left + 10, area.bottom - 20))

        def get_deny_button(self):
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.messager_length, area.height)
            
            return self.main.small_font.render('Deny', True, (200,50,50)).get_rect(topleft = (list_rect.left + 10 + self.messager_length/2, area.bottom - 20))

        def get_message_bar(self):
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.messager_length, area.height)
            
            return pygame.Rect(list_rect.left + 10, area.bottom - 30, self.messager_length-20, 20)

        def draw_content(self):
            screen = self.main.screen
            font = self.main.small_font
            msg_font =  self.main.smallest_font
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.messager_length, area.height)

            if self.clicker_size[0] > self.base_clicker_size[0]*self.width:
                self.resize_planet([i*self.clicker_shrink_rate for i in self.clicker_size])

            screen.blit(self.bk,(area.topleft))

            if self.messages:
                # inbox list
                screen.set_clip(list_rect)
                pygame.draw.rect(screen, (245, 245, 245), list_rect)
                if not self.main.friend_list:
                    screen.blit(font.render('No emails', True, (120, 120, 120)),
                                (list_rect.left + 10, list_rect.top + 10))
                for mail, rect in self.get_row_rects():
                    if mail is self.selected_mail:
                        pygame.draw.rect(screen, (200, 220, 255), rect)
                    if not mail['read']:
                        pygame.draw.circle(screen, (51, 153, 255), (rect.left + 10, rect.centery), 4)
                    screen.blit(font.render(mail['sender'], True, (0, 0, 0)), (rect.left + 20, rect.top + 4))
                    pygame.draw.line(screen, (210, 210, 210), rect.bottomleft, rect.bottomright)

                #reading pane
                screen.set_clip(area)
                pygame.draw.line(screen, (180, 180, 180), list_rect.topright, list_rect.bottomright)
                if self.selected_mail:
                    pygame.draw.rect(screen, (245, 245, 245), list_rect)
                    x = list_rect.left
                    y = area.top + 10
                    for text in ('',self.selected_mail['sender']):
                        screen.blit(font.render(text, True, (0, 0, 0)), (x, y))
                        y += 22
                    pygame.draw.line(screen, (180, 180, 180), [list_rect.right,y], [list_rect.left,y])

                    if not self.selected_mail['accepted']:
                        y = area.bottom - 20
                        screen.blit(font.render('Accept', True, (50,200,50)), (x + 10, y))
                        screen.blit(font.render('Deny', True, (200,50,50)), (x + 10 + self.messager_length/2, y))

                    else: 
                        #here is where the chating will happen, accepted will be the log,
                        #it will be a list of messages in order,
                        #accepted: [[True, 'this is your message, this is the first message']. [False,'this is their message, this is the second message']]
                        message_bar = self.get_message_bar()
                        y = area.bottom - 30
                        message_content = 'Send a chat'

                        pygame.draw.circle(screen, (180, 180, 180), message_bar.midright, message_bar.height/2, width = 3, draw_bottom_right=True, draw_top_right=True)
                        pygame.draw.circle(screen, (180, 180, 180), message_bar.midleft, message_bar.height/2, width = 3, draw_bottom_left=True, draw_top_left=True)
                        pygame.draw.line(screen, (180, 180, 180), message_bar.topleft, message_bar.topright, width = 3)
                        pygame.draw.line(screen, (180, 180, 180), message_bar.bottomleft, message_bar.bottomright, width = 3)

                        if self.typing:
                            message_content = self.typing

                        for line in self.wrap(message_content, message_bar.width*1.4):
                            screen.blit(msg_font.render(line, True, (130,130,130)),(self.get_message_bar().left,y))
                            y += 8

                        y = message_bar.top - 30
                        
                        if type(self.selected_mail['accepted']) == list:
                            for sent_by_user, message in reversed(self.selected_mail['accepted']): #so it does the second, then the first
                                message_box = None
                                content = []
                                if sent_by_user:
                                    y2 = y
                                    for line in self.wrap(message, message_bar.width*0.85):
                                        #.get_rect(topleft = (list_rect.left + 10 + self.messager_length/2, area.bottom - 20))
                                        content.append(msg_font.render(line, True, (80,80,80)))
                                        box = content[-1].get_rect(topleft = (self.get_message_bar().centerx,y))
                                        if message_box:
                                            message_box.union(box)
                                        else:
                                            message_box = box
                                        y += 8
                                    message_box = message_box.inflate(6, 6)
                                    pygame.draw.ellipse(screen,(100,200,100),message_box)
                                    for i in content:
                                        screen.blit(i,(message_box.left+3,y2)) #todo, is on the left side, want it on the right side
                                        y2 += 8
                                else:
                                    pass

                    y -= 10
                screen.set_clip(None)

            screen.blit(self.msg,(area.topleft))

            screen.blit(self.clicker_icon,(area.center[0]-self.clicker_size[0]/2,area.center[1]-self.clicker_size[1]/2))

            screen.blit(font.render(str(self.planet), True, (255, 255, 255)),area.midtop)

    def __init__(self):
        #window sizes
        self.height = 600
        self.width = 800

        #pygame logic
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

        self.running = True
        self.FPS = 60
        self.show_hit_boxes = False

        self.asset_path = './Nett detective assets/'

        self.bk = self.asset_path + 'windows-xp-desktop.png'
        self.bk = pygame.image.load(self.bk).convert_alpha()
        self.bk = pygame.transform.scale(self.bk, (self.width, self.height))

        self.alerted_bell = self.asset_path + 'mail_notification.png'
        self.alerted_bell = pygame.image.load(self.alerted_bell).convert_alpha()
        self.alerted_bell = pygame.transform.scale(self.alerted_bell, (30, 30))

        self.bell = self.asset_path + 'mail_plain.png'
        self.bell = pygame.image.load(self.bell).convert_alpha()
        self.bell = pygame.transform.scale(self.bell, (30,30))

        self.mouse = pygame.SYSTEM_CURSOR_ARROW
        
        self.notified = False
        self.inbox = []
        self.small_font = pygame.font.Font(None, 22)
        self.smallest_font = pygame.font.Font(None, 15)

        self.friend_list = []
        self.friend_list.insert(0, {'sender': ' ', 'accepted': False, 'read': True, 'ignor': True})
        self.messaged = False

        self.desktop_shortcuts = []
        self.open_windows = []

    def handle_task_bar(self):
        pygame.draw.rect(self.screen, (50,50,200), pygame.Rect(0,self.height-25,self.width,self.height))
        if self.notified:
            self.screen.blit(self.alerted_bell,(self.width-30,self.height-30))
        else:
            self.screen.blit(self.bell,(self.width-30,self.height-30))
    
    def Update_mouse(self,event):
        pygame.mouse.set_cursor(self.mouse)

    def handle_mouse_events(self, event):
        # windows get first pick, topmost (last in list) first
        for w in reversed(self.open_windows):
            if w.handle_event(event): #just True or false
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.open_windows.remove(w)      # bring to front
                    self.open_windows.append(w)
                if w.resizeing: #shocked this part works, self.open_windows realy is both
                    w.resize()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = None
            if self.notified and self.get_bell_rect().collidepoint(event.pos):
                self.notified = False
                self.email_shortcut.run()       # opens the app, or brings it to the front
                return
            for i in self.desktop_shortcuts:
                if i.get_box().collidepoint(event.pos):
                    clicked = i

            # select the clicked one, deselect the rest (empty desktop deselects all)
            for i in self.desktop_shortcuts:
                i.selected = (i is clicked)

            if clicked:
                clicked.grabbed = True
                clicked.grab_offset = (event.pos[0] - clicked.x, event.pos[1] - clicked.y)
                if clicked.count_down > 0:      # second click in time = double click
                    clicked.run()
                    clicked.count_down = 0
                else:
                    clicked.count_down = 30     # about 0.5 s at 60 FPS

        elif event.type == pygame.MOUSEBUTTONUP:
            for i in self.desktop_shortcuts:
                i.grabbed = False               # release everything, even if the mouse left the box

        elif event.type == pygame.MOUSEMOTION:
            for i in self.desktop_shortcuts:
                if i.grabbed:
                    i.x = event.pos[0] - i.grab_offset[0]
                    i.y = event.pos[1] - i.grab_offset[1]
                    # keep the icon (and its label) on the desktop, above the taskbar
                    i.x = max(0, min(i.x, self.width - i.width))
                    i.y = max(0, min(i.y, self.height - 25 - i.height - 30))
                i.hovered = i.get_box().collidepoint(event.pos) 

    def get_bell_rect(self):
        return pygame.Rect(self.width - 30, self.height - 30, 30, 30)

    def Friend_request(self, sender='Unknown'):
        self.friend_list.insert(1, {'sender': sender, 'accepted': False, 'read': False, 'ignor': False})
        self.messaged = True

    def Push_notification(self, subject, body, sender='Unknown'):
        self.inbox.insert(0, {'sender': sender, 'subject': subject, 'body': body, 'read': False})
        self.notified = True

    async def Start_Game(self):
        mail = self.shortcut(self)
        mail.set_icon('Evil-plane.png')
        mail.set_name('E-post')
        mail.opens = self.email_app
        mail.y = 170
        self.email_shortcut = mail
        self.desktop_shortcuts.append(mail)

        mail = self.shortcut(self)
        mail.set_icon('game_pixelworld.png')
        mail.set_name('Pixel World')
        mail.opens = self.clicker_app
        mail.y = 50
        self.desktop_shortcuts.append(mail)

        #self.Push_notification('Welcome', 'Hi! This is a test email.\n\nIf you can read this, the email app works.', 'Admin')
        self.Friend_request('Friendo')

        while self.running:

            self.screen.blit(self.bk,(0,0))

            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                self.handle_mouse_events(event)

            for i in self.desktop_shortcuts:
                if i.count_down > 0:
                    i.count_down -= 1
                i.draw()

            self.open_windows = [w for w in self.open_windows if not w.closed]
            for w in self.open_windows: #both the window and the application
                w.draw()
                w.draw_content()

            self.handle_task_bar()


            pygame.display.update()
            self.clock.tick(self.FPS)
            await asyncio.sleep(0)
            
        pygame.quit()

if __name__ == '__main__':
    EscaperoomGame = main()
    asyncio.run(EscaperoomGame.Start_Game())