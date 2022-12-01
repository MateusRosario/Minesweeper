import pygame as pg
from settings import *
from button import Button
from point import Point
import random

MENU = 0
MODE = 1
GAME = 2


class Game:
    running = False
    state = MENU
    screen = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()
    minefield = None

    def __init__(self):
        pg.init()
        pg.display.set_caption(TITLE)

    def run(self):
        # Game Loop
        event_mousedown = None
        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break
                if event.type == pg.MOUSEBUTTONDOWN:
                    event_mousedown = event
            if self.state == MENU:
                self.start_screen(event_mousedown)
            if self.state == MODE:
                self.mode_screen(event_mousedown)
            if self.state == GAME:
                self.game_screen(event_mousedown)
                if self.minefield.state is Minefield.FINILIZED:
                    self.state = MENU
            event_mousedown = None
            self.clock.tick(FPS)

    def start_screen(self, events_mouse):
        button_start = Button(Point(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2), 200, 60, 'START', COLORS['BUTTON_1'])

        text_credits = pg.font.SysFont('sans', 20).render('developed by: Mateus Rosario', True,
                                                          COLORS['CREDITS'])

        self.screen.fill(COLORS['BACKGROUND'])
        mouse = pg.mouse.get_pos()

        button_start.draw(self.screen, mouse)

        self.screen.blit(text_credits, (WIDTH - 290, HEIGHT - 30))
        pg.display.update()

        if button_start.get_action(events_mouse):
            self.state = MODE

    def mode_screen(self, events_mouse):
        easy_button = Button(Point(SCREEN_SIZE[0]/2, 30 + 20), 200, 60, 'EASY MODE', COLORS['BUTTON_1'])
        medium_button = Button(Point(SCREEN_SIZE[0]/2, 120 + 20), 200, 60, 'MEDIUM MODE', COLORS['BUTTON_1'])
        hard_button = Button(Point(SCREEN_SIZE[0]/2, 210 + 20), 200, 60, 'HARD MODE', COLORS['BUTTON_1'])

        self.screen.fill(COLORS['BACKGROUND'])
        mouse = pg.mouse.get_pos()

        easy_button.draw(self.screen, mouse)
        medium_button.draw(self.screen, mouse)
        hard_button.draw(self.screen, mouse)

        pg.display.update()

        if easy_button.get_action(events_mouse):
            self.state = GAME
            self.minefield = Minefield(Point(10, 10), 9, 9, 10)
            self.screen = pg.display.set_mode(self.minefield.size_screen)

        elif medium_button.get_action(events_mouse):
            self.state = GAME
            self.minefield = Minefield(Point(10, 10), 18, 18, 145)
            self.screen = pg.display.set_mode(self.minefield.size_screen)

        elif hard_button.get_action(events_mouse):
            self.state = GAME
            self.minefield = Minefield(Point(10, 10), 27, 27, 218)
            self.screen = pg.display.set_mode(self.minefield.size_screen)

    def game_screen(self, event_mousedown):
        self.screen.fill(COLORS['BACKGROUND'])
        self.minefield.draw(self.screen, pg.mouse.get_pos(), event_mousedown)
        pg.display.flip()


