"""Main application kernel for the Snake Game.

This module provides the ``GameApp`` class which manages application state,
rendering, input handling, and the main game loop. Game score is tracked by
the snake's current length and persisted via the history manager.
"""

import sys
import time
import random

import pygame

from config import (COLOR_BG, COLOR_GRID, COLOR_TEXT, COLOR_TEXT_MUTED, FPS,
                    GRID_HEIGHT, GRID_SIZE, GRID_WIDTH, HUD_HEIGHT, HUD_Y,
                    HEIGHT, TOTAL_TILES, WIDTH)
from decorators import log_game_event
from entities import Snake, NormalFood, SuperFood, PoisonFood
from history import GameHistoryManager
from ui import Button, TextInput


class GameApp:
    """ Primary application kernel managing GUI scene routing and layout composition. """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("the Snake Game")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Consolas", 44, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_sm = pygame.font.SysFont("Consolas", 15)

        self.history_manager = GameHistoryManager()
        self.state = "MENU"

        self.setup_menu_ui()
        self.reset_game_state()

    def setup_menu_ui(self):
        mid_x = WIDTH // 2
        self.name_input = TextInput(mid_x - 125, 170, 250, 45, self.font_ui)

        self.menu_buttons = [
            Button(
                mid_x - 125,
                240,
                250,
                45,
                "Start Simulation",
                self.font_ui,
                self.start_game,
            ),
            Button(
                mid_x - 125,
                300,
                250,
                45,
                "View Leaderboard",
                self.font_ui,
                self.open_leaderboard,
            ),
            Button(
                mid_x - 125,
                360,
                250,
                45,
                "Exit Application",
                self.font_ui,
                self.terminate_app,
            ),
        ]

        self.leaderboard_buttons = [
            Button(
                mid_x - 125,
                HEIGHT - 75,
                250,
                45,
                "Return to Menu",
                self.font_ui,
                self.open_menu,
            ),
        ]

    def reset_game_state(self):
        # Spawn snake near the center of the grid and reset session state
        self.snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.normal_food = None
        self.special_foods = []
        self.spawn_normal_food()
        self.last_special_spawn = time.time()
        self.game_over = False
        self.game_won = False
        # `score` removed: leaderboard now uses snake length directly
        self.paused = False

    def get_vacant_cells(self):
        # Compute grid cells not currently occupied by snake or food items.
        # This is used to place new food entities safely.
        occupied = set(self.snake.body)
        if self.normal_food:
            occupied.add(self.normal_food.get_position())
        for sf in self.special_foods:
            occupied.add(sf.get_position())
        vacant_cells = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in occupied:
                    vacant_cells.append((x, y))
        return vacant_cells

    def spawn_normal_food(self):
        """Place normal food on a random vacant cell within the grid."""
        vacant = self.get_vacant_cells()
        if vacant:
            pos = random.choice(vacant)
            self.normal_food = NormalFood(pos[0], pos[1])

    def resolve_food_interaction(self, next_head_pos):
        """Resolve food collisions and return (grow, shrink).

        Points are removed — length will be used as the score instead.
        """
        # Normal food: single-segment growth and immediate respawn.
        if self.normal_food and next_head_pos == self.normal_food.get_position():
            self.spawn_normal_food()
            return 1, 0

        # Check for collisions with time-limited special foods.
        eaten_item = next(
            (sf for sf in self.special_foods if next_head_pos == sf.get_position()),
            None,
        )
        if eaten_item is None:
            return 0, 0

        self.special_foods.remove(eaten_item)
        if isinstance(eaten_item, SuperFood):
            # Super food gives multiple segments of growth.
            return 3, 0

        if isinstance(eaten_item, PoisonFood):
            # Poison halves the snake length (rounded down) but never
            # removes the head immediately to avoid instant death.
            return 0, max(1, len(self.snake.body) // 2)

        return 0, 0

    @log_game_event
    def trigger_special_spawn(self):
        vacant = self.get_vacant_cells()
        if len(vacant) < 2:
            return "Rejected: Map full"

        choice = random.choice(["SUPER", "POISON", "BOTH"])
        if choice in ["SUPER", "BOTH"]:
            pos = random.choice(vacant)
            self.special_foods.append(SuperFood(pos[0], pos[1]))
            vacant.remove(pos)
        if choice in ["POISON", "BOTH"] and vacant:
            pos = random.choice(vacant)
            self.special_foods.append(PoisonFood(pos[0], pos[1]))
        return f"Dispatched entities matrix: {choice}"

    def start_game(self):
        if not self.name_input.text:
            self.name_input.text = "Anonymous"
        self.reset_game_state()
        self.state = "GAME"

    def open_leaderboard(self):
        self.state = "LEADERBOARD"

    def open_menu(self):
        self.state = "MENU"

    def terminate_app(self):
        pygame.quit()
        sys.exit()

    def execute(self):
        while True:
            self.process_events()
            self.update_states()
            self.render_graphics()
            if self.state == "GAME" and not self.game_over and not self.game_won and not self.paused:
                speed = min(FPS + len(self.snake.body) // 5, 20)
            else:
                speed = FPS
            self.clock.tick(speed)

    def process_events(self):
        """Process all pending events for the current application state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate_app()
                return

            if self.state == "MENU":
                self.name_input.handle_event(event)
                for button in self.menu_buttons:
                    button.handle_event(event)
            elif self.state == "LEADERBOARD":
                for button in self.leaderboard_buttons:
                    button.handle_event(event)
            elif self.state == "GAME":
                self.process_game_event(event)

    def process_game_event(self, event):
        """Handle game-specific keyboard input while a session is active."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_p and not self.game_over and not self.game_won:
            self.paused = not self.paused
            return

        if event.key == pygame.K_ESCAPE:
            self.paused = False
            self.state = "MENU"
            return

        if self.paused:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.snake.change_direction((0, -1))
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.snake.change_direction((0, 1))
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.snake.change_direction((-1, 0))
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.change_direction((1, 0))
        elif event.key == pygame.K_r and (self.game_over or self.game_won):
            self.reset_game_state()

    def update_states(self):
        if self.state != "GAME" or self.game_over or self.game_won or self.paused:
            return

        self.special_foods = [sf for sf in self.special_foods if sf.update()]

        if time.time() - self.last_special_spawn >= 8.0:
            self.trigger_special_spawn()
            self.last_special_spawn = time.time()

        head_x, head_y = self.snake.body[0]
        dx, dy = self.snake.next_direction
        next_head_pos = (head_x + dx, head_y + dy)

        grow, shrink = self.resolve_food_interaction(next_head_pos)
        self.snake.move(grow=grow, shrink=shrink)
        # Score attribute removed; use snake length directly when needed

        if len(self.snake.body) == 0 or self.snake.check_collision(GRID_WIDTH, GRID_HEIGHT):
            self.game_over = True
            self.history_manager.save_record(self.name_input.text, len(self.snake.body))
            return

        if len(self.snake.body) >= TOTAL_TILES:
            self.game_won = True
            self.history_manager.save_record(self.name_input.text, len(self.snake.body))

    # ── High-Fidelity Food Drawing Interceptor ─────────────────────────────────
    def draw_polished_food(self, food):
        col, row = food.get_position()
        cx = col * GRID_SIZE + GRID_SIZE // 2
        cy = row * GRID_SIZE + GRID_SIZE // 2 + HUD_HEIGHT
        r = GRID_SIZE // 2 - 1

        if isinstance(food, SuperFood):
            label = "⭐"
        elif isinstance(food, PoisonFood):
            label = "💀"
        else:
            label = "🍎"

        # Use food's actual color (respects blinking effect from update method)
        base_color = food.color

        # 1. Soft Alpha Radial Glow Vector Blit
        glow_surf = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*base_color, 55), (GRID_SIZE, GRID_SIZE), r + 6)
        self.screen.blit(glow_surf, (cx - GRID_SIZE, cy - GRID_SIZE))

        # 2. Centered Circular Entity Frame
        pygame.draw.circle(self.screen, base_color, (cx, cy), r)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r, 1)

        # 3. Dynamic Emoji Graphic Layout Overlay
        try:
            emoji_font = pygame.font.SysFont("Segoe UI Symbol", int(GRID_SIZE * 0.75))
            if not emoji_font:
                emoji_font = self.font_sm
            lbl_surf = emoji_font.render(label, True, (255, 255, 255))
            lbl_rect = lbl_surf.get_rect(center=(cx, cy))
            self.screen.blit(lbl_surf, lbl_rect)
        except Exception:
            pass

    def render_graphics(self):
        self.screen.fill(COLOR_BG)

        if self.state == "MENU":
            # Title Soft Panel Glow Backdrop
            title = self.font_title.render("SNAKE GAME", True, (46, 204, 113))
            tx = WIDTH // 2 - title.get_width() // 2
            ty = 60
            glow_panel = pygame.Surface(
                (title.get_width() + 32, title.get_height() + 12),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(glow_panel, (46, 204, 113, 18), glow_panel.get_rect(), border_radius=8)
            self.screen.blit(glow_panel, (tx - 16, ty - 6))
            self.screen.blit(title, (tx, ty))

            lbl = self.font_sm.render("Enter Profile Name Configuration:", True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl, (WIDTH // 2 - 125, 145))

            self.name_input.draw(self.screen)
            for btn in self.menu_buttons: btn.draw(self.screen)

        elif self.state == "LEADERBOARD":
            title = self.font_title.render("SCOREBOARD HISTORY", True, (241, 196, 15))
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 35))

            records = self.history_manager.load_history()
            start_y = 110

            header = self.font_ui.render(
                (
                    f"{'Rank':<8}{'Player Profile':<24}"
                    f"{'Length'}"
                ),
                True,
                COLOR_TEXT_MUTED,
            )
            self.screen.blit(header, (75, start_y))
            pygame.draw.line(
                self.screen,
                (70, 75, 85),
                (60, start_y + 32),
                (WIDTH - 60, start_y + 32),
                2,
            )

            start_y += 45
            # Display sorted records sequentially with alternating matrix shading
            for idx, item in enumerate(records[:8], 1):
                row_rect = pygame.Rect(60, start_y - 4, WIDTH - 120, 26)
                if idx % 2 == 0:
                    pygame.draw.rect(self.screen, (32, 36, 42), row_rect, border_radius=4)

                # Dynamic Podium Tier Color Maps
                if idx == 1:   rank_color = (241, 196, 15)  # Gold
                elif idx == 2: rank_color = (185, 190, 195) # Silver
                elif idx == 3: rank_color = (205, 127, 50)  # Bronze
                else:          rank_color = COLOR_TEXT

                r_txt = f"#{idx:<6}"
                n_txt = f"{item['name'][:18]:<25}"
                s_txt = f"{item['length']}"

                self.screen.blit(self.font_sm.render(r_txt, True, rank_color), (75, start_y))
                self.screen.blit(self.font_sm.render(n_txt, True, COLOR_TEXT), (145, start_y))
                score_surface = self.font_sm.render(
                    s_txt,
                    True,
                    (46, 204, 113),
                )
                self.screen.blit(score_surface, (WIDTH - 210, start_y))

                start_y += 30

            if not records:
                empty_surf = self.font_ui.render(
                    "No pipeline files initialized.",
                    True,
                    COLOR_TEXT_MUTED,
                )
                self.screen.blit(
                    empty_surf,
                    (WIDTH // 2 - empty_surf.get_width() // 2, HEIGHT // 2 - 20),
                )

            for btn in self.leaderboard_buttons: btn.draw(self.screen)

        elif self.state == "GAME":
            # Translucent structural ribbon behind text HUD (fixed at top)
            hud_ribbon = pygame.Surface((WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
            hud_ribbon.fill((15, 17, 22, 220))
            self.screen.blit(hud_ribbon, (0, HUD_Y))

            hud_str = (
                f"User Profile: {self.name_input.text}  │  "
                f"Length: {len(self.snake.body)} / {TOTAL_TILES}"
            )
            hud_surface = self.font_sm.render(hud_str, True, COLOR_TEXT)
            self.screen.blit(hud_surface, (15, HUD_Y + 15))

            # Grid lines (below HUD)
            for x in range(GRID_WIDTH + 1):
                pygame.draw.line(
                    self.screen,
                    COLOR_GRID,
                    (x * GRID_SIZE, HUD_HEIGHT),
                    (x * GRID_SIZE, HEIGHT),
                )
            for y in range(GRID_HEIGHT + 1):
                pygame.draw.line(
                    self.screen,
                    COLOR_GRID,
                    (0, y * GRID_SIZE + HUD_HEIGHT),
                    (WIDTH, y * GRID_SIZE + HUD_HEIGHT),
                )

            # Render upgraded vector overlays instead of basic rect blocks
            if self.normal_food:
                self.draw_polished_food(self.normal_food)
            for sf in self.special_foods:
                self.draw_polished_food(sf)

            self.snake.draw(self.screen)

            if self.paused:
                pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_overlay.fill((16, 18, 23, 150))
                self.screen.blit(pause_overlay, (0, 0))
                pt = self.font_ui.render("PAUSED  —  Press P to Resume", True, (52, 152, 219))
                self.screen.blit(pt, (WIDTH // 2 - pt.get_width() // 2, HEIGHT // 2 - pt.get_height() // 2))
            elif self.game_over:
                self.draw_overlay("CRITICAL COLLISION: GAME OVER", (231, 76, 60))
            elif self.game_won:
                self.draw_overlay("ECOSYSTEM COMPLETED: VICTORY!", (46, 204, 113))

        pygame.display.flip()

    def draw_overlay(self, message, txt_color):
        # Compound matte modal backdrop mask
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((16, 18, 23, 215))
        self.screen.blit(overlay, (0, 0))

        # Centered Dialog Display Box Panel
        pw, ph = 450, 200
        px = WIDTH // 2 - pw // 2
        py = HEIGHT // 2 - ph // 2
        panel = pygame.Rect(px, py, pw, ph)

        pygame.draw.rect(self.screen, (26, 30, 40), panel, border_radius=12)
        pygame.draw.rect(self.screen, txt_color, panel, 2, border_radius=12)

        t1 = self.font_ui.render(message, True, txt_color)
        t2 = self.font_sm.render("Press 'R' to Respawn simulation framework", True, (245, 245, 245))
        t3 = self.font_sm.render(
            "Press 'ESC' to break context back to Menu",
            True,
            COLOR_TEXT_MUTED,
        )

        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, py + 40))
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, py + 105))
        self.screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, py + 135))

if __name__ == "__main__":
    app = GameApp()
    app.execute()
