"""Entity models used by the Snake Game, including the snake and food types.

This module provides the following classes:
- ``Food``: Base drawable food entity.
- ``TimedFood``: Food that expires after a duration and blinks before removal.
- ``NormalFood``, ``SuperFood``, ``PoisonFood``: Concrete food types.
- ``Snake``: Manages the snake body segments, movement, growth, and collisions.

The ``Snake.move`` method supports optional ``grow`` and ``shrink`` parameters
to modify body length in response to food interactions.
"""

import time

import pygame

from config import (COLOR_BLINK_OFF, COLOR_NORMAL_FOOD, COLOR_POISON_FOOD,
                    COLOR_SNAKE_BODY, COLOR_SNAKE_HEAD, COLOR_SUPER_FOOD,
                    GRID_SIZE, HUD_HEIGHT)

class Food:
    """Base food model abstraction demonstrating polymorphic entity configurations."""

    def __init__(self, x, y, color):
        """Initialize a food entity at the given grid coordinates."""
        self.x = x
        self.y = y
        self.color = color

    def get_position(self):
        """Return the current grid position of this food item."""
        return (self.x, self.y)

    def update(self):
        """Return True when the food should remain active."""
        return True


class TimedFood(Food):
    """Subclass featuring runtime life cycle limits and end-stage frequency blinking."""

    def __init__(self, x, y, color, duration=5.0, blink_start=3.0):
        """Initialize a timed food item with a blink window and duration."""
        super().__init__(x, y, color)
        self.creation_time = time.time()
        self.duration = duration
        self.blink_start = blink_start
        self.base_color = color

    def update(self):
        """Update blink state and return whether this item should remain present."""
        elapsed = time.time() - self.creation_time
        if elapsed >= self.duration:
            return False

        if elapsed >= self.blink_start:
            blink_phase = int((elapsed - self.blink_start) * 5) % 2
            self.color = COLOR_BLINK_OFF if blink_phase == 0 else self.base_color
        return True


class NormalFood(Food):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_NORMAL_FOOD)


class SuperFood(TimedFood):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_SUPER_FOOD)


class PoisonFood(TimedFood):
    def __init__(self, x, y):
        super().__init__(x, y, COLOR_POISON_FOOD)


class Snake:
    """ Tracks array dimensions, collision vectors, and kinematic structural expansions. """
    def __init__(self, start_x, start_y):
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

    def change_direction(self, vector):
        # Prevent a 180-degree (direct reverse) direction change which would
        # immediately collide the head with the next segment.
        if (vector[0] * -1, vector[1] * -1) != self.direction:
            self.next_direction = vector

    def move(self, grow=0, shrink=0):
        """Advance the snake, optionally growing or shrinking its body."""
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        # When growing, we insert the new head and then duplicate the tail
        # segments to increase length by the requested amount.
        if grow:
            extra_growth = max(0, grow - 1)
            for _ in range(extra_growth):
                self.body.append(self.body[-1])
        else:
            # Standard movement removes the last segment (tail follows head)
            self.body.pop()
            if shrink:
                # Shrink should not remove the head segment; ensure at least
                # one segment remains after shrink operations.
                shrink_amount = min(shrink, len(self.body) - 1)
                for _ in range(shrink_amount):
                    self.body.pop()

    def check_collision(self, bounds_w, bounds_h):
        """Check whether the snake has collided with the bounds or itself."""
        head = self.body[0]
        if head[0] < 0 or head[0] >= bounds_w or head[1] < 0 or head[1] >= bounds_h:
            return True
        if head in self.body[1:]:
            return True
        return False

    def draw(self, surface):
        for idx, segment in enumerate(self.body):
            color = COLOR_SNAKE_HEAD if idx == 0 else COLOR_SNAKE_BODY
            rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE + HUD_HEIGHT,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(surface, color, rect, border_radius=3)
            pygame.draw.rect(surface, (16, 40, 20), rect, 1)
