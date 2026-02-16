class DPSolver:
    def __init__(self):
        self.logs = ["AI Ready (DP Mode)"]
        self.name = "Dynamic Programming"
        self.clusters = []

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8: self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        return None
