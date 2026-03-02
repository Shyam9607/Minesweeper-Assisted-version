import pygame
import sys
import datetime
import os
from constants import *
from board import Board
from ai_solver import make_solver, SOLVER_NAMES
from button import Button

# ============================================================
# APP — Main application class
# ============================================================
class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen_w = 800
        self.screen_h = 600
        self.screen   = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Minesweeper Graph AI")
        self.clock    = pygame.time.Clock()

        self.font     = pygame.font.SysFont("Segoe UI",  20, bold=True)
        self.font_sm  = pygame.font.SysFont("Consolas",  14)
        self.font_lg  = pygame.font.SysFont("Segoe UI",  40, bold=True)
        self.font_xl  = pygame.font.SysFont("Segoe UI",  80, bold=True)

        self.grid_size  = 8
        self.difficulty = "Easy"
        self.mode       = "Menu"
        self.vs_cpu     = False
        self.cell_size  = CELL_SIZE
        self.algo_name  = "Greedy"     # selected algorithm

        self.bg_image = None
        bg_path = r"Images\Startup-Page-BG-Image.jpg"
        try:
            loaded = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.smoothscale(loaded, (self.screen_w, self.screen_h))
        except Exception as e:
            print(f"Could not load background: {e}")

    # ── helpers ──────────────────────────────────────────────
    def run(self):
        while True:
            if   self.mode == "Menu":     self.menu_loop()
            elif self.mode == "Settings": self.settings_loop()
            elif self.mode == "Game":     self.game_loop()

    def calc_mines(self):
        total = self.grid_size * self.grid_size
        ratio = 0.12 if self.difficulty == "Easy" else 0.17 if self.difficulty == "Medium" else 0.22
        return int(total * ratio)

    def get_blurred_background(self):
        if not self.bg_image: return None
        small = pygame.transform.smoothscale(self.bg_image,
                    (self.screen_w // 10, self.screen_h // 10))
        blurred = pygame.transform.smoothscale(small, (self.screen_w, self.screen_h))
        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.fill((0, 0, 0)); overlay.set_alpha(100)
        blurred.blit(overlay, (0, 0))
        return blurred

    def fade_transition(self):
        surf = pygame.Surface((self.screen_w, self.screen_h))
        surf.fill((0, 0, 0))
        for alpha in range(0, 255, 15):
            surf.set_alpha(alpha)
            self.screen.blit(surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)

    # ── MENU ─────────────────────────────────────────────────
    def menu_loop(self):
        btn_single = Button(300, 400, 200, 50, "SOLO SWEEPER")
        btn_cpu    = Button(290, 470, 220, 50, "MIND VS MACHINE")

        while self.mode == "Menu":
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(C_BG)

            shadow = self.font_xl.render("MINESWEEPER AI", True, (0, 0, 0))
            self.screen.blit(shadow, shadow.get_rect(center=(self.screen_w // 2 + 4, 324)))
            title  = self.font_xl.render("MINESWEEPER AI", True, C_ACCENT)
            self.screen.blit(title,  title.get_rect(center=(self.screen_w // 2, 320)))

            btn_single.draw(self.screen, self.font)
            btn_cpu.draw(self.screen, self.font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_single.is_clicked(event):
                    self.fade_transition(); self.vs_cpu = False
                    self.mode = "Settings"; return
                if btn_cpu.is_clicked(event):
                    self.fade_transition(); self.vs_cpu = True
                    self.mode = "Settings"; return

            pygame.display.flip()
            self.clock.tick(60)

    # ── SETTINGS ─────────────────────────────────────────────
    def settings_loop(self):
        bg_blur = self.get_blurred_background()

        # Grid size buttons
        sizes = [8, 12, 16, 20]
        btns_size = [Button(200 + i*70, 200, 60, 40, str(s),
                            color=C_ACCENT if self.grid_size == s else C_PANEL)
                     for i, s in enumerate(sizes)]

        # Difficulty buttons
        diffs = ["Easy", "Medium", "Hard"]
        btns_diff = [Button(200 + i*120, 290, 100, 40, d,
                            color=C_ACCENT if self.difficulty == d else C_PANEL)
                     for i, d in enumerate(diffs)]

        # Algorithm selector buttons (only shown in vs_cpu mode)
        algo_colors = [C_ALGO_GREEDY, C_ALGO_BT, C_ALGO_DP, C_ALGO_DC]
        btns_algo = [Button(100 + i*155, 380, 140, 38, name,
                            color=algo_colors[i] if name == self.algo_name else C_PANEL)
                     for i, name in enumerate(SOLVER_NAMES)]

        btn_start     = Button(300, 470, 200, 55, "START GAME", color=C_FLAG)
        btn_clear_log = Button(40,  530, 140, 38, "CLEAR LOGS", color=(180, 50, 50))

        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(100)

        while self.mode == "Settings":
            if bg_blur:
                self.screen.blit(bg_blur, (0, 0))
            else:
                self.screen.fill(C_BG)

            title = self.font_lg.render("GAME SETUP", True, C_ACCENT)
            self.screen.blit(title, (280, 100))

            # Grid size
            self.screen.blit(self.font.render("GRID SIZE:", True, C_TEXT_MAIN), (60, 210))
            for b in btns_size: b.draw(self.screen, self.font)

            # Difficulty
            self.screen.blit(self.font.render("DIFFICULTY:", True, C_TEXT_MAIN), (40, 298))
            for b in btns_diff: b.draw(self.screen, self.font)

            # Algorithm (only shown in Mind vs Machine)
            if self.vs_cpu:
                self.screen.blit(self.font.render("AI ALGORITHM:", True, C_TEXT_MAIN), (40, 388))
                for b in btns_algo: b.draw(self.screen, self.font)
                # Show complexity hint
                cplx = ALGO_COMPLEXITY.get(self.algo_name, "")
                cplx_surf = self.font_sm.render(f"Complexity: {cplx}", True, C_FLAG)
                self.screen.blit(cplx_surf, (100, 428))

            btn_start.draw(self.screen, self.font)
            btn_clear_log.draw(self.screen, self.font)

            mines_surf = self.font.render(f"Mines: {self.calc_mines()}", True, (200, 200, 200))
            self.screen.blit(mines_surf, (350, 435))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                for i, b in enumerate(btns_size):
                    if b.is_clicked(event):
                        self.grid_size = sizes[i]
                        for k, bx in enumerate(btns_size):
                            bx.color = C_ACCENT if k == i else C_PANEL

                for i, b in enumerate(btns_diff):
                    if b.is_clicked(event):
                        self.difficulty = diffs[i]
                        for k, bx in enumerate(btns_diff):
                            bx.color = C_ACCENT if k == i else C_PANEL

                if self.vs_cpu:
                    for i, b in enumerate(btns_algo):
                        if b.is_clicked(event):
                            self.algo_name = SOLVER_NAMES[i]
                            for k, bx in enumerate(btns_algo):
                                bx.color = algo_colors[k] if k == i else C_PANEL

                if btn_start.is_clicked(event):
                    self.fade_transition(); self.mode = "Game"; return

                if btn_clear_log.is_clicked(event):
                    log_path = os.path.join("Game_logs", "all_game_logs.txt")
                    try:
                        os.makedirs("Game_logs", exist_ok=True)
                        with open(log_path, "w") as f:
                            f.write(f"LOG CLEARED: {datetime.datetime.now()}\n")
                    except Exception as e:
                        print(f"Error clearing logs: {e}")

            pygame.display.flip()
            self.clock.tick(60)

    # ── GAME ─────────────────────────────────────────────────
    def game_loop(self):
        # ── window sizing ────────────────────────────────────
        def update_window_size():
            grid_px = self.grid_size * int(self.cell_size)
            req_w   = max(800,  MARGIN * 2 + grid_px + SIDEBAR_WIDTH)
            req_h   = max(600,  MARGIN * 2 + grid_px)
            cw, ch  = self.screen.get_size()
            if int(req_w) != cw or int(req_h) != ch:
                self.screen = pygame.display.set_mode((int(req_w), int(req_h)))
            return int(req_w), int(req_h)

        game_w, game_h = update_window_size()

        # ── state ────────────────────────────────────────────
        def init_game():
            return Board(self.grid_size, self.grid_size, self.calc_mines())

        board         = init_game()
        ai            = make_solver(self.algo_name)
        turn          = "Human"
        scores        = {"Human": {'RS':0,'CF':0,'WF':0},
                         "AI":    {'RS':0,'CF':0,'WF':0}}
        ai_timer      = 0
        hint          = None
        last_ai_move  = None
        ai_moves      = set()
        move_log      = []
        game_started  = False
        start_ticks   = 0
        elapsed_time  = 0
        total_moves   = 0
        is_resizing   = False

        # ── helper: frontier cells for visualisation ─────────
        def get_frontier(b):
            frontier = set()
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    cell = b.grid[r][c]
                    if cell.is_revealed or cell.is_flagged:
                        continue
                    for nb in cell.neighbors:
                        if nb.is_revealed and nb.number > 0:
                            frontier.add((r, c))
                            break
            return frontier

        # ── helper: timing colour ────────────────────────────
        def time_color(ms):
            if ms < 1:   return C_TIME_FAST
            if ms < 10:  return C_TIME_MED
            return C_TIME_SLOW

        # ── DRAW ─────────────────────────────────────────────
        def draw_game(curr_time_str, curr_timer_col, show_undo_btn,
                      highlights=None, highlight_col=None):
            self.screen.fill(C_BG)
            mouse_pos  = pygame.mouse.get_pos()
            grid_px    = self.grid_size * int(self.cell_size)
            sidebar_x  = MARGIN + grid_px + 40
            draw_cs    = int(self.cell_size)

            # ── grid ─────────────────────────────────────────
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    x    = MARGIN + c * draw_cs
                    y    = MARGIN + r * draw_cs
                    cell = board.grid[r][c]
                    rect = pygame.Rect(x, y, draw_cs - 1, draw_cs - 1)

                    if cell.is_revealed:
                        pygame.draw.rect(self.screen, C_CELL_REVEALED, rect, border_radius=4)
                        if cell.is_mine:
                            pygame.draw.circle(self.screen, C_MINE, rect.center, draw_cs // 4)
                        elif cell.number > 0:
                            dyn = pygame.font.SysFont("Segoe UI",
                                                       int(draw_cs * 0.7), bold=True)
                            txt = dyn.render(str(cell.number), True, C_NUMS[cell.number])
                            self.screen.blit(txt, txt.get_rect(center=rect.center))
                    else:
                        is_hover = rect.collidepoint(mouse_pos)
                        col = (C_CELL_HOVER
                               if is_hover and not board.game_over and highlights is None
                               else C_CELL_HIDDEN)
                        pygame.draw.rect(self.screen, col, rect, border_radius=4)
                        if cell.is_flagged:
                            off = 5 * (draw_cs / 35)
                            pts = [(rect.centerx - off, rect.centery + off),
                                   (rect.centerx - off, rect.centery - off),
                                   (rect.centerx + off, rect.centery)]
                            pygame.draw.polygon(self.screen, C_FLAG, pts)

                    # AI-move red dot
                    if (r, c) in ai_moves:
                        pygame.draw.circle(self.screen, (200, 0, 0),
                                           (rect.right - 5, rect.bottom - 5), 3)

                    # Thinking / choosing highlight
                    if highlights and (r, c) in highlights and highlight_col:
                        pygame.draw.rect(self.screen, highlight_col, rect, 4, border_radius=4)

                    # Hint highlight
                    if hint and hint[0] == r and hint[1] == c:
                        h_col = C_HINT_SAFE if hint[2] == 'reveal' else C_HINT_MINE
                        pygame.draw.rect(self.screen, h_col, rect, 3, border_radius=4)

                    # Last AI move blue outline
                    if last_ai_move and last_ai_move == (r, c):
                        pygame.draw.rect(self.screen, (50, 100, 255), rect, 3, border_radius=4)

            # Resize handle
            h_x = MARGIN + grid_px
            h_y = MARGIN + grid_px
            pygame.draw.line(self.screen, (150,150,150), (h_x, h_y), (h_x+15, h_y+15), 3)
            pygame.draw.line(self.screen, (150,150,150), (h_x+6,  h_y+15),(h_x+15, h_y+6), 2)

            # ── sidebar panel ─────────────────────────────────
            panel_rect = pygame.Rect(sidebar_x, MARGIN, SIDEBAR_WIDTH, game_h - MARGIN * 2)
            pygame.draw.rect(self.screen, C_PANEL, panel_rect, border_radius=10)
            pygame.draw.rect(self.screen, C_ACCENT, panel_rect, 2, border_radius=10)

            sy = MARGIN + 12  # running y inside sidebar

            # Time & Moves row
            self.screen.blit(self.font.render("TIME", True, (150,150,150)),
                             (sidebar_x + 15, sy))
            self.screen.blit(self.font.render("MOVES", True, (150,150,150)),
                             (sidebar_x + 185, sy))
            sy += 26
            self.screen.blit(self.font_lg.render(curr_time_str, True, curr_timer_col),
                             (sidebar_x + 15, sy))
            self.screen.blit(self.font_lg.render(str(total_moves), True, C_ACCENT),
                             (sidebar_x + 185, sy))
            sy += 50

            # Status / winner
            status = f"TURN: {turn}" if not board.game_over else f"WINNER: {board.winner}"
            col    = C_MINE if board.game_over else C_ACCENT
            self.screen.blit(self.font.render(status, True, col), (sidebar_x + 15, sy))
            sy += 30

            # Scores
            def draw_score(lbl, s, y):
                val = s['RS'] + 2 * s['CF'] - s['WF']
                self.screen.blit(
                    self.font.render(f"{lbl}: {val}  (R:{s['RS']} CF:{s['CF']} WF:{s['WF']})",
                                     True, C_TEXT_MAIN),
                    (sidebar_x + 15, y))

            draw_score("HUMAN", scores['Human'], sy); sy += 24
            if self.vs_cpu:
                draw_score("AI", scores['AI'], sy);   sy += 24

            # ── ALGORITHM & TIMING PANEL ─────────────────────
            sy += 6
            pygame.draw.line(self.screen, (60,60,80),
                             (sidebar_x + 10, sy), (sidebar_x + SIDEBAR_WIDTH - 10, sy))
            sy += 8

            algo_col_map = dict(zip(SOLVER_NAMES,
                                    [C_ALGO_GREEDY, C_ALGO_BT, C_ALGO_DP, C_ALGO_DC]))
            a_col = algo_col_map.get(ai.name, C_ACCENT)

            self.screen.blit(
                self.font.render(f"ALGO: {ai.name}", True, a_col),
                (sidebar_x + 15, sy))
            self.screen.blit(
                self.font_sm.render(f"Complexity: {ai.complexity_label()}", True, C_FLAG),
                (sidebar_x + 15, sy + 22))
            sy += 46

            # Per-move timing
            last_ms  = ai.last_move_time * 1000
            avg_ms   = ai.avg_time()      * 1000
            total_ms = ai.total_time      * 1000

            self.screen.blit(
                self.font_sm.render(
                    f"Last move : {last_ms:7.3f} ms",
                    True, time_color(last_ms)),
                (sidebar_x + 15, sy));  sy += 18
            self.screen.blit(
                self.font_sm.render(
                    f"Avg / move: {avg_ms:7.3f} ms",
                    True, time_color(avg_ms)),
                (sidebar_x + 15, sy));  sy += 18
            self.screen.blit(
                self.font_sm.render(
                    f"Total AI  : {total_ms:7.3f} ms",
                    True, C_TEXT_MAIN),
                (sidebar_x + 15, sy));  sy += 18
            self.screen.blit(
                self.font_sm.render(
                    f"AI moves  : {ai.move_count}",
                    True, C_TEXT_MAIN),
                (sidebar_x + 15, sy));  sy += 22

            # ── AI log ───────────────────────────────────────
            pygame.draw.line(self.screen, (60,60,80),
                             (sidebar_x+10, sy), (sidebar_x + SIDEBAR_WIDTH - 10, sy))
            sy += 6
            for line in reversed(ai.logs[-7:]):
                self.screen.blit(
                    self.font_sm.render(f"> {line}", True, (180,180,180)),
                    (sidebar_x + 15, sy))
                sy += 18

            # ── buttons ──────────────────────────────────────
            btn_back.draw(self.screen, self.font)
            btn_reset.draw(self.screen, self.font)
            if show_undo_btn:
                btn_undo.draw(self.screen, self.font)
            btn_hint.draw(self.screen, self.font)
            btn_save.draw(self.screen, self.font)

        # ── flash effect ─────────────────────────────────────
        def flash_board(t_str, t_col):
            grid_px = self.grid_size * int(self.cell_size)
            overlay = pygame.Surface((grid_px, grid_px))
            overlay.fill((255, 0, 0)); overlay.set_alpha(150)
            for _ in range(2):
                draw_game(t_str, t_col, False)
                self.screen.blit(overlay, (MARGIN, MARGIN))
                pygame.display.flip(); pygame.time.delay(150)
                draw_game(t_str, t_col, False)
                pygame.display.flip(); pygame.time.delay(150)

        # ── log helpers ──────────────────────────────────────
        def log_move(actor, action, r, c, result, reason):
            entry = {
                "Time": datetime.datetime.now().strftime("%H:%M:%S"),
                "Actor": actor, "Action": action,
                "Coord": f"({r},{c})", "Result": result, "Reason": reason
            }
            move_log.append(entry)
            print(f"[LOG] {actor} {action} at ({r},{c}) -> {result} | {reason}")

        def save_logs_to_file():
            if not move_log: return
            log_dir = "Game_logs"
            os.makedirs(log_dir, exist_ok=True)
            filepath  = os.path.join(log_dir, "all_game_logs.txt")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines = [
                f"\n{'='*60}\n SESSION: {timestamp}  ALGO: {ai.name} [{ai.complexity_label()}]\n{'='*60}\n",
                f"Grid: {self.grid_size}x{self.grid_size}, Mines: {self.calc_mines()}\n",
                f"AI timing — last:{ai.last_move_time*1000:.3f}ms  avg:{ai.avg_time()*1000:.3f}ms  total:{ai.total_time*1000:.3f}ms\n",
                "-"*115 + "\n",
                f"{'TIME':<10} | {'ACTOR':<8} | {'ACTION':<10} | {'COORD':<8} | {'RESULT':<22} | REASON\n",
                "-"*115 + "\n",
            ]
            for e in move_log:
                lines.append(
                    f"{e['Time']:<10} | {e['Actor']:<8} | {e['Action']:<10} | "
                    f"{e['Coord']:<8} | {e['Result']:<22} | {e['Reason']}\n")
            lines.append("\n")
            new_block = "".join(lines)
            old = ""
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f: old = f.read()
                except: pass
            try:
                with open(filepath, "w") as f: f.write(new_block + old)
                ai.log("Logs saved.")
                move_log.clear()
            except Exception as e:
                print(f"Error saving log: {e}")

        def reveal_all_mines():
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if board.grid[r][c].is_mine:
                        board.grid[r][c].is_revealed = True

        # FIX: was `if points > 1: return` — that discarded cascade points!
        def add_points(actor, points):
            scores[actor]['RS'] += points

        def check_victory():
            if board.game_over: return
            total_safe    = self.grid_size * self.grid_size - self.calc_mines()
            count_revealed = sum(
                1 for r in range(self.grid_size)
                  for c in range(self.grid_size)
                  if board.grid[r][c].is_revealed)
            if count_revealed >= total_safe:
                board.game_over = True
                # Auto-flag only actual mines (not arbitrary hidden cells)
                for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        cell = board.grid[r][c]
                        if cell.is_mine and not cell.is_flagged:
                            cell.is_flagged = True
                h = scores['Human']['RS'] + 2*scores['Human']['CF'] - scores['Human']['WF']
                a = scores['AI']['RS']    + 2*scores['AI']['CF']    - scores['AI']['WF']
                board.winner = "Human" if h > a else "AI" if a > h else "Draw"
                ai.log(f"Board Cleared! Winner: {board.winner}")
                log_move("System", "GameOver", -1, -1, "Board Cleared",
                         f"Winner: {board.winner}")

        # ── main game loop ───────────────────────────────────
        running = True
        while running:
            mins = elapsed_time // 60
            secs = elapsed_time % 60
            time_str    = f"{mins:02}:{secs:02}"
            timer_color = C_ACCENT if game_started else (100,100,100)

            grid_px   = self.grid_size * int(self.cell_size)
            sidebar_x = MARGIN + grid_px + 40

            btn_back  = Button(game_w - 125, game_h - 50,  110, 32, "MENU",     color=C_PANEL)
            btn_reset = Button(game_w - 125, game_h - 90,  110, 32, "RESET",    color=C_PANEL)
            btn_undo  = Button(game_w - 245, game_h - 50,  110, 32, "UNDO",     color=C_PANEL)
            btn_hint  = Button(game_w - 245, game_h - 90,  110, 32, "HINT",     color=(100,100,120))
            btn_save  = Button(game_w - 125, game_h - 130, 110, 32, "SAVE LOG", color=(50,100,50))

            show_undo = not (board.game_over and board.winner == "AI")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_logs_to_file(); pygame.quit(); sys.exit()

                # Resize handle drag
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handle = pygame.Rect(MARGIN + grid_px, MARGIN + grid_px, 25, 25)
                    if handle.collidepoint(event.pos): is_resizing = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if is_resizing:
                        is_resizing = False
                        game_w, game_h = update_window_size()

                if event.type == pygame.MOUSEMOTION and is_resizing:
                    self.cell_size = max(15, min(50,
                        self.cell_size + (event.rel[0] + event.rel[1]) / 20))

                if btn_back.is_clicked(event):
                    save_logs_to_file()
                    self.mode = "Menu"
                    self.screen = pygame.display.set_mode((800, 600))
                    return

                if btn_save.is_clicked(event):
                    save_logs_to_file()

                if btn_reset.is_clicked(event):
                    save_logs_to_file()
                    board        = init_game()
                    ai           = make_solver(self.algo_name)
                    scores       = {"Human": {'RS':0,'CF':0,'WF':0},
                                    "AI":    {'RS':0,'CF':0,'WF':0}}
                    turn         = "Human"
                    hint         = None
                    last_ai_move = None
                    ai_moves.clear()
                    move_log.clear()
                    game_started = False
                    start_ticks  = 0
                    elapsed_time = 0
                    total_moves  = 0
                    ai.log("Game Reset.")

                if show_undo and btn_undo.is_clicked(event):
                    if turn == "Human" and board.undo():
                        ai.log("Undo done."); hint = None; last_ai_move = None

                if btn_hint.is_clicked(event):
                    move = ai.get_move(board, is_hint=True)
                    if move:
                        hint = move; ai.log("Hint shown.")
                    else:
                        ai.log("No logical hint available.")

                # ── human click ──────────────────────────────
                if event.type == pygame.MOUSEBUTTONDOWN and not board.game_over and not is_resizing:
                    mx, my = event.pos
                    if MARGIN <= mx < MARGIN + grid_px and MARGIN <= my < MARGIN + grid_px:
                        c = int((mx - MARGIN) // self.cell_size)
                        r = int((my - MARGIN) // self.cell_size)
                        if 0 <= r < self.grid_size and 0 <= c < self.grid_size and turn == "Human":
                            if not game_started:
                                game_started = True
                                start_ticks  = pygame.time.get_ticks()

                            action_taken = False
                            points       = 0
                            res_str      = ""

                            if event.button == 1:
                                cell = board.grid[r][c]
                                if not cell.is_revealed:
                                    res = board.reveal(r, c)
                                    if res == -999:
                                        flash_board(time_str, timer_color)
                                        ai.log("Human hit mine! Game over.")
                                        board.winner = "AI"
                                        board.game_over = True
                                        res_str = "Hit Mine"
                                        reveal_all_mines()
                                    else:
                                        points = res
                                        action_taken = True
                                        res_str = f"Safe ({res} cells)"
                                    log_move("Human","Reveal",r,c,res_str,"Manual Click")
                                elif cell.is_revealed:
                                    res = board.chord(r, c)
                                    if res == -999:
                                        flash_board(time_str, timer_color)
                                        ai.log("Human chord hit mine!")
                                        board.winner = "AI"
                                        board.game_over = True
                                        res_str = "Chord->Mine"
                                        reveal_all_mines()
                                    elif res > 0:
                                        points = res; action_taken = True
                                        res_str = f"Chord ({res} cells)"
                                    else:
                                        res_str = "Chord (no effect)"
                                    if res != 0:
                                        log_move("Human","Chord",r,c,res_str,"Manual Chord")

                            elif event.button == 3:
                                if board.toggle_flag(r, c):
                                    action_taken = True
                                    res_str = "Flag Toggled"
                                    if board.grid[r][c].is_mine: scores['Human']['CF'] += 1
                                    else:                        scores['Human']['WF'] += 1
                                    log_move("Human","Flag",r,c,res_str,"Right Click")

                            if action_taken:
                                total_moves += 1; hint = None
                                add_points("Human", points)
                                check_victory()
                                if not board.game_over and self.vs_cpu:
                                    turn = "AI"; ai_timer = 45

            # ── AI TURN ──────────────────────────────────────
            if self.vs_cpu and turn == "AI" and not board.game_over:
                ai_timer -= 1
                if ai_timer <= 0:
                    # Visualise frontier (thinking phase)
                    frontier = get_frontier(board)
                    if frontier:
                        draw_game(time_str, timer_color, show_undo,
                                  highlights=frontier, highlight_col=C_THINKING)
                        pygame.display.flip(); pygame.time.delay(300)

                    move = ai.get_move(board)
                    if move:
                        r, c, act = move

                        # Visualise chosen cell
                        draw_game(time_str, timer_color, show_undo,
                                  highlights={(r,c)}, highlight_col=C_CHOOSING)
                        pygame.display.flip(); pygame.time.delay(300)

                        last_ai_move = (r, c)
                        ai_moves.add((r, c))
                        total_moves += 1

                        ai_reason = ai.logs[-1] if ai.logs else "Unknown"
                        points = 0; res_str = ""

                        if act == 'reveal':
                            res = board.reveal(r, c)
                            if res == -999:
                                ai.log("AI hit mine! Game over.")
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
                            else:                        scores['AI']['WF'] += 1
                            res_str = "Flag Placed"

                        log_move("AI", act.capitalize(), r, c, res_str, ai_reason)
                        check_victory()

                    turn = "Human"

            if game_started and not board.game_over:
                elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

            draw_game(time_str, timer_color, show_undo)
            pygame.display.flip()
            self.clock.tick(60)




