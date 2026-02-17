import random
from collections import deque   

class DPSolver:
    def __init__(self):
        self.logs = ["AI Ready (DP Mode)"]
        self.name = "Dynamic Programming"
        self.clusters = []

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        frontier = board.get_revealed_numbered_nodes()
        self.clusters = self.find_clusters(frontier, board)

        all_safe_reveals = []
        all_safe_flags = []

        for cluster in self.clusters:
            safe, flags = self.dp_solve_cluster(cluster, board)
            all_safe_reveals.extend([m for m in safe if m not in all_safe_reveals])
            all_safe_flags.extend([m for m in flags if m not in all_safe_flags])

        if all_safe_reveals:
            target = all_safe_reveals[0]
            if not is_hint:
                self.log(f"DP: 100% Safe Reality at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        if all_safe_flags:
            target = all_safe_flags[0]
            if not is_hint:
                self.log(f"DP: 100% Mine Reality at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        if not is_hint:
            return self.make_guess(board)

        return None

    def find_clusters(self, frontier, board):
        """Graph BFS to isolate subproblems."""
        visited = set()
        clusters = []

        for cell in frontier:
            if cell in visited:
                continue

            cluster = []

            # USING DEQUE INSTEAD OF LIST
            queue = deque([cell])

            visited.add(cell)

            while queue:
                current = queue.popleft()   # O(1) instead of pop(0)
                cluster.append(current)

                for h_neighbor in board.get_hidden_neighbors(current):
                    for potential in h_neighbor.neighbors:
                        if potential in frontier and potential not in visited:
                            visited.add(potential)
                            queue.append(potential)

            clusters.append(cluster)

        return clusters

    def dp_solve_cluster(self, cluster, board):
        hidden_set = set()
        for cell in cluster:
            for h in board.get_hidden_neighbors(cell):
                hidden_set.add(h)

        hidden_list = list(hidden_set)

        if not hidden_list:
            return [], []

        initial_needs = []
        for cell in cluster:
            flagged_count = len(board.get_flagged_neighbors(cell))
            initial_needs.append(cell.number - flagged_count)

        memo = {}
        mine_counts = {h: 0 for h in hidden_list}

        def dp(index, current_needs):
            state = (index, tuple(current_needs))

            if state in memo:
                return memo[state]

            if index == len(hidden_list):
                if all(n == 0 for n in current_needs):
                    return 1
                return 0

            h_cell = hidden_list[index]
            total_valid_configs = 0

            # Branch 1: Safe
            total_valid_configs += dp(index + 1, current_needs)

            # Branch 2: Mine
            new_needs = list(current_needs)
            valid_mine_placement = True

            for i, constraint_cell in enumerate(cluster):
                if h_cell in constraint_cell.neighbors:
                    new_needs[i] -= 1
                    if new_needs[i] < 0:
                        valid_mine_placement = False
                        break

            if valid_mine_placement:
                ways_if_mine = dp(index + 1, new_needs)
                total_valid_configs += ways_if_mine

                if ways_if_mine > 0:
                    mine_counts[h_cell] += ways_if_mine

            memo[state] = total_valid_configs
            return total_valid_configs

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

    def make_guess(self, board):
        valid = [
            (r, c)
            for r in range(board.rows)
            for c in range(board.cols)
            if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged
        ]

        if valid:
            m = random.choice(valid)
            self.log(f"DP: Probability guess at ({m[0]},{m[1]})")
            return (m[0], m[1], 'reveal')

        return None