class Minefield:

    STARTING = 0
    PLAYING = 1
    LOST_SCREEN = 2
    WIN_SCREEN = 3
    FINILIZED = -1

    is_first_click = True
    column_gap = 10
    row_gap = 10
    text_color = (40, 40, 0)
    text_size = 30
    state = STARTING
    countdown = None
    start_tick = None
    final_tick = None
    bombs_flagged = 0

    def __init__(self, pos, size_x, size_y, num_bombs):
        self.pos = Point(self.column_gap, self.row_gap)
        self.size_x = size_x
        self.size_y = size_y
        self.num_bombs = num_bombs

        self.campo = [[Teile(False, x, y) for y in range(size_y)] for x in range(size_x)]
        self.tile_size = self.text_size + 10
        self.bottom_space = self.row_gap + self.text_size
        self.size_screen = (int(self.column_gap + (size_x*self.column_gap) + (self.tile_size*size_x)), int(self.row_gap + (size_y*self.row_gap) + (self.tile_size*size_y) + self.bottom_space))

    def draw(self, screen, mouse_pos, mousedown_event):
        if self.state is self.STARTING:
            self.start_screen(screen, mousedown_event)
        elif self.state is self.PLAYING:
            self.playing(screen, mouse_pos, mousedown_event)
        elif self.state is self.LOST_SCREEN:
            self.lost_screen(screen, mousedown_event)
        elif self.state is self.WIN_SCREEN:
            self.win_screen(screen, mousedown_event)

    def start_screen(self, screen, mousedown_event):
        if self.countdown is None:
            self.countdown = 2 * FPS
        self.countdown -= 1
        text = pg.font.SysFont('arial', 30).render('BOA SORTE', True, COLORS['TEXT'])
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2, HEIGHT/2)
        screen.blit(text, text_rect)
        if self.countdown == 0 or (mousedown_event is not None and self.countdown < 2 * FPS - FPS):
            self.countdown = None
            self.start_tick = pg.time.get_ticks()
            self.state = self.PLAYING

    def playing(self, screen, mouse_pos, mousedown_event):
        pos = Point(self.pos.x, self.pos.y)

        coord_hover = None

        if not self.is_first_click:
            self.show_blank_fields()

        for column in self.campo:
            for tile in column:
                tile_rect = pg.rect.Rect(pos.x, pos.y, self.tile_size, self.tile_size)
                if tile.get_action(tile_rect, mousedown_event) and self.is_first_click:
                    self.is_first_click = False
                    self.populate_field(tile)
                text = pg.font.SysFont('arial', self.text_size).render(tile.get_text(), True, self.text_color)
                text_rect = text.get_rect()
                text_rect.center = tile_rect.center
                pg.draw.rect(screen, COLORS[tile.get_color(tile_rect, mouse_pos)], tile_rect)
                screen.blit(text, text_rect)
                if tile.is_hovering(tile_rect, mouse_pos):
                    coord_hover = str(tile.x) + ', ' + str(tile.y)

                if tile.exploded:
                    self.state = self.LOST_SCREEN
                pos.y += self.tile_size + self.row_gap
            pos.y = self.pos.y
            pos.x += self.tile_size + self.column_gap

        timer = pg.font.SysFont('arial', self.text_size).render(str((pg.time.get_ticks() - self.start_tick)/1000), True, (140, 0, 0))
        timer_rect = timer.get_rect()
        timer_rect.center = (self.column_gap + timer_rect.width/2, self.tile_size*self.size_y + self.row_gap*self.size_y + self.text_size)
        screen.blit(timer, timer_rect)

    def lost_screen(self, screen, mousedown_event):
        if self.countdown is None:
            self.countdown = 5 * FPS
        self.countdown -= 1
        text = pg.font.SysFont('arial', 30).render('VOCÊ PERDEU ...', True, COLORS['TEXT'])
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2, HEIGHT/2)
        screen.blit(text, text_rect)
        if self.countdown == 0 or mousedown_event is not None:
            self.state = self.FINILIZED

    def win_screen(self, screen, mousedown_event):
        if self.countdown is None:
            self.countdown = 5 * FPS
        self.countdown -= 1
        text = pg.font.SysFont('arial', 30).render('VOCÊ VENCEU EM', True, COLORS['TEXT'])
        text2 = pg.font.SysFont('arial', 30).render(str((self.final_tick - self.start_tick)/1000) + 's', True, COLORS['TEXT'])
        text3 = pg.font.SysFont('arial', 30).render('PARABÊNS', True, COLORS['TEXT'])
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2, HEIGHT/2)
        screen.blit(text, text_rect)
        text_rect = text2.get_rect()
        text_rect.center = (WIDTH/2, HEIGHT/2 + 40)
        screen.blit(text2, text_rect)
        text_rect = text3.get_rect()
        text_rect.center = (WIDTH/2, HEIGHT/2 + 80)
        screen.blit(text3, text_rect)
        if self.countdown == 0 or mousedown_event is not None:
            self.state = self.FINILIZED

    def show_blank_fields(self):
        bombs_found = 0
        wrong_marked = False
        for line in self.campo:
            for tile in line:
                #print('Coord:', x, y, '\n[', end='')

                if tile.flagged:
                    if tile.bomb:
                        bombs_found += 1
                    else:
                        wrong_marked = True

                if tile.revealed and tile.value == 0:
                    if tile.y != 0:
                        self.campo[tile.x][tile.y - 1].reveal_next()
                        #print(' (', x, y - 1, '),', end='')
                        if tile.x != 0:
                            self.campo[tile.x - 1][tile.y - 1].reveal_next()
                            #print(' (', x - 1, y - 1, '),', end='')

                        if tile.x < self.size_x - 1:
                            self.campo[tile.x + 1][tile.y - 1].reveal_next()
                            #print(' (', x + 1, y - 1, '),', end='')

                    if tile.x != 0:
                        self.campo[tile.x - 1][tile.y].reveal_next()
                        #print(' (', x - 1, y, '),', end='')

                    if tile.x < self.size_x - 1:
                        self.campo[tile.x + 1][tile.y].reveal_next()
                        #print(' (', x + 1, y, '),', end='')

                    if tile.y < self.size_y - 1:
                        self.campo[tile.x][tile.y + 1].reveal_next()
                        #print(' (', x, y + 1, '),', end='')
                        if tile.x != 0:
                            self.campo[tile.x - 1][tile.y + 1].reveal_next()
                            #print(' (', x - 1, y + 1, '),', end='')

                        if tile.x < self.size_x - 1:
                            self.campo[tile.x + 1][tile.y + 1].reveal_next()
                            #print(' (', x + 1, y + 1, '),', end='')
                    #print(' ]')
        self.bombs_flagged = bombs_found
        if bombs_found == self.num_bombs and not wrong_marked:
            self.final_tick = pg.time.get_ticks()
            self.state = self.WIN_SCREEN

    def populate_field(self, tile):
        bombs = []
        for i in range(self.num_bombs):
            while True:
                coord = (random.randint(0, self.size_x - 1), random.randint(0, self.size_y - 1))
                if coord[0] != tile.x and coord[1] != tile.y and coord not in bombs:
                    bombs.append(coord)
                    break
        # print('Bombs', bombs)

        for x, y in bombs:
            # print('Coord:', x, y, '\n[', end='')

            self.campo[x][y].bomb = True

            if y != 0:
                self.campo[x][y - 1].add_count()
                #print(' (', x, y - 1, '),', end='')
                if x != 0:
                    self.campo[x - 1][y - 1].add_count()
                    #print(' (', x - 1, y - 1, '),', end='')

                if x < self.size_x - 1:
                    self.campo[x + 1][y - 1].add_count()
                    #print(' (', x + 1, y - 1, '),', end='')

            if x != 0:
                self.campo[x - 1][y].add_count()
                #print(' (', x - 1, y, '),', end='')

            if x < self.size_x - 1:
                self.campo[x + 1][y].add_count()
                #print(' (', x + 1, y, '),', end='')

            if y < self.size_y - 1:
                self.campo[x][y + 1].add_count()
                #print(' (', x, y + 1, '),', end='')
                if x != 0:
                    self.campo[x - 1][y + 1].add_count()
                    #print(' (', x - 1, y + 1, '),', end='')

                if x < self.size_x - 1:
                    self.campo[x + 1][y + 1].add_count()
                    #print(' (', x + 1, y + 1, '),', end='')
            #print(' ]')


