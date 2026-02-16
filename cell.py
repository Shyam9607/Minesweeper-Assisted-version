class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.number = 0
        self.neighbors = [] 

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['neighbors']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.neighbors = []

    def __repr__(self):
        return f"Cell({self.r}, {self.c})"
