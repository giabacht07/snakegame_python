"""User interface widgets for the Snake Game menu and input controls.

Contains small, focused UI primitives used by the main menu:
- ``Button``: Clickable button with hover visual state.
- ``TextInput``: Simple single-line text entry with cursor and basic validation.

These widgets directly use Pygame surfaces and events and intentionally avoid
any complex layout logic to remain lightweight.
"""

import time

import pygame

from config import COLOR_BUTTON_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED

class Button:
    """Fully interactive UI event button module tracking coordinate collision."""

    def __init__(self, x, y, width, height, text, font, callback):
        """Initialize a button widget with position, size, text, and callback."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self._hover_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self._hover_surf.fill((*COLOR_BUTTON_HOVER, 40))

    def draw(self, surface):
        """Render the button and hover state to the given surface."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)

        # Sleek dark composite button panel layout
        bg_color = (40, 50, 65) if hovered else (30, 34, 42)
        border_color = COLOR_BUTTON_HOVER if hovered else (70, 80, 95)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        if hovered:
            surface.blit(self._hover_surf, self.rect.topleft)

        text_color = COLOR_TEXT if hovered else (210, 215, 220)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Execute the button callback if the button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


class TextInput:
    """Canvas context graphical text widget tracking user keystroke events."""

    def __init__(self, x, y, width, height, font, default_text="Player1"):
        """Initialize text input with default text and visual settings."""
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = default_text
        self.active = False
        self.cursor_visible = True

    def handle_event(self, event):
        """Process click and typing events for the text input widget."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.active = False
            else:
                # Limit text input to a short username and allow only common
                # safe characters to avoid rendering surprises or injection.
                if len(self.text) < 14 and (event.unicode.isalnum() or event.unicode in " _-"):
                    self.text += event.unicode

    def draw(self, surface):
        """Draw the input box and blinking cursor onto the surface."""
        self.cursor_visible = int(time.time() * 2) % 2 == 0

        bg_color = (36, 40, 48) if self.active else (25, 27, 30)
        border_color = (52, 152, 219) if self.active else (65, 70, 80)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        display_text = self.text
        if not display_text and not self.active:
            display_text = "Type Profile..."
            text_color = COLOR_TEXT_MUTED
        else:
            text_color = COLOR_TEXT
            if self.active and self.cursor_visible:
                display_text += "│"

        text_surf = self.font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 14, self.rect.centery))
        surface.blit(text_surf, text_rect)
