# Minesweeper Graph AI

A modern, feature-rich Minesweeper clone built with Python and Pygame, featuring a smart "Greedy" AI opponent that plays alongside you.

## 🚀 How to Run

1.  **Prerequisites**: Ensure you have Python installed.
2.  **Dependencies**: Install `pygame`.
    ```bash
    pip install pygame
    ```
3.  **Start the Game**:
    ```bash
    python Main.py
    ```

## 📂 Project Structure

The project code is modularized for clarity and maintainability:

*   **`Main.py`**: The entry point. Imports and runs the `App`.
*   **`app.py`**: Handles the main application loop, state management (Menu, Settings, Game), and rendering logic.
*   **`board.py`**: Contains the core game logic (`Board` class). Manages the grid, mine placement, cell states, adjacency, and recursion (for clearing empty areas). saves history for undo.
*   **`cell.py`**: Defines the `Cell` class, representing a single node in the grid graph (location, state, etc.).
*   **`ai_solver.py`**: The brain of the CPU opponent. Implements the logic to solve the board.
*   **`button.py`**: A helper class for creating interactive UI buttons.
*   **`constants.py`**: Stores shared configuration values like colors, dimensions, and settings.

## 🎮 Game Features

*   **Game Modes**:
    *   **Solo Sweeper**: Classic single-player experience.
    *   **Mind vs Machine**: Turn-based competition against an AI. You race to clear mines or flag them.
*   **Difficulty Levels**: Easy, Medium, Hard (affects mine density).
*   **Dynamic Grid**: Customizable grid sizes (8x8 to 20x20).
*   **Tools**:
    *   **Hint System**: Ask the AI for a move if you are stuck.
    *   **Undo**: Revert accidental clicks (Human turn only).
    *   **Reset**: Quick restart.
*   **Modern UI**: Dark theme, smooth transitions, and distinct colors.

## 🧠 AI & Algorithms

The AI component (`ai_solver.py`) uses a **Greedy Constraint Satisfaction** approach. It treats the Minesweeper grid as a graph where each cell is a node connected to its neighbors.

The AI makes moves based on a hierarchy of logic, prioritizing guaranteed safe moves over guesses:

### 1. The satisfaction Rule ("Clear Around")
*   **Logic**: If a numbered cell has the correct number of flags around it (e.g., a '3' has 3 flags), then all other hidden neighbors **must be safe**.
*   **Action**: The AI reveals those safe neighbors.
*   **Effect**: This safely expands the playable area.

### 2. The Deduction Rule ("Mine Finding")
*   **Logic**: If a numbered cell has `Hidden Neighbors + Existing Flags == Cell Number` (e.g., a '2' touches exactly 2 hidden cells and has 0 flags), then **all** those hidden neighbors **must be mines**.
*   **Action**: The AI places flags on those cells.
*   **Effect**: This identifies mines with 100% certainty.

### 3. Fallback: Probabilistic Guessing
*   **Logic**: If neither of the above rules can be applied to any revealed cell on the board, the AI is "stuck" (no logical deductions possible).
*   **Action**: It picks a random hidden cell to reveal.
*   **Note**: While simple random guessing is used here, more advanced versions could calculate probabilities for each cell, but this "Greedy" approach mimics a standard human player's intuition well.

### Application Flow
Every time the AI takes a turn or provides a hint:
1.  It scans the "Frontier" (revealed cells bordering hidden ones).
2.  It checks **Rule 1** (Safe spots). If found, it executes immediately.
3.  If no safe spots, it checks **Rule 2** (Mines).
4.  If logical deduction is impossible, it defaults to **Rule 3** (Guess).