class Teile:
    value = 0
    revealed = False
    flagged = False
    questioned = False
    exploded = False

    def __init__(self, bomb, x, y):
        self.bomb = bomb
        self.x = x
        self.y = y

    def add_count(self):
        if not self.bomb:
            self.value += 1

    def get_color(self, rect, mouse_pos):
        if self.revealed:
            if self.bomb:
                return 'EXPLOSION'
            else:
                return 'TILE_BLANK'
        else:
            if self.flagged:
                return 'TILE_FLAGGED'
            else:
                if self.is_hovering(rect, mouse_pos):
                    return 'TILE_HOVER'
                else:
                    return 'TILE'

    def get_text(self):
        if not self.revealed:
            return None
        else:
            if self.bomb or self.value == 0:
                return None
            else:
                return str(self.value)

    def is_hovering(self, rect, mouse_pos):
        return rect.collidepoint(mouse_pos)

    def get_action(self, rect, mouse_event):
        if mouse_event is not None:
            if rect.collidepoint(mouse_event.pos):
                if mouse_event.button == 1:
                    self.revealed = True
                    self.flagged = False
                    if self.bomb:
                        self.exploded = True
                    return True
                else:
                    if self.flagged:
                        self.flagged = False
                    else:
                        self.flagged = True
                    return False
            else:
                return False
        else:
            return False

    def reveal_next(self):
        if not self.bomb:
            self.revealed = True
            self.flagged = False
