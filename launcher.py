import pygame
import sys
import importlib

# Import the game modules
import_path = "c:\\Users\\yassi\\Downloads\\game_launcher\\"
sys.path.append(import_path)
import tictactoe
import freecell
import connectfour
# Constants for the launcher
WIDTH, HEIGHT = 600, 500
DISPLAY_MODE = 0  # 0: windowed, 1: fullscreen
BG_COLOR = (30, 40, 60)
BTN_COLOR = (60, 120, 220)
BTN_HOVER = (90, 160, 255)
BTN_TEXT = (255, 255, 255)
ARROW_COLOR = (60, 60, 60)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game Launcher")
font = pygame.font.SysFont('arial', 48, bold=True)
btn_font = pygame.font.SysFont('arial', 32, bold=True)

def draw_button(rect, text, hovered):
    color = BTN_HOVER if hovered else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=18)
    pygame.draw.rect(screen, (30, 70, 160), rect, width=3, border_radius=18)
    text_surf = btn_font.render(text, True, BTN_TEXT)
    screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))

def draw_back_arrow():
    # Draw a back arrow at the top left
    arrow_rect = pygame.Rect(18, 18, 48, 48)
    pygame.draw.circle(screen, (230, 230, 230), arrow_rect.center, 24)
    pygame.draw.circle(screen, (180, 180, 180), arrow_rect.center, 24, 2)
    pts = [
        (arrow_rect.x + 32, arrow_rect.y + 12),
        (arrow_rect.x + 16, arrow_rect.y + 24),
        (arrow_rect.x + 32, arrow_rect.y + 36)
    ]
    pygame.draw.polygon(screen, ARROW_COLOR, pts)
    return arrow_rect

def set_display_mode(width, height, mode):
    global screen, WIDTH, HEIGHT, DISPLAY_MODE
    WIDTH, HEIGHT, DISPLAY_MODE = width, height, mode
    if mode == 1:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    else:
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen

