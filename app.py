import pygame
import sys
import datetime 
import os 
from constants import *
from board import Board
from ai_solver import AI_Solver
from button import Button   
from solver_dnc import DNCSolver
from solver_dp import DPSolver



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
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
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
        self.cell_size = CELL_SIZE 
        
        self.bg_image = None
        bg_path = r"Images\Startup-Page-BG-Image.jpg"
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
        btn_single = Button(300, 400, 200, 50, "SOLO SWEEPER") 
        btn_cpu = Button(290, 470, 220, 50, "MIND VS MACHINE")

        while self.mode == "Menu":
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(C_BG)

            shadow = self.font_xl.render("MINESWEEPER AI", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(self.screen_w // 2 + 4, 320 + 4))
            self.screen.blit(shadow, shadow_rect)

            title = self.font_xl.render("MINESWEEPER AI", True, C_ACCENT)
            title_rect = title.get_rect(center=(self.screen_w // 2, 320))
            self.screen.blit(title, title_rect)

            btn_single.draw(self.screen, self.font)
            btn_cpu.draw(self.screen, self.font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

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
        
        # 1. Setup Grid Size Buttons
        btns_size = []
        sizes = [8, 12, 16, 20]
        for i, s in enumerate(sizes):
            col = C_ACCENT if self.grid_size == s else C_PANEL
            btns_size.append(Button(200 + i*70, 200, 60, 40, str(s), color=col))

        # 2. Setup Difficulty Buttons
        btns_diff = []
        diffs = ["Easy", "Medium", "Hard"]
        for i, d in enumerate(diffs):
            col = C_ACCENT if self.difficulty == d else C_PANEL
            btns_diff.append(Button(200 + i*120, 300, 100, 40, d, color=col))
            
        # 3. Setup AI Mode Buttons (Fixed Indentation)
        btns_ai = []
        algos = ["Greedy", "D&C", "DP"]
        if self.vs_cpu:
            for i, a in enumerate(algos):
                col = C_ACCENT if self.ai_algorithm == a else C_PANEL
                btns_ai.append(Button(200 + i*130, 400, 100, 40, a, color=col))

        # 4. Moved Start Button down slightly to make room
        btn_start = Button(300, 500, 200, 60, "START GAME", color=C_FLAG)
        btn_clear_log = Button(40, 520, 140, 40, "CLEAR LOGS", color=(180, 50, 50))
        btn_back = Button(620, 520, 140, 40, "BACK", color=C_PANEL)

        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.time.delay(100)

        while self.mode == "Settings":
            if bg_blur:
                self.screen.blit(bg_blur, (0, 0))
            else:
                self.screen.fill(C_BG)

            title = self.font_lg.render("GAME SETUP", True, C_ACCENT)
            self.screen.blit(title, (280, 100))

            lbl_size = self.font.render("GRID SIZE:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_size, (80, 210))
            for b in btns_size: b.draw(self.screen, self.font)

            lbl_diff = self.font.render("DIFFICULTY:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_diff, (60, 310))
            for b in btns_diff: b.draw(self.screen, self.font)

            if self.vs_cpu:
                lbl_ai = self.font.render("AI MODE:", True, C_TEXT_MAIN)
                self.screen.blit(lbl_ai, (80, 410))
                for b in btns_ai: b.draw(self.screen, self.font)

            btn_start.draw(self.screen, self.font)
            btn_clear_log.draw(self.screen, self.font)
            btn_back.draw(self.screen, self.font)
            
            # FIXED OVERLAP: Moved the "Mines" text down so it doesn't block the D&C button
            info = f"Mines: {self.calc_mines()}"
            info_surf = self.font.render(info, True, (200, 200, 200)) 
            self.screen.blit(info_surf, (350, 465)) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                for i, b in enumerate(btns_size):
                    if b.is_clicked(event): 
                        self.grid_size = sizes[i]
                        for k, bx in enumerate(btns_size): bx.color = C_ACCENT if k == i else C_PANEL
                
                for i, b in enumerate(btns_diff):
                    if b.is_clicked(event): 
                        self.difficulty = diffs[i]
                        for k, bx in enumerate(btns_diff): bx.color = C_ACCENT if k == i else C_PANEL
                
                # FIXED: Added back the missing AI Button click logic!
                if self.vs_cpu:
                    for i, b in enumerate(btns_ai):
                        if b.is_clicked(event):
                            self.ai_algorithm = algos[i]
                            for k, bx in enumerate(btns_ai): bx.color = C_ACCENT if k == i else C_PANEL

                if btn_start.is_clicked(event):
                    self.fade_transition()
                    self.mode = "Game"
                    return
                
                if btn_clear_log.is_clicked(event):
                    log_path = r"D:\Mines_DAA\Minesweeper_V3.0\Game_logs\all_game_logs.txt"
                    try:
                        with open(log_path, "w") as f:
                            f.write(f"LOG CLEARED: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        print("Logs cleared successfully.")
                    except Exception as e:
                        print(f"Error clearing logs: {e}")

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
                self.screen = pygame.display.set_mode((int(req_w), int(req_h)))
            return int(req_w), int(req_h)

        game_w, game_h = update_window_size()

        def init_game():
            return Board(self.grid_size, self.grid_size, self.calc_mines())

        # --- SELECT THE CORRECT SOLVER ---
        if self.ai_algorithm == "DP":
            ai = DPSolver()
        elif self.ai_algorithm == "D&C":
            ai = DNCSolver()
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

        move_log = []

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

            # --- VISUALIZE D&C/DP CLUSTERS (Graph Edges) ---
            if self.vs_cpu and hasattr(ai, 'clusters') and ai.clusters:
                for cluster in ai.clusters:
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

            status = f"TURN: {turn}"
            if board.game_over: status = f"WINNER: {board.winner}"
            lbl_stat = self.font.render(status, True, C_ACCENT if not board.game_over else C_MINE)
            self.screen.blit(lbl_stat, (sidebar_x + 20, MARGIN + 100))

            def draw_score(lbl, s, y):
                val = s['RS'] + 2*s['CF'] - s['WF']
                txt = self.font.render(f"{lbl}: {val}", True, C_TEXT_MAIN)
                self.screen.blit(txt, (sidebar_x + 20, y))
            
            draw_score("HUMAN", scores['Human'], MARGIN + 140)
            if self.vs_cpu:
                draw_score("AI CPU", scores['AI'], MARGIN + 170)

            log_y_start = MARGIN + 220
            pygame.draw.line(self.screen, (60,60,70), (sidebar_x+10, log_y_start), (sidebar_x+SIDEBAR_WIDTH-10, log_y_start))
            for i, l in enumerate(reversed(ai.logs)):
                txt = font_log.render(f"> {l}", True, (180,180,180))
                self.screen.blit(txt, (sidebar_x + 20, log_y_start + 10 + i*20))

            # Buttons
            btn_back.draw(self.screen, self.font)
            btn_reset.draw(self.screen, self.font)
            if show_undo_btn:
                btn_undo.draw(self.screen, self.font)
            btn_hint.draw(self.screen, self.font)
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
            log_dir = r"D:\Mines_DAA\Minesweeper_V3.0\Game_logs"
            if not os.path.exists(log_dir):
                try: os.makedirs(log_dir)
                except OSError as e: print(f"Error creating log directory: {e}"); return

            filename = "all_game_logs.txt"
            filepath = os.path.join(log_dir, filename)
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
            if points > 1: return 
            else: scores[actor]['RS'] += points

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
                
                ai.log(f"Board Cleared! Winner: {board.winner}")
                log_move("System", "Game Over", -1, -1, "Board Cleared", f"Winner: {board.winner}")

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
            btn_save = Button(game_w - 120, game_h - 130, 100, 30, "SAVE LOG", color=(50, 100, 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_logs_to_file() 
                    pygame.quit(); sys.exit()
                
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
                    self.screen = pygame.display.set_mode((800, 600)) 
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
                        game_started = False
                        start_ticks = 0
                        elapsed_time = 0
                        total_moves = 0

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
            if self.vs_cpu and turn == "AI" and not board.game_over:
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

                    turn = "Human"

            if game_started and not board.game_over:
                elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

            # Standard draw call (no highlights)
            draw_game(time_str, timer_color, show_undo)
            pygame.display.flip()
            self.clock.tick(60)