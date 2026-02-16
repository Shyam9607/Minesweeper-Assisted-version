import random

# --- 3. RULE-ACCURATE AI SOLVER ---
class AI_Solver:
    def __init__(self):
        self.logs = ["Game Started. AI Ready."]

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8: self.logs.pop(0)

    # --- CUSTOM MERGE SORT IMPLEMENTATION ---
    # Justification: Used to sort the frontier nodes by 'constraint' (fewest hidden neighbors).
    # This acts as a heuristic to solve easy/obvious parts of the graph first.
    def merge_sort(self, arr, board):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid], board)
        right = self.merge_sort(arr[mid:], board)
        
        return self.merge(left, right, board)

    def merge(self, left, right, board):
        sorted_arr = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            # HEURISTIC: Sort by number of hidden neighbors (Ascending)
            # Nodes with FEWER hidden neighbors are more "constrained" and easier to solve.
            left_metric = len(board.get_hidden_neighbors(left[i]))
            right_metric = len(board.get_hidden_neighbors(right[j]))
            
            if left_metric <= right_metric:
                sorted_arr.append(left[i])
                i += 1
            else:
                sorted_arr.append(right[j])
                j += 1
        
        sorted_arr.extend(left[i:])
        sorted_arr.extend(right[j:])
        return sorted_arr

    def get_move(self, board, is_hint=False):
        # 1. GRAPH TRAVERSAL: Get the "Frontier" (Nodes on the edge of the unknown)
        raw_frontier = board.get_revealed_numbered_nodes()
        
        # 2. SORTING ALGORITHM APPLICATION
        # We apply Merge Sort to prioritize processing moves.
        frontier = self.merge_sort(raw_frontier, board)
        
        moves_reveal = []
        moves_flag = []
        
        for cell in frontier:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)
            
            if not hidden: continue

            # RULE 1: SATISFACTION (Graph Node Degree Check)
            # If Flagged Neighbors == Cell Value -> All edges to Hidden are SAFE.
            if len(flagged) == cell.number:
                for h in hidden:
                    if h not in moves_reveal:
                        moves_reveal.append(h)

            # RULE 2: DEDUCTION (Graph Constraint)
            # If (Hidden + Flagged) == Cell Value -> All edges to Hidden are MINES.
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in moves_flag:
                        moves_flag.append(h)

        # --- EXECUTION ---
        
        # 1. SAFE MOVES (Expands Graph)
        if moves_reveal:
            target = moves_reveal[0]
            if not is_hint: 
                self.log(f"AI: Safe 'Clear Around' at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        # 2. FLAGGING (Reduces Complexity)
        if moves_flag:
            target = moves_flag[0]
            if not is_hint: 
                self.log(f"AI: Flagging deduced mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        # 3. RANDOM WALK (Graph Disconnected)
        # If the graph traversal hits a dead end, we pick a random unvisited node.
        if not is_hint:
            valid_moves = []
            for r in range(board.rows):
                for c in range(board.cols):
                    cell = board.grid[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        valid_moves.append((r, c))
            
            if valid_moves:
                move = random.choice(valid_moves)
                self.log(f"AI: Guessing ({move[0]},{move[1]})")
                return (move[0], move[1], 'reveal')
        
        return None