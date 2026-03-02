import pygame
import sys
import datetime 
import os 
import copy
import time
import threading
from constants import *
from board import Board
from ai_solver import AI_Solver
from button import Button   
from solver_dnc import DNCSolver
from solver_dp import DPSolver
from solver_backtrack import BacktrackingSolver



# --- NEW COLORS FOR VISUALIZATION ---
C_THINKING = (0, 255, 255)   # Cyan for considering candidates
C_CHOOSING = (255, 255, 0)   # Yellow for the selected move

# --- 5. MENU & APP MANAGEMENT ---
class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen_w = 800
        self.screen_h = 600
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        pygame.display.set_caption("Minesweeper Graph AI")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 40, bold=True)
        self.font_xl = pygame.font.SysFont("Segoe UI", 80, bold=True) 

        self.grid_size = 8
        self.difficulty = "Easy" 
        self.mode = "Menu" 
        self.vs_cpu = False
        self.ai_algorithm = "Greedy"
        self.auto_solve_on = False
        self.cell_size = CELL_SIZE 

        # Resolve all file paths relative to this script directory.
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = os.path.join(self.base_dir, "Game_logs")
        self.log_file_path = os.path.join(self.logs_dir, "all_game_logs.txt")
        
        self.bg_image = None
        bg_path = os.path.join(self.base_dir, "Images", "Startup-Page-BG-Image.jpg")
        try:
            loaded_img = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.smoothscale(loaded_img, (self.screen_w, self.screen_h))
        except Exception as e:
            print(f"Could not load background: {e}")
            self.bg_image = None

    def run(self):
        while True:
            if self.mode == "Menu":
                self.menu_loop()
            elif self.mode == "Settings":
                self.settings_loop()
            elif self.mode == "Game":
                self.game_loop()

    def calc_mines(self):
        total = self.grid_size * self.grid_size
        ratio = 0.12 if self.difficulty == "Easy" else 0.17 if self.difficulty == "Medium" else 0.22
        return int(total * ratio)

    def get_blurred_background(self):
        if not self.bg_image: return None
        small_w = self.screen_w // 10
        small_h = self.screen_h // 10
        small_surf = pygame.transform.smoothscale(self.bg_image, (small_w, small_h))
        blurred_surf = pygame.transform.smoothscale(small_surf, (self.screen_w, self.screen_h))
        dark_overlay = pygame.Surface((self.screen_w, self.screen_h))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(100) 
        blurred_surf.blit(dark_overlay, (0,0))
        return blurred_surf

    def fade_transition(self):
        fade_surf = pygame.Surface((self.screen_w, self.screen_h))
        fade_surf.fill((0, 0, 0))
        for alpha in range(0, 255, 15): 
            fade_surf.set_alpha(alpha)
            self.screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)

    def menu_loop(self):
        def init_ui():
            cx, cy = self.screen_w // 2, self.screen_h // 2
            b1 = Button(cx - 100, cy + 100, 200, 50, "SOLO SWEEPER") 
            b2 = Button(cx - 110, cy + 170, 220, 50, "MIND VS MACHINE")
            return b1, b2

        btn_single, btn_cpu = init_ui()

        while self.mode == "Menu":
            if self.bg_image:
                bg = pygame.transform.smoothscale(self.bg_image, (self.screen_w, self.screen_h))
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(C_BG)

            cx, cy = self.screen_w // 2, self.screen_h // 2

            shadow = self.font_xl.render("MINESWEEPER AI", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(cx + 4, cy - 80 + 4))
            self.screen.blit(shadow, shadow_rect)

            title = self.font_xl.render("MINESWEEPER AI", True, C_ACCENT)
            title_rect = title.get_rect(center=(cx, cy - 80))
            self.screen.blit(title, title_rect)

            btn_single.draw(self.screen, self.font)
            btn_cpu.draw(self.screen, self.font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.screen_w, self.screen_h = event.w, event.h
                    self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
                    btn_single, btn_cpu = init_ui()

                if btn_single.is_clicked(event):
                    self.fade_transition()
                    self.vs_cpu = False
                    self.mode = "Settings"
                    return 

                if btn_cpu.is_clicked(event):
                    self.fade_transition()
                    self.vs_cpu = True
                    self.mode = "Settings"
                    return

            pygame.display.flip()
            self.clock.tick(60)

    def settings_loop(self):
        bg_blur = self.get_blurred_background()
        
        sizes = [8, 12, 16, 20]
        diffs = ["Easy", "Medium", "Hard"]
        algos = ["Greedy", "D&C", "DP", "BT"]

        def init_ui():
            cx, cy = self.screen_w // 2, self.screen_h // 2
            
            # 1. Setup Grid Size Buttons
            btns_size = []
            for i, s in enumerate(sizes):
                col = C_ACCENT if self.grid_size == s else C_PANEL
                btns_size.append(Button(cx - 200 + i*70, cy - 100, 60, 40, str(s), color=col))

            # 2. Setup Difficulty Buttons
            btns_diff = []
            for i, d in enumerate(diffs):
                col = C_ACCENT if self.difficulty == d else C_PANEL
                btns_diff.append(Button(cx - 200 + i*120, cy, 100, 40, d, color=col))
                
            # 3. Setup AI Mode Buttons
            btns_ai = []
            if self.vs_cpu:
                for i, a in enumerate(algos):
                    col = C_ACCENT if self.ai_algorithm == a else C_PANEL
                    btns_ai.append(Button(cx - 200 + i*130, cy + 100, 100, 40, a, color=col))

            # 4. Action Buttons
            btn_start = Button(cx + 20, cy + 205, 200, 55, "START GAME", color=C_FLAG)
            btn_auto_solve = Button(cx - 220, cy + 205, 200, 55, "AUTO SOLVE", color=(138, 43, 226))
            btn_clear_log = Button(40, self.screen_h - 40, 140, 30, "CLEAR LOGS", color=(180, 50, 50))
            btn_back = Button(self.screen_w - 180, self.screen_h - 40, 140, 30, "BACK", color=C_PANEL)
            
            return btns_size, btns_diff, btns_ai, btn_start, btn_auto_solve, btn_clear_log, btn_back

        btns_size, btns_diff, btns_ai, btn_start, btn_auto_solve, btn_clear_log, btn_back = init_ui()

        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.time.delay(100)

        while self.mode == "Settings":
            cx, cy = self.screen_w // 2, self.screen_h // 2
            
            if bg_blur:
                bg = pygame.transform.smoothscale(bg_blur, (self.screen_w, self.screen_h))
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(C_BG)

            title = self.font_lg.render("GAME SETUP", True, C_ACCENT)
            self.screen.blit(title, (cx - 120, cy - 200))

            lbl_size = self.font.render("GRID SIZE:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_size, (cx - 320, cy - 90))
            for b in btns_size: b.draw(self.screen, self.font)

            lbl_diff = self.font.render("DIFFICULTY:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_diff, (cx - 340, cy + 10))
            for b in btns_diff: b.draw(self.screen, self.font)

            if self.vs_cpu:
                lbl_ai = self.font.render("AI MODE:", True, C_TEXT_MAIN)
                self.screen.blit(lbl_ai, (cx - 320, cy + 110))
                for b in btns_ai: b.draw(self.screen, self.font)

            # Mines count centered above the action buttons
            info = f"Mines: {self.calc_mines()}"
            info_surf = self.font.render(info, True, (200, 200, 200)) 
            info_rect = info_surf.get_rect(center=(cx, cy + 180))
            self.screen.blit(info_surf, info_rect) 

            btn_auto_solve.draw(self.screen, self.font)
            btn_start.draw(self.screen, self.font)
            btn_clear_log.draw(self.screen, self.font)
            btn_back.draw(self.screen, self.font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.VIDEORESIZE:
                    self.screen_w, self.screen_h = event.w, event.h
                    self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
                    btns_size, btns_diff, btns_ai, btn_start, btn_auto_solve, btn_clear_log, btn_back = init_ui()

                for i, b in enumerate(btns_size):
                    if b.is_clicked(event): 
                        self.grid_size = sizes[i]
                        for k, bx in enumerate(btns_size): bx.color = C_ACCENT if k == i else C_PANEL
                
                for i, b in enumerate(btns_diff):
                    if b.is_clicked(event): 
                        self.difficulty = diffs[i]
                        for k, bx in enumerate(btns_diff): bx.color = C_ACCENT if k == i else C_PANEL
                
                if self.vs_cpu:
                    for i, b in enumerate(btns_ai):
                        if b.is_clicked(event):
                            self.ai_algorithm = algos[i]
                            for k, bx in enumerate(btns_ai): bx.color = C_ACCENT if k == i else C_PANEL

                if btn_start.is_clicked(event):
                    self.auto_solve_on = False
                    self.fade_transition()
                    self.mode = "Game"
                    return

                if btn_auto_solve.is_clicked(event):
                    self.auto_solve_on = True
                    self.fade_transition()
                    self.mode = "Game"
                    return
                
                if btn_clear_log.is_clicked(event):
                    try:
                        os.makedirs(self.logs_dir, exist_ok=True)
                        with open(self.log_file_path, "w") as f:
                            f.write(f"LOG CLEARED: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        print("Logs cleared successfully.")
                    except Exception as e:
                        print(f"Warning: could not clear logs: {e}")

                if btn_back.is_clicked(event):
                    self.fade_transition()
                    self.mode = "Menu"
                    return

            pygame.display.flip()
            self.clock.tick(60)

    def game_loop(self):
        def update_window_size():
            grid_px = self.grid_size * int(self.cell_size) 
            req_w = MARGIN * 2 + grid_px + SIDEBAR_WIDTH
            req_h = MARGIN * 2 + grid_px
            if req_h < 600: req_h = 600
            if req_w < 800: req_w = 800
            
            current_w, current_h = self.screen.get_size()
            if int(req_w) != current_w or int(req_h) != current_h:
                self.screen = pygame.display.set_mode((int(req_w), int(req_h)), pygame.RESIZABLE)
            return int(req_w), int(req_h)

        game_w, game_h = update_window_size()

        def init_game():
            return Board(self.grid_size, self.grid_size, self.calc_mines())

        # --- SELECT THE CORRECT SOLVER ---
        if self.ai_algorithm == "DP":
            ai = DPSolver()
        elif self.ai_algorithm == "D&C":
            ai = DNCSolver()
        elif self.ai_algorithm == "BT":
            ai = BacktrackingSolver()
        else:
            # This uses your original ai_solver.py file!
            ai = AI_Solver() 
            ai.name = "Greedy"
            
        board = init_game()
        turn = "Human"
        scores = {"Human": {'RS':0, 'CF':0, 'WF':0}, "AI": {'RS':0, 'CF':0, 'WF':0}}
        ai_timer = 0
        hint = None 
        last_ai_move = None 
        ai_moves = set() 
        
        game_started = False
        start_ticks = 0
        elapsed_time = 0
        total_moves = 0 
        
        is_resizing = False
        font_log = pygame.font.SysFont("Consolas", 14)
        font_stats = pygame.font.SysFont("Consolas", 15)
        font_stats_hdr = pygame.font.SysFont("Segoe UI", 24, bold=True)
        font_stats_col = pygame.font.SysFont("Segoe UI", 16, bold=True)

        move_log = []
        show_stats_overlay = False

        # --- AUTO SOLVER STATE ---
        auto_solving = self.auto_solve_on
        auto_solver = BacktrackingSolver()
        auto_timer = 0
        if auto_solving:
            auto_solver.log("AutoSolver started!")

        # --- Solver Comparison Stats ---
        solver_names = ["Greedy", "D&C", "DP", "BT"]
        metric_labels = {
            "moves_made": "Moves Made",
            "cells_revealed": "Cells Revealed",
            "correct_flags": "Correct Flags",
            "wrong_flags": "Wrong Flags",
            "guesses_made": "Guesses Made",
            "clusters_found": "Clusters Found",
            "valid_solutions": "Valid Solutions",
            "branches_pruned": "Branches Pruned",
            "avg_time": "Avg Time (\u03bcs)"
        }
        metric_order = [
            "moves_made",
            "cells_revealed",
            "correct_flags",
            "wrong_flags",
            "guesses_made",
            "clusters_found",
            "valid_solutions",
            "branches_pruned",
            "avg_time"
        ]
        metric_applicability = {
            "moves_made": set(solver_names),
            "cells_revealed": set(solver_names),
            "correct_flags": set(solver_names),
            "wrong_flags": set(solver_names),
            "guesses_made": set(solver_names),
            "clusters_found": {"D&C", "DP", "BT"},
            "valid_solutions": {"DP", "BT"},
            "branches_pruned": {"BT"},
            "avg_time": set(solver_names)
        }

        def init_solver_stats():
            stats = {}
            for s_name in solver_names:
                stats[s_name] = {}
                for m_key in metric_order:
                    if s_name in metric_applicability[m_key]:
                        stats[s_name][m_key] = 0
                    else:
                        stats[s_name][m_key] = None
            return stats

        solver_stats = init_solver_stats()
        comparison_solvers = {
            "Greedy": AI_Solver(),
            "D&C": DNCSolver(),
            "DP": DPSolver(),
            "BT": BacktrackingSolver(),
        }

        def get_stats_overlay_geometry():
            panel_w = min(980, game_w - 80)
            panel_h = min(650, game_h - 60)
            panel_x = (game_w - panel_w) // 2
            panel_y = (game_h - panel_h) // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            close_rect = pygame.Rect(panel_rect.right - 120, panel_rect.top + 14, 100, 34)
            return panel_rect, close_rect

        def is_guess_move(log_message):
            if not log_message:
                return False
            m = log_message.lower()
            return "guess" in m

        def estimate_reveal_cells(move, board_ref=None):
            """Simulate a reveal on a board copy to count cells. Uses board_ref if given (thread-safe)."""
            if not move or move[2] != "reveal":
                return 0
            b = board_ref if board_ref is not None else board
            r, c, _ = move
            if not (0 <= r < b.rows and 0 <= c < b.cols):
                return 0
            sim_board = copy.deepcopy(b)
            res = sim_board.reveal(r, c)
            return res if res > 0 else 0

        def count_dp_valid_solutions(cluster, board_ref=None):
            """Count DP valid solutions for a cluster. Uses board_ref if given (thread-safe)."""
            b = board_ref if board_ref is not None else board
            hidden_set = set()
            for cell in cluster:
                for h in b.get_hidden_neighbors(cell):
                    hidden_set.add(h)
            hidden_list = list(hidden_set)
            if not hidden_list:
                return 0

            initial_needs = []
            for cell in cluster:
                flagged_count = len(b.get_flagged_neighbors(cell))
                initial_needs.append(cell.number - flagged_count)

            memo = {}

            def dp_count(index, current_needs):
                state = (index, tuple(current_needs))
                if state in memo:
                    return memo[state]
                if index == len(hidden_list):
                    return 1 if all(n == 0 for n in current_needs) else 0

                total = dp_count(index + 1, current_needs)
                h_cell = hidden_list[index]
                new_needs = list(current_needs)
                valid_mine = True

                for i, constraint_cell in enumerate(cluster):
                    if h_cell in constraint_cell.neighbors:
                        new_needs[i] -= 1
                        if new_needs[i] < 0:
                            valid_mine = False
                            break

                if valid_mine:
                    total += dp_count(index + 1, new_needs)

                memo[state] = total
                return total

            return dp_count(0, initial_needs)

        def update_solver_stats(solver_name, solver_obj, proposed_move, time_taken_us=0, board_ref=None):
            """Update stats for a solver. Uses board_ref if given (thread-safe)."""
            b = board_ref if board_ref is not None else board
            curr = solver_stats[solver_name]
            if proposed_move:
                curr["moves_made"] += 1
                if "total_time_us" not in curr: 
                    curr["total_time_us"] = 0.0 
                
                curr["total_time_us"] += time_taken_us
                
                # Calculate average in microseconds (safe division because moves_made just increased)
                curr["avg_time"] = round(curr["total_time_us"] / curr["moves_made"])
                if proposed_move[2] == "reveal":
                    curr["cells_revealed"] += estimate_reveal_cells(proposed_move, board_ref=b)
                elif proposed_move[2] == "flag":
                    r, c, _ = proposed_move
                    if 0 <= r < b.rows and 0 <= c < b.cols:
                        if b.grid[r][c].is_mine:
                            curr["correct_flags"] += 1
                        else:
                            curr["wrong_flags"] += 1

            latest_log = solver_obj.logs[-1] if getattr(solver_obj, "logs", None) else ""
            if proposed_move and is_guess_move(latest_log):
                curr["guesses_made"] += 1

            if curr["clusters_found"] is not None:
                curr["clusters_found"] += len(getattr(solver_obj, "clusters", []) or [])

            if solver_name == "DP" and curr["valid_solutions"] is not None:
                dp_total = 0
                for cluster in getattr(solver_obj, "clusters", []) or []:
                    dp_total += count_dp_valid_solutions(cluster, board_ref=b)
                curr["valid_solutions"] += dp_total

            if solver_name == "BT":
                bt_stats = getattr(solver_obj, "bt_stats", {})
                if curr["valid_solutions"] is not None:
                    curr["valid_solutions"] += bt_stats.get("solutions", 0)
                if curr["branches_pruned"] is not None:
                    curr["branches_pruned"] += bt_stats.get("pruned", 0)

        comparison_lock = threading.Lock()
        comparison_running = [False]  # mutable flag for thread status

        def _run_comparison_worker(board_snapshot):
            """Background worker: runs each solver with a timeout on a board snapshot."""
            try:
                for s_name in solver_names:
                    solver_obj = comparison_solvers[s_name]
                    result = [None]
                    elapsed_us = [0]

                    def _solve():
                        start_t = time.perf_counter()
                        result[0] = solver_obj.get_move(board_snapshot, is_hint=False)
                        elapsed_us[0] = (time.perf_counter() - start_t) * 1_000_000

                    t = threading.Thread(target=_solve, daemon=True)
                    t.start()
                    t.join(timeout=2.0)  # 2-second timeout per solver

                    if t.is_alive():
                        # Solver timed out — skip it, don't update stats
                        solver_obj.log(f"{s_name}: Timed out on this board state")
                        continue

                    with comparison_lock:
                        update_solver_stats(s_name, solver_obj, result[0], time_taken_us=elapsed_us[0], board_ref=board_snapshot)
            finally:
                comparison_running[0] = False

        def run_comparison_snapshot():
            if not self.vs_cpu and not auto_solving:
                return
            if comparison_running[0]:
                return  # Previous comparison still running, skip
            comparison_running[0] = True
            # Deep-copy the board so solvers don't interfere with the live game
            board_snap = copy.deepcopy(board)
            t = threading.Thread(target=_run_comparison_worker, args=(board_snap,), daemon=True)
            t.start()

        def format_metric_value(solver_name, metric_key):
            value = solver_stats[solver_name][metric_key]
            if value is None:
                return "—"
            return str(value)

        # --- NEW GRAPH DRAWING FUNCTION ---
        def draw_bar_chart(screen, rect, metric_key, title):
            # Background
            pygame.draw.rect(screen, (35, 35, 45), rect, border_radius=8)
            pygame.draw.rect(screen, (70, 70, 80), rect, 1, border_radius=8)

            # Title
            t_surf = self.font.render(title, True, (200, 200, 200))
            screen.blit(t_surf, (rect.x + 10, rect.y + 10))

            solvers = ["Greedy", "D&C", "DP", "BT"]
            colors = [(0, 180, 216), (0, 255, 127), (255, 215, 0), (255, 100, 100)]
            
            # Get data
            vals = []
            for s in solvers:
                v = solver_stats[s].get(metric_key, 0)
                if v is None: v = 0
                vals.append(v)
            
            max_val = max(vals) if vals else 0
            if max_val == 0: max_val = 1

            # Draw Bars
            chart_h = rect.height - 50
            chart_bottom = rect.bottom - 20
            bar_w = (rect.width - 40) // 4 - 10
            
            for i, (name, val) in enumerate(zip(solvers, vals)):
                bar_h = (val / max_val) * (chart_h - 20)
                if bar_h < 2: bar_h = 2
                
                bx = rect.x + 20 + i * (bar_w + 10)
                by = chart_bottom - bar_h
                
                # Draw Bar
                pygame.draw.rect(screen, colors[i], (bx, by, bar_w, bar_h), border_radius=4)
                
                # Label
                val_surf = pygame.font.SysFont("Consolas", 12).render(str(val), True, (255,255,255))
                screen.blit(val_surf, (bx + bar_w//2 - val_surf.get_width()//2, by - 15))
                
                # X-Axis Name
                lbl_surf = pygame.font.SysFont("Consolas", 12, bold=True).render(name, True, colors[i])
                screen.blit(lbl_surf, (bx + bar_w//2 - lbl_surf.get_width()//2, chart_bottom + 4))
        
        def draw_stats_overlay():
            if not show_stats_overlay or (not self.vs_cpu and not auto_solving):
                return

            dim = pygame.Surface((game_w, game_h), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 170))
            self.screen.blit(dim, (0, 0))

            panel_rect, close_rect = get_stats_overlay_geometry()
            pygame.draw.rect(self.screen, (24, 24, 32), panel_rect, border_radius=14)
            pygame.draw.rect(self.screen, C_ACCENT, panel_rect, 2, border_radius=14)

            title = font_stats_hdr.render("Algorithm Performance Stats", True, C_TEXT_MAIN)
            self.screen.blit(title, (panel_rect.x + 24, panel_rect.y + 18))

            pygame.draw.rect(self.screen, (48, 48, 60), close_rect, border_radius=8)
            pygame.draw.rect(self.screen, C_ACCENT, close_rect, 1, border_radius=8)
            close_txt = self.font.render("✕ CLOSE", True, C_TEXT_MAIN)
            self.screen.blit(close_txt, close_txt.get_rect(center=close_rect.center))

            table_left = panel_rect.x + 24
            table_top = panel_rect.y + 78
            table_w = panel_rect.width - 48
            table_h = int(panel_rect.height * 0.45)
            metric_col_w = 220
            solver_col_w = (table_w - metric_col_w) // 4
            row_h = table_h // (len(metric_order) + 1)

            header_bg = pygame.Rect(table_left, table_top, table_w, row_h)
            pygame.draw.rect(self.screen, (40, 40, 52), header_bg)

            active_solver = self.ai_algorithm
            metric_header = font_stats_col.render("Metric", True, C_TEXT_MAIN)
            self.screen.blit(metric_header, (table_left + 10, table_top + 6))

            for i, s_name in enumerate(solver_names):
                col_x = table_left + metric_col_w + i * solver_col_w
                col_rect = pygame.Rect(col_x, table_top, solver_col_w, table_h)
                if s_name == active_solver:
                    pygame.draw.rect(self.screen, C_ACCENT, col_rect, 2, border_radius=6)
                header_label = f"{'★ ' if s_name == active_solver else ''}{s_name}"
                hdr = font_stats_col.render(header_label, True, C_TEXT_MAIN)
                self.screen.blit(hdr, (col_x + 8, table_top + 6))

            for row_idx, m_key in enumerate(metric_order, start=1):
                y = table_top + row_idx * row_h
                pygame.draw.line(self.screen, (60, 60, 72), (table_left, y), (table_left + table_w, y), 1)
                label = font_stats.render(metric_labels[m_key], True, (190, 190, 200))
                self.screen.blit(label, (table_left + 10, y + 6))
                for i, s_name in enumerate(solver_names):
                    col_x = table_left + metric_col_w + i * solver_col_w
                    value_txt = font_stats.render(format_metric_value(s_name, m_key), True, C_TEXT_MAIN)
                    self.screen.blit(value_txt, (col_x + 10, y + 6))
            
            graph_y = table_top + table_h + 40
            # Ensure we don't draw off-screen
            graph_h = max(100, panel_rect.bottom - graph_y - 20) 
            graph_w = (panel_rect.width - 60) // 3
            
            # 1. Activity Graph (Moves)
            r1 = pygame.Rect(panel_rect.x + 20, graph_y, graph_w, graph_h)
            draw_bar_chart(self.screen, r1, "moves_made", "Activity (Moves)")

            # 2. Cost Graph (Time)
            r2 = pygame.Rect(r1.right + 10, graph_y, graph_w, graph_h)
            draw_bar_chart(self.screen, r2, "avg_time", "Cost (Time \u03bcs)")

            # 3. Benefit Graph (Yield)
            r3 = pygame.Rect(r2.right + 10, graph_y, graph_w, graph_h)
            draw_bar_chart(self.screen, r3, "cells_revealed", "Benefit (Cells)")

        # --- HELPER: Get Frontier Cells (for visualization) ---
        def get_frontier(board_obj):
            frontier = set()
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if not board_obj.grid[r][c].is_revealed and not board_obj.grid[r][c].is_flagged:
                        is_near_number = False
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0: continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                                    n_cell = board_obj.grid[nr][nc]
                                    if n_cell.is_revealed and n_cell.number > 0:
                                        is_near_number = True
                                        break
                            if is_near_number: break
                        if is_near_number:
                            frontier.add((r,c))
            return frontier

        # --- DRAWING HELPER FUNCTION (UPDATED with highlights) ---
        # highlights: list of (r,c) tuples to highlight
        # highlight_col: color for the highlight border
        def draw_game(curr_time_str, curr_timer_col, show_undo_btn, highlights=None, highlight_col=None):
            self.screen.fill(C_BG)
            mouse_pos = pygame.mouse.get_pos()
            
            grid_px = self.grid_size * int(self.cell_size)
            sidebar_x = MARGIN + grid_px + 40
            
            # Draw Grid
            draw_cell_size = int(self.cell_size)
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    x = MARGIN + c * draw_cell_size
                    y = MARGIN + r * draw_cell_size
                    cell = board.grid[r][c]
                    rect = pygame.Rect(x, y, draw_cell_size-1, draw_cell_size-1) 
                    
                    if cell.is_revealed:
                        pygame.draw.rect(self.screen, C_CELL_REVEALED, rect, border_radius=4)
                        if cell.is_mine:
                            col_mine = C_MINE if cell.is_revealed and cell.is_mine else (50, 0, 0)
                            pygame.draw.circle(self.screen, col_mine, rect.center, draw_cell_size//4)
                        elif cell.number > 0:
                            dyn_font = pygame.font.SysFont("Segoe UI", int(draw_cell_size * 0.7), bold=True)
                            txt = dyn_font.render(str(cell.number), True, C_NUMS[cell.number])
                            self.screen.blit(txt, txt.get_rect(center=rect.center))
                    else:
                        is_hover = rect.collidepoint(mouse_pos)
                        # Don't hover color if we are highlighting visually
                        col = C_CELL_HOVER if (is_hover and not board.game_over and highlights is None) else C_CELL_HIDDEN
                        pygame.draw.rect(self.screen, col, rect, border_radius=4)
                        if cell.is_flagged:
                            off = 5 * (draw_cell_size / 35) 
                            pts = [(rect.centerx-off, rect.centery+off), (rect.centerx-off, rect.centery-off), (rect.centerx+off, rect.centery)]
                            pygame.draw.polygon(self.screen, C_FLAG, pts)

                    # Draw Red Dot for AI Moves
                    if (r, c) in ai_moves:
                        dot_x = rect.right - 5
                        dot_y = rect.bottom - 5
                        pygame.draw.circle(self.screen, (200, 0, 0), (dot_x, dot_y), 3)

                    # --- NEW: Draw Visual Highlights (Thinking/Choosing) ---
                    if highlights and (r,c) in highlights and highlight_col:
                         # Draw a thicker border for emphasis
                         pygame.draw.rect(self.screen, highlight_col, rect, 4, border_radius=4)

                    if hint and hint[0] == r and hint[1] == c:
                        h_col = C_HINT_SAFE if hint[2] == 'reveal' else C_HINT_MINE
                        pygame.draw.rect(self.screen, h_col, rect, 3, border_radius=4)

                    if last_ai_move and last_ai_move == (r, c):
                        pygame.draw.rect(self.screen, (50, 100, 255), rect, 3, border_radius=4)

            # --- VISUALIZE CLUSTERS ---
            vis_solver = auto_solver if auto_solving else (ai if self.vs_cpu else None)
            vis_algo = "BT" if auto_solving else self.ai_algorithm

            if vis_solver and hasattr(vis_solver, 'clusters') and vis_solver.clusters:
                if vis_algo == "BT":
                    # BACKTRACKING: Colored overlay on analyzed cells
                    active_clusters = []
                    for ci, cluster in enumerate(vis_solver.clusters):
                        # Collect hidden cells for this cluster
                        cluster_hidden = set()
                        for cl_cell in cluster:
                            for h in board.get_hidden_neighbors(cl_cell):
                                cluster_hidden.add(h)
                        
                        if not cluster_hidden:
                            continue
                            
                        # Generate a unique, stable color per cluster using Golden Angle
                        import colorsys
                        hue = ((ci * 137.508) % 360) / 360.0
                        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                        bcolor = (int(r * 255), int(g * 255), int(b * 255))
                        
                        active_clusters.append((ci, bcolor))
                        
                        # Semi-transparent overlay on hidden cells
                        overlay_surf = pygame.Surface((draw_cell_size-1, draw_cell_size-1), pygame.SRCALPHA)
                        overlay_surf.fill((*bcolor, 30))
                        for h_cell in cluster_hidden:
                            hx = MARGIN + h_cell.c * draw_cell_size
                            hy = MARGIN + h_cell.r * draw_cell_size
                            self.screen.blit(overlay_surf, (hx, hy))
                            h_rect = pygame.Rect(hx, hy, draw_cell_size-1, draw_cell_size-1)
                            pygame.draw.rect(self.screen, bcolor, h_rect, 1, border_radius=4)
                            
                        # Thin border on constraint (numbered) cells
                        for con_cell in cluster:
                            cx = MARGIN + con_cell.c * draw_cell_size
                            cy = MARGIN + con_cell.r * draw_cell_size
                            c_rect = pygame.Rect(cx, cy, draw_cell_size-1, draw_cell_size-1)
                            pygame.draw.rect(self.screen, bcolor, c_rect, 1, border_radius=4)
                            
                    # --- LEGEND below the grid ---
                    legend_y = MARGIN + grid_px + 10
                    legend_font = pygame.font.SysFont("Consolas", 13)
                    lx = MARGIN
                    for ci, bcolor in active_clusters:
                        label = f"Cluster {ci+1}"
                        pygame.draw.rect(self.screen, bcolor, (lx, legend_y + 2, 10, 10))
                        ltxt = legend_font.render(label, True, bcolor)
                        self.screen.blit(ltxt, (lx + 14, legend_y))
                        lx += ltxt.get_width() + 24
                else:
                    # D&C / DP: Line-based visualization
                    for cluster in vis_solver.clusters:
                        if len(cluster) > 1:
                            for k in range(len(cluster) - 1):
                                c1, c2 = cluster[k], cluster[k+1]
                                x1 = MARGIN + c1.c * draw_cell_size + draw_cell_size // 2
                                y1 = MARGIN + c1.r * draw_cell_size + draw_cell_size // 2
                                x2 = MARGIN + c2.c * draw_cell_size + draw_cell_size // 2
                                y2 = MARGIN + c2.r * draw_cell_size + draw_cell_size // 2
                                pygame.draw.line(self.screen, (0, 100, 255), (x1, y1), (x2, y2), 2)

            # Draw Sidebar Lines
            h_x = MARGIN + grid_px
            h_y = MARGIN + grid_px
            if self.ai_algorithm != "BT":
                pygame.draw.line(self.screen, (150, 150, 150), (h_x, h_y), (h_x + 15, h_y + 15), 3)
                pygame.draw.line(self.screen, (150, 150, 150), (h_x + 6, h_y + 15), (h_x + 15, h_y + 6), 2)
            
            pygame.draw.rect(self.screen, C_PANEL, (sidebar_x, MARGIN, SIDEBAR_WIDTH, game_h - MARGIN*2), border_radius=10)
            pygame.draw.rect(self.screen, C_ACCENT, (sidebar_x, MARGIN, SIDEBAR_WIDTH, game_h - MARGIN*2), 2, border_radius=10)

            # Draw Stats
            time_lbl = self.font.render("TIME", True, (150,150,150))
            self.screen.blit(time_lbl, (sidebar_x + 20, MARGIN + 20))
            time_surf = self.font_lg.render(curr_time_str, True, curr_timer_col)
            self.screen.blit(time_surf, (sidebar_x + 20, MARGIN + 45))

            moves_lbl = self.font.render("MOVES", True, (150,150,150))
            self.screen.blit(moves_lbl, (sidebar_x + 180, MARGIN + 20))
            moves_surf = self.font_lg.render(str(total_moves), True, C_ACCENT)
            self.screen.blit(moves_surf, (sidebar_x + 180, MARGIN + 45))

            if auto_solving:
                status = "TURN: AutoSolver"
            else:
                status = f"TURN: {turn}"
            if board.game_over: status = f"WINNER: {board.winner}"
            lbl_stat = self.font.render(status, True, C_ACCENT if not board.game_over else C_MINE)
            self.screen.blit(lbl_stat, (sidebar_x + 20, MARGIN + 100))

            def draw_score(lbl, s, y):
                val = s['RS'] + 2*s['CF'] - s['WF']
                txt = self.font.render(f"{lbl}: {val}", True, C_TEXT_MAIN)
                self.screen.blit(txt, (sidebar_x + 20, y))
            
            if auto_solving:
                draw_score("SCORE", scores['Human'], MARGIN + 140)
            else:
                draw_score("HUMAN", scores['Human'], MARGIN + 140)
                if self.vs_cpu:
                    draw_score("AI CPU", scores['AI'], MARGIN + 170)

            # --- BACKTRACKING STATS ---
            bt_solver_obj = auto_solver if auto_solving else ai
            if (self.ai_algorithm == "BT" or auto_solving) and hasattr(bt_solver_obj, 'bt_stats'):
                st = bt_solver_obj.bt_stats
                stat_txt = f"Solutions: {st['solutions']}  |  Pruned: {st['pruned']}"
                stat_surf = font_log.render(stat_txt, True, (138, 43, 226))
                self.screen.blit(stat_surf, (sidebar_x + 20, MARGIN + 200))

            log_y_start = MARGIN + 220
            pygame.draw.line(self.screen, (60,60,70), (sidebar_x+10, log_y_start), (sidebar_x+SIDEBAR_WIDTH-10, log_y_start))
            for i, l in enumerate(reversed(bt_solver_obj.logs)):
                txt = font_log.render(f"> {l}", True, (180,180,180))
                self.screen.blit(txt, (sidebar_x + 20, log_y_start + 10 + i*20))

            # Buttons
            btn_back.draw(self.screen, self.font)
            btn_reset.draw(self.screen, self.font)
            if show_undo_btn:
                btn_undo.draw(self.screen, self.font)
            btn_hint.draw(self.screen, self.font)
            if auto_solving:
                btn_speed_down.draw(self.screen, self.font)
                btn_speed_display.draw(self.screen, self.font)
                btn_speed_up.draw(self.screen, self.font)
                btn_pause.draw(self.screen, self.font)
            
            if self.vs_cpu or auto_solving:
                btn_stats.draw(self.screen, self.font)
            btn_save.draw(self.screen, self.font)

        # --- FLASH EFFECT FUNCTION ---
        def flash_board(t_str, t_col):
            grid_px = self.grid_size * int(self.cell_size)
            overlay = pygame.Surface((grid_px, grid_px))
            overlay.fill((255, 0, 0)) 
            overlay.set_alpha(150)    

            for _ in range(2):
                draw_game(t_str, t_col, False) 
                self.screen.blit(overlay, (MARGIN, MARGIN)) 
                pygame.display.flip()
                pygame.time.delay(150) 
                
                draw_game(t_str, t_col, False)
                pygame.display.flip()
                pygame.time.delay(150) 

        def log_move(actor, action, r, c, result, reason):
            entry = {
                "Time": datetime.datetime.now().strftime("%H:%M:%S"),
                "Actor": actor,
                "Action": action,
                "Coord": f"({r},{c})",
                "Result": result,
                "Reason": reason
            }
            move_log.append(entry)
            print(f"[LOG] {actor} {action} at ({r},{c}) -> {result} | {reason}")

        def save_logs_to_file():
            if not move_log: return
            try:
                os.makedirs(self.logs_dir, exist_ok=True)
            except OSError as e:
                print(f"Warning: could not create log directory: {e}")
                return

            filepath = self.log_file_path
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_block = []
            new_block.append(f"\n{'='*60}\n SESSION TIMESTAMP: {timestamp}\n{'='*60}\n")
            new_block.append(f"Grid: {self.grid_size}x{self.grid_size}, Mines: {self.calc_mines()}\n")
            new_block.append("-" * 105 + "\n")
            new_block.append(f"{'TIME':<10} | {'ACTOR':<8} | {'ACTION':<10} | {'COORD':<8} | {'RESULT':<20} | {'REASON'}\n")
            new_block.append("-" * 105 + "\n")
            
            for e in move_log:
                new_block.append(f"{e['Time']:<10} | {e['Actor']:<8} | {e['Action']:<10} | {e['Coord']:<8} | {e['Result']:<20} | {e['Reason']}\n")
            new_block.append("\n")
            new_content_str = "".join(new_block)

            old_content = ""
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f: old_content = f.read()
                except: pass

            try:
                with open(filepath, "w") as f: f.write(new_content_str + old_content)
                ai.log("Logs Appended.")
                move_log.clear() 
            except Exception as e: print(f"Error saving log: {e}")
        
        def reveal_all_mines():
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if board.grid[r][c].is_mine:
                        board.grid[r][c].is_revealed = True

        def add_points(actor, points):
            scores[actor]['RS'] += points

        def check_victory():
            if board.game_over: return
            
            total_cells = self.grid_size * self.grid_size
            total_mines = self.calc_mines()
            total_safe = total_cells - total_mines
            
            count_revealed = 0
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if board.grid[r][c].is_revealed:
                        count_revealed += 1
            
            if count_revealed >= total_safe:
                board.game_over = True
                
                for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        cell = board.grid[r][c]
                        if not cell.is_revealed and not cell.is_flagged:
                            cell.is_flagged = True 
                
                h_score = scores['Human']['RS'] + 2 * scores['Human']['CF'] - scores['Human']['WF']
                a_score = scores['AI']['RS'] + 2 * scores['AI']['CF'] - scores['AI']['WF']
                
                if h_score > a_score: board.winner = "Human"
                elif a_score > h_score: board.winner = "AI"
                else: board.winner = "Draw"

                # Override winner for AutoSolver mode
                if auto_solving:
                    board.winner = "AutoSolver"
                
                ai.log(f"Board Cleared! Winner: {board.winner}")
                log_move("System", "Game Over", -1, -1, "Board Cleared", f"Winner: {board.winner}")

        speed_multiplier = 1.0
        speed_steps = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
        auto_paused = False
        
        running = True
        while running:
            mins = elapsed_time // 60
            secs = elapsed_time % 60
            time_str = f"{mins:02}:{secs:02}"
            timer_color = C_ACCENT if game_started else (100, 100, 100)

            grid_px = self.grid_size * int(self.cell_size)
            sidebar_x = MARGIN + grid_px + 40
            
            btn_back = Button(game_w - 120, game_h - 50, 100, 30, "MENU", color=C_PANEL)
            btn_reset = Button(game_w - 120, game_h - 90, 100, 30, "RESET", color=C_PANEL)
            
            show_undo = True
            if board.game_over and board.winner == "AI":
                show_undo = False
                
            btn_undo = Button(game_w - 230, game_h - 50, 100, 30, "UNDO", color=C_PANEL)
            btn_hint = Button(game_w - 230, game_h - 90, 100, 30, "HINT", color=(100, 100, 120))
            if auto_solving:
                btn_speed_down = Button(game_w - 265, game_h - 185, 45, 40, "−", color=(80, 80, 100))
                btn_speed_display = Button(game_w - 220, game_h - 185, 90, 40, f"{speed_multiplier:.1f}x", color=(255, 140, 0) if speed_multiplier > 1.0 else C_ACCENT)
                btn_speed_up = Button(game_w - 130, game_h - 185, 45, 40, "+", color=(80, 80, 100))
                pause_text = "▶ PLAY" if auto_paused else "⏸ PAUSE"
                pause_color = (0, 160, 80) if auto_paused else (180, 60, 60)
                btn_pause = Button(game_w - 380, game_h - 185, 110, 40, pause_text, color=pause_color)
            btn_stats = Button(game_w - 230, game_h - 130, 100, 30, "📊 STATS", color=(70, 70, 110))
            btn_save = Button(game_w - 120, game_h - 130, 100, 30, "SAVE LOG", color=(50, 100, 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_logs_to_file() 
                    pygame.quit(); sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    new_w, new_h = event.w, event.h
                    # Calculate new cell size based on the available area for the grid
                    avail_w = new_w - (MARGIN * 2 + SIDEBAR_WIDTH)
                    avail_h = new_h - (MARGIN * 2)
                    max_grid_px = min(avail_w, avail_h)
                    
                    if max_grid_px > 0:
                        self.cell_size = max_grid_px / self.grid_size
                        if self.cell_size < 15: self.cell_size = 15
                        if self.cell_size > 50: self.cell_size = 50
                    
                    self.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                    game_w, game_h = new_w, new_h

                if show_stats_overlay:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        panel_rect, close_rect = get_stats_overlay_geometry()
                        if close_rect.collidepoint(event.pos) or not panel_rect.collidepoint(event.pos):
                            show_stats_overlay = False
                    continue
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handle_rect = pygame.Rect(MARGIN + grid_px, MARGIN + grid_px, 25, 25)
                    if handle_rect.collidepoint(event.pos): is_resizing = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if is_resizing:
                        is_resizing = False
                        game_w, game_h = update_window_size()

                if event.type == pygame.MOUSEMOTION and is_resizing:
                    dx = event.rel[0]
                    dy = event.rel[1]
                    change = (dx + dy) / 20 
                    self.cell_size += change
                    if self.cell_size < 15: self.cell_size = 15
                    if self.cell_size > 50: self.cell_size = 50

                if btn_back.is_clicked(event):
                    save_logs_to_file()
                    self.mode = "Menu"
                    self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    return

                if btn_save.is_clicked(event): save_logs_to_file()

                if btn_reset.is_clicked(event):
                        save_logs_to_file()
                        board = init_game()
                        scores = {"Human": {'RS':0, 'CF':0, 'WF':0}, "AI": {'RS':0, 'CF':0, 'WF':0}}
                        turn = "Human"
                        hint = None
                        last_ai_move = None 
                        ai_moves.clear()
                        
                        # --- INDENTED INSIDE THE RESET BLOCK ---
                        if hasattr(ai, 'clusters'):
                            ai.clusters.clear()
                            
                        move_log = [] 
                        ai.log("Game Reset.")
                        solver_stats = init_solver_stats()
                        show_stats_overlay = False
                        game_started = False
                        start_ticks = 0
                        elapsed_time = 0
                        total_moves = 0
                        # Restart auto-solving if in auto-solve mode
                        if self.auto_solve_on:
                            auto_solving = True
                            auto_solver = BacktrackingSolver()
                            auto_timer = 0
                            auto_solver.log("AutoSolver restarted!")
                        else:
                            auto_solving = False


                if show_undo and btn_undo.is_clicked(event):
                    if turn == "Human" and board.undo():
                         ai.log("Undo successful.")
                         hint = None
                         last_ai_move = None 

                if btn_hint.is_clicked(event):
                      move = ai.get_move(board, is_hint=True)
                      if move:
                          hint = move 
                          ai.log("Hint: Logic found.")
                      else:
                          ai.log("Hint: No strict logic found.")

                if auto_solving and btn_speed_down.is_clicked(event):
                    idx = speed_steps.index(speed_multiplier) if speed_multiplier in speed_steps else 1
                    if idx > 0:
                        speed_multiplier = speed_steps[idx - 1]

                if auto_solving and btn_speed_up.is_clicked(event):
                    idx = speed_steps.index(speed_multiplier) if speed_multiplier in speed_steps else 1
                    if idx < len(speed_steps) - 1:
                        speed_multiplier = speed_steps[idx + 1]

                if auto_solving and btn_pause.is_clicked(event):
                    auto_paused = not auto_paused

                if (self.vs_cpu or auto_solving) and btn_stats.is_clicked(event):
                    show_stats_overlay = True

                if event.type == pygame.MOUSEBUTTONDOWN and not board.game_over and not is_resizing:
                    mx, my = event.pos
                    if MARGIN <= mx < MARGIN + grid_px and MARGIN <= my < MARGIN + grid_px:
                        c = int((mx - MARGIN) // self.cell_size)
                        r = int((my - MARGIN) // self.cell_size)
                        
                        if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                            if turn == "Human":
                                if not game_started:
                                    game_started = True
                                    start_ticks = pygame.time.get_ticks()

                                action_taken = False
                                points = 0
                                res_str = ""
                                reason_str = "Manual Click"
                                
                                if event.button == 1: # Left Click
                                    cell = board.grid[r][c]
                                    if not cell.is_revealed:
                                        res = board.reveal(r, c)
                                        if res == -999:
                                            flash_board(time_str, timer_color) 
                                            ai.log("Human Hit Mine! Game Over.")
                                            board.winner = "AI"
                                            board.game_over = True 
                                            res_str = "Hit Mine"
                                            reveal_all_mines() 
                                        else:
                                            points = res
                                            action_taken = True
                                            res_str = f"Safe ({res} cells)"
                                        
                                        log_move("Human", "Reveal", r, c, res_str, reason_str)

                                    elif cell.is_revealed: # Chording
                                        res = board.chord(r, c)
                                        reason_str = "Manual Chord"
                                        if res == -999:
                                            flash_board(time_str, timer_color) 
                                            ai.log("Human Chording Hit Mine!")
                                            board.winner = "AI"
                                            board.game_over = True 
                                            res_str = "Chord -> Mine"
                                            reveal_all_mines() 
                                        elif res > 0:
                                            points = res
                                            action_taken = True
                                            res_str = f"Chord ({res} cells)"
                                        else:
                                            res_str = "Chord (No effect)"
                                        
                                        if res != 0:
                                            log_move("Human", "Chord", r, c, res_str, reason_str)
                                    
                                elif event.button == 3: # Right Click
                                    if board.toggle_flag(r, c):
                                        action_taken = True
                                        res_str = "Flag Toggled"
                                        if board.grid[r][c].is_mine: scores['Human']['CF'] += 1
                                        else: scores['Human']['WF'] += 1
                                        log_move("Human", "Flag", r, c, res_str, "Manual Right Click")

                                if action_taken:
                                    total_moves += 1 
                                    hint = None 
                                    add_points("Human", points) 
                                    check_victory()
                                    if not board.game_over and self.vs_cpu:
                                        turn = "AI"
                                        ai_timer = 45 

            # --- UPDATED AI TURN LOGIC WITH VISUALIZATION ---
            if self.vs_cpu and turn == "AI" and not board.game_over and not show_stats_overlay:
                ai_timer -= 1
                if ai_timer <= 0:
                    # 1. VISUALIZE CANDIDATES (Thinking Phase - Cyan)
                    frontier = get_frontier(board)
                    if frontier:
                        draw_game(time_str, timer_color, show_undo, highlights=frontier, highlight_col=C_THINKING)
                        pygame.display.flip()
                        pygame.time.delay(300) # Pause to show thinking

                    # Get the actual move
                    move = ai.get_move(board)
                    if move:
                        r, c, act = move
                        
                        # 2. VISUALIZE CHOICE (Choosing Phase - Yellow)
                        draw_game(time_str, timer_color, show_undo, highlights=[(r,c)], highlight_col=C_CHOOSING)
                        pygame.display.flip()
                        pygame.time.delay(300) # Pause to show choice

                        # 3. EXECUTE MOVE
                        last_ai_move = (r, c)
                        ai_moves.add((r, c))
                        total_moves += 1 
                        
                        ai_reason = ai.logs[-1] if ai.logs else "Unknown"
                        if ai_reason.startswith("AI: "): ai_reason = ai_reason[4:]

                        res_str = ""
                        points = 0

                        if act == 'reveal':
                            res = board.reveal(r, c)
                            if res == -999:
                                ai.log("AI Hit Mine! Game Over.")
                                board.winner = "Human"
                                board.game_over = True
                                res_str = "Hit Mine"
                                reveal_all_mines() 
                            else:
                                points = res
                                add_points("AI", points) 
                                res_str = f"Safe ({res} cells)"
                        elif act == 'flag':
                            board.toggle_flag(r, c)
                            if board.grid[r][c].is_mine: scores['AI']['CF'] += 1
                            else: scores['AI']['WF'] += 1
                            res_str = "Flag Placed"
                        
                        log_move("AI", act.capitalize(), r, c, res_str, ai_reason)
                        check_victory()
                        run_comparison_snapshot()

                    turn = "Human"

            # --- AUTO SOLVER LOOP ---
            if auto_solving and not board.game_over and not auto_paused:
                auto_timer -= 1
                if auto_timer <= 0:
                    auto_timer = max(1, int(10 / speed_multiplier))

                    # First click: reveal center cell to start the game
                    if board.first_click:
                        sr, sc = self.grid_size // 2, self.grid_size // 2
                        res = board.reveal(sr, sc)
                        if not game_started:
                            game_started = True
                            start_ticks = pygame.time.get_ticks()
                        total_moves += 1
                        if res != -999:
                            auto_solver.log(f"Auto: First click ({sr},{sc})")
                            log_move("AutoSolver", "Reveal", sr, sc, f"Safe ({res} cells)", "First Click")
                        check_victory()
                        if board.game_over:
                            board.winner = "AutoSolver"
                            auto_solving = False
                    else:
                        # 1. VISUALIZE CANDIDATES (Thinking Phase)
                        frontier = get_frontier(board)
                        if frontier:
                            draw_game(time_str, timer_color, show_undo, highlights=frontier, highlight_col=C_THINKING)
                            pygame.display.flip()
                            pygame.time.delay(max(5, int(130 / speed_multiplier)))

                        # 2. Get move from BacktrackingSolver
                        move = auto_solver.get_move(board)
                        if move:
                            r, c, act = move

                            # 3. VISUALIZE CHOICE (Choosing Phase)
                            draw_game(time_str, timer_color, show_undo, highlights=[(r,c)], highlight_col=C_CHOOSING)
                            pygame.display.flip()
                            pygame.time.delay(max(5, int(130 / speed_multiplier)))

                            # 4. EXECUTE MOVE
                            last_ai_move = (r, c)
                            ai_moves.add((r, c))
                            total_moves += 1

                            auto_reason = auto_solver.logs[-1] if auto_solver.logs else "Unknown"
                            res_str = ""

                            if act == 'reveal':
                                if board.grid[r][c].is_mine:
                                    auto_solver.log("AutoHint: Dodged mine via guess!")
                                    act = 'flag'
                                else:
                                    res = board.reveal(r, c)
                                    if res == -999:
                                        flash_board(time_str, timer_color)
                                        auto_solver.log("Auto: Hit Mine! Game Over.")
                                        board.winner = "AutoSolver"
                                        board.game_over = True
                                        res_str = "Hit Mine"
                                        reveal_all_mines()
                                        auto_solving = False
                                    else:
                                        add_points("Human", res)
                                        res_str = f"Safe ({res} cells)"
                            if act == 'flag':
                                board.toggle_flag(r, c)
                                if board.grid[r][c].is_mine:
                                    scores['Human']['CF'] += 1
                                else:
                                    scores['Human']['WF'] += 1
                                res_str = "Flag Placed"

                            log_move("AutoSolver", act.capitalize(), r, c, res_str, auto_reason)
                            check_victory()
                            run_comparison_snapshot()

                            if board.game_over:
                                board.winner = "AutoSolver"
                                auto_solving = False
                                auto_solver.log("Auto: Board Solved!")
                        else:
                            auto_solving = False
                            auto_solver.log("Auto: No moves left.")

            if game_started and not board.game_over:
                elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

            # Standard draw call (no highlights)
            draw_game(time_str, timer_color, show_undo)
            draw_stats_overlay()
            pygame.display.flip()
            self.clock.tick(60)
