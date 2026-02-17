import random

# ------------------------------------------------------------
# GREEDY AI SOLVER FOR MINESWEEPER
# ------------------------------------------------------------
# This module implements a greedy, constraint-based AI strategy
# for playing Minesweeper. The AI makes decisions using only
# visible information (revealed cells and flags) without
# accessing hidden mine locations.
#
# Algorithmic Concepts Used:
# - Greedy Strategy
# - Constraint Satisfaction
# - Graph-based neighbor analysis (via board methods)
# ------------------------------------------------------------

class AI_Solver:
    def __init__(self):
        # Stores recent AI decisions for display and debugging
        self.logs = ["Game Started. AI Ready."]

    def log(self, message):
        """
        Adds a message to the AI log.
        Maintains only the most recent log entries to avoid clutter.
        """
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        """
        Determines the next move for the AI.

        Parameters:
        - board: Current game board state
        - is_hint: If True, AI suggests a move without logging or executing it

        Returns:
        - (row, column, action) tuple where action is 'reveal' or 'flag'
        """

        # Frontier consists of revealed numbered cells
        # These cells provide constraints for decision making
        frontier = board.get_revealed_numbered_nodes()

        # Separate move lists for greedy prioritization
        moves_reveal = []   # Guaranteed safe cells
        moves_flag = []     # Guaranteed mine cells

        # Analyze each constraint-providing cell
        for cell in frontier:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)

            # Skip cells with no unresolved neighbors
            if not hidden:
                continue

            # ------------------------------------------------
            # RULE 1: SATISFACTION RULE (Clear Around)
            # If the number of flagged neighbors equals the
            # number on the cell, all remaining hidden
            # neighbors are safe.
            # ------------------------------------------------
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in moves_reveal:
                        moves_reveal.append(h)

            # ------------------------------------------------
            # RULE 2: DEDUCTION RULE (Mine Finding)
            # If the number of hidden neighbors plus existing
            # flags equals the cell number, all hidden
            # neighbors must be mines.
            # ------------------------------------------------
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in moves_flag:
                        moves_flag.append(h)

        # ------------------------------------------------
        # GREEDY EXECUTION ORDER
        # Priority:
        # 1. Reveal guaranteed safe cells
        # 2. Flag guaranteed mines
        # 3. Guess if no logical move exists
        # ------------------------------------------------

        # Priority 1: Safe reveal
        if moves_reveal:
            target = moves_reveal[0]  # Greedy choice: first safe move
            if not is_hint:
                self.log(f"AI: Safe clear at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        # Priority 2: Flag mine
        if moves_flag:
            target = moves_flag[0]  # Greedy choice: first deduced mine
            if not is_hint:
                self.log(f"AI: Flagging mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        # Priority 3: Guess (only when logically stuck)
        if not is_hint:
            valid_moves = []

            # Collect all unrevealed and unflagged cells
            for r in range(board.rows):
                for c in range(board.cols):
                    cell = board.grid[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        valid_moves.append((r, c))

            # Random selection represents unavoidable uncertainty
            if valid_moves:
                move = random.choice(valid_moves)
                self.log(f"AI: Guessing at ({move[0]},{move[1]})")
                return (move[0], move[1], 'reveal')

        # No valid move available
        return None




