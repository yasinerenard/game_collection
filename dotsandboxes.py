import pygame

WIDTH, HEIGHT = 600, 500
screen = None

DIFFICULTY_LEVELS = {
    "easy": (5, 5),    # 5x5 grid
    "medium": (10, 10),  # 10x10 grid
    "hard": (15, 15)     # 15x15 grid
}
DOT_RADIUS = 8
LINE_WIDTH = 6
BOX_COLOR = [(220, 60, 60), (60, 120, 220)]
LINE_COLOR = (255, 255, 255)  # White for default lines
PLAYER_LINE_COLOR = [(220, 60, 60), (60, 120, 220)]  # Red, Blue
DOT_COLOR = (230, 230, 230)
BG_COLOR = (30, 40, 60)
FONT = None
SMALL_FONT = None
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for hover

class PygameDotsAndBoxesGame:
    def __init__(self, width, height, surface, difficulty="easy"):
        global FONT, SMALL_FONT
        self.WIDTH, self.HEIGHT = width, height
        self.screen = surface
        FONT = pygame.font.SysFont('arial', 36, bold=True)
        SMALL_FONT = pygame.font.SysFont('arial', 24, bold=True)
        self.difficulty = difficulty
        self.set_difficulty(difficulty)
        self.running = True
        self.restart()
        self.hovered_line = None

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.ROWS, self.COLS = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["easy"])

    def restart(self):
        self.turn = 0  # 0: Player 1, 1: Player 2
        self.lines = {}  # {(r1, c1, r2, c2): owner}
        self.boxes = [[None for _ in range(self.COLS-1)] for _ in range(self.ROWS-1)]
        self.scores = [0, 0]
        self.finished = False

    def resize(self, width, height, surface):
        self.WIDTH, self.HEIGHT = width, height
        self.screen = surface

    def get_grid_rect(self):
        margin = 60
        size = min(self.WIDTH, self.HEIGHT) - 2 * margin
        left = (self.WIDTH - size) // 2
        top = (self.HEIGHT - size) // 2
        return pygame.Rect(left, top, size, size)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        grid_rect = self.get_grid_rect()
        cell = grid_rect.width // (self.COLS-1)
        # Draw all possible lines in white by default, highlight hovered if not drawn yet
        for r in range(self.ROWS):
            for c in range(self.COLS):
                # Horizontal lines
                if c < self.COLS-1:
                    key = (r, c, r, c+1)
                    x1 = grid_rect.left + c * cell
                    y1 = grid_rect.top + r * cell
                    x2 = grid_rect.left + (c+1) * cell
                    y2 = y1
                    if key in self.lines:
                        color = PLAYER_LINE_COLOR[self.lines[key]]
                    elif self.hovered_line == key:
                        color = HIGHLIGHT_COLOR
                    else:
                        color = LINE_COLOR
                    pygame.draw.line(surface, color, (x1, y1), (x2, y2), LINE_WIDTH)
                # Vertical lines
                if r < self.ROWS-1:
                    key = (r, c, r+1, c)
                    x1 = grid_rect.left + c * cell
                    y1 = grid_rect.top + r * cell
                    x2 = x1
                    y2 = grid_rect.top + (r+1) * cell
                    if key in self.lines:
                        color = PLAYER_LINE_COLOR[self.lines[key]]
                    elif self.hovered_line == key:
                        color = HIGHLIGHT_COLOR
                    else:
                        color = LINE_COLOR
                    pygame.draw.line(surface, color, (x1, y1), (x2, y2), LINE_WIDTH)
        # Draw boxes
        for r in range(self.ROWS-1):
            for c in range(self.COLS-1):
                owner = self.boxes[r][c]
                if owner is not None:
                    x = grid_rect.left + c * cell
                    y = grid_rect.top + r * cell
                    # Fill the whole square with the player's color
                    pygame.draw.rect(surface, BOX_COLOR[owner], (x, y, cell, cell))
        # Draw scores and turn
        msg = f"Red: {self.scores[0]}   Blue: {self.scores[1]}"
        text = SMALL_FONT.render(msg, True, (255,255,255))
        surface.blit(text, (self.WIDTH//2 - text.get_width()//2, 20))
        turn_msg = "Red's turn" if self.turn == 0 else "Blue's turn"
        turn_text = SMALL_FONT.render(turn_msg, True, BOX_COLOR[self.turn])
        surface.blit(turn_text, (self.WIDTH//2 - turn_text.get_width()//2, self.HEIGHT - 40))
        # Draw restart button
        self.restart_rect = pygame.Rect(self.WIDTH-140, self.HEIGHT-60, 120, 40)
        pygame.draw.rect(surface, (90,160,255), self.restart_rect, border_radius=12)
        pygame.draw.rect(surface, (30,70,160), self.restart_rect, 2, border_radius=12)
        btn_text = SMALL_FONT.render("Restart", True, (255,255,255))
        surface.blit(btn_text, (self.restart_rect.x + (self.restart_rect.width-btn_text.get_width())//2,
                                self.restart_rect.y + (self.restart_rect.height-btn_text.get_height())//2))
        # Game over
        if self.finished:
            winner = None
            if self.scores[0] > self.scores[1]:
                winner = "Red wins!"
            elif self.scores[1] > self.scores[0]:
                winner = "Blue wins!"
            else:
                winner = "Draw!"
            over_text = FONT.render(winner, True, (0,220,0))
            surface.blit(over_text, (self.WIDTH//2 - over_text.get_width()//2, self.HEIGHT//2 - over_text.get_height()//2))

    def handle_click(self, pos):
        if self.finished:
            return
        # Restart button
        if self.restart_rect.collidepoint(pos):
            self.restart()
            return
        grid_rect = self.get_grid_rect()
        cell = grid_rect.width // (self.COLS-1)
        # Find closest line
        min_dist = 20
        chosen = None
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x = grid_rect.left + c * cell
                y = grid_rect.top + r * cell
                # Horizontal line
                if c < self.COLS-1:
                    nx = grid_rect.left + (c+1) * cell
                    ny = y
                    mx = (x + nx) // 2
                    my = y
                    dist = ((pos[0]-mx)**2 + (pos[1]-my)**2)**0.5
                    key = (r, c, r, c+1)
                    if dist < min_dist and key not in self.lines:
                        chosen = key
                        min_dist = dist
                # Vertical line
                if r < self.ROWS-1:
                    nx = x
                    ny = grid_rect.top + (r+1) * cell
                    mx = x
                    my = (y + ny) // 2
                    dist = ((pos[0]-mx)**2 + (pos[1]-my)**2)**0.5
                    key = (r, c, r+1, c)
                    if dist < min_dist and key not in self.lines:
                        chosen = key
                        min_dist = dist
        if chosen:
            self.lines[chosen] = self.turn
            scored = False
            # Check for completed boxes
            for r in range(self.ROWS-1):
                for c in range(self.COLS-1):
                    if self.boxes[r][c] is None:
                        edges = [
                            (r, c, r, c+1),
                            (r, c, r+1, c),
                            (r+1, c, r+1, c+1),
                            (r, c+1, r+1, c+1)
                        ]
                        if all(e in self.lines for e in edges):
                            self.boxes[r][c] = self.turn
                            self.scores[self.turn] += 1
                            scored = True
                            # Fix the color of all four lines to the player who completed the square
                            for edge in edges:
                                self.lines[edge] = self.turn
            # If no box scored, switch turn
            if not scored:
                self.turn = 1 - self.turn
            # Check for game over
            if all(all(b is not None for b in row) for row in self.boxes):
                self.finished = True

    def handle_mouse_motion(self, pos):
        grid_rect = self.get_grid_rect()
        cell = grid_rect.width // (self.COLS-1)
        min_dist = 20
        hovered = None
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x = grid_rect.left + c * cell
                y = grid_rect.top + r * cell
                # Horizontal line
                if c < self.COLS-1:
                    nx = grid_rect.left + (c+1) * cell
                    ny = y
                    mx = (x + nx) // 2
                    my = y
                    dist = ((pos[0]-mx)**2 + (pos[1]-my)**2)**0.5
                    key = (r, c, r, c+1)
                    if dist < min_dist and key not in self.lines:
                        hovered = key
                        min_dist = dist
                # Vertical line
                if r < self.ROWS-1:
                    nx = x
                    ny = grid_rect.top + (r+1) * cell
                    mx = x
                    my = (y + ny) // 2
                    dist = ((pos[0]-mx)**2 + (pos[1]-my)**2)**0.5
                    key = (r, c, r+1, c)
                    if dist < min_dist and key not in self.lines:
                        hovered = key
                        min_dist = dist
        self.hovered_line = hovered

present_surface = None  # launcher sets this if needed
