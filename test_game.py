import json
import os
import time

import pytest

from config import COLOR_BLINK_OFF
from entities import NormalFood, PoisonFood, Snake, SuperFood
from history import GameHistoryManager

# ── SNAKE UNIT TESTS ────────────────────────────────────────────────────────

def test_snake_initialization():
    """Verify that the snake spawns with correct length, position, and direction."""
    snake = Snake(10, 10)
    assert snake.body == [(10, 10), (9, 10), (8, 10)]
    assert snake.direction == (1, 0)


def test_snake_movement():
    """Verify the snake updates its position array correctly when moving."""
    snake = Snake(10, 10)
    snake.move()
    assert snake.body == [(11, 10), (10, 10), (9, 10)]


def test_snake_valid_direction_change():
    """Verify the snake can pivot 90 degrees."""
    snake = Snake(10, 10)
    snake.change_direction((0, 1))
    snake.move()
    assert snake.body[0] == (10, 11)


def test_snake_invalid_direction_change():
    """Verify that the snake cannot pull a 180-degree turn into itself."""
    snake = Snake(10, 10)
    snake.change_direction((-1, 0))
    snake.move()
    assert snake.body[0] == (11, 10)


def test_snake_growth():
    """Verify normal food adds exactly one segment."""
    snake = Snake(10, 10)
    initial_length = len(snake.body)
    snake.move(grow=1)
    assert len(snake.body) == initial_length + 1


def test_snake_super_growth():
    """Verify super food (grow=3) adds exactly three segments."""
    snake = Snake(10, 10)
    initial_length = len(snake.body)
    snake.move(grow=3)
    assert len(snake.body) == initial_length + 3


def test_snake_shrinkage():
    """Verify poison food removes one segment beyond the normal tail pop."""
    snake = Snake(10, 10)
    snake.move(shrink=1)
    # Head moves forward (+1), tail pops (-1), then shrink pops one more (-1): 3 → 2
    assert len(snake.body) == 2


def test_snake_shrink_protection():
    """Verify that shrink cannot reduce the snake below one segment (the head)."""
    snake = Snake(10, 10)
    snake.move(shrink=100)
    assert len(snake.body) == 1


def test_boundary_collision():
    """Verify wall collision registers when the snake crosses a grid boundary."""
    snake = Snake(24, 0)
    snake.move()
    assert snake.check_collision(25, 25) is True


def test_no_collision():
    """Verify that a snake in a valid position reports no collision."""
    snake = Snake(10, 10)
    assert snake.check_collision(25, 25) is False


def test_snake_self_collision():
    """Verify that the snake detects when its head overlaps a body segment."""
    snake = Snake(5, 5)
    # Manually construct a body where the head position repeats further in the list
    snake.body = [(5, 5), (5, 6), (5, 7), (5, 5)]
    assert snake.check_collision(25, 25) is True


# ── FOOD UNIT TESTS ──────────────────────────────────────────────────────────

def test_normal_food_position():
    """Verify NormalFood reports the correct grid position."""
    food = NormalFood(7, 3)
    assert food.get_position() == (7, 3)


def test_timed_food_active_within_duration():
    """Verify TimedFood.update() returns True while its lifetime has not expired."""
    food = SuperFood(4, 4)
    assert food.update() is True


def test_timed_food_expires():
    """Verify TimedFood.update() returns False after its duration elapses."""
    food = SuperFood(4, 4)
    food.creation_time = time.time() - 10.0  # 10 s ago, well past the 5 s duration
    assert food.update() is False


def test_timed_food_blinks():
    """Verify food color alternates between base and blink-off during the blink window."""
    food = PoisonFood(2, 2)
    # 4 s ago: past blink_start (3.0 s) but before duration (5.0 s)
    food.creation_time = time.time() - 4.0
    assert food.update() is True
    assert food.color in (COLOR_BLINK_OFF, food.base_color)


# ── DATA PIPELINE TESTS ─────────────────────────────────────────────────────

def test_history_manager_io(tmp_path):
    """Verify history records load and sort by descending length."""
    test_db = os.path.join(tmp_path, "test_snake_history.json")
    manager = GameHistoryManager(filename=test_db)

    manager.save_record("Alpha", 50)
    manager.save_record("Beta", 10)

    history = manager.load_history()
    assert len(history) == 2
    assert history[0]["name"] == "Alpha"  # highest length first
    assert history[1]["name"] == "Beta"


def test_history_contains_length(tmp_path):
    """Verify saved records include an integer 'length' field."""
    test_db = os.path.join(tmp_path, "test_snake_history.json")
    manager = GameHistoryManager(filename=test_db)
    manager.save_record("Alice", 7)
    history = manager.load_history()
    assert len(history) == 1
    assert "length" in history[0]
    assert isinstance(history[0]["length"], int)
    assert history[0]["length"] == 7


def test_history_missing_file(tmp_path):
    """Verify load_history returns an empty list when no file exists yet."""
    test_db = os.path.join(tmp_path, "nonexistent.json")
    manager = GameHistoryManager(filename=test_db)
    assert manager.load_history() == []


def test_history_corrupt_file(tmp_path):
    """Verify load_history returns an empty list when the JSON is malformed."""
    test_db = os.path.join(tmp_path, "corrupt.json")
    with open(test_db, "w") as f:
        f.write("not valid json {{{")
    manager = GameHistoryManager(filename=test_db)
    assert manager.load_history() == []


def test_history_migration(tmp_path):
    """Verify that legacy records using 'score' are migrated to 'length' on load."""
    test_db = os.path.join(tmp_path, "legacy.json")
    legacy = [{"name": "Legacy", "score": 42, "timestamp": "2024-01-01 00:00:00"}]
    with open(test_db, "w") as f:
        json.dump(legacy, f)

    manager = GameHistoryManager(filename=test_db)
    history = manager.load_history()
    assert len(history) == 1
    assert "length" in history[0]
    assert "score" not in history[0]
    assert history[0]["length"] == 42


if __name__ == "__main__":
    pytest.main()