def main_menu():
    global WIDTH, HEIGHT, screen, DISPLAY_MODE
    running = True
    while running:
        screen.fill(BG_COLOR)
        title = font.render("Choose a Game", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        btn1 = pygame.Rect(WIDTH//2 - 150, 180, 300, 70)
        btn2 = pygame.Rect(WIDTH//2 - 150, 280, 300, 70)
        btn3 = pygame.Rect(WIDTH//2 - 150, 380, 300, 70)
        mouse = pygame.mouse.get_pos()
        draw_button(btn1, "Tic-Tac-Toe", btn1.collidepoint(mouse))
        draw_button(btn2, "Freecell", btn2.collidepoint(mouse))
        draw_button(btn3, "Connect Four", btn3.collidepoint(mouse))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                DISPLAY_MODE = 0
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Toggle fullscreen
                    if DISPLAY_MODE == 0:
                        set_display_mode(WIDTH, HEIGHT, 1)
                    else:
                        set_display_mode(WIDTH, HEIGHT, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn1.collidepoint(event.pos):
                    run_tictactoe()
                elif btn2.collidepoint(event.pos):
                    run_freecell()
                elif btn3.collidepoint(event.pos):
                    run_connectfour()

def run_tictactoe():
    global WIDTH, HEIGHT, screen, DISPLAY_MODE
    # Do not resize window, just update caption and pass current size
    pygame.display.set_caption("Tic-Tac-Toe")
    def draw_back():
        return draw_back_arrow()
    import importlib
    importlib.reload(tictactoe)
    orig_main = tictactoe.main
    def main_with_back():
        global WIDTH, HEIGHT, screen, DISPLAY_MODE
        tictactoe.WIDTH, tictactoe.HEIGHT = WIDTH, HEIGHT
        tictactoe.screen = screen
        running = True
        while running:
            tictactoe.WIDTH, tictactoe.HEIGHT = WIDTH, HEIGHT
            tictactoe.screen = screen
            tictactoe.draw_board(tictactoe.current_board)
            tictactoe.draw_scores()
            btn_rect = tictactoe.draw_restart_button()
            arrow_rect = draw_back()
            if hasattr(tictactoe, "winner") and tictactoe.winner:
                if tictactoe.win_line and not tictactoe.animated:
                    tictactoe.animate_win_line(*tictactoe.win_line, persist=True)
                    tictactoe.animated = True
                elif tictactoe.win_line and tictactoe.animated:
                    board_rect = tictactoe.get_board_rect()
                    cell_size = board_rect.width // 3
                    start_cell, end_cell = tictactoe.win_line
                    start_px = (board_rect.left + start_cell[0] * cell_size + cell_size // 2,
                                board_rect.top + start_cell[1] * cell_size + cell_size // 2)
                    end_px = (board_rect.left + end_cell[0] * cell_size + cell_size // 2,
                              board_rect.top + end_cell[1] * cell_size + cell_size // 2)
                    pygame.draw.line(screen, (0, 180, 0), start_px, end_px, 10)
                msg = f"{tictactoe.winner} gagne !" if tictactoe.winner in ['X', 'O'] else "Match nul !"
                text = tictactoe.small_font.render(msg, True, (0, 128, 0))
                screen.blit(text, (tictactoe.WIDTH//2 - text.get_width()//2, tictactoe.HEIGHT//2 - text.get_height()//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h
                    DISPLAY_MODE = 0
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    tictactoe.WIDTH, tictactoe.HEIGHT = WIDTH, HEIGHT
                    tictactoe.screen = screen
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        # Toggle fullscreen
                        if DISPLAY_MODE == 0:
                            set_display_mode(WIDTH, HEIGHT, 1)
                        else:
                            set_display_mode(WIDTH, HEIGHT, 0)
                        tictactoe.WIDTH, tictactoe.HEIGHT = WIDTH, HEIGHT
                        tictactoe.screen = screen
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if arrow_rect.collidepoint(mx, my):
                        return
                    if btn_rect.collidepoint(mx, my):
                        tictactoe.current_board = [['' for _ in range(3)] for _ in range(3)]
                        tictactoe.turn = 'X'
                        tictactoe.winner = None
                        tictactoe.win_line = None
                        tictactoe.animated = False
                        continue
                    if not getattr(tictactoe, "winner", None):
                        board_rect = tictactoe.get_board_rect()
                        cell_size = board_rect.width // 3
                        if board_rect.collidepoint(mx, my):
                            x = (mx - board_rect.left) // cell_size
                            y = (my - board_rect.top) // cell_size
                            if 0 <= x < 3 and 0 <= y < 3 and tictactoe.current_board[y][x] == '':
                                tictactoe.animate_symbol(tictactoe.current_board, x, y, tictactoe.turn)
                                tictactoe.current_board[y][x] = tictactoe.turn
                                w, line = tictactoe.check_winner(tictactoe.current_board)
                                if w:
                                    tictactoe.winner = w
                                    tictactoe.win_line = line
                                    tictactoe.animated = False
                                    if w == 'X':
                                        tictactoe.score_X += 1
                                    elif w == 'O':
                                        tictactoe.score_O += 1
                                elif tictactoe.is_full(tictactoe.current_board):
                                    tictactoe.winner = 'Draw'
                                    tictactoe.win_line = None
                                    tictactoe.animated = False
                                tictactoe.turn = 'O' if tictactoe.turn == 'X' else 'X'
    tictactoe.current_board = [['' for _ in range(3)] for _ in range(3)]
    tictactoe.turn = 'X'
    tictactoe.winner = None
    tictactoe.win_line = None
    tictactoe.animated = False
    main_with_back()

def run_freecell():
    global WIDTH, HEIGHT, screen, DISPLAY_MODE
    pygame.display.set_caption("Freecell (5 Freecells)")
    import importlib
    importlib.reload(freecell)

    # --- Patch: provide a present_surface callback for animation ---
    def present_surface(surface):
        screen.blit(surface, (0, 0))
        pygame.display.flip()
    freecell.present_surface = present_surface

    game = freecell.PygameFreecellGame()
    clock = pygame.time.Clock()
    running = True
    arrow_rect = None  # Store the arrow rect for click detection
    while running and game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if arrow_rect and arrow_rect.collidepoint(event.pos):
                    return
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_p:
                    game.undo()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    game.running = False
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    if DISPLAY_MODE == 0:
                        set_display_mode(WIDTH, HEIGHT, 1)
                    else:
                        set_display_mode(WIDTH, HEIGHT, 0)
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                DISPLAY_MODE = 0
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        # --- Double buffering to prevent flicker ---
        buffer = pygame.Surface((WIDTH, HEIGHT))
        if game.animations:
            # Temporarily swap the screen to buffer for drawing
            old_screen = game.__dict__.get('screen', None)
            game.screen = buffer
            game.process_animations(buffer)
            if old_screen is not None:
                game.screen = old_screen
            arrow_rect = draw_back_arrow_on_surface(buffer)
        else:
            # Temporarily swap the screen to buffer for drawing
            old_screen = game.__dict__.get('screen', None)
            game.screen = buffer
            game.draw(buffer)
            if old_screen is not None:
                game.screen = old_screen
            arrow_rect = draw_back_arrow_on_surface(buffer)
        screen.blit(buffer, (0, 0))
        pygame.display.update()
        fps = clock.get_fps()
        pygame.display.set_caption(f'Freecell (5 Freecells) - FPS: {fps:.1f}')
        clock.tick(60)
    return

def run_connectfour():
    global WIDTH, HEIGHT, screen, DISPLAY_MODE
    pygame.display.set_caption("Connect Four")
    import importlib
    importlib.reload(connectfour)
    connectfour.WIDTH = WIDTH
    connectfour.HEIGHT = HEIGHT
    connectfour.screen = screen

    # --- Patch: provide a present_surface callback for animation ---
    def present_surface(surface):
        screen.blit(surface, (0, 0))
        pygame.display.flip()
    connectfour.present_surface = present_surface

    running = True
    clock = pygame.time.Clock()
    arrow_rect = None
    board = connectfour.create_board()
    selected_col = None
    game_over = False
    winner = None
    turn = 1
    btn_rect = None

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if arrow_rect and arrow_rect.collidepoint(mx, my):
                    return
                if btn_rect and btn_rect.collidepoint(mx, my):
                    board = connectfour.create_board()
                    game_over = False
                    turn = 1
                    winner = None
                    continue
                if game_over:
                    continue
                # Handle column selection
                width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
                if offset_y <= my < offset_y + squaresize and offset_x <= mx < offset_x + squaresize*connectfour.COLS:
                    col = int((mx - offset_x) // squaresize)
                    if 0 <= col < connectfour.COLS and connectfour.is_valid_location(board, col):
                        row = connectfour.get_next_open_row(board, col)
                        connectfour.animate_drop(board, col, row, turn, squaresize, radius, offset_x, offset_y)
                        connectfour.drop_piece(board, row, col, turn)
                        if connectfour.winning_move(board, turn):
                            winner = turn
                            game_over = True
                            if turn == 1:
                                connectfour.score_1 += 1
                            else:
                                connectfour.score_2 += 1
                        elif connectfour.is_full(board):
                            winner = None
                            game_over = True
                        turn = 2 if turn == 1 else 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Toggle fullscreen
                    if DISPLAY_MODE == 0:
                        set_display_mode(WIDTH, HEIGHT, 1)
                    else:
                        set_display_mode(WIDTH, HEIGHT, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                DISPLAY_MODE = 0
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                connectfour.WIDTH = WIDTH
                connectfour.HEIGHT = HEIGHT
                connectfour.screen = screen

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
                if offset_y <= my < offset_y + squaresize and offset_x <= mx < offset_x + squaresize*connectfour.COLS:
                    selected_col = int((mx - offset_x) // squaresize)
                else:
                    selected_col = None

        # --- Double buffering to prevent flicker and draw arrow ---
        buffer = pygame.Surface((WIDTH, HEIGHT))
        connectfour.screen = buffer
        btn_rect = connectfour.draw_board(board, selected_col, surface=buffer)
        # Draw the back arrow on the buffer
        arrow_rect = draw_back_arrow_on_surface(buffer)
        # Draw winner/game over message if needed
        width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
        if game_over:
            msg = f"{'Rouge' if winner == 1 else 'Bleu'} gagne !" if winner else "Match nul !"
            text = connectfour.small_font.render(msg, True, (0, 128, 0))
            buffer.blit(text, (offset_x + squaresize*connectfour.COLS//2 - text.get_width()//2, offset_y + squaresize - text.get_height() - 10))
        screen.blit(buffer, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        # --- Handle animation on click ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if arrow_rect and arrow_rect.collidepoint(mx, my):
                    return
                if btn_rect and btn_rect.collidepoint(mx, my):
                    board = connectfour.create_board()
                    game_over = False
                    turn = 1
                    winner = None
                    continue
                if game_over:
                    continue
                width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
                if offset_y <= my < offset_y + squaresize and offset_x <= mx < offset_x + squaresize*connectfour.COLS:
                    col = int((mx - offset_x) // squaresize)
                    if 0 <= col < connectfour.COLS and connectfour.is_valid_location(board, col):
                        row = connectfour.get_next_open_row(board, col)
                        # Pass buffer as surface for animation
                        connectfour.animate_drop(board, col, row, turn, squaresize, radius, offset_x, offset_y, surface=buffer)
                        connectfour.drop_piece(board, row, col, turn)
                        if connectfour.winning_move(board, turn):
                            winner = turn
                            game_over = True
                            if turn == 1:
                                connectfour.score_1 += 1
                            else:
                                connectfour.score_2 += 1
                        elif connectfour.is_full(board):
                            winner = None
                            game_over = True
                        turn = 2 if turn == 1 else 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Toggle fullscreen
                    if DISPLAY_MODE == 0:
                        set_display_mode(WIDTH, HEIGHT, 1)
                    else:
                        set_display_mode(WIDTH, HEIGHT, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                DISPLAY_MODE = 0
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                connectfour.WIDTH = WIDTH
                connectfour.HEIGHT = HEIGHT
                connectfour.screen = screen

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
                if offset_y <= my < offset_y + squaresize and offset_x <= mx < offset_x + squaresize*connectfour.COLS:
                    selected_col = int((mx - offset_x) // squaresize)
                else:
                    selected_col = None

        # --- Double buffering to prevent flicker and draw arrow ---
        buffer = pygame.Surface((WIDTH, HEIGHT))
        connectfour.screen = buffer
        btn_rect = connectfour.draw_board(board, selected_col, surface=buffer)
        # Draw the back arrow on the buffer
        arrow_rect = draw_back_arrow_on_surface(buffer)
        # Draw winner/game over message if needed
        width, height, squaresize, radius, offset_x, offset_y = connectfour.get_sizes()
        if game_over:
            msg = f"{'Rouge' if winner == 1 else 'Bleu'} gagne !" if winner else "Match nul !"
            text = connectfour.small_font.render(msg, True, (0, 128, 0))
            buffer.blit(text, (offset_x + squaresize*connectfour.COLS//2 - text.get_width()//2, offset_y + squaresize - text.get_height() - 10))
        screen.blit(buffer, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def draw_back_arrow_on_surface(surface):
    # Draw a back arrow at the top left on the given surface
    arrow_rect = pygame.Rect(18, 18, 48, 48)
    pygame.draw.circle(surface, (230, 230, 230), arrow_rect.center, 24)
    pygame.draw.circle(surface, (180, 180, 180), arrow_rect.center, 24, 2)
    pts = [
        (arrow_rect.x + 32, arrow_rect.y + 12),
        (arrow_rect.x + 16, arrow_rect.y + 24),
        (arrow_rect.x + 32, arrow_rect.y + 36)
    ]
    pygame.draw.polygon(surface, ARROW_COLOR, pts)
    return arrow_rect

if __name__ == '__main__':
    main_menu()
    #return arrow_rect

if __name__ == '__main__':
    main_menu()
