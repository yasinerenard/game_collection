import pygame
import sys
import math

# Constants
WIDTH, HEIGHT = 400, 400
LINE_COLOR = (60, 60, 60)
BG_COLOR = (230, 240, 230)
X_COLOR = (220, 60, 60)
O_COLOR = (60, 120, 220)
LINE_WIDTH = 6
CELL_SIZE = WIDTH // 3
ANIM_FRAMES = 18

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tic-Tac-Toe")
font = pygame.font.SysFont('arial', 80, bold=True)
small_font = pygame.font.SysFont('arial', 32, bold=True)

# Global scores
score_X = 0
score_O = 0

def get_board_rect():
    # Compute the centered square area for the board
    min_dim = min(WIDTH, HEIGHT) * 0.85
    size = int(min_dim // 3 * 3)  # multiple of 3
    x = (WIDTH - size) // 2
    y = (HEIGHT - size) // 2
    return pygame.Rect(x, y, size, size)

def draw_board(board):
    screen.fill(BG_COLOR)
    board_rect = get_board_rect()
    cell_size = board_rect.width // 3

    # Draw the board area with rounded corners
    pygame.draw.rect(screen, (255, 255, 255), board_rect, border_radius=32)
    pygame.draw.rect(screen, (200, 210, 200), board_rect, width=6, border_radius=32)

    # Draw grid lines
    for i in range(1, 3):
        # Horizontal lines
        start = (board_rect.left, board_rect.top + i * cell_size)
        end = (board_rect.right, board_rect.top + i * cell_size)
        pygame.draw.line(screen, LINE_COLOR, start, end, LINE_WIDTH)
        # Vertical lines
        start = (board_rect.left + i * cell_size, board_rect.top)
        end = (board_rect.left + i * cell_size, board_rect.bottom)
        pygame.draw.line(screen, LINE_COLOR, start, end, LINE_WIDTH)

    # Draw X and O
    for y in range(3):
        for x in range(3):
            if board[y][x] == 'X':
                draw_cross(x, y, 1.0, board_rect, cell_size)
            elif board[y][x] == 'O':
                draw_circle(x, y, 1.0, board_rect, cell_size)

def draw_cross(cell_x, cell_y, progress=1.0, board_rect=None, cell_size=None):
    # Draw an animated cross in cell (cell_x, cell_y)
    if board_rect is None or cell_size is None:
        board_rect = get_board_rect()
        cell_size = board_rect.width // 3
    cx = board_rect.left + cell_x * cell_size + cell_size // 2
    cy = board_rect.top + cell_y * cell_size + cell_size // 2
    size = cell_size // 2 - 18
    # Two lines: from top-left to bottom-right, and top-right to bottom-left
    for i in range(2):
        angle1 = math.pi/4 if i == 0 else 3*math.pi/4
        angle2 = 5*math.pi/4 if i == 0 else 7*math.pi/4
        x1 = cx + size * math.cos(angle1)
        y1 = cy + size * math.sin(angle1)
        x2 = cx + size * math.cos(angle2)
        y2 = cy + size * math.sin(angle2)
        # Animate line drawing
        x_end = x1 + (x2 - x1) * progress
        y_end = y1 + (y2 - y1) * progress
        pygame.draw.line(screen, X_COLOR, (x1, y1), (x_end, y_end), 10)
        # Only draw the moving endpoint for animation, not both ends
        if progress < 1.0:
            pygame.draw.circle(screen, X_COLOR, (int(x_end), int(y_end)), 5)
        # Do not draw static endpoints

def draw_circle(cell_x, cell_y, progress=1.0, board_rect=None, cell_size=None):
    # Draw an animated circle in cell (cell_x, cell_y)
    if board_rect is None or cell_size is None:
        board_rect = get_board_rect()
        cell_size = board_rect.width // 3
    cx = board_rect.left + cell_x * cell_size + cell_size // 2
    cy = board_rect.top + cell_y * cell_size + cell_size // 2
    radius = cell_size // 2 - 18
    start_angle = -math.pi / 2
    end_angle = start_angle + 2 * math.pi * progress
    rect = pygame.Rect(cx - radius, cy - radius, 2 * radius, 2 * radius)
    # Draw arc for animation
    pygame.draw.arc(screen, O_COLOR, rect, start_angle, end_angle, 10)
    # Only draw the moving endpoint for animation, not both ends
    if progress < 1.0 and progress > 0.01:
        x_end = cx + radius * math.cos(end_angle)
        y_end = cy + radius * math.sin(end_angle)
        pygame.draw.circle(screen, O_COLOR, (int(x_end), int(y_end)), 5)
    # Do not draw static start point

def check_winner(board):
    # Rows, columns, diagonals
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '':
            return board[i][0], ((0, i), (2, i))
        if board[0][i] == board[1][i] == board[2][i] != '':
            return board[0][i], ((i, 0), (i, 2))
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0], ((0, 0), (2, 2))
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2], ((2, 0), (0, 2))
    return None, None

def is_full(board):
    return all(board[y][x] != '' for y in range(3) for x in range(3))

