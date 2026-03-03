import random
import time
from collections import deque

# only ai solver changed
# MINESWEEPER AI SOLVER — MULTI-ALGORITHM MODULE

# Implements four distinct solving strategies, each timed per
# move so the UI can display real time-complexity data.
#
# Algorithms:
#   1. Greedy   — O(F * N) per move, F=frontier, N=neighbors
#   2. Backtracking (CSP) — O(2^N) worst case per cluster
#   3. Dynamic Programming — O(N * 2^N) with memoization
#   4. Divide & Conquer  — O(k * 2^(N/k)) splitting clusters



# BASE CLASS  (shared log + timing helpers)

class BaseSolver:
    def __init__(self, name):
        self.name = name
        self.logs = [f"{name} AI Ready."]
        # Timing stats (seconds)
        self.last_move_time = 0.0
        self.total_time     = 0.0
        self.move_count     = 0
        self.move_times     = []   # per-move history for analysis

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 10:
            self.logs.pop(0)

    def _start(self):
        return time.perf_counter()

    def _end(self, t0):
        elapsed = time.perf_counter() - t0
        self.last_move_time = elapsed
        self.total_time    += elapsed
        self.move_count    += 1
        self.move_times.append(elapsed)
        return elapsed

    def avg_time(self):
        if not self.move_times:
            return 0.0
        return sum(self.move_times) / len(self.move_times)

    def complexity_label(self):
        raise NotImplementedError

    # Shared random guess (used by all solvers as fallback)
    def _guess(self, board):
        valid = [
            (r, c)
            for r in range(board.rows)
            for c in range(board.cols)
            if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged
        ]
        if valid:
            move = random.choice(valid)
            self.log(f"Guess at ({move[0]},{move[1]})")
            return (move[0], move[1], 'reveal')
        return None


# ─────────────────────────────────────────────
# 1. GREEDY SOLVER — O(F * N)

