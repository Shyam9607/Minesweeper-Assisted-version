import random
from collections import deque

# --- BACKTRACKING SOLVER ---
# Uses systematic trial-and-error with constraint pruning.
# Assigns mine/safe to each hidden cell, checks constraints, and
# backtracks immediately when a contradiction is detected.

CLUSTER_SIZE_LIMIT = 25  # Max hidden cells per cluster before fallback

class BacktrackingSolver:
    def __init__(self):
        self.logs = ["AI Ready (Backtrack Mode)"]
        self.name = "Backtracking"
        self.clusters = []
        self.bt_stats = {"solutions": 0, "pruned": 0}

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    # ── Public Interface ──────────────────────────────────────────
    def get_move(self, board, is_hint=False):
        frontier = board.get_revealed_numbered_nodes()
        self.clusters = self.find_clusters(frontier, board)
        self.bt_stats = {"solutions": 0, "pruned": 0}

        all_safe = []
        all_flags = []
        best_guess = None
        best_prob = 1.0

        for cluster in self.clusters:
            safe, flags, guess = self.backtrack_solve(cluster, board)
            all_safe.extend([m for m in safe if m not in all_safe])
            all_flags.extend([m for m in flags if m not in all_flags])
            if guess and guess[1] < best_prob:
                best_guess, best_prob = guess

        # Priority 1: Deterministic safe reveal
        if all_safe:
            t = all_safe[0]
            if not is_hint:
                self.log(f"BT: 100% Safe ({t.r},{t.c}) [{self.bt_stats['pruned']} pruned]")
            return (t.r, t.c, 'reveal')

        # Priority 2: Deterministic mine flag
        if all_flags:
            t = all_flags[0]
            if not is_hint:
                self.log(f"BT: 100% Mine ({t.r},{t.c}) [{self.bt_stats['pruned']} pruned]")
            return (t.r, t.c, 'flag')

        # Priority 3: Probability-informed guess
        if best_guess and not is_hint:
            self.log(f"BT: Best guess ({best_guess.r},{best_guess.c}) P={1-best_prob:.0%} safe")
            return (best_guess.r, best_guess.c, 'reveal')

        # Priority 4: Random fallback
        if not is_hint:
            return self.make_guess(board)
        return None

    # ── Cluster Isolation (BFS) ───────────────────────────────────
    def find_clusters(self, frontier, board):
        """DIVIDE: BFS to find independent connected components."""
        visited = set()
        clusters = []
        for cell in frontier:
            if cell in visited:
                continue
            cluster, queue = [], deque([cell])
            visited.add(cell)
            while queue:
                current = queue.popleft()
                cluster.append(current)
                for h in board.get_hidden_neighbors(current):
                    for p in h.neighbors:
                        if p in frontier and p not in visited:
                            visited.add(p)
                            queue.append(p)
            clusters.append(cluster)
        return clusters

    # ── Core Backtracking Engine ──────────────────────────────────
    def backtrack_solve(self, cluster, board):
        """
        BACKTRACKING CORE:
        1. Gather hidden cells (variables) for the cluster
        2. Build constraints from numbered cells
        3. Recursively try safe/mine for each cell
        4. Prune on constraint violation (backtrack)
        5. Count mine appearances across all valid solutions
        """
        # 1. Gather hidden variables
        hidden_set = set()
        for cell in cluster:
            for h in board.get_hidden_neighbors(cell):
                hidden_set.add(h)
        hidden_list = list(hidden_set)

        if not hidden_list:
            return [], [], None

        # Safety: fall back to basic rules for very large clusters
        if len(hidden_list) > CLUSTER_SIZE_LIMIT:
            self.log(f"BT: Cluster too large ({len(hidden_list)}), using rules")
            return self._basic_solve(cluster, board)

        n = len(hidden_list)
        cell_to_idx = {h: i for i, h in enumerate(hidden_list)}

        # 2. Build constraints: (remaining_need, [indices of hidden neighbors])
        constraints = []
        for cell in cluster:
            flagged = len(board.get_flagged_neighbors(cell))
            need = cell.number - flagged
            indices = [cell_to_idx[h] for h in hidden_list if h in cell.neighbors]
            constraints.append((need, indices))

        # 3. Map each hidden cell → which constraints it participates in
        cell_constraints = [[] for _ in range(n)]
        for ci, (_, indices) in enumerate(constraints):
            for idx in indices:
                cell_constraints[idx].append(ci)

        # 4. Backtracking state
        assignment = [0] * n     # current assignment (0=safe, 1=mine)
        mine_counts = [0] * n    # how many valid solutions has cell as mine
        total_solutions = [0]
        pruned = [0]

        def check_constraints(cell_idx):
            """
            PRUNING CHECK: After assigning cell_idx, verify no constraint
            is violated. Only checks constraints involving this cell.
            - Too many mines assigned  → prune
            - Not enough cells left to fill remaining need → prune
            """
            for ci in cell_constraints[cell_idx]:
                need, indices = constraints[ci]
                mines = 0
                unassigned = 0
                for i in indices:
                    if i > cell_idx:     # not yet decided
                        unassigned += 1
                    elif assignment[i] == 1:
                        mines += 1
                # Constraint violations
                if mines > need:
                    return False
                if mines + unassigned < need:
                    return False
            return True

        def backtrack(idx):
            # BASE CASE: all cells assigned
            if idx == n:
                # Final check: all constraints exactly satisfied
                for need, indices in constraints:
                    if sum(assignment[i] for i in indices) != need:
                        return
                total_solutions[0] += 1
                for i in range(n):
                    if assignment[i] == 1:
                        mine_counts[i] += 1
                return

            # BRANCH 1: Try SAFE (0)
            assignment[idx] = 0
            if check_constraints(idx):
                backtrack(idx + 1)
            else:
                pruned[0] += 1

            # BRANCH 2: Try MINE (1)
            assignment[idx] = 1
            if check_constraints(idx):
                backtrack(idx + 1)
            else:
                pruned[0] += 1

            # BACKTRACK: reset
            assignment[idx] = 0

        backtrack(0)

        self.bt_stats['solutions'] += total_solutions[0]
        self.bt_stats['pruned'] += pruned[0]

        # 5. Interpret results
        safe_moves = []
        flag_moves = []
        best_guess = None
        lowest_prob = 1.0

        if total_solutions[0] > 0:
            for i, h in enumerate(hidden_list):
                prob = mine_counts[i] / total_solutions[0]
                if prob == 1.0:           # mine in EVERY solution
                    flag_moves.append(h)
                elif prob == 0.0:         # mine in NO solution
                    safe_moves.append(h)
                elif prob < lowest_prob:  # best guess candidate
                    lowest_prob = prob
                    best_guess = h

        guess_info = (best_guess, lowest_prob) if best_guess else None
        return safe_moves, flag_moves, guess_info

    # ── Fallback: Basic Constraint Rules ──────────────────────────
    def _basic_solve(self, cluster, board):
        """Simple single-pass rules for clusters too large to backtrack."""
        safe = []
        flags = []
        checks = 0
        for cell in cluster:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)
            checks += 1
            if not hidden:
                continue
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in safe:
                        safe.append(h)
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in flags:
                        flags.append(h)
        # Record that we did constraint work even though we didn't backtrack
        self.bt_stats['solutions'] += 1 if (safe or flags) else 0
        self.bt_stats['pruned'] += checks
        return safe, flags, None

    # ── Random Guess ──────────────────────────────────────────────
    def make_guess(self, board):
        valid = [(r, c) for r in range(board.rows) for c in range(board.cols)
                 if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged]
        if valid:
            m = random.choice(valid)
            self.log(f"BT: Random guess at ({m[0]},{m[1]})")
            return (m[0], m[1], 'reveal')
        return None
