import pygame as pg


class Button:

    def __init__(self, point, width, height, text, button_color=(0, 0, 0), text_color=(255, 255, 255)):
        self.height = height
        self.width = width
        self.point = point
        self.text_color = text_color
        self.button_color = button_color

        self.rect = pg.rect.Rect(self.point.x - (width/2), self.point.y - (height/2), self.width, self.height)
        self.text = pg.font.SysFont('arial', 10).render(text, True, self.text_color)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center

    def draw(self, screen, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, (20, 20, 20), self.rect)
        else:
            pg.draw.rect(screen, self.button_color, self.rect)
        screen.blit(self.text, self.text_rect)

    def get_action(self, mouse_event):
        return self.rect.collidepoint(mouse_event.pos) if mouse_event is not None else False


