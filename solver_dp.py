import random

class DPSolver:
    def __init__(self):
        self.logs = ["AI Ready (DP Mode)"]
        self.name = "Dynamic Programming"
        self.clusters = []

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8: self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        frontier = board.get_revealed_numbered_nodes()
        self.clusters = self.find_clusters(frontier, board)
        return None

    def find_clusters(self, frontier, board):
        visited = set()
        clusters = []
        for cell in frontier:
            if cell in visited: continue
            cluster, queue = [], [cell]
            visited.add(cell)
            while queue:
                current = queue.pop(0)
                cluster.append(current)
                for h_neighbor in board.get_hidden_neighbors(current):
                    for potential in h_neighbor.neighbors:
                        if potential in frontier and potential not in visited:
                            visited.add(potential)
                            queue.append(potential)
            clusters.append(cluster)
        return clusters
