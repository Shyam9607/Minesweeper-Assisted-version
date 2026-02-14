import random


from region_utils import get_connected_frontier_regions, map_frontier_constraints


class GreedySolver:
    """Region-local greedy strategy with heuristic ranking.

    Strategy:
    1) Apply deterministic minesweeper rules per numbered constraint.
    2) Score candidate moves and sort by heuristic strength.

    Region complexity (rough): O(K * D), where K is region cell count and D
    is nearby numbered constraints examined.
    """

    def __init__(self):
        pass

    def solve_region(self, board, region):
        """Return ranked candidates for one independent frontier region.

        Each candidate is a dictionary with keys:
        - cell: target Cell
        - action: 'reveal' or 'flag'
        - score: greedy heuristic score
        - certainty: 1.0 for logical certainty, else estimated confidence
        - reason: short explanation
        - state_key: compact region state signature for DP memoization
        """
        if not region:
            return []

        region_set = set(region)
        frontier_constraints = map_frontier_constraints(board)
        numbered_nodes = board.get_revealed_numbered_nodes()

        # Region-local candidate maps prevent duplicate entries from multiple
        # overlapping numbered constraints.
        reveal_map = {}
        flag_map = {}

        for node in numbered_nodes:
            hidden = [n for n in board.get_hidden_neighbors(node) if n in region_set]
            if not hidden:
                continue

            flagged = board.get_flagged_neighbors(node)
            required_mines = node.number - len(flagged)

            # Rule 1: all hidden neighbors are safe when requirement is satisfied.
            if required_mines == 0:
                for h in hidden:
                    score = self._heuristic_score(h, action='reveal', constraints=frontier_constraints[h])
                    prev = reveal_map.get(h)
                    if (not prev) or (score > prev['score']):
                        reveal_map[h] = {
                            'cell': h,
                            'action': 'reveal',
                            'score': score + 50.0,  # deterministic-safe boost
                            'certainty': 1.0,
                            'reason': 'satisfaction-rule',
                            'state_key': self._build_state_key(board, h, frontier_constraints[h]),
                        }

            # Rule 2: all hidden neighbors are mines when all must be mines.
            elif required_mines == len(hidden):
                for h in hidden:
                    score = self._heuristic_score(h, action='flag', constraints=frontier_constraints[h])
                    prev = flag_map.get(h)
                    if (not prev) or (score > prev['score']):
                        flag_map[h] = {
                            'cell': h,
                            'action': 'flag',
                            'score': score + 40.0,  # deterministic-mine boost
                            'certainty': 1.0,
                            'reason': 'deduction-rule',
                            'state_key': self._build_state_key(board, h, frontier_constraints[h]),
                        }

        candidates = list(reveal_map.values()) + list(flag_map.values())

        # If strict logic is unavailable inside this region, propose a best-effort
        # reveal candidate using local risk heuristics.
        if not candidates:
            for h in region_set:
                constraints = frontier_constraints[h]
                risk = self._estimated_risk(board, constraints)
                score = self._heuristic_score(h, action='reveal', constraints=constraints) - (risk * 30.0)
                candidates.append({
                    'cell': h,
                    'action': 'reveal',
                    'score': score,
                    'certainty': max(0.05, 1.0 - risk),
                    'reason': 'heuristic-region-guess',
                    'state_key': self._build_state_key(board, h, constraints),
                })

        # Greedy ordering: highest confidence/score first.
        candidates.sort(
            key=lambda x: (x['certainty'], x['score'], -x['cell'].r, -x['cell'].c),
            reverse=True,
        )
        return candidates

    def _heuristic_score(self, cell, action, constraints):
        """Weighted local heuristic for ranking region candidates.

        Features:
        - Constraint strength: more nearby numbered constraints => stronger signal
        - Hidden pressure: fewer hidden around constraints usually means tighter info
        - Action bias: safe reveals are preferred over flags for progression
        """
        constraint_strength = float(len(constraints))

        hidden_pressure = 0.0
        for node in constraints:
            hidden_count = len([n for n in node.neighbors if not n.is_revealed and not n.is_flagged])
            hidden_pressure += 1.0 / max(1, hidden_count)

        action_bias = 3.0 if action == 'reveal' else 1.5
        return (5.0 * constraint_strength) + (8.0 * hidden_pressure) + action_bias

    def _estimated_risk(self, board, constraints):
        """Estimate mine risk using local constraint ratios.

        Returns value in [0, 1]. Lower is better for reveals.
        """
        if not constraints:
            remaining_hidden = 0
            flagged = 0
            for r in range(board.rows):
                for c in range(board.cols):
                    cell = board.grid[r][c]
                    if not cell.is_revealed:
                        remaining_hidden += 1
                    if cell.is_flagged:
                        flagged += 1
            mines_left = max(0, board.total_mines - flagged)
            return mines_left / max(1, remaining_hidden)

        risks = []
        for node in constraints:
            hidden = len([n for n in node.neighbors if not n.is_revealed and not n.is_flagged])
            flagged = len([n for n in node.neighbors if n.is_flagged])
            remaining = max(0, node.number - flagged)
            risks.append(remaining / max(1, hidden))

        return min(1.0, sum(risks) / len(risks))

    def _build_state_key(self, board, cell, constraints):
        """Compact state signature used by DP memo table."""
        local = []
        for node in constraints:
            hidden = len([n for n in node.neighbors if not n.is_revealed and not n.is_flagged])
            flagged = len([n for n in node.neighbors if n.is_flagged])
            local.append((node.r, node.c, node.number, hidden, flagged))
        local.sort()
        return (cell.r, cell.c, tuple(local))


