import pygame
from constants import *

# --- 4. UI HELPER: BUTTONS ---
class Button:
    def __init__(self, x, y, w, h, text, action=None, color=C_PANEL):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = C_BTN_HOVER

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        col = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, C_ACCENT, self.rect, 2, border_radius=8)
        
        txt_surf = font.render(self.text, True, C_TEXT_MAIN)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
