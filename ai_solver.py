import random

class AI_Solver:
    def __init__(self):
        self.logs = ["Game Started. AI Ready."]
        self.name = "Integrated D&C + DP"

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    # ------------------------------------------------------------
    # DIVIDE: Split frontier into independent clusters
    
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
    # CONQUER USING  DYNAMIC PROGRAMMING
   
    def dp_solve_region(self, board, region):

        hidden_set = set()
        for cell in region:
            for h in board.get_hidden_neighbors(cell):
                hidden_set.add(h)

        hidden_list = list(hidden_set)
        if not hidden_list:
            return [], []

        # Calculate how many mines each numbered cell still needs
        initial_needs = []
        for cell in region:
            flagged = len(board.get_flagged_neighbors(cell))
            initial_needs.append(cell.number - flagged)

        memo = {}
        mine_counts = {h: 0 for h in hidden_list}

        # Recursive DP
        def dp(index, needs):

            state = (index, tuple(needs))
            if state in memo:
                return memo[state]

            # Base case
            if index == len(hidden_list):
                if all(n == 0 for n in needs):
                    return 1
                return 0

            total = 0
            h_cell = hidden_list[index]

            # --- Assume SAFE ---
            total += dp(index + 1, needs)

            # --- Assume MINE ---
            new_needs = list(needs)
            valid = True

            for i, constraint_cell in enumerate(region):
                if h_cell in constraint_cell.neighbors:
                    new_needs[i] -= 1
                    if new_needs[i] < 0:
                        valid = False
                        break

            if valid:
                ways = dp(index + 1, new_needs)
                total += ways
                if ways > 0:
                    mine_counts[h_cell] += ways

            memo[state] = total
            return total

        total_configs = dp(0, initial_needs)

        safe_moves = []
        flag_moves = []

        if total_configs > 0:
            for h in hidden_list:
                if mine_counts[h] == total_configs:
                    flag_moves.append(h)
                elif mine_counts[h] == 0:
                    safe_moves.append(h)

        return safe_moves, flag_moves

    # ------------------------------------------------------------
    # MAIN MOVE FUNCTION
   
    def get_move(self, board, is_hint=False):

        regions = self.get_constraint_regions(board)

        all_safe = []
        all_flags = []

        for region in regions:
            safe, flags = self.dp_solve_region(board, region)
            all_safe.extend([m for m in safe if m not in all_safe])
            all_flags.extend([m for m in flags if m not in all_flags])

        if all_safe:
            target = all_safe[0]
            if not is_hint:
                self.log(f"DP: 100% Safe at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        if all_flags:
            target = all_flags[0]
            if not is_hint:
                self.log(f"DP: 100% Mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        # Fallback Guess
        if not is_hint:
            valid = [(r, c) for r in range(board.rows)
                     for c in range(board.cols)
                     if not board.grid[r][c].is_revealed
                     and not board.grid[r][c].is_flagged]

            if valid:
                move = random.choice(valid)
                self.log(f"Guessing at ({move[0]},{move[1]})")
                return (move[0], move[1], 'reveal')

        return None