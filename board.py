import random
import copy
from collections import deque
from cell import Cell

# --- 2. BOARD CLASS ---
class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.game_over = False
        self.winner = None
        self.first_click = True
        self.history = [] 
        self._build_adjacency()

    def _build_adjacency(self):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                      (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].neighbors = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.grid[r][c].neighbors.append(self.grid[nr][nc])

    def save_state(self):
        if len(self.history) > 10: 
            self.history.pop(0)
        self.history.append(copy.deepcopy(self.grid))

    def undo(self):
        if not self.history: return False
        self.grid = self.history.pop()
        self.game_over = False
        self.winner = None
        self._build_adjacency()
        return True

    def place_mines(self, safe_r, safe_c):
        safe_zone = [self.grid[safe_r][safe_c]] + self.grid[safe_r][safe_c].neighbors
        candidates = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] not in safe_zone:
                    candidates.append(self.grid[r][c])
        
        mines_placed = random.sample(candidates, self.total_mines)
        for cell in mines_placed:
            cell.is_mine = True
        
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    self.grid[r][c].number = sum(1 for n in self.grid[r][c].neighbors if n.is_mine)

    def reveal(self, r, c):
        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged: return 0

        self.save_state()

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False

        cell.is_revealed = True
        if cell.is_mine:
            self.game_over = True
            return -999

        revealed_count = 1
        if cell.number == 0:
            queue = deque([cell])
            while queue:
                curr = queue.popleft()
                for n in curr.neighbors:
                    if not n.is_revealed and not n.is_flagged:
                        n.is_revealed = True
                        revealed_count += 1
                        if n.number == 0:
                            queue.append(n)
        return revealed_count

    def chord(self, r, c):
        cell = self.grid[r][c]
        if not cell.is_revealed or cell.number == 0: return 0
        
        flag_count = sum(1 for n in cell.neighbors if n.is_flagged)
        if flag_count == cell.number:
            self.save_state()
            points = 0
            mine_hit = False
            for n in cell.neighbors:
                if not n.is_revealed and not n.is_flagged:
                    n.is_revealed = True
                    if n.is_mine:
                        mine_hit = True
                    else:
                        points += 1
                        if n.number == 0:
                            q = deque([n])
                            while q:
                                curr = q.popleft()
                                for neighbor in curr.neighbors:
                                    if not neighbor.is_revealed and not neighbor.is_flagged:
                                        neighbor.is_revealed = True
                                        points += 1
                                        if neighbor.number == 0:
                                            q.append(neighbor)

            if mine_hit: 
                self.game_over = True
                return -999
            return points
        return 0

    def toggle_flag(self, r, c):
        cell = self.grid[r][c]
        if not cell.is_revealed:
            self.save_state()
            cell.is_flagged = not cell.is_flagged
            return True
        return False

    def get_hidden_neighbors(self, cell):
        return [n for n in cell.neighbors if not n.is_revealed and not n.is_flagged]

    def get_flagged_neighbors(self, cell):
        return [n for n in cell.neighbors if n.is_flagged]

    def get_revealed_numbered_nodes(self):
        nodes = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.is_revealed and cell.number > 0:
                    nodes.append(cell)
        return nodes
