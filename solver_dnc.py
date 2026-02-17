import random

class DNCSolver:
    def __init__(self):
        self.logs = ["AI Ready (D&C Mode)"]
        self.name = "Divide & Conquer"
        self.clusters = []

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8: self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        # 1. DIVIDE: Find Independent Clusters using Graph BFS
        frontier = board.get_revealed_numbered_nodes()
        self.clusters = self.find_clusters(frontier, board)
        
        all_safe_reveals = []
        all_safe_flags = []

        # 2. CONQUER: Solve each sub-problem independently
        for cluster in self.clusters:
            safe, flags = self.solve_cluster(cluster, board)
            all_safe_reveals.extend([m for m in safe if m not in all_safe_reveals])
            all_safe_flags.extend([m for m in flags if m not in all_safe_flags])

        # 3. COMBINE: Execute the findings
        if all_safe_reveals:
            target = all_safe_reveals[0]
            if not is_hint: self.log(f"D&C: Local constraints safe at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        if all_safe_flags:
            target = all_safe_flags[0]
            if not is_hint: self.log(f"D&C: Local constraints mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        if not is_hint: return self.make_guess(board)
        return None

    def find_clusters(self, frontier, board):
        """DIVIDE STEP: Uses BFS to find connected components."""
        visited = set()
        clusters = []
        for cell in frontier:
            if cell in visited: continue
            cluster = []
            queue = [cell]
            visited.add(cell)
            while queue:
                current = queue.pop(0)
                cluster.append(current)
                # Cells are 'connected' if they share a hidden neighbor
                current_hidden = board.get_hidden_neighbors(current)
                for h_neighbor in current_hidden:
                    for potential in h_neighbor.neighbors:
                        if potential in frontier and potential not in visited:
                            visited.add(potential)
                            queue.append(potential)
            clusters.append(cluster)
        return clusters

    def solve_cluster(self, cluster, board):
        """CONQUER STEP: Apply basic constraint rules to the isolated cluster."""
        c_safe = []
        c_flags = []
        for cell in cluster:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)
            if not hidden: continue
            
            if len(flagged) == cell.number:
                for h in hidden: 
                    if h not in c_safe: c_safe.append(h)
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden: 
                    if h not in c_flags: c_flags.append(h)
        return c_safe, c_flags

    def make_guess(self, board):
        valid = [(r, c) for r in range(board.rows) for c in range(board.cols) 
                 if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged]
        if valid:
            m = random.choice(valid)
            self.log(f"D&C: Guessing at ({m[0]},{m[1]})")
            return (m[0], m[1], 'reveal')
        return None