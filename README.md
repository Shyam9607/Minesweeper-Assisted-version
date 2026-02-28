# Minesweeper Graph AI

A modern, feature-rich Minesweeper clone built with Python and Pygame, featuring four interchangeable AI opponents (Greedy, Divide & Conquer, Dynamic Programming, and Backtracking) that play alongside you.

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

* **`Main.py`**: The entry point. Imports and runs the `App`.
* **`app.py`**: Handles the main application loop, state management (Menu, Settings, Game), algorithmic UI visualization (graph edges), and rendering logic.
* **`board.py`**: Contains the core game logic (`Board` class). Manages the grid, mine placement, cell states, adjacency, and recursion (for clearing empty areas). Saves history for undo.
* **`cell.py`**: Defines the `Cell` class, representing a single node in the grid graph (location, state, etc.).
* **`ai_solver.py`**: The baseline Greedy AI opponent. Implements basic constraint satisfaction logic.
* **`solver_dnc.py`**: The Divide & Conquer AI module. Implements graph partitioning to isolate sub-problems.
* **`solver_dp.py`**: The Dynamic Programming AI module. Implements state-space search and memoization.
* **`solver_backtrack.py`**: The Backtracking AI module. Implements recursive trial-and-error with constraint pruning.
* **`button.py`**: A helper class for creating interactive UI buttons.
* **`constants.py`**: Stores shared configuration values like colors, dimensions, and settings.

## 🎮 Game Features

* **Game Modes**:
    * **Solo Sweeper**: Classic single-player experience.
    * **Mind vs Machine**: Turn-based competition against an AI. You race to clear mines or flag them.
* **Difficulty Levels**: Easy, Medium, Hard (affects mine density).
* **Dynamic Grid**: Customizable grid sizes (8x8 to 20x20).
* **Tools**:
    * **Swappable AI Brains**: Switch between Greedy, D&C, DP, and Backtracking solvers on the fly from the settings.
    * **Algorithmic Visualizer**: Watch the AI "think" with dynamic highlights — blue graph edges for D&C/DP clusters, colored overlays for Backtracking analysis regions.
    * **Backtracking Stats**: Live display of valid solutions found and branches pruned during Backtracking mode.
    * **Hint System**: Ask the AI for a move if you are stuck.
    * **Undo**: Revert accidental clicks (Human turn only).
    * **Reset**: Quick restart with deep memory flushing.
* **Modern UI**: Dark theme, smooth transitions, and distinct colors.

## 🧠 AI & Algorithms

This project implements four distinct tiers of artificial intelligence, allowing users to observe the evolution of constraint satisfaction and state-space search.

### 1. The Greedy Strategy (Baseline)
The default AI (`ai_solver.py`) uses a **Greedy Constraint Satisfaction** approach, evaluating one cell at a time based on a hierarchy of logic:
* **Satisfaction Rule**: If a numbered cell has the correct number of flags around it, all other hidden neighbors **must be safe**. It reveals them.
* **Deduction Rule**: If a numbered cell has `Hidden Neighbors + Existing Flags == Cell Number`, then **all** those hidden neighbors **must be mines**. It flags them.
* **Fallback**: If neither rule applies, it is "stuck" and picks a random hidden cell to reveal. 

### 2. Divide & Conquer (Graph Partitioning)
To handle larger boards efficiently, the D&C solver (`solver_dnc.py`) models the Minesweeper frontier as an implicit graph.
* **Logic (Divide)**: Uses Breadth-First Search (BFS) to group the frontier into mathematically independent sub-graphs (clusters). Two cells are connected only if they share overlapping hidden neighbors.
* **Action (Conquer)**: Applies the Greedy rules (Satisfaction and Deduction) to each isolated cluster independently.
* **Effect**: Drastically reduces the computational problem space by splitting the board into smaller, mathematically isolated islands.

### 3. Dynamic Programming (State-Space Search)
The DP solver (`solver_dp.py`) handles complex overlapping constraints (like a 1-2-1 pattern) that defeat basic logic.
* **Logic (Simulation)**: Takes the isolated clusters from the D&C step and exhaustively simulates all valid permutations of mine placements within that specific sub-graph.
* **Action (Memoization)**: Caches evaluated board states in memory to prevent combinatorial explosion. By mathematically tallying all valid realities, it identifies cells that are mines in 100% of configurations.
* **Effect**: Safely solves advanced, overlapping patterns without guessing, acting as the ultimate, mathematically perfect solver.

### 4. Backtracking (Recursive Constraint Pruning)
The Backtracking solver (`solver_backtrack.py`) uses systematic trial-and-error with aggressive pruning to explore the solution space.
* **Logic (Explore)**: For each hidden cell in a cluster, recursively tries two assignments — "safe" or "mine". After each assignment, it immediately checks all affected constraints.
* **Action (Prune & Backtrack)**: If a partial assignment violates any constraint (too many mines, or not enough cells left), it **prunes** the entire branch and **backtracks** to try the other option. This avoids exploring invalid configurations.
* **Result Analysis**: Across all valid solutions, it tallies how often each cell is a mine. Cells that are mines in 100% of solutions → flag. Cells that are mines in 0% → safe reveal. Otherwise, it picks the cell with the lowest mine probability.
* **Safety Fallback**: For clusters with >25 hidden cells (where 2^n exploration is too costly), it falls back to basic constraint rules.
* **Complexity**: O(2^n) worst case per cluster, but constraint pruning makes it much faster in practice. Space: O(n) recursion stack.

### Application Flow
Every time the AI takes a turn or provides a hint:
1.  It scans the "Frontier" (revealed cells bordering hidden ones).
2.  It routes the board data to the selected AI Brain (Greedy, D&C, DP, or Backtracking).
3.  The UI visualizer renders the AI's internal process (e.g., blue graph edges for BFS clusters, colored overlays for Backtracking regions).
4.  It executes guaranteed safe moves or flags guaranteed mines based on its specific algorithmic depth.
5.  If logical deduction is mathematically impossible across all algorithms, it defaults to a calculated guess.
