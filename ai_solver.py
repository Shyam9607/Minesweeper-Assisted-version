import random

class AI_Solver:
    def __init__(self):
        self.logs = ["Game Started. AI Ready."]
        self.memo = {}  # DP memoization storage

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    # ------------------------------------------------------------
    # DIVIDE & CONQUER: Split frontier into independent regions
    # ------------------------------------------------------------
    def get_constraint_regions(self, board):
        frontier = board.get_revealed_numbered_nodes()
        visited = set()
        regions = []

        for cell in frontier:
            if cell in visited:
                continue

            stack = [cell]
            region = []

            while stack:
                current = stack.pop()
                if current in visited:
                    continue

                visited.add(current)
                region.append(current)

                # Connect cells if they share hidden neighbors
                hidden_current = set(board.get_hidden_neighbors(current))

                for other in frontier:
                    if other not in visited:
                        hidden_other = set(board.get_hidden_neighbors(other))
                        if hidden_current & hidden_other:
                            stack.append(other)

            if region:
                regions.append(region)

        return regions

    # ------------------------------------------------------------
    # DP-BASED REGION SOLVER (Memoized Evaluation)
    # ------------------------------------------------------------
    def solve_region(self, board, region):
        region_key = tuple(sorted((cell.r, cell.c) for cell in region))

        # Dynamic Programming: reuse computed results
        if region_key in self.memo:
            return self.memo[region_key]

        moves_reveal = []
        moves_flag = []

        for cell in region:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)

            if not hidden:
                continue

            # Same Stage 1 rules applied per region
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in moves_reveal:
                        moves_reveal.append(h)

            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in moves_flag:
                        moves_flag.append(h)

        result = (moves_reveal, moves_flag)
        self.memo[region_key] = result
        return result

    # ------------------------------------------------------------
    # MAIN MOVE FUNCTION
    # ------------------------------------------------------------
    def get_move(self, board, is_hint=False):

        moves_reveal = []
        moves_flag = []

        # -------- DIVIDE STEP --------
        regions = self.get_constraint_regions(board)

        # -------- CONQUER STEP --------
        for region in regions:
            reveal, flag = self.solve_region(board, region)
            moves_reveal.extend(reveal)
            moves_flag.extend(flag)

        # -------- GREEDY PRIORITY --------
        if moves_reveal:
            target = moves_reveal[0]
            if not is_hint:
                self.log(f"AI: Safe clear at ({target.r},{target.c}) [D&C+DP]")
            return (target.r, target.c, 'reveal')

        if moves_flag:
            target = moves_flag[0]
            if not is_hint:
                self.log(f"AI: Flagging mine at ({target.r},{target.c}) [D&C+DP]")
            return (target.r, target.c, 'flag')

        # -------- FALLBACK GUESS --------
        if not is_hint:
            valid_moves = []
            for r in range(board.rows):
                for c in range(board.cols):
                    cell = board.grid[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        valid_moves.append((r, c))

            if valid_moves:
                move = random.choice(valid_moves)
                self.log(f"AI: Guessing at ({move[0]},{move[1]})")
                return (move[0], move[1], 'reveal')

        return None