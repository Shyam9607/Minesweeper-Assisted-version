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

# import random
# from collections import deque

# class AI_Solver:
#     def __init__(self):
#         self.logs = ["Game Started. AI Ready."]

#     def log(self, message):
#         self.logs.append(message)
#         if len(self.logs) > 8:
#             self.logs.pop(0)

#     def get_move(self, board, is_hint=False):
#         frontier = board.get_revealed_numbered_nodes()
#         clusters = self._find_clusters(frontier, board)
#         all_safe  = []
#         all_flags = []
#         for cluster in clusters:
#             safe, mines = self._solve_cluster(cluster, board)
#             for s in safe:
#                 if s not in all_safe: all_safe.append(s)
#             for m in mines:
#                 if m not in all_flags: all_flags.append(m)
#         if all_safe:
#             target = all_safe[0]
#             if not is_hint: self.log(f"AI: Safe at ({target.r},{target.c})")
#             return (target.r, target.c, 'reveal')
#         if all_flags:
#             target = all_flags[0]
#             if not is_hint: self.log(f"AI: Mine at ({target.r},{target.c})")
#             return (target.r, target.c, 'flag')
#         if not is_hint:
#             valid = [
#                 (r, c) for r in range(board.rows) for c in range(board.cols)
#                 if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged
#             ]
#             if valid:
#                 move = random.choice(valid)
#                 self.log(f"AI: Guessing at ({move[0]},{move[1]})")
#                 return (move[0], move[1], 'reveal')
#         return None

#     def _find_clusters(self, frontier, board):
#         frontier_set = set(frontier)
#         visited      = set()
#         clusters     = []
#         for cell in frontier:
#             if cell in visited:
#                 continue
#             cluster = []
#             queue   = deque([cell])
#             visited.add(cell)
#             while queue:
#                 cur = queue.popleft()
#                 cluster.append(cur)
#                 for h in board.get_hidden_neighbors(cur):
#                     for nb in h.neighbors:
#                         if nb in frontier_set and nb not in visited:
#                             visited.add(nb)
#                             queue.append(nb)
#             clusters.append(cluster)
#         return clusters

#     def _solve_cluster(self, cluster, board):

#         # collect all hidden unrevealed unflagged cells touching this cluster
#         hidden_set = set()
#         for cell in cluster:
#             for h in board.get_hidden_neighbors(cell):
#                 hidden_set.add(h)
#         hidden = list(hidden_set)

#         # nothing to solve if no hidden cells
#         if not hidden:
#             return [], []

#         # None=unassigned  True=mine  False=safe
#         assignment = [None] * len(hidden)

#         # for each constraint cell store which hidden[] indices are its neighbours
#         # done once here to avoid repeating inside recursion
#         constraint_map = [
#             (cell, [i for i, h in enumerate(hidden) if h in cell.neighbors])
#             for cell in cluster
#         ]

#         # these will hold the intersection across all valid assignments
#         always_safe = None
#         always_mine = None

#         def is_consistent():
#             for cell, idxs in constraint_map:
#                 # mines still required by this constraint after existing flags
#                 flagged    = len(board.get_flagged_neighbors(cell))
#                 needed     = cell.number - flagged
#                 # how many hidden neighbours already assigned as mine
#                 assigned_m = sum(1 for i in idxs if assignment[i] is True)
#                 # how many hidden neighbours not yet decided
#                 unassigned = sum(1 for i in idxs if assignment[i] is None)
#                 # prune — already placed more mines than needed
#                 if assigned_m > needed:
#                     return False
#                 # prune — even if all unassigned become mines still cant reach needed
#                 if assigned_m + unassigned < needed:
#                     return False
#             return True

#         def backtrack(idx):
#             nonlocal always_safe, always_mine

#             # base case — every hidden cell has been assigned
#             if idx == len(hidden):
#                 # verify every constraint is exactly satisfied not just not violated
#                 for cell, idxs in constraint_map:
#                     flagged  = len(board.get_flagged_neighbors(cell))
#                     mines_in = sum(1 for i in idxs if assignment[i])
#                     if mines_in + flagged != cell.number:
#                         # this assignment breaks a constraint discard it
#                         return
#                 # valid complete assignment — build mine and safe sets
#                 mines_now = {hidden[i] for i in range(len(hidden)) if assignment[i]}
#                 safe_now  = set(hidden) - mines_now
#                 if always_mine is None:
#                     # first valid assignment found — initialise sets directly
#                     always_mine = set(mines_now)
#                     always_safe = set(safe_now)
#                 else:
#                     # intersect — only keep cells that are mine in EVERY valid assignment
#                     always_mine &= mines_now
#                     # intersect — only keep cells that are safe in EVERY valid assignment
#                     always_safe &= safe_now
#                 return

#             # recursive case — try mine first then safe
#             for val in (True, False):
#                 # assign current hidden cell as mine or safe
#                 assignment[idx] = val
#                 # only recurse if this assignment doesnt violate any constraint
#                 if is_consistent():
#                     backtrack(idx + 1)
#                 # undo the assignment — this is the backtrack step
#                 assignment[idx] = None

#         # start recursion from index 0
#         backtrack(0)

#         # no valid assignment found
#         if always_mine is None:
#             return [], []

#         # always_safe = safe in every valid assignment = definitely safe
#         # always_mine = mine in every valid assignment = definitely a mine
#         return list(always_safe), list(always_mine)