def animate_win_line(start_cell, end_cell, persist=False):
    # Animate a line from start_cell to end_cell (cell coordinates)
    board_rect = get_board_rect()
    cell_size = board_rect.width // 3
    start_px = (board_rect.left + start_cell[0] * cell_size + cell_size // 2,
                board_rect.top + start_cell[1] * cell_size + cell_size // 2)
    end_px = (board_rect.left + end_cell[0] * cell_size + cell_size // 2,
              board_rect.top + end_cell[1] * cell_size + cell_size // 2)
    duration = 0.5  # seconds
    fps = 60
    frames = int(duration * fps)
    for i in range(1, frames + 1):
        t = i / frames
        x = int(start_px[0] + (end_px[0] - start_px[0]) * t)
        y = int(start_px[1] + (end_px[1] - start_px[1]) * t)
        draw_board(current_board)
        draw_scores()
        draw_restart_button()
        pygame.draw.line(screen, (0, 180, 0), start_px, (x, y), 10)
        pygame.display.flip()
        pygame.time.Clock().tick(fps)
    if persist:
        draw_board(current_board)
        draw_scores()
        draw_restart_button()
        pygame.draw.line(screen, (0, 180, 0), start_px, end_px, 10)
        pygame.display.flip()

def animate_symbol(board, cell_x, cell_y, symbol):
    board_rect = get_board_rect()
    cell_size = board_rect.width // 3
    for frame in range(1, ANIM_FRAMES + 1):
        progress = frame / ANIM_FRAMES
        draw_board(board)
        draw_scores()
        draw_restart_button()
        if symbol == 'X':
            draw_cross(cell_x, cell_y, progress, board_rect, cell_size)
        elif symbol == 'O':
            draw_circle(cell_x, cell_y, progress, board_rect, cell_size)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def draw_restart_button():
    # Draw a "Restart" button at the bottom right
    btn_font = pygame.font.SysFont('arial', 26, bold=True)
    text = btn_font.render("Recommencer", True, (255,255,255))
    padding = 18
    btn_w, btn_h = text.get_width() + 32, text.get_height() + 16
    rect = pygame.Rect(WIDTH - btn_w - padding, HEIGHT - btn_h - padding, btn_w, btn_h)
    pygame.draw.rect(screen, (60, 120, 220), rect, border_radius=16)
    pygame.draw.rect(screen, (30, 70, 160), rect, width=3, border_radius=16)
    screen.blit(text, (rect.x + 16, rect.y + 8))
    return rect

def draw_scores():
    # Display X (red) and O (blue) scores at the top
    score_font = pygame.font.SysFont('arial', 32, bold=True)
    x_text = score_font.render(f"X : {score_X}", True, X_COLOR)
    o_text = score_font.render(f"O : {score_O}", True, O_COLOR)
    screen.blit(x_text, (32, 18))
    screen.blit(o_text, (WIDTH - o_text.get_width() - 32, 18))

def main():
    global current_board, score_X, score_O
    board = [['' for _ in range(3)] for _ in range(3)]
    current_board = board
    turn = 'X'
    running = True
    winner = None
    win_line = None
    animated = False

    global WIDTH, HEIGHT, screen

    while running:
        draw_board(board)
        draw_scores()
        btn_rect = draw_restart_button()
        if winner:
            if win_line and not animated:
                animate_win_line(*win_line, persist=True)
                animated = True
            elif win_line and animated:
                # Always redraw the win line after animation
                board_rect = get_board_rect()
                cell_size = board_rect.width // 3
                start_cell, end_cell = win_line
                start_px = (board_rect.left + start_cell[0] * cell_size + cell_size // 2,
                            board_rect.top + start_cell[1] * cell_size + cell_size // 2)
                end_px = (board_rect.left + end_cell[0] * cell_size + cell_size // 2,
                          board_rect.top + end_cell[1] * cell_size + cell_size // 2)
                pygame.draw.line(screen, (0, 180, 0), start_px, end_px, 10)
            msg = f"{winner} gagne !" if winner in ['X', 'O'] else "Match nul !"
            text = small_font.render(msg, True, (0, 128, 0))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN and winner:
                if event.key == pygame.K_r:
                    board = [['' for _ in range(3)] for _ in range(3)]
                    current_board = board
                    turn = 'X'
                    winner = None
                    win_line = None
                    animated = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_rect.collidepoint(mx, my):
                    board = [['' for _ in range(3)] for _ in range(3)]
                    current_board = board
                    turn = 'X'
                    winner = None
                    win_line = None
                    animated = False
                    continue
                if not winner:
                    board_rect = get_board_rect()
                    cell_size = board_rect.width // 3
                    # Check if click is inside the board
                    if board_rect.collidepoint(mx, my):
                        x = (mx - board_rect.left) // cell_size
                        y = (my - board_rect.top) // cell_size
                        if 0 <= x < 3 and 0 <= y < 3 and board[y][x] == '':
                            animate_symbol(board, x, y, turn)
                            board[y][x] = turn
                            w, line = check_winner(board)
                            if w:
                                winner = w
                                win_line = line
                                animated = False
                                if w == 'X':
                                    score_X += 1
                                elif w == 'O':
                                    score_O += 1
                            elif is_full(board):
                                winner = 'Draw'
                                win_line = None
                                animated = False
                            turn = 'O' if turn == 'X' else 'X'
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
