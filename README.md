# Snake Game

A modern, feature-rich implementation of the classic Snake game built with Python and Pygame. The game includes special food items, a persistent leaderboard system, and an intuitive graphical interface.

## Features

- **Classic Snake Gameplay**: Navigate the snake to eat food and grow longer
- **Three Food Types**:
  - 🍎 **Normal Food**: Grows the snake by 1 segment
  - ⭐ **Super Food**: Grows the snake by 3 segments (appears randomly, lasts 5 seconds)
  - 💀 **Poison Food**: Shrinks the snake by half its length (appears randomly, lasts 5 seconds)
- **Blinking Effect**: Special foods blink after 3 seconds to warn before they disappear
- **Persistent Leaderboard**: Records and ranks player scores based on maximum snake length
- **Descending Score Ranking**: Longest snakes are ranked first
- **Fixed HUD**: UI legend stays at the top without obscuring the playable grid
- **Smooth Controls**: Arrow keys or WASD to navigate
- **Game States**: Menu, Gameplay, and Leaderboard views

## System Requirements

- Python 3.7+
- Pygame 2.6.0

## Installation

### 1. Install Python
Ensure Python 3.7 or higher is installed on your system. Download from [python.org](https://www.python.org/).

### 2. Clone or Download the Project
Navigate to the project directory:
```bash
cd final
```

### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

## Running the Game

Execute the main program:
```bash
python main.py
```

The game window will open with the main menu.

## Game Controls

### Main Menu
- **Type** to enter your player name
- **Click** "Start Simulation" to begin playing
- **Click** "View Leaderboard" to see high scores
- **Click** "Exit Application" to quit

### During Gameplay
- **⬆️ Arrow Up / W**: Move snake up
- **⬇️ Arrow Down / S**: Move snake down
- **⬅️ Arrow Left / A**: Move snake left
- **➡️ Arrow Right / D**: Move snake right
- **ESC**: Return to main menu
- **R** (after game over): Restart the game

### Leaderboard
- **Click** "Return to Menu" to go back to the main menu

## Game Rules

1. **Objective**: Grow your snake to fill as much of the grid as possible without colliding
2. **Collision**: The game ends if the snake hits:
   - The game boundaries
   - Itself
3. **Win Condition**: Fill the entire 25×25 grid (625 segments)
4. **Score**: Your score is the length of your snake when you lose or win
5. **Food Mechanics**:
   - Normal food appears immediately when eaten
   - Super and Poison foods appear randomly and disappear after 5 seconds
   - Both special foods blink at the 3-second mark as a warning

## Project Structure

```
final/
├── main.py              # Main game application and event loop
├── entities.py          # Snake and food entity classes
├── config.py            # Game configuration constants
├── ui.py                # UI components (buttons, text input)
├── history.py           # Leaderboard persistence manager
├── decorators.py        # Event logging decorators
├── snake_history.json   # Persistent leaderboard data (auto-created)
├── requirements.txt     # Python package dependencies
└── README.md            # This file
```

## File Descriptions

- **main.py**: Primary game kernel managing GUI scenes, state transitions, and rendering
- **entities.py**: Defines the Snake class and Food types (NormalFood, SuperFood, PoisonFood)
- **config.py**: Centralized configuration for grid size, colors, and FPS settings
- **ui.py**: UI widgets including Button and TextInput components
- **history.py**: Manages leaderboard persistence to `snake_history.json`
- **decorators.py**: Provides logging decorators for game events and data pipeline validation

## Leaderboard

The leaderboard is automatically saved to `snake_history.json` and persists between sessions. Records are sorted by:
- **Primary**: Snake length (descending - longest first)
- **Secondary**: Timestamp (most recent first for tied lengths)

You can view the leaderboard by clicking "View Leaderboard" in the main menu.

## Gameplay Tips

1. **Plan Ahead**: Try to anticipate where the snake will move to avoid trapping yourself
2. **Special Foods**: Super food is worth 3 segments - prioritize collecting it before it disappears
3. **Poison Food**: Avoid unless your snake is very long and you need to reduce size for strategic advantage
4. **Corner Tricks**: Use corners and walls strategically to create longer, safer paths
5. **Blinking Warning**: When special foods start blinking (at 3 seconds), they'll disappear soon

## Technical Details

- **Grid Size**: 25×25 tiles (625 total)
- **Tile Size**: 25 pixels
- **Window Size**: 625×675 pixels (25×25 grid + 50px HUD)
- **FPS**: 10 (one move per frame)
- **Special Food Duration**: 5 seconds
- **Blink Warning**: Starts at 3 seconds
- **Blink Frequency**: 200ms alternation

## Troubleshooting

### "Module not found: pygame"
```bash
pip install pygame
```

### Game runs slowly
- Ensure no other resource-intensive applications are running
- Check that FPS is set correctly in `config.py`

### Leaderboard not saving
- Ensure the program has write permissions in the game directory
- Check that `snake_history.json` is not corrupted

## License

This project is provided as-is for educational purposes.

## Changelog

### v1.0
- Initial release with core gameplay
- Leaderboard system
- Three food types
- HUD UI with fixed positioning