class DPSolver:
    """Dynamic-programming selector for global best move.

    Uses memoization to avoid recalculating candidate values for equivalent
    region-state signatures and a simple DP scan to select the best candidate
    across all independent regions.
    """

    def evaluate_candidates(self, candidates, memo):
        """Return best candidate among all region candidates.

        Args:
            candidates: list of candidate dicts.
            memo: dict used as memoization table.
        """
        if not candidates:
            return None

        scored = []
        for idx, cand in enumerate(candidates):
            value = self._candidate_value(cand, memo)
            scored.append((idx, value))

        # DP over candidate suffixes for max selection.
        dp_memo = {}

        def best_from(i):
            if i >= len(scored):
                return None
            if i in dp_memo:
                return dp_memo[i]

            current_idx, current_value = scored[i]
            tail_best = best_from(i + 1)
            if tail_best is None or current_value >= tail_best[1]:
                ans = (current_idx, current_value)
            else:
                ans = tail_best

            dp_memo[i] = ans
            return ans

        best_idx, _ = best_from(0)
        return candidates[best_idx]

    def _candidate_value(self, candidate, memo):
        """Memoized candidate value derived from certainty + heuristic score."""
        key = ('cand', candidate['state_key'], candidate['action'])
        if key in memo:
            return memo[key]

        # Emphasize certainty first, then region-local heuristic score.
        value = (candidate['certainty'] * 100.0) + candidate['score']
        memo[key] = value
        return value


class AI_Solver:
    """Hybrid AI: Divide & Conquer + Greedy + Dynamic Programming.

    Workflow:
    1) Divide frontier into independent connected regions.
    2) Solve each region with improved greedy heuristics.
    3) Use DP memoization to pick the best global move.
    4) Preserve original fallback behavior (random reveal when stuck).
    """

    def __init__(self):
        self.logs = ["Game Started. AI Ready."]
        self.greedy_solver = GreedySolver()
        self.dp_solver = DPSolver()
        self.memo = {}

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        """Return `(r, c, action)` using hybrid strategy."""
        regions = get_connected_frontier_regions(board)

        # Collect ranked candidates from each independent region.
        global_candidates = []
        for region_id, region in enumerate(regions):
            region_candidates = self.greedy_solver.solve_region(board, region)
            for cand in region_candidates:
                cand['region_id'] = region_id
                global_candidates.append(cand)

        # DP-based global selection over all region candidates.
        best = self.dp_solver.evaluate_candidates(global_candidates, self.memo)
        if best:
            r, c = best['cell'].r, best['cell'].c
            action = best['action']
            if not is_hint:
                self.log(
                    f"AI: {action.upper()} at ({r},{c}) via {best['reason']} "
                    f"[region={best['region_id']}, certainty={best['certainty']:.2f}]"
                )
            return (r, c, action)

        # Baseline fallback: no region logic found -> random unrevealed reveal.
        valid_moves = []
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if not cell.is_revealed and not cell.is_flagged:
                    valid_moves.append((r, c))

        if valid_moves and not is_hint:
            move = random.choice(valid_moves)
            self.log(f"AI: Guessing at ({move[0]},{move[1]})")
            return (move[0], move[1], 'reveal')

        if valid_moves and is_hint:
            # Hints can still suggest the fallback move.
            move = random.choice(valid_moves)
            return (move[0], move[1], 'reveal')

        return None
