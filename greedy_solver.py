import random

class GreedySolver:
    def __init__(self):
        self.logs = ["AI Ready (Greedy Mode)"]
        self.name = "Greedy"

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        # The Greedy approach looks at every revealed numbered cell at once
        frontier = board.get_revealed_numbered_nodes()
        
        moves_reveal = []
        moves_flag = []

        for cell in frontier:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)

            if not hidden:
                continue

            # Rule 1: Satisfaction (Clear Around)
            # If the cell already has enough flags around it, the rest are safe.
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in moves_reveal:
                        moves_reveal.append(h)

            # Rule 2: Deduction (Mine Finding)
            # If the remaining hidden cells perfectly match the remaining numbers, they are mines.
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in moves_flag:
                        moves_flag.append(h)

        # Priority 1: Safe reveal
        if moves_reveal:
            target = moves_reveal[0]
            if not is_hint:
                self.log(f"Greedy: Safe clear at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        # Priority 2: Flag mine
        if moves_flag:
            target = moves_flag[0]
            if not is_hint:
                self.log(f"Greedy: Flagging mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        # Priority 3: Guess
        if not is_hint:
            return self.make_guess(board)

        return None

    def make_guess(self, board):
        valid_moves = []
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if not cell.is_revealed and not cell.is_flagged:
                    valid_moves.append((r, c))

        if valid_moves:
            move = random.choice(valid_moves)
            self.log(f"Greedy: Guessing at ({move[0]},{move[1]})")
            return (move[0], move[1], 'reveal')

        return None