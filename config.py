"""Configuration values and shared color constants for the Snake Game."""
# Screen / Grid Structural Framework
GRID_SIZE = 25
GRID_WIDTH = 25
GRID_HEIGHT = 25
HUD_HEIGHT = 50  # Fixed legend area at top
WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE + HUD_HEIGHT
TOTAL_TILES = GRID_WIDTH * GRID_HEIGHT
FPS = 10
HUD_Y = 0  # Y position where legend starts
WINDOW_BORDER = 5  # Thickness in pixels of the outer window border

# Color Configuration Matrix (RGB Palettes)
COLOR_BG = (24, 26, 27)
COLOR_GRID = (35, 38, 39)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_MUTED = (140, 145, 145)

COLOR_SNAKE_HEAD = (46, 204, 113)
COLOR_SNAKE_BODY = (39, 174, 96)

COLOR_NORMAL_FOOD = (231, 76, 60)
COLOR_SUPER_FOOD = (241, 196, 15)
COLOR_POISON_FOOD = (155, 89, 182)
COLOR_BLINK_OFF = (40, 40, 40)

COLOR_BUTTON = (52, 73, 94)
COLOR_BUTTON_HOVER = (41, 128, 185)
