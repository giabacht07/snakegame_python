import os
import pytest
from entities import Snake
from history import GameHistoryManager

# ── SNAKE UNIT TESTS ────────────────────────────────────────────────────────

def test_snake_initialization():
    """Verify that the snake spawns with correct length, position, and direction."""
    snake = Snake(10, 10)
    # Default body should be 3 segments long starting at the head going left
    assert snake.body == [(10, 10), (9, 10), (8, 10)]
    assert snake.direction == (1, 0)


def test_snake_movement():
    """Verify the snake updates its position array correctly when moving."""
    snake = Snake(10, 10)
    snake.move()
    # Moves right by default vector (1, 0)
    assert snake.body == [(11, 10), (10, 10), (9, 10)]


def test_snake_valid_direction_change():
    """Verify the snake can pivot 90 degrees."""
    snake = Snake(10, 10)
    snake.change_direction((0, 1))  # Pivot Down
    snake.move()
    assert snake.body[0] == (10, 11)


def test_snake_invalid_direction_change():
    """Verify that the snake cannot pull a 180-degree turn into itself."""
    snake = Snake(10, 10)
    snake.change_direction((-1, 0))  # Attempt to force turn Left while moving Right
    snake.move()
    # It should ignore the input and proceed right to (11, 10)
    assert snake.body[0] == (11, 10)


def test_snake_growth():
    """Verify snake length expands and updates positioning upon food consumption."""
    snake = Snake(10, 10)
    initial_length = len(snake.body)
    snake.move(grow=True)
    assert len(snake.body) == initial_length + 1


def test_snake_shrinkage():
    """Verify poison food triggers body segmentation removal."""
    snake = Snake(10, 10)
    snake.move(shrink=True)
    # Initial size 3 -> drops to 2 due to compound pop logic
    assert len(snake.body) == 2


def test_boundary_collision():
    """Verify wall collision registers when the snake breaks past limits."""
    # Place the snake right on the edge of a 25x25 grid (indices 0 to 24)
    snake = Snake(24, 0) 
    # Moving forward right (1, 0) will push the head to x=25, which is out of bounds
    snake.move() 
    assert snake.check_collision(25, 25) is True


# ── DATA PIPELINE TESTS ─────────────────────────────────────────────────────

def test_history_manager_io(tmp_path):
    """Verify that history logs load and sort safely using a temporary isolated file."""
    # Use pytest's built-in tmp_path fixture to ensure a clean environment
    test_db = os.path.join(tmp_path, "test_snake_history.json")
    manager = GameHistoryManager(filename=test_db)
    
    # Save dummy profiles out-of-order to test the automatic low->high sort feature
    manager.save_record("Alpha", 50)
    manager.save_record("Beta", 10)
    
    history = manager.load_history()
    assert len(history) == 2
    assert history[1]["name"] == "Beta"   # Lower score (10) must sort to index 1
    assert history[0]["name"] == "Alpha"  # Higher score (50) must sort to index 0


def test_history_contains_length(tmp_path):
    """Verify saved history records include the `length` key and store integer lengths."""
    test_db = os.path.join(tmp_path, "test_snake_history.json")
    manager = GameHistoryManager(filename=test_db)
    manager.save_record("Alice", 7)
    history = manager.load_history()
    assert len(history) == 1
    assert "length" in history[0]
    assert isinstance(history[0]["length"], int)
    assert history[0]["length"] == 7


if __name__ == "__main__":
    import pytest
    pytest.main()