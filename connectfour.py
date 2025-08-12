import pygame
import sys
import time

# Constants
COLS, ROWS = 7, 6
BG_COLOR = (30, 40, 60)
BOARD_COLOR = (20, 60, 120)
PLAYER1_COLOR = (220, 60, 60)
PLAYER2_COLOR = (60, 120, 220)
EMPTY_COLOR = (230, 230, 230)
FONT_COLOR = (255, 255, 255)

pygame.init()
pygame.display.set_caption("Connect Four")
screen = pygame.display.set_mode((COLS*100, (ROWS+2)*100), pygame.RESIZABLE)
font = pygame.font.SysFont('arial', 64, bold=True)
small_font = pygame.font.SysFont('arial', 32, bold=True)

score_1 = 0
score_2 = 0

present_surface = None  # Will be set by launcher if running from launcher

def create_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def get_sizes():
    width, height = screen.get_width(), screen.get_height()
    board_size = min(width, height - 60)
    squaresize = board_size // max(COLS, ROWS)
    radius = squaresize // 2 - max(6, squaresize // 16)
    offset_x = (width - squaresize*COLS) // 2
    offset_y = (height - squaresize*ROWS) // 2
    return width, height, squaresize, radius, offset_x, offset_y

def draw_board(board, selected_col=None, surface=None, hover_y=None):
    if surface is None:
        surface = screen
    _, _, squaresize, radius, offset_x, offset_y = get_sizes()
    surface.fill(BG_COLOR)
    # Draw board background
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(offset_x + c*squaresize, offset_y + r*squaresize, squaresize, squaresize)
            pygame.draw.rect(surface, BOARD_COLOR, rect)
            pygame.draw.circle(surface, EMPTY_COLOR, (offset_x + c*squaresize + squaresize//2, offset_y + r*squaresize + squaresize//2), radius)
    # Draw tokens
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1:
                pygame.draw.circle(surface, PLAYER1_COLOR, (offset_x + c*squaresize + squaresize//2, offset_y + r*squaresize + squaresize//2), radius)
            elif board[r][c] == 2:
                pygame.draw.circle(surface, PLAYER2_COLOR, (offset_x + c*squaresize + squaresize//2, offset_y + r*squaresize + squaresize//2), radius)
    # Draw selection indicator as a floating token
    if selected_col is not None and 0 <= selected_col < COLS:
        # If hover_y is not provided, default to above the board
        if hover_y is None:
            token_y = offset_y - squaresize // 2
        else:
            # Clamp hover_y to the board area
            token_y = min(max(hover_y, offset_y + radius), offset_y + (ROWS-1)*squaresize + squaresize//2)
        # Determine whose turn it is by counting tokens
        count1 = sum(cell == 1 for row in board for cell in row)
        count2 = sum(cell == 2 for row in board for cell in row)
        turn = 1 if count1 == count2 else 2
        color = PLAYER1_COLOR if turn == 1 else PLAYER2_COLOR
        pygame.draw.circle(surface, color, (offset_x + selected_col*squaresize + squaresize//2, int(token_y)-radius*2), radius)
    draw_scores(squaresize, offset_x, offset_y, surface=surface)
    return draw_restart_button(squaresize, offset_x, offset_y, surface=surface)

def draw_scores(squaresize, offset_x, offset_y, surface=None):
    if surface is None:
        surface = screen
    x_text = small_font.render(f"Rouge: {score_1}", True, PLAYER1_COLOR)
    o_text = small_font.render(f"Bleu: {score_2}", True, PLAYER2_COLOR)
    surface.blit(x_text, (offset_x, offset_y - squaresize + 10))
    surface.blit(o_text, (offset_x + squaresize*COLS - o_text.get_width(), offset_y - squaresize + 10))

def draw_restart_button(squaresize, offset_x, offset_y, surface=None):
    if surface is None:
        surface = screen
    btn_font = pygame.font.SysFont('arial', max(18, squaresize//5), bold=True)
    text = btn_font.render("Recommencer", True, (255,255,255))
    padding = int(squaresize * 0.18)
    btn_w, btn_h = text.get_width() + 2*padding, text.get_height() + padding
    rect = pygame.Rect(offset_x + squaresize*COLS - btn_w - padding, offset_y + squaresize*ROWS + padding, btn_w, btn_h)
    pygame.draw.rect(surface, (60, 120, 220), rect, border_radius=int(squaresize*0.16))
    pygame.draw.rect(surface, (30, 70, 160), rect, width=3, border_radius=int(squaresize*0.16))
    surface.blit(text, (rect.x + padding, rect.y + padding//2))
    return rect

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            return r
    return None

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def winning_move(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Positive diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

def is_full(board):
    return all(board[0][c] != 0 for c in range(COLS))

def animate_drop(board, col, row, piece, squaresize=None, radius=None, offset_x=None, offset_y=None, surface=None):
    if surface is None:
        surface = screen
    if squaresize is None or radius is None or offset_x is None or offset_y is None:
        _, _, squaresize, radius, offset_x, offset_y = get_sizes()
    fps = 60
    clock = pygame.time.Clock()
    start_y = offset_y - squaresize // 2
    end_y = offset_y + row * squaresize + squaresize // 2
    x = offset_x + col * squaresize + squaresize // 2
    duration = 0.45  # seconds
    frames = int(duration * fps)
    for frame in range(frames + 1):
        t = frame / frames
        y = start_y + (end_y - start_y) * t
        if t > 0.92:
            bounce = (1 - (t - 0.92) / 0.08)
            y = min(y - 12 * bounce * (1 - bounce), end_y)
        draw_board(board, surface=surface)
        color = PLAYER1_COLOR if piece == 1 else PLAYER2_COLOR
        pygame.draw.circle(surface, color, (x, int(y)), radius)
        # --- Use present_surface callback if set ---
        if callable(globals().get("present_surface", None)):
            globals()["present_surface"](surface)
        else:
            pygame.display.update(surface.get_rect())
        clock.tick(fps)
    # Final position will be drawn by main loop

def main():
    global score_1, score_2, screen
    board = create_board()
    game_over = False
    turn = 1
    selected_col = None
    hover_y = None
    winner = None
    running = True
    btn_rect = None

    while running:
        btn_rect = draw_board(board, selected_col, hover_y=hover_y)
        _, _, squaresize, radius, offset_x, offset_y = get_sizes()
        if game_over:
            msg = f"{'Rouge' if winner == 1 else 'Bleu'} gagne !" if winner else "Match nul !"
            text = small_font.render(msg, True, (0, 200, 0))
            screen.blit(text, (offset_x + squaresize*COLS//2 - text.get_width()//2, offset_y + squaresize*ROWS//2 - text.get_height()//2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                _, _, squaresize, radius, offset_x, offset_y = get_sizes()
                # Afficher le token au-dessus de la colonne survolée (au-dessus du plateau)
                if offset_x <= mx < offset_x + squaresize*COLS:
                    selected_col = int((mx - offset_x) // squaresize)
                    hover_y = offset_y - squaresize // 2  # Token au-dessus du plateau
                else:
                    selected_col = None
                    hover_y = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                _, _, squaresize, radius, offset_x, offset_y = get_sizes()
                if btn_rect and btn_rect.collidepoint(mx, my):
                    board = create_board()
                    game_over = False
                    turn = 1
                    winner = None
                    continue
                if game_over:
                    continue
                # Allow clicking anywhere in the board area (not just the top row)
                if offset_x <= mx < offset_x + squaresize*COLS and offset_y <= my < offset_y + squaresize*ROWS:
                    col = int((mx - offset_x) // squaresize)
                    if 0 <= col < COLS and is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        animate_drop(board, col, row, turn, squaresize, radius, offset_x, offset_y)
                        drop_piece(board, row, col, turn)
                        if winning_move(board, turn):
                            winner = turn
                            game_over = True
                            if turn == 1:
                                score_1 += 1
                            else:
                                score_2 += 1
                        elif is_full(board):
                            winner = None
                            game_over = True
                        turn = 2 if turn == 1 else 1
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
    sys.exit()