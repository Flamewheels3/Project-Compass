import pygame
import os
import asyncio
import json
import random
import hashlib
import hmac
import math
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
1 hour 10/27/26
wednessday
Clock in 8:15
Clock out 3:36
wdnessday
Clock in 12:15
Clock out 3:30 ish
'''

#cd Cybersikerhet
#pygbag --build "Nett detective/main.py"
#Copy-Item -Recurse -Force "Nett Detective\build\web\*" docs

#todo list (still open):
#scroll bar to the email if it's resized too small
#rezise the text so that it fits

#done in this version:
#notification bell is on until ALL mails are read (not just when E-post is opened)
#prestige in Pixel World
#list of unsafe passwords that are compromised automatically
#sticky note with missions in the top right corner
#icons unlock one by one
#shortcuts are placed on a grid and snap to it
#report button on emails and on friends
#summary at the end (also F9 for testing, and the 'Oppsummering' icon once it has been unlocked)

PRESTIGE_BASE = 1_000_000   # planets needed for the first prestige (x2 for the second, and so on)

# passwords that are "already known to hackers": using one marks the account as unsafe straight away
UNSAFE_PASSWORDS = {
    '1234', '12345', '123456', '1234567', '12345678', '123456789', '1234567890', '0000', '1111', '111111',
    '000000', '123123', 'password', 'password1', 'password123', 'passord', 'passord1', 'passord123',
    'qwerty', 'qwerty123', 'qwertyuiop', 'abc123', 'abcd', 'abcd1234', 'letmein', 'welcome', 'admin',
    'admin123', 'iloveyou', 'monkey', 'dragon', 'master', 'login', 'hei123', 'hallo', 'hallo123',
    'norge', 'norway', 'fotball', 'football', 'baseball', 'princess', 'sunshine', 'superman', 'pokemon',
    'minecraft', 'roblox', 'fortnite', 'amogus', 'test', 'test123', 'secret', 'hemmelig', 'passw0rd',
    'p@ssw0rd', 'pixelworld', 'pixel', 'planet', 'jorda',
}

FRIEND_REPORT_POPUP = {
    'ShadowX': 'Bra jobba! ShadowX spurte hvor gammel du er, hva du heter på ekte og ville flytte samtalen til andre apper. '
               'Det er faresignaler. Fortell alltid en voksen du stoler på hvis noen på nett får deg til å føle deg utrygg.',
    'Mika': 'Riktig! Mika ville låne kontoen din. Du skal aldri låne bort kontoen eller passordet ditt, heller ikke til venner. '
            'Si nei, og fortell det gjerne til en voksen.',
    'Filip': 'Takk for at du sa fra! Filip var egentlig en snill venn, men det er alltid greit å rapportere når du er usikker. '
             'Les gjerne hva personen faktisk skriver før du bestemmer deg.',
    'default': 'Takk for at du sa fra! Er du usikker på noen på nett, så spør en voksen du stoler på.',
}

# what the summary says about each friend: (was it right?, text). None = neutral
FRIEND_FEEDBACK = {
    'ShadowX': {
        'reported': (True, 'Du rapporterte og blokkerte ShadowX. Riktig! Folk som spør om alder, ekte navn og bilder, eller som vil '
                           'flytte samtalen til andre apper, er et faresignal. Fortell også en voksen du stoler på.'),
        'denied': (True, 'Du sa nei til ShadowX. Bra! Neste gang kan du også rapportere og si fra til en voksen.'),
        'accepted': (False, 'Du ble venn med ShadowX. Han spurte hvor gammel du er, hva du heter og ba om bilde. Det er faresignaler. '
                            'Rapporter og fortell en voksen når noen gjør deg utrygg.'),
        'pending': (True, 'Du svarte aldri på forespørselen fra ShadowX. Det er trygt, men du kunne også rapportert den.'),
    },
    'Mika': {
        'reported': (True, 'Du rapporterte og blokkerte Mika. Riktig! Å be om å låne kontoen din er ikke greit.'),
        'denied': (True, 'Du sa nei til Mika. Bra! Kontoen din er din.'),
        'accepted': (None, 'Mika ba om å låne kontoen din. Du skal aldri låne bort konto eller passord, heller ikke til venner. '
                           'Tenk over hva du svarte.'),
        'pending': (None, 'Du svarte ikke på forespørselen fra Mika. Hun ville senere ha lånt kontoen din, så det er helt greit.'),
    },
    'Filip': {
        'reported': (None, 'Filip var snill og ufarlig. Det er greit å rapportere når du er usikker, men sjekk gjerne hva '
                           'personen faktisk skriver.'),
        'denied': (None, 'Du sa nei til Filip, som var snill. Du bestemmer selv hvem du vil snakke med.'),
        'accepted': (True, 'Filip var en god venn. Å støtte hverandre og passe på hverandre er viktig på nett også.'),
        'pending': (None, 'Du svarte aldri på forespørselen fra Filip.'),
    },
}

SUMMARY_RULES = [
    'Del aldri passordet ditt med noen. Bare du (og en voksen du stoler på) skal vite det.',
    'Ikke klikk på lenker som lover gratis ting.',
    'Hvis noen på nett spør om personlige ting eller får deg til å føle deg utrygg: rapporter, og fortell det til en voksen.',
]


class main:
    class shortcut:
        def __init__(self,main):
            self.main = main
            self.name = ''
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

            self.visible = True      # False until it has been unlocked
            self.unlock = None       # function that returns True when it should unlock

            self.opens = main.window # which window class this shortcut opens

        def run(self):
            # if its window is already open, bring it to the front instead of making another
            if self.link is not None and not self.link.closed:
                self.main.open_windows.remove(self.link)
                self.main.open_windows.append(self.link)
                return

            self.link = self.opens(self.main)
            self.main.open_windows.append(self.link)

        def draw(self):
            if not self.visible:
                return

            self.update_text_rect()

            if self.selected == True:
                box = self.get_box()
                # semi-transparent fill
                fill = pygame.Surface(box.size, pygame.SRCALPHA)
                fill.fill((51, 153, 255, 90))
                self.main.screen.blit(fill, box.topleft)
                # solid border
                pygame.draw.rect(self.main.screen, (51, 153, 255), box, 1)

            elif self.hovered == True:
                box = self.get_box() # a few pixels of padding around icon + label
                # semi-transparent fill
                fill = pygame.Surface(box.size, pygame.SRCALPHA)
                fill.fill((51, 153, 255, 30))
                self.main.screen.blit(fill, box.topleft)
                # solid border
                pygame.draw.rect(self.main.screen, (51, 153, 255), box, 1)

            self.main.screen.blit(self.image,(self.x,self.y))
            self.main.screen.blit(self.shadow, self.text_rect.move(1, 1))
            self.main.screen.blit(self.text, self.text_rect)

        def set_name(self,name):
            self.name = name
            label = self.main.fit_text(name, 96)
            self.text = self.main.small_font.render(label, True, (255, 255, 255))
            self.shadow = self.main.small_font.render(label, True, (0, 0, 0))
            self.update_text_rect()

        def update_text_rect(self):
            self.text_rect = self.text.get_rect(center=(self.x+self.width/2, self.y+self.height+14))

        def get_box(self):
            self.update_text_rect()
            return self.text_rect.union(pygame.Rect(self.x,self.y,self.width,self.height)).inflate(6, 6)

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
            self.edge_size = 6                       # how thick the grab zone is, in pixels
            self.resize_edges = (False, False, False, False)   # left, right, top, bottom
            self.resize_start_rect = pygame.Rect(0, 0, 0, 0)
            self.min_width = 150
            self.min_height = 80
            self.maximized = False
            self.restore_rect = None
            self.can_maximize = True      # set to False for windows with a fixed layout

        def get_rect(self):
            return pygame.Rect(self.x, self.y, self.width, self.height)

        def get_title_rect(self):
            return pygame.Rect(self.x, self.y, self.width, self.title_height)

        def get_close_rect(self):
            return pygame.Rect(self.x + self.width - 22, self.y + 3, 19, 19)

        def get_edges(self, pos):
            if self.maximized:
                return (False, False, False, False)
            r = self.get_rect()
            e = self.edge_size
            return (pos[0] < r.left + e,       # left
                    pos[0] >= r.right - e,     # right
                    pos[1] < r.top + e,        # top
                    pos[1] >= r.bottom - e)    # bottom

        def get_max_rect(self):
            return pygame.Rect(self.x + self.width - 44, self.y + 3, 19, 19)

        def on_resize(self):
            pass                          # windows override this to rebuild size-dependent things

        def draw_content(self):
            pass                          # windows override this to draw what is inside them

        def toggle_maximize(self):
            if self.maximized:
                r = self.restore_rect
                self.x, self.y, self.width, self.height = r.x, r.y, r.width, r.height
                self.maximized = False
            else:
                self.restore_rect = self.get_rect()
                self.x, self.y = 0, 0
                self.width = self.main.width
                self.height = self.main.height - 40      # leave the taskbar visible
                self.maximized = True
            self.on_resize()

        def handle_event(self, event):
            """Returns True if the window used the event."""
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.get_rect().collidepoint(event.pos):
                    return False
                if self.get_close_rect().collidepoint(event.pos):
                    self.closed = True
                elif self.can_maximize and self.get_max_rect().collidepoint(event.pos):
                    self.toggle_maximize()
                else:
                    edges = self.get_edges(event.pos)
                    if any(edges):                       # edges first, so the top edge wins over the title bar
                        self.resizeing = True
                        self.resize_edges = edges
                        self.resize_start_mouse = event.pos
                        self.resize_start_rect = self.get_rect()
                    elif self.get_title_rect().collidepoint(event.pos):
                        self.dragging = True
                        self.drag_offset = (event.pos[0] - self.x, event.pos[1] - self.y)
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
                    left, right, top, bottom = self.resize_edges
                    r = self.resize_start_rect
                    dx = event.pos[0] - self.resize_start_mouse[0]
                    dy = event.pos[1] - self.resize_start_mouse[1]

                    if right:
                        self.width = max(self.min_width, r.width + dx)
                    if left:
                        new_left = min(r.left + dx, r.right - self.min_width)
                        self.x = new_left
                        self.width = r.right - new_left
                    if bottom:
                        self.height = max(self.min_height, r.height + dy)
                    if top:
                        new_top = min(max(0, r.top + dy), r.bottom - self.min_height)
                        self.y = new_top
                        self.height = r.bottom - new_top
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

            if self.can_maximize:
                m = self.get_max_rect()
                pygame.draw.rect(screen, (60, 130, 220), m, border_radius=3)
                pygame.draw.rect(screen, (255, 255, 255), m, 1, border_radius=3)
                if self.maximized:      # restore icon: two overlapping squares
                    pygame.draw.rect(screen, (255, 255, 255), (m.left + 7, m.top + 4, 8, 8), 1)
                    pygame.draw.rect(screen, (255, 255, 255), (m.left + 4, m.top + 7, 8, 8), 1)
                else:                   # maximize icon: one square
                    pygame.draw.rect(screen, (255, 255, 255), (m.left + 4, m.top + 4, 11, 11), 2)

    class message_window(window):
        """A small window that just shows some text (report feedback, prestige info, ...)."""
        def __init__(self, main, title, text, width=380):
            super().__init__(main)
            self.title = title
            self.text = text
            self.width = width
            self.can_maximize = False
            lines = main.wrap_text(text, width - 36)
            self.height = self.title_height + 30 + len(lines) * 22 + 10
            self.min_width = width
            self.min_height = self.height
            self.x = (main.width - width) // 2 + random.randint(-30, 30)
            self.y = max(20, (main.height - self.height) // 2 - 40 + random.randint(-20, 20))

        def draw_content(self):
            lines = self.main.wrap_text(self.text, self.width - 36)
            y = self.y + self.title_height + 15
            for line in lines:
                self.main.screen.blit(self.main.small_font.render(line, True, (0, 0, 0)), (self.x + 18, y))
                y += 22

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
            self.link_rect = None
            self.report_rect = None

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
                    if self.report_rect and self.selected_mail and self.report_rect.collidepoint(event.pos):
                        self.main.report_mail(self.selected_mail)
                    elif self.link_rect and self.link_rect.collidepoint(event.pos):
                        self.main.scam_clicked()

                    for mail, rect in self.get_row_rects():
                        if rect.collidepoint(event.pos):
                            self.selected_mail = mail
                            mail['read'] = True
                            self.main.save_inbox()
            return used

        def wrap(self, text, max_width):
            return self.main.wrap_text(text, max_width)

        def draw_content(self):
            screen = self.main.screen
            font = self.main.small_font
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.list_width, area.height)
            self.link_rect = None
            self.report_rect = None

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
                mail = self.selected_mail
                x = list_rect.right + 10
                y = area.top + 10
                for text in ('From: ' + mail['sender'],
                             'Subject: ' + mail['subject']):
                    screen.blit(font.render(text, True, (0, 0, 0)), (x, y))
                    y += 22
                pygame.draw.line(screen, (180, 180, 180), (x, y + 2), (area.right - 10, y + 2))
                y += 10
                for line in self.wrap(mail['body'], area.right - x - 10):
                    screen.blit(font.render(line, True, (0, 0, 0)), (x, y))
                    y += 22

                if mail.get('scam'):
                    if mail.get('reported'):
                        note = font.render('Du har rapportert denne e-posten. \n Lenken er blokkert.', True, (120, 120, 120))
                        screen.blit(note, (x, y + 6))
                    else:
                        link = font.render(mail['scam'], True, (0, 0, 238))
                        self.link_rect = link.get_rect(topleft=(x, y + 6))
                        screen.blit(link, self.link_rect)
                        pygame.draw.line(screen, (0, 0, 238), self.link_rect.bottomleft, self.link_rect.bottomright)   # underline

                # report button (top right of the reading pane)
                if mail.get('reported'):
                    label = font.render('Rapportert', True, (120, 120, 120))
                    screen.blit(label, (area.right - label.get_width() - 10, area.top + 10))
                else:
                    self.report_rect = pygame.Rect(area.right - 88, area.top + 8, 78, 20)
                    pygame.draw.rect(screen, (200, 70, 50), self.report_rect, border_radius=4)
                    label = font.render('Rapporter', True, (255, 255, 255))
                    screen.blit(label, label.get_rect(center=self.report_rect.center))
            screen.set_clip(None)

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
            self.clicker_shrink_rate = 0.9 #how much prosent it goes down by, so it will be % of the size of the old one
            self.clicker_max_size = [0.4,0.625] #how much prosent of the width and height
            self.clicker_grow_rate = [10**-4 * i for i in [320,500]] #how much it grows by, prosent of width and height

            self.resize()
            self.load()

            self.messages = False
            self.messager_length = self.width*0.25
            self.shop_length = self.messager_length
            self.typing = None              # None = not typing, a string = the message being typed
            self.friend_multiplier = {'Filip': 1, 'Mika': 0, 'ShadowX': 0.1}

            self.auto_save_timer = 0
            self.auto_save_intervouls = 100

            self.prestige_confirm_until = 0

            main.stats['opened_pixel'] = True

            self.num = 0

            # images are loaded once here instead of every frame
            self.shop_icons = {}
            self.rotating_icons = {}
            self.rotating_images = {}
            for i in self.shop_list:
                icon = pygame.image.load(self.main.asset_path + i['asset']).convert_alpha()
                self.shop_icons[i['sender']] = pygame.transform.scale(icon, (40, 40))
                self.rotating_icons[i['sender']] = [random.randint(0,360) for _ in range(i['number'])] #it will be [deg,deg], where it is degresse on a loop, with some minor shaking, like a sin function
                icon = self.main.asset_path + i['sender'] + '.png'
                icon = pygame.image.load(icon).convert_alpha()
                icon = pygame.transform.scale(icon, (10,10))
                self.rotating_images[i['sender']] = icon

        def get_area(self):
            return pygame.Rect(self.x + 3, self.y + self.title_height,
                               self.width - 6, self.height - self.title_height - 3)

        def get_any_unread_messages(self):
            for i in self.main.friend_list:
                if not i['read']:
                    return True
            return False

        def check_messages(self):
            for friend in self.main.friend_list:
                script = self.main.message_script.get(friend['sender'])
                if not script or not friend['accepted']:       # no script, or not accepted yet
                    continue
                i = friend['next']
                if i >= len(script):                            # everything already sent
                    continue
                needed, text = script[i]
                if self.planet >= needed:
                    if self.main.Send_message(friend['sender'], text):
                        friend['next'] += 1

        # ---------- prestige ----------
        def multiplier(self):
            return 1 + self.prestige

        def prestige_cost(self):
            return PRESTIGE_BASE * (self.prestige + 1)

        def can_prestige(self):
            return self.planet >= self.prestige_cost()

        def get_prestige_button(self):
            area = self.get_area()
            b = pygame.Rect(0, 0, 130, 24)
            b.center = (area.centerx, area.bottom - 22)
            return b

        def click_prestige(self):
            now = pygame.time.get_ticks()
            if now < self.prestige_confirm_until:        # second click within 3 s = confirmed
                self.do_prestige()
            else:
                self.prestige_confirm_until = now + 3000

        def do_prestige(self):
            self.prestige += 1
            self.prestige_confirm_until = 0
            self.planet = 0
            for item in self.shop_list:
                item['number'] = 0
            self.rotating_icons = {i['sender']: [] for i in self.shop_list}
            self.reload_planet()

            self.main.stats['prestiged'] = True
            self.main.stats['prestige_count'] = self.prestige
            if self.main.unsafe and not self.main.warning_sent:
                # planets were reset, so make sure the security warning can still arrive
                self.main.unsafe_goal = min(self.main.unsafe_goal, 100)
                self.main.update_save(unsafe_goal=self.main.unsafe_goal)
            self.save()
            self.main.open_message('Prestige!',
                                   f'Prestige {self.prestige}! Alt starter på nytt, men nå tjener du {int(100 * self.prestige)} % mer på alt.')

        # ---------- friends / reporting ----------
        def get_report_button(self):
            area = self.get_area()
            return pygame.Rect(area.left + self.messager_length - 62, area.top + 43, 58, 17)

        def report_selected_friend(self):
            friend = self.selected_mail
            self.selected_mail = None
            self.typing = None
            self.main.report_friend(friend)
            self.resize()
            self.save()

        # ---------- events ----------
        def handle_event(self, event):
            used = super().handle_event(event) #the window.handle_event, runs and checks if it should check for mouse in this one
            if used and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.get_area().collidepoint(event.pos): #if it is clicked in the app
                    if self.messages and self.selected_mail and self.get_report_button().collidepoint(event.pos):
                        self.report_selected_friend()
                    elif self.can_prestige() and self.get_prestige_button().collidepoint(event.pos):
                        self.click_prestige()
                    else:
                        self.handle_area_click(event.pos)

            if event.type == pygame.KEYDOWN and self.typing is not None:
                self.handle_typing(event)

            if self.closed:
                self.save()

            return used

        def handle_area_click(self, pos):
            if self.selected_mail:
                if not self.selected_mail['accepted']:
                    if self.get_accsept_button().collidepoint(pos):
                        self.selected_mail['accepted'] = True
                        if self.selected_mail['sender'] in self.main.message_script:
                            self.main.stats['accepted_friend'] = True
                            self.main.save_progress()
                        self.save()
                    elif self.get_deny_button().collidepoint(pos):
                        name = self.selected_mail['sender']
                        self.main.friend_list.remove(self.selected_mail)
                        self.main.stats.setdefault('denied_friends', []).append(name)
                        self.main.save_progress()
                        self.selected_mail = None
                        self.resize()
                        self.save()
                else:
                    if self.get_message_bar().collidepoint(pos):
                        self.typing = ''

            if self.get_clicker_location().collidepoint(pos):
                self.planet += self.multiplier() + self.shop_list[0]['number']
                self.resize_planet([self.clicker_size[0]+self.clicker_grow_rate[0]*self.width, self.clicker_size[1]+self.clicker_grow_rate[1]*self.height])

            elif self.get_bell_location().collidepoint(pos):
                if self.selected_mail:
                    self.selected_mail = None
                    self.typing = None
                    self.resize()
                elif self.messages:
                    self.messages = False
                else:
                    self.messages = True
            else:
                if self.messages:
                    for mail, rect in self.get_row_rects():
                        if rect.collidepoint(pos) and not mail.get('ignor'):
                            self.selected_mail = mail
                            self.typing = None
                            mail['read'] = True
                            self.resize()
                for mail, rect in self.get_shop_rects():
                    if rect.collidepoint(pos):
                        if self.planet >= int(mail['price']):
                            mail['number'] += 1
                            if mail['sender'] in self.rotating_icons:
                                self.rotating_icons[mail['sender']].append(random.randint(0,360))
                            else:
                                self.rotating_icons[mail['sender']] = [random.randint(0,360)]
                            self.planet -= int(mail['price'])
                            self.main.stats['bought'] = True
                            self.save()
                        self.resize()

        def handle_typing(self, event):
            if not self.selected_mail:
                self.typing = None
                return
            # only the top window gets the keyboard
            if not (self.main.open_windows and self.main.open_windows[-1] is self):
                return

            if event.key == pygame.K_BACKSPACE:
                self.typing = self.typing[:-1]
            elif event.key == pygame.K_RETURN:
                text = self.typing.strip()
                if text:
                    self.main.check_password_leak(text, self.selected_mail['sender'])
                    if type(self.selected_mail['accepted']) == list:
                        self.selected_mail['accepted'].append([True, text])
                    else:
                        self.selected_mail['accepted'] = [[True, text]]
                    self.save()
                self.typing = None
            elif event.unicode and event.unicode.isprintable() and len(self.typing) < 200:
                self.typing += event.unicode

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
            return pygame.rect.Rect(area.topleft[0],area.topleft[1], 40, 40)

        def resize(self):
            self.msg = self.main.asset_path + 'bell.png'
            if self.selected_mail:
                self.msg = self.main.asset_path + 'arrow.png' #placeholder back arrow
            elif self.get_any_unread_messages(): #if unread messages
                self.msg = self.main.asset_path + 'bell_alerted.png'
            self.msg = pygame.image.load(self.msg).convert_alpha()
            self.msg = pygame.transform.scale(self.msg, (40,40))

            self.bk = self.main.asset_path + 'bg_pixel_space.png'
            self.bk = pygame.image.load(self.bk).convert_alpha()
            self.bk = pygame.transform.scale(self.bk, (self.width - 6, self.height-self.title_height - 3))

        def on_resize(self):
            self.messager_length = self.width * 0.25
            self.shop_length = self.messager_length
            self.resize()
            self.reload_planet()

        def get_point_on_circle(self, degrey, multi):
            degrey = math.radians(degrey)
            return [self.width*self.base_clicker_size[0] * math.sin(degrey) * multi - 5, self.height*self.base_clicker_size[1] * math.cos(degrey) * multi - 5]

        def wrap(self, text, max_width):
            return self.main.wrap_text(text, max_width)

        def get_row_rects(self):
            area = self.get_area()
            return [(mail, pygame.Rect(area.left, area.top + i * self.row_height,
                                       self.messager_length, self.row_height))
                    for i, mail in enumerate(self.main.friend_list)]

        def get_shop_rects(self):
            area = self.get_area()
            return [(mail,pygame.Rect(area.right-self.shop_length, area.top + i * self.row_height,
                                        self.shop_length, self.row_height))
                    for i, mail in enumerate(self.shop_list)]

        def default_shop(self):
            return [{'sender': 'clicker', 'number': 0, 'price': '10', 'asset':'clicker.png', 'pps': 1},
                    {'sender': 'satilite', 'number': 0, 'price': '100', 'asset':'satilite.png', 'pps': 10/2},
                    {'sender': 'moon', 'number': 0, 'price': '1000', 'asset':'moon.png', 'pps': 100/2},
                    {'sender': 'planet', 'number': 0, 'price': '10000', 'asset':'planet.png', 'pps': 1_000/2},
                    {'sender': 'sun', 'number': 0, 'price': '100000', 'asset':'sun.png', 'pps': 10_000/2},
                    {'sender': 'galaxy', 'number': 0, 'price': '1000000', 'asset':'galaxy.png', 'pps': 100_000/2},
                    {'sender': 'universe', 'number': 0, 'price': '10000000', 'asset':'universe.png', 'pps': 1_000_000/2}]

        def get_pps(self):
            return sum(item['number'] * item['pps'] for item in self.shop_list) * self.multiplier()

        def reload_planet(self):
            self.resize_planet([self.width*self.base_clicker_size[0],self.height*self.base_clicker_size[1]])

        def load(self):
            self.planet = 0
            self.prestige = 0
            self.shop_list = self.default_shop()
            data = self.main.read_save()
            if not data:
                return # no save yet, or a broken one: start fresh

            self.planet = data.get('planet', 0)
            self.prestige = data.get('prestige', 0)
            owned = data.get('owned', {})
            for item in self.shop_list:
                item['number'] = owned.get(item['sender'], 0)

        def save(self):
            friends = self.main.friend_list
            self.main.update_save(
                planet=self.planet,
                prestige=self.prestige,
                friends={f['sender']: {'accepted': f['accepted'], 'read': f['read'], 'next': f['next']}
                         for f in friends if f['sender'] in self.main.message_script},
                denied=[n for n in self.main.message_script
                        if not any(f['sender'] == n for f in friends)],
                owned={item['sender']: item['number'] for item in self.shop_list})
            self.main.save_progress()

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
            dt = self.main.clock.get_time() / 1000 # seconds since the last frame
            self.planet += self.get_pps() * dt
            if self.planet > self.main.stats.get('max_planets', 0):
                self.main.stats['max_planets'] = self.planet
            self.auto_save_timer += dt
            if self.auto_save_timer > self.auto_save_intervouls:
                self.auto_save_timer = 0
                self.save()

            self.check_messages()
            self.main.check_unsafe(self.planet)

            screen = self.main.screen
            font = self.main.small_font
            msg_font =  self.main.smallest_font
            area = self.get_area()
            list_rect = pygame.Rect(area.left, area.top, self.messager_length, area.height)
            shop_rect = pygame.Rect(area.right-self.shop_length, area.top, self.shop_length, area.height)

            if self.clicker_size[0] > self.base_clicker_size[0]*self.width:
                self.resize_planet([i*self.clicker_shrink_rate for i in self.clicker_size])

            screen.blit(self.bk,(area.topleft))

            multi = 0.5
            if self.rotating_icons:
                for i in self.rotating_icons:
                    if i == 'clicker':
                        continue
                    multi += 0.2
                    for j in range(len(self.rotating_icons[i])):
                        bop = self.get_point_on_circle(self.rotating_icons[i][j],multi)
                        self.rotating_icons[i][j] += 1
                        screen.blit(self.rotating_images[i],(area.centerx+bop[0], area.centery+bop[1]))

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
                    if mail['accepted'] and mail['sender'] in self.friend_multiplier:
                        number = self.planet * self.friend_multiplier[mail['sender']]
                        screen.blit(font.render(self.main.short_number(number), True, (90, 90, 90)),
                                    (rect.left + 20, rect.top + 21))

                #reading pane
                screen.set_clip(area)
                pygame.draw.line(screen, (180, 180, 180), list_rect.topright, list_rect.bottomright)
                if self.selected_mail:
                    pygame.draw.rect(screen, (245, 245, 245), list_rect)

                    if not self.selected_mail['accepted']:
                        y = area.bottom - 20
                        screen.blit(font.render('Accept', True, (50,200,50)), (list_rect.left + 10, y))
                        screen.blit(font.render('Deny', True, (200,50,50)), (list_rect.left + 10 + self.messager_length/2, y))

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

                        y = message_bar.top - 10

                        if type(self.selected_mail['accepted']) == list:
                            for sent_by_user, message in reversed(self.selected_mail['accepted']): #so it does the second, then the first
                                lines = [msg_font.render(l, True, (80, 80, 80))
                                        for l in self.wrap(message, message_bar.width * 0.95)]
                                line_h = 8
                                box = pygame.Rect(0, 0,
                                        max(l.get_width() for l in lines) + 6,
                                        len(lines) * line_h + 12)

                                box.bottom = y #y is the bottom of the space still free, the gap between

                                if sent_by_user:
                                    box.right = message_bar.right# right-aligned
                                    colour = (100, 200, 100)
                                else:
                                    box.left = message_bar.left
                                    colour = (200, 200, 200)

                                pygame.draw.rect(screen, colour, box, border_radius=8)

                                temp_y = box.top + 3
                                for l in lines:
                                    screen.blit(l, (box.left + 6, temp_y))
                                    temp_y += line_h
                                y = box.top - line_h

                    # header is drawn last, so a long chat can never cover it
                    pygame.draw.rect(screen, (245, 245, 245), (list_rect.left, area.top, list_rect.width, 66))
                    screen.blit(font.render(self.selected_mail['sender'], True, (0, 0, 0)), (list_rect.left, area.top + 42))
                    pygame.draw.line(screen, (180, 180, 180), [list_rect.right, area.top + 64], [list_rect.left, area.top + 64])
                    if self.selected_mail['sender'] in self.main.message_script:
                        rb = self.get_report_button()
                        pygame.draw.rect(screen, (200, 70, 50), rb, border_radius=4)
                        label = msg_font.render('Rapporter', True, (255, 255, 255))
                        screen.blit(label, label.get_rect(center=rb.center))
                screen.set_clip(None)

            screen.set_clip(shop_rect)
            pygame.draw.rect(screen, (245, 245, 245), shop_rect)
            for mail, rect in self.get_shop_rects():
                if self.planet >= int(mail['price']):
                    pygame.draw.rect(screen, (180, 180, 180), rect)
                    pygame.draw.rect(screen, (100, 200, 100), rect.inflate(0,-1))
                screen.blit(font.render(f"{mail['sender']}:{mail['number']}", True, (0, 0, 0)), (rect.left + 10, rect.top + 4))
                screen.blit(font.render(mail['price'], True, (90, 90, 90)), (rect.left + 10, rect.top + 21))
                screen.blit(self.shop_icons[mail['sender']], (rect.right - 40, rect.top))
                pygame.draw.line(screen, (180, 180, 180), rect.bottomleft, rect.bottomright)
            screen.set_clip(None)

            screen.blit(self.msg,(area.topleft))

            screen.blit(self.clicker_icon,(area.center[0]-self.clicker_size[0]/2,area.center[1]-self.clicker_size[1]/2))
            
            screen.blit(font.render(self.main.short_number(self.planet), True, (255, 255, 255)),area.midtop)

            # prestige
            if self.prestige > 0:
                txt = font.render(f"Prestige {self.prestige}  x{self.multiplier():.1f}", True, (255, 215, 0))
                screen.blit(txt, (area.centerx - txt.get_width() // 2, area.top + 22))

            if self.can_prestige():
                b = self.get_prestige_button()
                confirming = pygame.time.get_ticks() < self.prestige_confirm_until
                pygame.draw.rect(screen, (200, 60, 40) if confirming else (230, 160, 20), b, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), b, 1, border_radius=6)
                label = font.render('Er du sikker?' if confirming else 'Prestige', True, (255, 255, 255))
                screen.blit(label, label.get_rect(center=b.center))
            else:
                hint = msg_font.render(f"Prestige ved {self.main.short_number(self.prestige_cost())}", True, (190, 190, 210))
                screen.blit(hint, (area.centerx - hint.get_width() // 2, area.bottom - 16))

    class scam_popup(window):
        def __init__(self, main):
            super().__init__(main)
            self.title = 'Advarsel'
            self.width = 320
            self.height = 140
            self.x, self.y = random.randint(10,500), random.randint(10,450)
            self.can_maximize = False

        def draw_content(self):
            font = self.main.small_font
            lines = ['Det var en svindel-e-post!',
                     'Ekte selskaper gir deg ikke gratis penger.',
                     'OBS. Noen har stjålet passordet ditt']
            for i, line in enumerate(lines):
                self.main.screen.blit(font.render(line, True, (0, 0, 0)),
                                      (self.x + 15, self.y + self.title_height + 15 + i * 24))

    class settings_window(window):
        def __init__(self, main):
            super().__init__(main)
            self.title = 'Innstillinger'
            self.width = 320
            self.height = 360
            self.min_width = 320            # the layout is fixed
            self.min_height = 360
            self.x, self.y = 240, 100
            self.fields = ['', '', '', '']  # current pw, new username, new pw, repeat pw
            self.labels = ['Nåværende passord', 'Nytt brukernavn', 'Nytt passord', 'Gjenta nytt passord']
            self.masked = [True, False, True, True]
            self.focus = 0
            self.message = ''
            self.message_kind = 'err'       # 'ok', 'warn' or 'err'
            self.can_maximize = False

        def get_field_rect(self, i):
            return pygame.Rect(self.x + 20, self.y + self.title_height + 28 + i * 52,
                               self.width - 40, 26)

        def get_button_rect(self):
            return pygame.Rect(self.x + self.width // 2 - 50, self.y + self.title_height + 241, 100, 28)

        def submit(self):
            cur, new_name, new_pw, rep = self.fields
            user = self.main.logged_in
            new_name = new_name.strip()
            rename = bool(new_name) and new_name != user

            self.message_kind = 'err'
            if not self.main.check_password(user, cur):
                self.message = 'Feil nåværende passord.'
                self.fields[0] = ''
                self.focus = 0
                return
            if not rename and not new_pw:
                self.message = 'Ingenting å endre.'
                return
            if rename and new_name in self.main.accounts:
                self.message = 'Brukernavnet er tatt.'
                return
            if new_pw and len(new_pw) < 4:
                self.message = 'Passordet må ha minst 4 tegn.'
                return
            if new_pw and new_pw != rep:
                self.message = 'Passordene er ikke like.'
                self.fields[3] = ''
                return

            result = self.main.change_account(user, new_name if rename else None, new_pw or None)
            self.fields = ['', '', '', '']
            self.focus = 0
            if result == 'weak':
                self.message = 'Lagret, men passordet er svakt og lett å gjette. Velg et sterkere!'
                self.message_kind = 'warn'
            elif result == 'fixed':
                self.message = 'Bra! Passordet er byttet, og kontoen er trygg igjen.'
                self.message_kind = 'ok'
            else:
                self.message = 'Endringene er lagret.'
                self.message_kind = 'ok'

        def handle_event(self, event):
            used = super().handle_event(event)
            if used and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.closed:
                for i in range(4):
                    if self.get_field_rect(i).collidepoint(event.pos):
                        self.focus = i
                if self.get_button_rect().collidepoint(event.pos):
                    self.submit()

            elif event.type == pygame.KEYDOWN and self.main.open_windows \
                    and self.main.open_windows[-1] is self:          # only the top window gets typing
                f = self.focus
                if event.key == pygame.K_TAB:
                    self.focus = (f + 1) % 4
                elif event.key == pygame.K_RETURN:
                    if f < 3:
                        self.focus += 1
                    else:
                        self.submit()
                elif event.key == pygame.K_BACKSPACE:
                    self.fields[f] = self.fields[f][:-1]
                elif event.unicode and event.unicode.isprintable() \
                        and len(self.fields[f]) < (16 if f == 1 else 24):
                    self.fields[f] += event.unicode
                return True
            return used

        def draw_content(self):
            screen = self.main.screen
            font = self.main.small_font
            screen.set_clip(self.get_area_rect())

            for i in range(4):
                r = self.get_field_rect(i)
                screen.blit(font.render(self.labels[i], True, (0, 0, 0)), (r.left, r.top - 17))
                pygame.draw.rect(screen, (255, 255, 255), r)
                pygame.draw.rect(screen, (51, 153, 255) if i == self.focus else (130, 130, 130), r, 2)

                if self.fields[i]:
                    text = '*' * len(self.fields[i]) if self.masked[i] else self.fields[i]
                    surf = font.render(text, True, (0, 0, 0))
                elif i == 1:
                    surf = font.render(self.main.logged_in or '', True, (150, 150, 150))   # shows the current name
                else:
                    surf = font.render('', True, (0, 0, 0))
                screen.blit(surf, (r.left + 5, r.centery - surf.get_height() // 2))

                if i == self.focus and (pygame.time.get_ticks() // 500) % 2 == 0:
                    cx = r.left + 5 + (font.size('*' * len(self.fields[i]) if self.masked[i] else self.fields[i])[0]) + 1
                    pygame.draw.line(screen, (0, 0, 0), (cx, r.top + 5), (cx, r.bottom - 5))

            b = self.get_button_rect()
            pygame.draw.rect(screen, (60, 130, 220), b, border_radius=4)
            label = font.render('Lagre', True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=b.center))

            if self.message:
                colour = {'ok': (30, 140, 50), 'warn': (210, 120, 20), 'err': (200, 50, 50)}[self.message_kind]
                y = b.bottom + 8
                for line in self.main.wrap_text(self.message, self.width - 30):
                    msg = font.render(line, True, colour)
                    screen.blit(msg, msg.get_rect(midtop=(self.x + self.width // 2, y)))
                    y += 18
            screen.set_clip(None)

        def get_area_rect(self):
            return pygame.Rect(self.x + 3, self.y + self.title_height,
                               self.width - 6, self.height - self.title_height - 3)

    class summary_window(window):
        """Shown at the end of the game: what the player did right and wrong."""
        def __init__(self, main):
            super().__init__(main)
            self.title = 'Oppsummering'
            self.width = 600
            self.height = 440
            self.min_width = 400
            self.min_height = 250
            self.x, self.y = 100, 40
            self.scroll = 0
            self.content_height = 0
            self.items, self.ok_count, self.total = main.build_summary()

        def get_area(self):
            return pygame.Rect(self.x + 3, self.y + self.title_height,
                               self.width - 6, self.height - self.title_height - 3)

        def handle_event(self, event):
            if event.type == pygame.MOUSEWHEEL and self.get_rect().collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, self.scroll - event.y * 30)
                return True
            if event.type == pygame.KEYDOWN and self.main.open_windows and self.main.open_windows[-1] is self:
                if event.key == pygame.K_DOWN:
                    self.scroll += 30
                    return True
                if event.key == pygame.K_UP:
                    self.scroll = max(0, self.scroll - 30)
                    return True
            return super().handle_event(event)

        def draw_content(self):
            screen = self.main.screen
            font = self.main.small_font
            bold = self.main.bold_font
            area = self.get_area()

            screen.set_clip(area)
            pygame.draw.rect(screen, (250, 250, 250), area)

            max_scroll = max(0, self.content_height - area.height)
            self.scroll = min(self.scroll, max_scroll)

            x = area.left + 16
            text_w = area.width - 32 - 30 - 14
            y = area.top + 12 - self.scroll

            screen.blit(self.main.font.render('Oppsummering', True, (0, 60, 160)), (x, y))
            y += 32
            score = f'Du gjorde {self.ok_count} av {self.total} ting riktig.'
            screen.blit(font.render(score, True, (40, 40, 40)), (x, y))
            y += 30

            for item in self.items:
                self.main.draw_status_icon(screen, x + 10, y + 9, item['ok'])
                screen.blit(bold.render(item['title'], True, (20, 20, 20)), (x + 30, y))
                y += 20
                for line in self.main.wrap_text(item['text'], text_w):
                    screen.blit(font.render(line, True, (60, 60, 60)), (x + 30, y))
                    y += 18
                y += 12

            # rules to remember
            rule_lines = [self.main.wrap_text(f'{n}. {r}', text_w) for n, r in enumerate(SUMMARY_RULES, start=1)]
            box_h = 34 + sum(len(l) * 18 + 6 for l in rule_lines)
            box = pygame.Rect(x, y, area.width - 32 - 14, box_h)
            pygame.draw.rect(screen, (255, 241, 150), box, border_radius=6)
            pygame.draw.rect(screen, (235, 210, 90), box, 1, border_radius=6)
            screen.blit(bold.render('3 regler å huske', True, (90, 70, 0)), (box.left + 10, box.top + 8))
            ty = box.top + 30
            for lines in rule_lines:
                for line in lines:
                    screen.blit(font.render(line, True, (60, 45, 0)), (box.left + 10, ty))
                    ty += 18
                ty += 6
            y = box.bottom + 16

            self.content_height = y + self.scroll - area.top

            if max_scroll > 0:
                track = pygame.Rect(area.right - 10, area.top + 2, 6, area.height - 4)
                pygame.draw.rect(screen, (225, 225, 225), track, border_radius=3)
                thumb_h = max(24, int(track.height * area.height / self.content_height))
                thumb_y = track.top + int((track.height - thumb_h) * self.scroll / max_scroll)
                pygame.draw.rect(screen, (150, 150, 150), (track.left, thumb_y, track.width, thumb_h), border_radius=3)
            screen.set_clip(None)

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
        self.asset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Nett detective assets') + os.sep

        self.save_path = self.asset_path + 'Progress.json'
        flags = self.read_save()
        self.unsafe = flags.get('unsafe', False)
        self.unsafe_goal = flags.get('unsafe_goal', 0)
        self.unsafe_reason = flags.get('unsafe_reason', 'scam')
        self.warning_sent = flags.get('warning_sent', False)

        # progress through the story
        self.stats = flags.get('stats', {})                   # everything the summary needs
        self.done_missions = set(flags.get('missions_done', []))
        self.unlocked = set(flags.get('unlocked', []))        # names of icons that have been unlocked
        self.summary_shown = flags.get('summary_shown', False)

        self.bk = self.asset_path + 'windows-xp-desktop.png'
        self.bk = pygame.image.load(self.bk).convert_alpha()
        self.bk = pygame.transform.scale(self.bk, (self.width, self.height))

        self.alerted_bell = self.asset_path + 'mail_notification.png'
        self.alerted_bell = pygame.image.load(self.alerted_bell).convert_alpha()
        self.alerted_bell = pygame.transform.scale(self.alerted_bell, (50, 50))

        self.bell = self.asset_path + 'mail_plain.png'
        self.bell = pygame.image.load(self.bell).convert_alpha()
        self.bell = pygame.transform.scale(self.bell, (50,50))

        self.mouse = pygame.SYSTEM_CURSOR_ARROW

        self.notified = False
        self.inbox = []
        self.small_font = pygame.font.Font(None, 22)
        self.smallest_font = pygame.font.Font(None, 15)
        self.bold_font = pygame.font.Font(None, 22)
        self.bold_font.set_bold(True)

        self.friend_list = []
        self.friend_list.insert(0, {'sender': ' ', 'accepted': False, 'read': True, 'ignor': True, 'next': -1})
        self.messaged = False
        with open((self.asset_path + 'Messages.json'), encoding='utf-8') as f:
            raw = json.load(f)
            self.message_script = {name: sorted((int(k), text) for k, text in msgs.items())
                                for name, msgs in raw.items()}

        self.desktop_shortcuts = []
        self.open_windows = []

        # desktop grid (icons snap to it)
        self.grid_origin = (10, 10)
        self.grid_cell = (100, 95)
        self.grid_cols = (self.width - 210) // self.grid_cell[0]      # keeps the sticky note free
        self.grid_rows = (self.height - 40 - 10) // self.grid_cell[1]

        self.accounts = self.load_accounts()         # {name: {'salt': ..., 'hash': ...}}
        self.logged_in = None
        self.login_mode = 'login' if self.accounts else 'create'
        self.login_user = next(iter(self.accounts), '')
        self.login_password = ''
        self.login_error = ''
        self.create_fields = ['', '', '']            # username, password, repeat password
        self.create_focus = 0

        self.power_icon = pygame.image.load(self.asset_path + 'power.png').convert_alpha()
        self.power_icon = pygame.transform.scale(self.power_icon, (32, 32))

        self.toasts = []
        self.toast_icon = pygame.transform.scale(self.bell, (32, 32))

        self.build_missions()

    # ------------------------------------------------------------------ missions / unlocks
    def build_missions(self):
        s = self.stats
        self.missions = [
            {'id': 'mail', 'text': 'Les alle e-postene dine',
             'check': lambda: bool(self.inbox) and all(m['read'] for m in self.inbox)},
            {'id': 'open_pixel', 'text': 'Åpne Pixel World (dobbeltklikk)',
             'check': lambda: s.get('opened_pixel', False)},
            {'id': 'planets10', 'text': 'Klikk på planeten til du har 10 planeter',
             'check': lambda: s.get('max_planets', 0) >= 10},
            {'id': 'friend', 'text': 'Godta en venneforespørsel (bjella i Pixel World)',
             'check': lambda: s.get('accepted_friend', False)},
            {'id': 'shop', 'text': 'Kjøp noe i butikken til høyre',
             'check': lambda: s.get('bought', False)},
            {'id': 'planets100', 'text': 'Få 100 planeter',
             'check': lambda: s.get('max_planets', 0) >= 100},
            {'id': 'report', 'text': 'Bruk Rapporter-knappen på noe som virker feil',
             'check': lambda: s.get('reported_any', False)},
            {'id': 'password', 'text': 'Bytt passordet ditt i Innstillinger',
             'check': lambda: s.get('fixed', False),
             'applies': lambda: s.get('warned', False)},
        ]

    def mission_applies(self, m):
        return not m.get('applies') or m['applies']()

    def pending_missions(self):
        return [m for m in self.missions if m['id'] not in self.done_missions and self.mission_applies(m)]

    def update_missions(self):
        changed = False
        for m in self.pending_missions():
            if m['check']():
                self.done_missions.add(m['id'])
                changed = True
                #self.toast_message('Oppdrag fullført!', m['text'])
        if changed:
            self.save_progress()

        if not self.summary_shown and not self.pending_missions():
            self.summary_shown = True
            self.save_progress()
            self.open_summary()

    def update_unlocks(self):
        for s in self.desktop_shortcuts:
            if not s.visible and s.unlock and s.unlock():
                s.visible = True
                self.place_shortcut(s)
                self.unlocked.add(s.name)
                self.save_progress()
                self.toast_message('Nytt program!', f'{s.name} er låst opp')

    def save_progress(self):
        self.update_save(stats=self.stats,
                         missions_done=sorted(self.done_missions),
                         unlocked=sorted(self.unlocked),
                         summary_shown=self.summary_shown)

    def open_message(self, title, text):
        self.open_windows.append(self.message_window(self, title, text))

    def open_summary(self):
        for w in self.open_windows:
            if isinstance(w, self.summary_window):
                self.open_windows.remove(w)
                self.open_windows.append(w)
                return
        self.open_windows.append(self.summary_window(self))

    def build_summary(self):
        s = self.stats
        items = []

        def add(ok, title, text):
            items.append({'ok': ok, 'title': title, 'text': text})

        # the scam email
        if s.get('scam_clicked'):
            add(False, 'Svindel-e-posten',
                'Du klikket på lenken som lovet gratis planeter. Ekte selskaper gir deg ikke gratis penger, '
                'og slike lenker kan brukes til å stjele passordet ditt.')
        elif s.get('reported_scam'):
            add(True, 'Svindel-e-posten',
                'Du oppdaget at e-posten var en svindel og rapporterte den uten å klikke på lenken. Perfekt!')
        else:
            add(True, 'Svindel-e-posten',
                'Du lot lenken i svindel-e-posten være i fred. Bra! Neste gang kan du også rapportere den.')

        # the password itself
        if s.get('weak_password'):
            if s.get('fixed'):
                add(True, 'Valg av passord',
                    'Passordet ditt sto på en liste over svake passord, men du byttet det til et sterkere. Bra!')
            else:
                add(False, 'Valg av passord',
                    'Passordet ditt er et av de mest brukte i verden, så det er lett å gjette. '
                    'Bruk minst 8 tegn og bland bokstaver og tall.')
        else:
            add(True, 'Valg av passord', 'Du brukte et passord som ikke er lett å gjette. Bra!')

        if s.get('password_leaked'):
            who = s.get('leaked_to', 'en venn')
            add(False, 'Dele passord',
                f'Du sendte passordet ditt i en melding til {who}. Passord er hemmelige og skal aldri deles, heller ikke med venner.')
        else:
            add(True, 'Dele passord', 'Du delte aldri passordet ditt med noen. Det er helt riktig!')

        # the security warning
        if s.get('warned'):
            if s.get('fixed'):
                add(True, 'Sikkerhetsadvarselen',
                    'Du fikk en advarsel om at kontoen var i fare, og du byttet passord. Akkurat det du skal gjøre!')
            else:
                add(False, 'Sikkerhetsadvarselen',
                    'Du fikk en advarsel om at kontoen var i fare, men byttet ikke passord. Bytt passord med en gang når du får slike varsler.')

        # the friends
        for name in self.message_script:
            feedback = FRIEND_FEEDBACK.get(name)
            if not feedback:
                continue
            ok, text = feedback[self.friend_status(name)]
            add(ok, name, text)

        if s.get('false_reports', 0) > 0:
            add(None, 'Rapportering',
                'Du rapporterte noe som var ufarlig. Det er greit! Det er bedre å spørre én gang for mye enn én gang for lite.')

        ok_count = sum(1 for i in items if i['ok'] is True)
        total = sum(1 for i in items if i['ok'] is not None)
        return items, ok_count, total

    def friend_status(self, name):
        s = self.stats
        if name in s.get('reported_friends', []):
            return 'reported'
        if name in s.get('denied_friends', []):
            return 'denied'
        friend = next((f for f in self.friend_list if f['sender'] == name), None)
        if friend is None:
            return 'denied'
        return 'accepted' if friend['accepted'] else 'pending'

    def draw_status_icon(self, screen, cx, cy, ok):
        colour = (40, 160, 70) if ok is True else (200, 60, 50) if ok is False else (150, 150, 150)
        pygame.draw.circle(screen, colour, (cx, cy), 9)
        white = (255, 255, 255)
        if ok is True:
            pygame.draw.lines(screen, white, False, [(cx - 4, cy), (cx - 1, cy + 4), (cx + 5, cy - 4)], 2)
        elif ok is False:
            pygame.draw.line(screen, white, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
            pygame.draw.line(screen, white, (cx - 4, cy + 4), (cx + 4, cy - 4), 2)
        else:
            pygame.draw.circle(screen, white, (cx, cy), 3)

    def draw_sticky(self):
        pending = self.pending_missions()[:3]
        w = 190
        font = self.small_font
        if pending:
            blocks = [self.wrap_text(m['text'], w - 44) for m in pending]
        else:
            blocks = [self.wrap_text('Alt er gjort! Åpne Oppsummering på skrivebordet.', w - 24)]
        h = 40 + sum(len(b) * 17 + 10 for b in blocks)
        rect = pygame.Rect(self.width - w - 10, 10, w, h)

        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        self.screen.blit(shadow, rect.move(4, 4))
        pygame.draw.rect(self.screen, (255, 241, 150), rect)
        pygame.draw.rect(self.screen, (235, 210, 90), (rect.left, rect.top, w, 22))
        self.screen.blit(self.bold_font.render('Oppdrag', True, (90, 70, 0)), (rect.left + 10, rect.top + 4))

        y = rect.top + 32
        for i, block in enumerate(blocks):
            colour = (40, 30, 0) if i == 0 else (120, 105, 50)
            if pending:
                pygame.draw.rect(self.screen, colour, (rect.left + 10, y + 2, 12, 12), 2)
                tx = rect.left + 32
            else:
                tx = rect.left + 12
            for line in block:
                self.screen.blit(font.render(line, True, colour), (tx, y))
                y += 17
            y += 10

    # ------------------------------------------------------------------ desktop grid
    def grid_cell_pos(self, col, row):
        ox, oy = self.grid_origin
        cw, ch = self.grid_cell
        return ox + col * cw + (cw - 50) // 2, oy + row * ch + 6

    def grid_cell_of(self, s):
        ox, oy = self.grid_origin
        cw, ch = self.grid_cell
        col = round((s.x - ox - (cw - 50) / 2) / cw)
        row = round((s.y - oy - 6) / ch)
        return max(0, min(self.grid_cols - 1, col)), max(0, min(self.grid_rows - 1, row))

    def occupied_cells(self, ignore=None):
        return {self.grid_cell_of(s) for s in self.desktop_shortcuts if s.visible and s is not ignore}

    def snap_shortcut(self, s):
        col, row = self.grid_cell_of(s)
        taken = self.occupied_cells(ignore=s)
        if (col, row) in taken:                          # cell is taken: use the closest free one
            best = None
            for c in range(self.grid_cols):
                for r in range(self.grid_rows):
                    if (c, r) not in taken:
                        d = (c - col) ** 2 + (r - row) ** 2
                        if best is None or d < best[0]:
                            best = (d, c, r)
            if best:
                col, row = best[1], best[2]
        s.x, s.y = self.grid_cell_pos(col, row)

    def place_shortcut(self, s):
        taken = self.occupied_cells(ignore=s)
        for c in range(self.grid_cols):                  # fill column by column, like a real desktop
            for r in range(self.grid_rows):
                if (c, r) not in taken:
                    s.x, s.y = self.grid_cell_pos(c, r)
                    return

    def add_shortcut(self, name, icon, opens, unlock=None):
        s = self.shortcut(self)
        s.set_icon(icon)
        s.opens = opens
        s.unlock = unlock
        s.visible = unlock is None or name in self.unlocked
        s.set_name(name)
        self.desktop_shortcuts.append(s)
        if s.visible:
            self.place_shortcut(s)
        return s

    # ------------------------------------------------------------------ taskbar / cursor
    def handle_task_bar(self):
        pygame.draw.rect(self.screen, (50,50,200), pygame.Rect(0,self.height-40,self.width,self.height))
        if self.notified:
            self.screen.blit(self.alerted_bell,(self.width-50,self.height-45))
        else:
            self.screen.blit(self.bell,(self.width-50,self.height-45))
        self.screen.blit(self.power_icon, self.get_power_rect())
        if self.get_power_rect().collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (255, 255, 255), self.get_power_rect(), 1, border_radius=4)   # hover outline

    def cursor_for_edges(self, edges):
        left, right, top, bottom = edges
        if (left and top) or (right and bottom):
            return pygame.SYSTEM_CURSOR_SIZENWSE
        if (right and top) or (left and bottom):
            return pygame.SYSTEM_CURSOR_SIZENESW
        if left or right:
            return pygame.SYSTEM_CURSOR_SIZEWE
        if top or bottom:
            return pygame.SYSTEM_CURSOR_SIZENS
        return pygame.SYSTEM_CURSOR_ARROW

    def update_cursor(self, pos):
        wanted = pygame.SYSTEM_CURSOR_ARROW

        resizing = [w for w in self.open_windows if w.resizeing]
        if resizing:
            # keep the resize cursor while dragging, even if the mouse leaves the edge
            wanted = self.cursor_for_edges(resizing[0].resize_edges)
        elif not any(w.dragging for w in self.open_windows):
            for w in reversed(self.open_windows):          # topmost window under the mouse decides
                if w.get_rect().collidepoint(pos):
                    if not w.get_close_rect().collidepoint(pos):
                        wanted = self.cursor_for_edges(w.get_edges(pos))
                    break

        if wanted != self.mouse:                            # only touch the cursor when it changes
            self.mouse = wanted
            try:
                pygame.mouse.set_cursor(wanted)
            except Exception:
                pass                                        # some platforms (e.g. the web build) lack system cursors

    # ------------------------------------------------------------------ scam / reporting
    def scam_clicked(self):
        self.stats['scam_clicked'] = True
        self.save_progress()
        self.mark_unsafe('scam')
        self.open_windows.append(self.scam_popup(self))

    def report_mail(self, mail):
        if mail.get('reported'):
            return
        mail['reported'] = True
        self.stats['reported_any'] = True
        if mail.get('scam'):
            self.stats['reported_scam'] = True
            text = ('Bra jobba! Denne e-posten lovet gratis planeter og ba deg klikke på en lenke. Det er et typisk '
                    'svindelforsøk. Ikke klikk på slike lenker, og si fra til en voksen.')
        else:
            self.stats['false_reports'] = self.stats.get('false_reports', 0) + 1
            text = ('Takk for at du sa fra! Denne e-posten var egentlig ufarlig, men det er alltid lurt å spørre '
                    'en voksen når du er usikker.')
        self.save_inbox()
        self.save_progress()
        self.open_message('Rapport sendt', text)

    def report_friend(self, friend):
        name = friend['sender']
        if friend in self.friend_list:
            self.friend_list.remove(friend)                 # reporting also blocks
        reported = self.stats.setdefault('reported_friends', [])
        if name not in reported:
            reported.append(name)
        self.stats['reported_any'] = True
        if friend['next'] > 0:
            text = FRIEND_REPORT_POPUP.get(name, FRIEND_REPORT_POPUP['default'])
        else:
            text = (f'Du rapporterte og blokkerte {name}. Det er helt greit å si nei til folk du ikke kjenner. '
                    'Er du usikker, så spør en voksen du stoler på.')
        self.save_progress()
        self.open_message('Rapport sendt', text)

    def toast_message(self, title, text):
        self.toasts.append({'sender': title, 'subject': text, 'mail': None, 'born': None, 'rect': None})

    def handle_mouse_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.update_cursor(event.pos)

        # things drawn on top of the windows get the click first: toasts and the taskbar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for t in self.toasts:
                if t['rect'] and t['rect'].collidepoint(event.pos):
                    self.toasts.remove(t)
                    mail = t.get('mail')
                    if mail is not None:
                        self.email_shortcut.run()            # opens E-post, or raises it if already open
                        app = self.email_shortcut.link
                        if app and mail in self.inbox:
                            app.selected_mail = mail         # show this email in the reading pane
                            mail['read'] = True
                            self.save_inbox()
                    return

            if self.get_bell_rect().collidepoint(event.pos):
                self.email_shortcut.run() # opens the app, or brings it to the front
                return

            if self.get_power_rect().collidepoint(event.pos):
                self.log_out()
                return

        # windows get first pick, topmost (last in list) first
        for w in reversed(self.open_windows):
            if w.handle_event(event): #just True or false
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.open_windows.remove(w) # bring to front
                    self.open_windows.append(w)

                if w.resizeing:
                    w.on_resize()

                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = None
            for i in self.desktop_shortcuts:
                if i.visible and i.get_box().collidepoint(event.pos):
                    clicked = i

            # select the clicked one, deselect the rest (empty desktop deselects all)
            for i in self.desktop_shortcuts:
                i.selected = (i is clicked)

            if clicked:
                clicked.grabbed = True
                clicked.grab_offset = (event.pos[0] - clicked.x, event.pos[1] - clicked.y)
                if clicked.count_down > 0: # second click in time = double click
                    clicked.run()
                    clicked.count_down = 0
                else:
                    clicked.count_down = 30 # about 0.5 s at 60 FPS

        elif event.type == pygame.MOUSEBUTTONUP:
            for i in self.desktop_shortcuts:
                if i.grabbed:
                    i.grabbed = False # release everything, even if the mouse left the box
                    self.snap_shortcut(i)

        elif event.type == pygame.MOUSEMOTION:
            for i in self.desktop_shortcuts:
                if not i.visible:
                    continue
                if i.grabbed:
                    i.x = event.pos[0] - i.grab_offset[0]
                    i.y = event.pos[1] - i.grab_offset[1]
                    # keep the icon (and its label) on the desktop, above the taskbar
                    i.x = max(0, min(i.x, self.width - i.width))
                    i.y = max(0, min(i.y, self.height - 40 - i.height - 24))
                i.hovered = i.get_box().collidepoint(event.pos)

    def get_bell_rect(self):
        return pygame.Rect(self.width - 50, self.height - 50, 50, 50)

    def get_power_rect(self):
        return pygame.Rect(4, self.height - 38, 32, 32)

    def log_out(self):
        for w in self.open_windows:
            if hasattr(w, 'save'):
                w.save()                         # keep planets and chats
        self.save_progress()
        self.open_windows.clear()
        for s in self.desktop_shortcuts:
            s.link = None                        # so shortcuts open fresh windows after login
            s.selected = False
            s.grabbed = False
        self.logged_in = None
        self.login_mode = 'login'
        self.login_user = next(iter(self.accounts), '')
        self.login_password = ''
        self.login_error = ''
        self.mouse = pygame.SYSTEM_CURSOR_ARROW
        self.toasts.clear()
        try:
            pygame.mouse.set_cursor(self.mouse)  # in case a resize cursor was showing
        except Exception:
            pass

    # ------------------------------------------------------------------ friends / mail
    def load_friends(self):
        data = self.read_save()
        saved = data.get('friends', {})
        denied = data.get('denied', [])
        for friend in self.friend_list[:]:
            name = friend['sender']
            if name in denied:
                self.friend_list.remove(friend)          # you denied or reported them last time
            elif name in saved:
                friend.update(saved[name])               # accepted (or chat log), read, next

    def Friend_request(self, sender='Unknown'):
        self.friend_list.insert(1, {'sender': sender, 'accepted': False, 'read': False, 'ignor': False, 'next': 0})
        self.messaged = True

    def Send_message(self, sender, text):
        """A friend sends the player a message. Returns False if they aren't an accepted friend."""
        for friend in self.friend_list:
            if friend['sender'] == sender and friend['accepted']:
                if friend['accepted'] is True: # accepted, but no messages yet
                    friend['accepted'] = [[False, text]] # not an empty list: [] counts as "not accepted"
                else:
                    friend['accepted'].append([False, text])

                # only mark unread if the player isn't looking at this chat right now
                viewing = any(isinstance(w, self.clicker_app) and w.selected_mail is friend
                              for w in self.open_windows)
                if not viewing:
                    friend['read'] = False

                    # refresh the bell icon in any open Pixel World window
                    for w in self.open_windows:
                        if isinstance(w, self.clicker_app):
                            w.resize()
                return True
        return False

    def Push_notification(self, subject, body, sender='Unknown', read=False, scam=False):
        mail = {'sender': sender, 'subject': subject, 'body': body, 'read': read, 'scam': scam}
        self.inbox.insert(0, mail)
        self.toasts.append({'sender': sender, 'subject': subject, 'mail': mail, 'born': None, 'rect': None})
        self.save_inbox()

    # ------------------------------------------------------------------ unsafe account
    def get_planets(self):
        for w in self.open_windows:
            if isinstance(w, self.clicker_app):
                return w.planet
        return self.read_save().get('planet', 0)      # Pixel World closed: use the saved count

    def mark_unsafe(self, reason='scam'):
        if self.unsafe:
            return                                    # already marked, keep the original goal
        self.unsafe = True
        self.unsafe_reason = reason
        self.unsafe_goal = max(self.get_planets(), 1) * 10    # max(..., 1) handles 0 planets: goal becomes 10
        self.update_save(unsafe=True, unsafe_goal=self.unsafe_goal, unsafe_reason=reason)

    def check_unsafe(self, planets):
        if self.unsafe and not self.warning_sent and planets >= self.unsafe_goal:
            self.warning_sent = True
            self.stats['warned'] = True
            reasons = {
                'scam': 'Vi ser at du har clicket på en link fra "Piksel world".',
                'leak': 'Vi tror noen har sett passordet ditt, fordi det ble sendt i en melding.',
                'weak': 'Passordet ditt er et av de mest brukte passordene i verden, så det er lett å gjette.',
            }
            self.Push_notification('Sikkerhetsadvarsel',
                                   'Vi har oppdaget uvanlig aktivitet på kontoen din.\n'
                                   + reasons.get(self.unsafe_reason, '') + '\n'
                                   'Bytt passordet ditt i Innstillinger så snart som mulig.',
                                   'Microsoft')
            self.update_save(warning_sent=True)
            self.save_progress()

    def check_password_leak(self, text, friend=None):
        user = self.logged_in
        if not user or self.stats.get('password_leaked'):
            return
        # the whole message, plus each word with punctuation stripped (every check is a slow hash)
        words = {w.strip('.,!?;:"\'()') for w in text.split()}
        words.add(text.strip())
        for c in [w for w in words if 4 <= len(w) <= 24][:8]:
            if self.check_password(user, c):
                self.stats['password_leaked'] = True
                if friend:
                    self.stats['leaked_to'] = friend
                self.save_progress()
                self.mark_unsafe('leak')
                return

    def is_unsafe_password(self, pw, username=''):
        p = pw.lower()
        return p in UNSAFE_PASSWORDS or (bool(username) and p == username.lower()) or len(set(p)) == 1

    # ------------------------------------------------------------------ accounts / saving
    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100_000).hex()

    def load_accounts(self):
        return self.read_save().get('accounts', {})

    def read_save(self):
        try:
            with open(self.save_path, encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def update_save(self, **values):
        data = self.read_save()
        data.update(values)                          # only touches the keys you pass
        tmp = self.save_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        os.replace(tmp, self.save_path)

    def save_accounts(self):
        self.update_save(accounts=self.accounts)

    def save_inbox(self):
        self.update_save(inbox=self.inbox)

    def check_password(self, user, pw):
        acc = self.accounts.get(user)
        return bool(acc) and hmac.compare_digest(acc['hash'], self.hash_password(pw, acc['salt']))

    def change_account(self, user, new_name=None, new_pw=None):
        """Returns 'weak' (new password is on the unsafe list), 'fixed' (an unsafe account is safe again) or 'ok'."""
        acc = self.accounts[user]
        if new_pw:
            salt = os.urandom(16).hex()
            acc = {'salt': salt, 'hash': self.hash_password(new_pw, salt)}
        name = new_name or user
        # rebuild the dict so the account keeps its place in the login screen's list
        self.accounts = {(name if k == user else k): (acc if k == user else v)
                         for k, v in self.accounts.items()}
        if self.logged_in == user:
            self.logged_in = name
        if self.login_user == user:
            self.login_user = name
        self.save_accounts()

        result = 'ok'
        if new_pw:
            if self.is_unsafe_password(new_pw, name):
                self.stats['weak_password'] = True
                self.mark_unsafe('weak')
                result = 'weak'
            elif self.unsafe or self.stats.get('warned'):
                self.stats['fixed'] = True
                self.unsafe = False                  # the password is new, so the old leak no longer matters
                self.warning_sent = False
                self.update_save(unsafe=False, warning_sent=False)
                result = 'fixed'
            self.save_progress()
        return result

    def try_login(self, user, pw):
        acc = self.accounts.get(user)
        if acc and hmac.compare_digest(acc['hash'], self.hash_password(pw, acc['salt'])):
            self.logged_in = user
            return True
        return False

    def create_account(self):
        name, pw, pw2 = [s.strip() if i == 0 else s for i, s in enumerate(self.create_fields)]
        if not name:
            self.login_error = 'Skriv inn et brukernavn.'
        elif name in self.accounts:
            self.login_error = 'Brukernavnet er tatt.'
        elif len(pw) < 4:
            self.login_error = 'Passordet må ha minst 4 tegn.'
        elif pw != pw2:
            self.login_error = 'Passordene er ikke like.'
            self.create_fields[2] = ''
        else:
            salt = os.urandom(16).hex()
            self.accounts[name] = {'salt': salt, 'hash': self.hash_password(pw, salt)}
            self.save_accounts()
            if self.is_unsafe_password(pw, name):    # on the list of known passwords: compromised from the start
                self.stats['weak_password'] = True
                self.mark_unsafe('weak')
                self.save_progress()
            self.login_user = name
            self.logged_in = name
            self.login_error = ''
            self.create_fields = ['', '', '']

    # ------------------------------------------------------------------ small helpers
    def short_number(self, n):
        n = int(n)
        for limit, suffix in ((10**9, 'B'), (10**6, 'M'), (10**3, 'K')):
            if n >= limit:
                return f"{n / limit:.1f}{suffix}"
        return str(n)

    def wrap_text(self, text, max_width, font=None):
        font = font or self.small_font
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

    def fit_text(self, text, max_width):
        if self.small_font.size(text)[0] <= max_width:
            return text
        while text and self.small_font.size(text + '...')[0] > max_width:
            text = text[:-1]
        return text + '...'

    # ------------------------------------------------------------------ login screen
    def get_user_tiles(self):
        return [(name, pygame.Rect(self.width // 2 - 130, 150 + i * 70, 260, 60))
                for i, name in enumerate(self.accounts)]

    def get_password_rect(self):
        y = 150 + len(self.accounts) * 70 + 15
        return pygame.Rect(self.width // 2 - 130, y, 226, 28)

    def get_login_button(self):
        r = self.get_password_rect()
        return pygame.Rect(r.right + 6, r.top, 28, 28)

    def get_create_field(self, i):
        return pygame.Rect(self.width // 2 - 130, 170 + i * 65, 260, 28)

    def get_create_button(self):
        return pygame.Rect(self.width // 2 - 60, 170 + 3 * 65, 120, 32)

    def draw_create(self):
        screen = self.screen
        title = self.font.render('Opprett bruker', True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.width // 2, 90)))
        hint = self.small_font.render('Ingen brukere funnet. Lag den første.', True, (200, 220, 255))
        screen.blit(hint, hint.get_rect(center=(self.width // 2, 120)))

        labels = ['Brukernavn', 'Passord', 'Gjenta passord']
        for i in range(3):
            r = self.get_create_field(i)
            screen.blit(self.small_font.render(labels[i], True, (255, 255, 255)), (r.left, r.top - 18))
            pygame.draw.rect(screen, (255, 255, 255), r, border_radius=4)
            pygame.draw.rect(screen, (51, 153, 255) if i == self.create_focus else (130, 130, 130), r, 2, border_radius=4)
            text = self.create_fields[i] if i == 0 else '*' * len(self.create_fields[i])
            surf = self.small_font.render(text, True, (0, 0, 0))
            screen.blit(surf, (r.left + 6, r.centery - surf.get_height() // 2))
            if i == self.create_focus and (pygame.time.get_ticks() // 500) % 2 == 0:
                cx = r.left + 6 + surf.get_width() + 1
                pygame.draw.line(screen, (0, 0, 0), (cx, r.top + 5), (cx, r.bottom - 5))

        b = self.get_create_button()
        pygame.draw.rect(screen, (60, 170, 70), b, border_radius=4)
        label = self.small_font.render('Opprett', True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=b.center))

        if self.login_error:
            err = self.small_font.render(self.login_error, True, (255, 150, 150))
            screen.blit(err, err.get_rect(center=(self.width // 2, b.bottom + 22)))

    def draw_toasts(self):
        now = pygame.time.get_ticks()
        duration, slide = 4000, 250                      # total ms on screen, ms for sliding in/out
        w, h, gap = 260, 52, 6

        self.toasts = [t for t in self.toasts if t['born'] is None or now - t['born'] < duration]

        y = self.height - 48                             # bottom edge, just above the taskbar
        for t in reversed(self.toasts[-3:]):             # at most 3 visible, newest at the bottom
            if t['born'] is None:
                t['born'] = now
            age = now - t['born']
            if age < slide:
                p = age / slide
            elif age > duration - slide:
                p = (duration - age) / slide
            else:
                p = 1
            p = max(0, min(1, p))

            rect = pygame.Rect(self.width - (w + 10) * p, y - h, w, h)
            t['rect'] = rect
            y -= h + gap

            pygame.draw.rect(self.screen, (35, 60, 130), rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 1, border_radius=6)
            self.screen.blit(self.toast_icon, (rect.left + 8, rect.centery - 16))
            text_w = w - 56
            self.screen.blit(self.small_font.render(self.fit_text(t['sender'], text_w), True, (255, 255, 255)),
                             (rect.left + 48, rect.top + 8))
            self.screen.blit(self.small_font.render(self.fit_text(t['subject'], text_w), True, (190, 210, 255)),
                             (rect.left + 48, rect.top + 28))

    def attempt_login(self):
        if self.try_login(self.login_user, self.login_password):
            self.login_password = ''
            self.login_error = ''
        else:
            self.login_password = ''
            self.login_error = 'Feil passord. Prøv igjen.'

    def handle_login_event(self, event):
        if self.login_mode == 'create':
            if event.type == pygame.KEYDOWN:
                f = self.create_focus
                if event.key == pygame.K_TAB:
                    self.create_focus = (f + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if f < 2:
                        self.create_focus += 1
                    else:
                        self.create_account()
                elif event.key == pygame.K_BACKSPACE:
                    self.create_fields[f] = self.create_fields[f][:-1]
                elif event.unicode and event.unicode.isprintable() and len(self.create_fields[f]) < (16 if f == 0 else 24):
                    self.create_fields[f] += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(3):
                    if self.get_create_field(i).collidepoint(event.pos):
                        self.create_focus = i
                if self.get_create_button().collidepoint(event.pos):
                    self.create_account()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.attempt_login()
            elif event.key == pygame.K_BACKSPACE:
                self.login_password = self.login_password[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.login_password) < 24:
                self.login_password += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.get_user_tiles():
                if rect.collidepoint(event.pos):
                    self.login_user = name
                    self.login_password = ''
                    self.login_error = ''
            if self.get_login_button().collidepoint(event.pos):
                self.attempt_login()

    def draw_login(self):
        screen = self.screen
        screen.blit(self.bk, (0, 0))
        shade = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        shade.fill((0, 40, 120, 210))
        screen.blit(shade, (0, 0))
        if self.login_mode == 'create':
            self.draw_create()
            return

        title = self.font.render('Velkommen', True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.width // 2, 90)))
        hint = self.small_font.render('Velg bruker og skriv inn passordet', True, (200, 220, 255))
        screen.blit(hint, hint.get_rect(center=(self.width // 2, 120)))

        for name, rect in self.get_user_tiles():
            selected = name == self.login_user
            pygame.draw.rect(screen, (60, 130, 220) if selected else (30, 70, 160), rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2 if selected else 1, border_radius=8)
            pygame.draw.circle(screen, (230, 230, 230), (rect.left + 30, rect.centery), 20)
            letter = self.font.render(name[0].upper(), True, (30, 70, 160))
            screen.blit(letter, letter.get_rect(center=(rect.left + 30, rect.centery)))
            screen.blit(self.font.render(name, True, (255, 255, 255)), (rect.left + 62, rect.centery - 10))

        # password field
        r = self.get_password_rect()
        pygame.draw.rect(screen, (255, 255, 255), r, border_radius=4)
        pygame.draw.rect(screen, (51, 153, 255), r, 2, border_radius=4)
        text = '*' * len(self.login_password) if self.login_password else 'Passord'
        colour = (0, 0, 0) if self.login_password else (150, 150, 150)
        surf = self.small_font.render(text, True, colour)
        screen.blit(surf, (r.left + 6, r.centery - surf.get_height() // 2))
        if (pygame.time.get_ticks() // 500) % 2 == 0:                       # blinking caret
            cx = r.left + 6 + (surf.get_width() if self.login_password else 0) + 1
            pygame.draw.line(screen, (0, 0, 0), (cx, r.top + 5), (cx, r.bottom - 5))

        # arrow button
        b = self.get_login_button()
        pygame.draw.rect(screen, (60, 170, 70), b, border_radius=4)
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(b.left + 9, b.top + 7), (b.left + 9, b.bottom - 7), (b.right - 7, b.centery)])

        if self.login_error:
            err = self.small_font.render(self.login_error, True, (255, 150, 150))
            screen.blit(err, err.get_rect(center=(self.width // 2, b.bottom + 22)))

    # ------------------------------------------------------------------ main loop
    async def Start_Game(self):
        # icons unlock one by one (E-post is there from the start)
        self.email_shortcut = self.add_shortcut('E-post', 'mail_plain.png', self.email_app)
        self.add_shortcut('Pixel World', 'game_pixelworld.png', self.clicker_app,
                          unlock=lambda: 'mail' in self.done_missions)           # after all mails are read
        self.add_shortcut('Innstillinger', 'cogwheel.png', self.settings_window,
                          unlock=lambda: self.stats.get('warned', False) or 'planets100' in self.done_missions)
        self.add_shortcut('Oppsummering', 'Evil-plane.png', self.summary_window,   # swap for a proper icon
                          unlock=lambda: self.summary_shown)

        saved_inbox = self.read_save().get('inbox')
        if saved_inbox is not None:
            self.inbox = saved_inbox
        else:
            self.Push_notification('Welcome', 'Hei og takk for at du signet opp for Pixel World!\n Bare double trykk på den for å åpne den\n Click på planeten, lag venner og har det gøy :D', 'Pixel World')
            self.Push_notification('Welcome', 'Hei og takk for at du signet opp for Piksel World!\n Click på lenken for å få din sign up bonus på 1 MILLIONER PLANETER!!!!!!!', 'Piksel World', scam='Click meg')

        for name in self.message_script:
            self.Friend_request(name)
        self.load_friends()

        while self.running:

            self.screen.blit(self.bk,(0,0))

            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_F9 and self.logged_in:
                        self.open_summary()             # for testing: shows the summary at any time

                if self.logged_in:
                    self.handle_mouse_events(event)
                else:
                    self.handle_login_event(event)

            if not self.logged_in:
                self.draw_login()
                pygame.display.update()
                self.clock.tick(self.FPS)
                await asyncio.sleep(0)
                continue

            # the bell stays on until every mail has been read
            self.notified = any(not m['read'] for m in self.inbox)
            self.update_missions()
            self.update_unlocks()

            for i in self.desktop_shortcuts:
                if i.count_down > 0:
                    i.count_down -= 1
                i.draw()

            self.draw_sticky()

            self.open_windows = [w for w in self.open_windows if not w.closed]
            for w in self.open_windows: #both the window and the application
                w.draw()
                w.draw_content()

            self.handle_task_bar()
            self.draw_toasts()

            pygame.display.update()
            self.clock.tick(self.FPS)
            await asyncio.sleep(0)

        # every way of quitting (X button or Esc) ends up here
        for w in self.open_windows:
            if hasattr(w, 'save'): #if w has the save function, neat
                w.save()
        self.save_progress()
        pygame.quit()

if __name__ == '__main__':
    EscaperoomGame = main()
    asyncio.run(EscaperoomGame.Start_Game())