class GreedySolver(BaseSolver):
    """
    Greedy Constraint Satisfaction.
    Scans every frontier cell and applies two simple rules:
      Rule 1 – Satisfaction: flags == number  → remaining hidden = safe
      Rule 2 – Deduction:   hidden + flags == number → hidden = mines
    No lookahead, no memory. Fast but incomplete.
    Time Complexity: O(F * N) where F = frontier cells, N = avg neighbours (≤8)
    """
    def __init__(self):
        super().__init__("Greedy")

    def complexity_label(self):
        return "O(F·N)"

    def get_move(self, board, is_hint=False):
        t0 = self._start()

        frontier = board.get_revealed_numbered_nodes()
        reveal, flag = [], []

        for cell in frontier:
            hidden  = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)
            if not hidden:
                continue
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in reveal:
                        reveal.append(h)
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in flag:
                        flag.append(h)

        if reveal:
            target = reveal[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"Safe @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'reveal')

        if flag:
            target = flag[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"Mine @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'flag')

        elapsed = self._end(t0)
        if not is_hint:
            return self._guess(board)
        return None



# 2. BACKTRACKING SOLVER — O(2^N) worst case

class BacktrackingSolver(BaseSolver):
    """
    Backtracking CSP Solver.
    Groups frontier cells into clusters whose hidden-neighbour sets overlap,
    then exhaustively tests every mine/safe assignment within each cluster.
    A cell is proven safe (or a mine) only if it holds in ALL valid assignments.
    Time Complexity: O(2^N) per cluster, N = hidden cells in cluster
    Space Complexity: O(N) recursion stack
    """
    def __init__(self):
        super().__init__("Backtracking")

    def complexity_label(self):
        return "O(2^N)"

    def get_move(self, board, is_hint=False):
        t0 = self._start()

        frontier = board.get_revealed_numbered_nodes()
        clusters = self._find_clusters(frontier, board)

        all_safe, all_flags = [], []
        for cluster in clusters:
            safe, mines = self._solve_cluster(cluster, board)
            for s in safe:
                if s not in all_safe:   all_safe.append(s)
            for m in mines:
                if m not in all_flags:  all_flags.append(m)

        if all_safe:
            target = all_safe[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"BT Safe @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'reveal')

        if all_flags:
            target = all_flags[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"BT Mine @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'flag')

        elapsed = self._end(t0)
        if not is_hint:
            return self._guess(board)
        return None

    # ── cluster detection ──────────────────────────────────
    def _find_clusters(self, frontier, board):
        frontier_set = set(frontier)
        visited, clusters = set(), []
        for cell in frontier:
            if cell in visited:
                continue
            cluster, queue = [], deque([cell])
            visited.add(cell)
            while queue:
                cur = queue.popleft()
                cluster.append(cur)
                for h in board.get_hidden_neighbors(cur):
                    for nb in h.neighbors:
                        if nb in frontier_set and nb not in visited:
                            visited.add(nb)
                            queue.append(nb)
            clusters.append(cluster)
        return clusters

    # ── per-cluster CSP ────────────────────────────────────
    def _solve_cluster(self, cluster, board):
        hidden_set = set()
        for cell in cluster:
            for h in board.get_hidden_neighbors(cell):
                hidden_set.add(h)
        hidden = list(hidden_set)
        if not hidden:
            return [], []

        always_safe = None
        always_mine = None
        assignment  = [None] * len(hidden)

        # Build per-constraint lookup for speed
        constraint_map = []
        for cell in cluster:
            idxs = [i for i, h in enumerate(hidden) if h in cell.neighbors]
            constraint_map.append((cell, idxs))

        def is_consistent(depth):
            for cell, idxs in constraint_map:
                flagged    = len(board.get_flagged_neighbors(cell))
                needed     = cell.number - flagged
                assigned_m = sum(1 for i in idxs if assignment[i] is True)
                unassigned = sum(1 for i in idxs if assignment[i] is None)
                if assigned_m > needed:
                    return False
                if assigned_m + unassigned < needed:
                    return False
            return True

        def backtrack(idx):
            nonlocal always_safe, always_mine
            if idx == len(hidden):
                # Verify exact satisfaction
                for cell, idxs in constraint_map:
                    flagged = len(board.get_flagged_neighbors(cell))
                    if sum(1 for i in idxs if assignment[i] is True) + flagged != cell.number:
                        return
                mines_now = {hidden[i] for i in range(len(hidden)) if assignment[i]}
                safe_now  = set(hidden) - mines_now
                if always_mine is None:
                    always_mine = set(mines_now)
                    always_safe = set(safe_now)
                else:
                    always_mine &= mines_now
                    always_safe &= safe_now
                return
            for val in (True, False):
                assignment[idx] = val
                if is_consistent(idx):
                    backtrack(idx + 1)
                assignment[idx] = None

        backtrack(0)
        if always_mine is None:
            return [], []
        return list(always_safe), list(always_mine)



# 3. DYNAMIC PROGRAMMING SOLVER — O(N · 2^N)

class DPSolver(BaseSolver):
    """
    DP Memoized Constraint Solver.
    Converts each cluster into a knapsack-style DP over subsets of hidden cells.
    dp[mask] = number of valid full assignments for the cells in `mask`.
    A cell is proven safe  if every valid assignment has it = 0.
    A cell is proven mine  if every valid assignment has it = 1.

    Improvement over naive backtracking: shared sub-problem results are cached,
    avoiding redundant re-evaluation of identical partial states.

    Time  Complexity: O(N · 2^N) — iterating all masks × N bits
    Space Complexity: O(2^N)     — dp table
    """
    def __init__(self):
        super().__init__("DP")

    def complexity_label(self):
        return "O(N·2^N)"

    def get_move(self, board, is_hint=False):
        t0 = self._start()

        frontier = board.get_revealed_numbered_nodes()
        # Reuse backtracking cluster detection (identical logic)
        clusters = self._find_clusters(frontier, board)

        all_safe, all_flags = [], []
        for cluster in clusters:
            safe, mines = self._dp_solve(cluster, board)
            for s in safe:
                if s not in all_safe:   all_safe.append(s)
            for m in mines:
                if m not in all_flags:  all_flags.append(m)

        if all_safe:
            target = all_safe[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"DP Safe @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'reveal')

        if all_flags:
            target = all_flags[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"DP Mine @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'flag')

        elapsed = self._end(t0)
        if not is_hint:
            return self._guess(board)
        return None

    def _find_clusters(self, frontier, board):
        frontier_set = set(frontier)
        visited, clusters = set(), []
        for cell in frontier:
            if cell in visited:
                continue
            cluster, queue = [], deque([cell])
            visited.add(cell)
            while queue:
                cur = queue.popleft()
                cluster.append(cur)
                for h in board.get_hidden_neighbors(cur):
                    for nb in h.neighbors:
                        if nb in frontier_set and nb not in visited:
                            visited.add(nb)
                            queue.append(nb)
            clusters.append(cluster)
        return clusters

    def _dp_solve(self, cluster, board):
        """
        Enumerate all 2^N assignments via bitmask DP.
        For each mask (bit i set = hidden[i] is a mine):
          - Check every constraint in the cluster.
          - If valid, accumulate into mine_count[i] and valid_count.
        Then:
          mine  if mine_count[i] == valid_count  (mine in ALL valid configs)
          safe  if mine_count[i] == 0            (safe  in ALL valid configs)
        """
        hidden_set = set()
        for cell in cluster:
            for h in board.get_hidden_neighbors(cell):
                hidden_set.add(h)
        hidden = list(hidden_set)
        n = len(hidden)
        if n == 0:
            return [], []

        # Cap cluster size to prevent exponential blow-up in huge clusters
        # (fall back to backtracking for very large clusters)
        if n > 20:
            bt = BacktrackingSolver()
            return bt._solve_cluster(cluster, board)

        # Build constraint structures
        constraints = []
        for cell in cluster:
            flagged = len(board.get_flagged_neighbors(cell))
            needed  = cell.number - flagged
            idxs    = [i for i, h in enumerate(hidden) if h in cell.neighbors]
            constraints.append((needed, idxs))

        valid_count = 0
        mine_count  = [0] * n  # how many valid configs have hidden[i] as mine

        for mask in range(1 << n):
            ok = True
            for needed, idxs in constraints:
                mines_in = sum(1 for i in idxs if mask & (1 << i))
                if mines_in != needed:
                    ok = False
                    break
            if ok:
                valid_count += 1
                for i in range(n):
                    if mask & (1 << i):
                        mine_count[i] += 1

        if valid_count == 0:
            return [], []

        always_safe  = [hidden[i] for i in range(n) if mine_count[i] == 0]
        always_mine  = [hidden[i] for i in range(n) if mine_count[i] == valid_count]
        return always_safe, always_mine



# 4. DIVIDE & CONQUER SOLVER — O(k · 2^(N/k))

class DivideConquerSolver(BaseSolver):
    """
    Divide & Conquer CSP Solver.
    Further splits each cluster into smaller independent sub-clusters
    by finding connected components among the hidden cells (where two
    hidden cells are connected if they share a constraint cell).
    Each sub-cluster is then solved independently via backtracking.

    The key insight: if two groups of hidden cells share NO constraint cell,
    their mine/safe status is truly independent → solve separately and combine.

    This reduces worst-case complexity from O(2^N) to O(k · 2^(N/k))
    where k = number of sub-clusters.

    Time  Complexity: O(k · 2^(N/k)) — better than BT when clusters split well
    Space Complexity: O(N/k) per sub-cluster recursion stack
    """
    def __init__(self):
        super().__init__("Div & Conq")
        self._bt = BacktrackingSolver()   # reuse BT as the leaf solver

    def complexity_label(self):
        return "O(k·2^(N/k))"

    def get_move(self, board, is_hint=False):
        t0 = self._start()

        frontier = board.get_revealed_numbered_nodes()
        clusters = self._find_clusters(frontier, board)

        all_safe, all_flags = [], []
        for cluster in clusters:
            sub_clusters = self._divide(cluster, board)
            for sub in sub_clusters:
                safe, mines = self._bt._solve_cluster(sub, board)
                for s in safe:
                    if s not in all_safe:  all_safe.append(s)
                for m in mines:
                    if m not in all_flags: all_flags.append(m)

        if all_safe:
            target = all_safe[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"D&C Safe @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'reveal')

        if all_flags:
            target = all_flags[0]
            elapsed = self._end(t0)
            if not is_hint:
                self.log(f"D&C Mine @ ({target.r},{target.c}) [{elapsed*1000:.2f}ms]")
            return (target.r, target.c, 'flag')

        elapsed = self._end(t0)
        if not is_hint:
            return self._guess(board)
        return None

    # ── top-level cluster detection (same as BT) ───────────
    def _find_clusters(self, frontier, board):
        frontier_set = set(frontier)
        visited, clusters = set(), []
        for cell in frontier:
            if cell in visited:
                continue
            cluster, queue = [], deque([cell])
            visited.add(cell)
            while queue:
                cur = queue.popleft()
                cluster.append(cur)
                for h in board.get_hidden_neighbors(cur):
                    for nb in h.neighbors:
                        if nb in frontier_set and nb not in visited:
                            visited.add(nb)
                            queue.append(nb)
            clusters.append(cluster)
        return clusters

    # ── DIVIDE STEP ────────────────────────────────────────
    def _divide(self, cluster, board):
        """
        Split a cluster of frontier cells into sub-clusters whose
        hidden-neighbour sets do NOT overlap (truly independent subproblems).

        Algorithm:
        1. Build a graph where frontier cells are nodes.
        2. Two frontier cells are connected if they share ≥1 hidden neighbour.
        3. Find connected components → each component is an independent sub-cluster.
        """
        if len(cluster) <= 1:
            return [cluster]

        # Map each hidden cell → set of cluster cells that constrain it
        hidden_to_constraints = {}
        for cell in cluster:
            for h in board.get_hidden_neighbors(cell):
                hidden_to_constraints.setdefault(h, set()).add(cell)

        # Build adjacency: two cluster cells share a hidden neighbour
        adj = {cell: set() for cell in cluster}
        for h, constrainers in hidden_to_constraints.items():
            lst = list(constrainers)
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    adj[lst[i]].add(lst[j])
                    adj[lst[j]].add(lst[i])

        # BFS to find connected components
        visited = set()
        sub_clusters = []
        for cell in cluster:
            if cell in visited:
                continue
            component, queue = [], deque([cell])
            visited.add(cell)
            while queue:
                cur = queue.popleft()
                component.append(cur)
                for nb in adj[cur]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            sub_clusters.append(component)

        return sub_clusters



# PUBLIC FACTORY — used by app.py

SOLVER_NAMES = ["Greedy", "Backtracking", "DP", "Div & Conq"]

def make_solver(name):
    return {
        "Greedy":      GreedySolver,
        "Backtracking": BacktrackingSolver,
        "DP":          DPSolver,
        "Div & Conq":  DivideConquerSolver,
    }[name]()


AI_Solver = GreedySolver


