# --- CONFIGURATION & COLORS ---
CELL_SIZE = 35
MARGIN = 50
SIDEBAR_WIDTH = 370   # slightly wider for timing panel

# Modern Dark Theme
C_BG           = (18, 18, 24)
C_PANEL        = (30, 30, 40)
C_GRID         = (45, 45, 55)
C_CELL_HIDDEN  = (60, 60, 70)
C_CELL_REVEALED= (25, 25, 30)
C_CELL_HOVER   = (80, 80, 100)
C_TEXT_MAIN    = (220, 220, 220)
C_ACCENT       = (0, 180, 216)
C_MINE         = (230, 57, 70)
C_FLAG         = (255, 209, 102)
C_BTN_HOVER    = (50, 50, 60)
C_HINT_SAFE    = (0, 255, 127)   # Spring Green
C_HINT_MINE    = (255, 69, 0)    # Red Orange

# AI visualisation
C_THINKING     = (0, 255, 255)   # Cyan  — considering candidates
C_CHOOSING     = (255, 255, 0)   # Yellow — selected move

# Algorithm-selector button tints
C_ALGO_GREEDY  = (0,  140, 170)
C_ALGO_BT      = (170, 80,  0)
C_ALGO_DP      = (0,  150,  80)
C_ALGO_DC      = (140,  0, 170)

# Timing panel
C_TIME_FAST    = (0,  220, 100)   # green  < 1 ms
C_TIME_MED     = (255, 200,  50)  # yellow 1–10 ms
C_TIME_SLOW    = (230,  57,  70)  # red    > 10 ms

C_NUMS = {
    1: (100, 200, 255), 2: (100, 255, 100), 3: (255, 100, 100),
    4: (200, 100, 255), 5: (255, 165,   0), 6: (  0, 255, 255),
    7: (255, 255, 255), 8: (100, 100, 100)
}

# Algorithm display names → complexity strings (for sidebar)
ALGO_COMPLEXITY = {
    "Greedy":      "O(F·N)",
    "Backtracking":"O(2^N)",
    "DP":          "O(N·2^N)",
    "Div & Conq":  "O(k·2^(N/k))",
}
