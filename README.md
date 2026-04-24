Name: Zaid Hasan

## Description
This project implements a fully functional, text-based version of the board game Cluedo, featuring an intelligent AI opponent. Beyond the core movement mechanics, this version includes a sophisticated AI agent capable of logical deduction using a "negative knowledge" constraint satisfaction system. The game features a complete loop including suggestions, clockwise refutations, dragging mechanics, and win/loss states via accusations. It also includes a custom Terminal UI using ANSI colors for a retro-style board visualization.

## Folder Structure
- `main.py`: The entry point script to run the game loop.
- `game_logic.py`: The controller class handling turns, rules, and state management.
- `ai_logic.py`: Contains the `AIBrain` class which handles the AI's knowledge base, deduction engine, and decision-making strategies.
- `board.py`: Handles the grid layout, dynamic rendering of players, and coordinate validation.
- `models.py`: Contains data structures for `Player`, `Card`, and the AI's "Notebook" (`possible_solutions`).
- `ui.py`: A helper module for handling ANSI color codes, screen clearing, and formatting the console output.
- `config.py`: Stores game constants (Room names, grid size, secret passage logic).

## Features
- **AI Opponent:** An autonomous agent that tracks information, eliminates suspects based on public and private knowledge, and makes strategic suggestions.
- **Terminal UI:** A color-coded, grid-based interface that renders the mansion map and player positions clearly using standard console outputs.
- **Full Game Logic:** - **Suggestions:** Implements the "dragging" rule where suspects are moved to the current room.
  - **Refutations:** Clockwise checking of opponents to disprove suggestions.
  - **Accusations:** Win/Loss condition based on matching the hidden envelope.
- **Secret Passages:** Functional travel between corner rooms (e.g., Study to Kitchen).

## Prerequisites
- Python 3.x installed on your machine.
- No external libraries are required (uses standard `random` and `os` libraries).

## How to Run
1. **Navigate to the Source Code:**
   Open your terminal or command prompt and navigate to the folder containing the files:
   ```bash
   cd path/to/Project_SourceCode
2. Run main.py to start the game
