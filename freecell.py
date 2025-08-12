import pygame
import random
import sys
import time

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# --- Pygame Freecell Implementation ---

CARD_WIDTH, CARD_HEIGHT = 80, 120
MARGIN = 20
TABLEAU_GAP = 30
FREECELL_GAP = 20
FOUNDATION_GAP = 20
BG_COLOR = (0, 120, 0)
CARD_COLOR = (255, 255, 255)
CARD_BORDER = (0, 0, 0)
SELECTED_COLOR = (255, 215, 0)
FONT_COLOR = (0, 0, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# Add new constants for small foundation piles and undo button
FOUNDATION_WIDTH = 48
FOUNDATION_HEIGHT = 72
UNDO_BTN_SIZE = 48
UNDO_BTN_MARGIN = 10

BASE_SCREEN_WIDTH = MARGIN*2 + 8*(CARD_WIDTH+TABLEAU_GAP)-TABLEAU_GAP
BASE_SCREEN_HEIGHT = 700

pygame.init()
FONT = pygame.font.SysFont('arial', 24)
SMALL_FONT = pygame.font.SysFont('arial', 18)

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = RANKS.index(rank)
    def __str__(self):
        return f'{self.rank}{self.suit}'
    def __repr__(self):
        return str(self)

def create_deck():
    return [Card(s, r) for s in SUITS for r in RANKS]

def shuffle_deck(deck):
    random.shuffle(deck)

class FreecellGame:
    def __init__(self):
        self.deck = create_deck()
        shuffle_deck(self.deck)
        self.freecells = [None for _ in range(5)]
        self.foundations = {suit: [] for suit in SUITS}
        self.tableau = [[] for _ in range(8)]
        self.deal_cards()
    def deal_cards(self):
        for i, card in enumerate(self.deck):
            self.tableau[i % 8].append(card)
    def display(self):
        print('\nFreecells:', [str(c) if c else '  ' for c in self.freecells])
        print('Foundations:', {s: (str(p[-1]) if p else '--') for s, p in self.foundations.items()})
        print('Tableau:')
        max_len = max(len(col) for col in self.tableau)
        for i in range(max_len):
            row = []
            for col in self.tableau:
                row.append(str(col[i]) if i < len(col) else '   ')
            print(' '.join(row))
    def move_tableau_to_freecell(self, t_col, f_idx):
        if self.freecells[f_idx] is not None:
            print('Freecell not empty!')
            return False
        if not self.tableau[t_col]:
            print('Tableau column empty!')
            return False
        self.freecells[f_idx] = self.tableau[t_col].pop()
        return True
    def move_freecell_to_tableau(self, f_idx, t_col):
        card = self.freecells[f_idx]
        if card is None:
            print('Freecell empty!')
            return False
        if not self.tableau[t_col]:
            self.tableau[t_col].append(card)
            self.freecells[f_idx] = None
            return True
        top = self.tableau[t_col][-1]
        if top.suit in ['♠', '♣']:
            valid = card.suit in ['♥', '♦']
        else:
            valid = card.suit in ['♠', '♣']
        if valid and card.value == top.value - 1:
            self.tableau[t_col].append(card)
            self.freecells[f_idx] = None
            return True
        print('Invalid move!')
        return False
    def move_tableau_to_tableau(self, from_col, to_col):
        if not self.tableau[from_col]:
            print('Source tableau empty!')
            return False
        card = self.tableau[from_col][-1]
        if not self.tableau[to_col]:
            self.tableau[to_col].append(self.tableau[from_col].pop())
            return True
        top = self.tableau[to_col][-1]
        if top.suit in ['♠', '♣']:
            valid = card.suit in ['♥', '♦']
        else:
            valid = card.suit in ['♠', '♣']
        if valid and card.value == top.value - 1:
            self.tableau[to_col].append(self.tableau[from_col].pop())
            return True
        print('Invalid move!')
        return False
    def move_tableau_to_foundation(self, t_col):
        if not self.tableau[t_col]:
            print('Tableau column empty!')
            return False
        card = self.tableau[t_col][-1]
        foundation = self.foundations[card.suit]
        if (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1):
            self.foundations[card.suit].append(self.tableau[t_col].pop())
            return True
        print('Invalid move to foundation!')
        return False
    def move_freecell_to_foundation(self, f_idx):
        card = self.freecells[f_idx]
        if card is None:
            print('Freecell empty!')
            return False
        foundation = self.foundations[card.suit]
        if (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1):
            self.foundations[card.suit].append(card)
            self.freecells[f_idx] = None
            return True
        print('Invalid move to foundation!')
        return False
    def is_won(self):
        return all(len(pile) == 13 for pile in self.foundations.values())
    def play(self):
        print('Welcome to Freecell (5 free cells)!')
        while True:
            self.display()
            if self.is_won():
                print('Congratulations! You won!')
                break
            print('\nCommands:')
            print('  tf <tableau> <freecell>   (tableau to freecell)')
            print('  ft <freecell> <tableau>   (freecell to tableau)')
            print('  tt <from> <to>            (tableau to tableau)')
            print('  tfnd <tableau>            (tableau to foundation)')
            print('  ffnd <freecell>           (freecell to foundation)')
            print('  q                        (quit)')
            cmd = input('Enter command: ').strip().split()
            if not cmd:
                continue
            if cmd[0] == 'q':
                print('Goodbye!')
                break
            try:
                if cmd[0] == 'tf':
                    t, f = int(cmd[1]), int(cmd[2])
                    self.move_tableau_to_freecell(t, f)
                elif cmd[0] == 'ft':
                    f, t = int(cmd[1]), int(cmd[2])
                    self.move_freecell_to_tableau(f, t)
                elif cmd[0] == 'tt':
                    f, t = int(cmd[1]), int(cmd[2])
                    self.move_tableau_to_tableau(f, t)
                elif cmd[0] == 'tfnd':
                    t = int(cmd[1])
                    self.move_tableau_to_foundation(t)
                elif cmd[0] == 'ffnd':
                    f = int(cmd[1])
                    self.move_freecell_to_foundation(f)
                else:
                    print('Unknown command!')
            except (IndexError, ValueError):
                print('Invalid input!')

class PygameCard(Card):
    font_cache = {}
    def __init__(self, suit, rank):
        super().__init__(suit, rank)
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.selected = False

    def get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.SysFont('arial', size)
        return self.font_cache[size]

    def draw(self, surface, pos, selected=False, small=False, hovered=False, scale=1.0):
        border_radius = int((12 if not small else 8) * scale)
        if small:
            rect = pygame.Rect(pos[0], pos[1], int(FOUNDATION_WIDTH*scale), int(FOUNDATION_HEIGHT*scale))
        else:
            self.rect.topleft = pos
            rect = pygame.Rect(pos[0], pos[1], int(CARD_WIDTH*scale), int(CARD_HEIGHT*scale))
        if hovered or selected:
            color = (255, 255, 180)
        else:
            color = CARD_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=border_radius)
        pygame.draw.rect(surface, CARD_BORDER, rect, 2, border_radius=border_radius)
        # Dynamically scale font
        font_size = int((18 if small else 24) * scale)
        font = self.get_font(font_size)
        text_color = RED if self.suit in ['♥', '♦'] else BLACK
        text = font.render(str(self), True, text_color)
        text_pos = (rect.x + int(4*scale), rect.y + int(4*scale)) if small else (rect.x + int(10*scale), rect.y + int(10*scale))
        surface.blit(text, text_pos)
        # Mirrored text
        text_rev = font.render(str(self), True, text_color)
        if small:
            rev_x = rect.right - text_rev.get_width() - int(4*scale)
            rev_y = rect.bottom - text_rev.get_height() - int(4*scale)
        else:
            rev_x = rect.right - text_rev.get_width() - int(10*scale)
            rev_y = rect.bottom - text_rev.get_height() - int(10*scale)
        text_rev_img = pygame.transform.rotate(text_rev, 180)
        surface.blit(text_rev_img, (rev_x, rev_y))

class PygameFreecellGame(FreecellGame):
    def __init__(self):
        self.deck = [PygameCard(s, r) for s in SUITS for r in RANKS]
        shuffle_deck(self.deck)
        self.freecells = [None for _ in range(5)]
        self.foundations = {suit: [] for suit in SUITS}
        self.tableau = [[] for _ in range(8)]
        self.deal_cards()
        self.selected = None  # (zone, idx, card)
        self.running = True
        self.win = False
        self.move_history = []  # For undo
        # Place undo and restart buttons at bottom right
        screen_width = MARGIN*2 + 8*(CARD_WIDTH+TABLEAU_GAP)-TABLEAU_GAP
        screen_height = 700
        self.undo_btn_rect = pygame.Rect(
            screen_width - UNDO_BTN_SIZE*2 - UNDO_BTN_MARGIN*2,
            screen_height - UNDO_BTN_SIZE - UNDO_BTN_MARGIN,
            UNDO_BTN_SIZE,
            UNDO_BTN_SIZE
        )
        self.restart_btn_rect = pygame.Rect(
            screen_width - UNDO_BTN_SIZE - UNDO_BTN_MARGIN,
            screen_height - UNDO_BTN_SIZE - UNDO_BTN_MARGIN,
            UNDO_BTN_SIZE,
            UNDO_BTN_SIZE
        )
        self.animations = []  # List of (card, start_pos, end_pos, on_complete)
        self.animating = False
        self.animating_card_info = None  # (zone, idx) of card being animated
        self.base_card_width = CARD_WIDTH
        self.base_card_height = CARD_HEIGHT
        self.base_margin = MARGIN
        self.base_tableau_gap = TABLEAU_GAP
        self.base_freecell_gap = FREECELL_GAP
        self.base_foundation_gap = FOUNDATION_GAP
        self.base_foundation_width = FOUNDATION_WIDTH
        self.base_foundation_height = FOUNDATION_HEIGHT
        self.base_undo_btn_size = UNDO_BTN_SIZE
        self.base_undo_btn_margin = UNDO_BTN_MARGIN
        self.base_screen_width = BASE_SCREEN_WIDTH
        self.base_screen_height = BASE_SCREEN_HEIGHT
    def draw(self, screen, anim_card=None):
        mouse_pos = pygame.mouse.get_pos()
        scale = self.get_scale(screen)
        # Dynamically scale all constants
        CARD_W = int(self.base_card_width * scale)
        CARD_H = int(self.base_card_height * scale)
        MARG = int(self.base_margin * scale)
        TABLEAU_G = int(self.base_tableau_gap * scale)
        FREECELL_G = int(self.base_freecell_gap * scale)
        FOUNDATION_G = int(self.base_foundation_gap * scale)
        FOUNDATION_W = int(self.base_foundation_width * scale)
        FOUNDATION_H = int(self.base_foundation_height * scale)
        UNDO_SIZE = int(self.base_undo_btn_size * scale)
        UNDO_MARGIN = int(self.base_undo_btn_margin * scale)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        screen.fill(BG_COLOR)
        # Store hitboxes for click detection (freecells and tableau tops)
        self._last_hover_boxes = []
        # Draw freecells
        for i in range(5):
            x = int(self.base_margin * scale) + i * (int(self.base_card_width * scale) + int(self.base_freecell_gap * scale))
            y = int(self.base_margin * scale)
            rect = pygame.Rect(x, y, int(self.base_card_width * scale), int(self.base_card_height * scale))
            pygame.draw.rect(screen, CARD_COLOR, rect, 2, border_radius=int(12*scale))
            card = self.freecells[i]
            if self.animating_card_info == ('freecell', i):
                continue
            hovered = card and rect.collidepoint(mouse_pos)
            if card:
                card.draw(screen, (x, y), self.selected == ('freecell', i, card), hovered=hovered, small=False, scale=scale)
                self._last_hover_boxes.append(('freecell', i, card, rect))
        # Draw small foundations (move them closer to the right edge)
        foundation_area_width = 4 * (FOUNDATION_W + FOUNDATION_G) - FOUNDATION_G
        foundation_start_x = screen_width - MARG - foundation_area_width
        for i, suit in enumerate(SUITS):
            x = foundation_start_x + i * (FOUNDATION_W + FOUNDATION_G)
            y = MARG + int(10*scale)
            rect = pygame.Rect(x, y, FOUNDATION_W, FOUNDATION_H)
            pygame.draw.rect(screen, CARD_COLOR, rect, 2, border_radius=int(8*scale))
            pile = self.foundations[suit]
            if pile and self.animating_card_info == ('foundation', i):
                continue
            if pile:
                pile[-1].draw(screen, (x, y), small=True, scale=scale)
            suit_text = SMALL_FONT.render(suit, True, BLACK)
            screen.blit(suit_text, (x + FOUNDATION_W//2 - 8, y + FOUNDATION_H - 20))
        # Draw tableau
        for col in range(8):
            x = int(self.base_margin * scale) + col * (int(self.base_card_width * scale) + int(self.base_tableau_gap * scale))
            y = int(self.base_margin * scale) + int(self.base_card_height * scale) + int(60*scale)
            for row, card in enumerate(self.tableau[col]):
                if self.animating_card_info == ('tableau', (col, row)):
                    continue
                offset_y = y + row * int(30*scale)
                rect = pygame.Rect(x, offset_y, int(self.base_card_width * scale), int(self.base_card_height * scale))
                hovered = card and rect.collidepoint(mouse_pos) and row == len(self.tableau[col])-1
                card.draw(screen, (x, offset_y), self.selected == ('tableau', col, card) and row == len(self.tableau[col])-1, hovered=hovered, small=False, scale=scale)
                if row == len(self.tableau[col])-1:
                    self._last_hover_boxes.append(('tableau', col, card, rect))
            if not self.tableau[col]:
                rect = pygame.Rect(x, y, int(self.base_card_width * scale), int(self.base_card_height * scale))
                pygame.draw.rect(screen, CARD_COLOR, rect, 2, border_radius=int(12*scale))
        # Draw undo button (circle arrow) at bottom right
        undo_btn_rect = pygame.Rect(
            screen_width - UNDO_SIZE*2 - UNDO_MARGIN*2,
            screen_height - UNDO_SIZE - UNDO_MARGIN,
            UNDO_SIZE,
            UNDO_SIZE
        )
        restart_btn_rect = pygame.Rect(
            screen_width - UNDO_SIZE - UNDO_MARGIN,
            screen_height - UNDO_SIZE - UNDO_MARGIN,
            UNDO_SIZE,
            UNDO_SIZE
        )
        self.undo_btn_rect = undo_btn_rect
        self.restart_btn_rect = restart_btn_rect
        pygame.draw.circle(screen, (220,220,220), undo_btn_rect.center, UNDO_SIZE//2)
        pygame.draw.circle(screen, (100,100,100), undo_btn_rect.center, UNDO_SIZE//2, 2)
        cx, cy = undo_btn_rect.center
        r = UNDO_SIZE//3
        pygame.draw.arc(screen, (60,60,60), (cx-r, cy-r, 2*r, 2*r), 0.7, 2.5, 4)
        arrow_tip = (int(cx + r*0.9), int(cy - r*0.2))
        pygame.draw.polygon(screen, (60,60,60), [arrow_tip, (arrow_tip[0]-int(10*scale), arrow_tip[1]-int(5*scale)), (arrow_tip[0]-int(5*scale), arrow_tip[1]+int(10*scale))])
        # Draw restart button (circular arrow with dot) at bottom right
        pygame.draw.circle(screen, (220,220,220), restart_btn_rect.center, UNDO_SIZE//2)
        pygame.draw.circle(screen, (100,100,100), restart_btn_rect.center, UNDO_SIZE//2, 2)
        cx, cy = restart_btn_rect.center
        r = UNDO_SIZE//3
        pygame.draw.arc(screen, (60,60,60), (cx-r, cy-r, 2*r, 2*r), 0.7, 2.5, 4)
        pygame.draw.circle(screen, (60,60,60), (int(cx + r*0.7), int(cy)), int(5*scale))
        if self.win:
            win_text = FONT.render('Congratulations! You won!', True, (255,255,0))
            screen.blit(win_text, (MARG, 10 + CARD_HEIGHT + 8*30))
            restart_text = SMALL_FONT.render('Press R to restart', True, (255,255,255))
            screen.blit(restart_text, (MARG, 40 + CARD_HEIGHT + 8*30))
        if anim_card is not None:
            card, pos = anim_card
            card.draw(screen, pos, scale=scale)
        pygame.display.flip()
        # Draw the back arrow on top of everything
        draw_back_arrow(screen)

    def get_scale(self, screen):
        w, h = screen.get_width(), screen.get_height()
        scale_x = w / self.base_screen_width
        scale_y = h / self.base_screen_height
        return min(scale_x, scale_y)

    def process_animations(self, screen):
        if not self.animations:
            self.animating = False
            self.animating_card_info = None
            self.auto_move_to_foundation(screen)
            return
        card, start, end, on_complete, from_zone, from_idx = self.animations[0]
        duration = 0.5  # seconds for animation
        fps = 60
        frames = int(duration * fps)
        clock = pygame.time.Clock()
        for i in range(1, frames+1):
            t = i / frames
            x = int(start[0] + (end[0] - start[0]) * t)
            y = int(start[1] + (end[1] - start[1]) * t)
            self.draw(screen, anim_card=(card, (x, y)))
            # --- Use present_surface callback if set ---
            if callable(globals().get("present_surface", None)):
                globals()["present_surface"](screen)
            else:
                pygame.display.flip()
            clock.tick(fps)
        on_complete()
        self.animations.pop(0)
        self.animating = False
        self.animating_card_info = None
        self.auto_move_to_foundation(screen)

    def save_state(self):
        # Save a deep copy of the current state for undo
        import copy
        self.move_history.append((copy.deepcopy(self.freecells), copy.deepcopy(self.foundations), copy.deepcopy(self.tableau)))
        if len(self.move_history) > 100:
            self.move_history.pop(0)

    def undo(self):
        if self.move_history:
            self.freecells, self.foundations, self.tableau = self.move_history.pop()
            self.win = False

    def restart(self):
        self.__init__()

    def check_win(self):
        if self.is_won():
            self.win = True

    def get_card_at_pos(self, pos):
        # Freecells
        for i, card in enumerate(self.freecells):
            x = MARGIN + i * (CARD_WIDTH + FREECELL_GAP)
            y = MARGIN
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if card and rect.collidepoint(pos):
                return ('freecell', i, card)
        # Tableau
        for col in range(8):
            x = MARGIN + col * (CARD_WIDTH + TABLEAU_GAP)
            y = MARGIN + CARD_HEIGHT + 60
            for row, card in enumerate(self.tableau[col]):
                offset_y = y + row * 30
                rect = pygame.Rect(x, offset_y, CARD_WIDTH, CARD_HEIGHT)
                if rect.collidepoint(pos) and row == len(self.tableau[col])-1:
                    return ('tableau', col, card)
        return None
    def get_foundation_at_pos(self, pos):
        for i, suit in enumerate(SUITS):
            x = MARGIN + (i + 5) * (CARD_WIDTH + FOUNDATION_GAP)
            y = MARGIN + 10
            rect = pygame.Rect(x, y, FOUNDATION_WIDTH, FOUNDATION_HEIGHT)
            if rect.collidepoint(pos):
                return suit
        return None
    def get_freecell_at_pos(self, pos):
        for i in range(5):
            x = MARGIN + i * (CARD_WIDTH + FREECELL_GAP)
            y = MARGIN
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos):
                return i
        return None
    def get_tableau_at_pos(self, pos):
        for col in range(8):
            x = MARGIN + col * (CARD_WIDTH + TABLEAU_GAP)
            y = MARGIN + CARD_HEIGHT + 60
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT + 30*max(0, len(self.tableau[col])-1))
            if rect.collidepoint(pos):
                return col
        return None
    def handle_click(self, pos):
        if self.win or self.animating:
            return
        # Undo button (bottom right)
        if self.undo_btn_rect.collidepoint(pos):
            self.undo()
            return
        # Restart button (bottom right)
        if self.restart_btn_rect.collidepoint(pos):
            self.restart()
            return
        # Use the same hitboxes as hover for click detection
        for zone, idx, card, rect in getattr(self, '_last_hover_boxes', []):
            if rect.collidepoint(pos):
                if zone == 'freecell':
                    i = idx
                    self.save_state()
                    suit = card.suit
                    foundation = self.foundations[suit]
                    can_move_to_foundation = (
                        (not foundation and card.rank == 'A') or
                        (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)
                    )
                    if can_move_to_foundation:
                        def do_move(i=i, suit=suit, card=card):
                            self.foundations[suit].append(self.freecells[i])
                            self.freecells[i] = None
                            self.check_win()
                        self.animate_move(
                            card,
                            'freecell', i,
                            'foundation', SUITS.index(suit),
                            do_move
                        )
                        return
                    for tcol in range(8):
                        if self.move_freecell_to_tableau(i, tcol):
                            return
                    return
                elif zone == 'tableau':
                    col = idx
                    row = len(self.tableau[col]) - 1
                    self.save_state()
                    suit = card.suit
                    foundation = self.foundations[suit]
                    can_move_to_foundation = (
                        (not foundation and card.rank == 'A') or
                        (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)
                    )
                    if can_move_to_foundation:
                        def do_move(col=col, suit=suit, card=card):
                            self.foundations[suit].append(self.tableau[col].pop())
                            self.check_win()
                        self.animate_move(
                            card,
                            'tableau', (col, row),
                            'foundation', SUITS.index(suit),
                            do_move
                        )
                        return
                    for tcol in range(8):
                        if tcol != col and self.can_move_tableau_to_tableau(col, tcol):
                            def do_move(col=col, tcol=tcol, card=card):
                                self.tableau[tcol].append(self.tableau[col].pop())
                            self.animate_move(
                                card,
                                'tableau', (col, row),
                                'tableau', (tcol, len(self.tableau[tcol])),
                                do_move
                            )
                            return
                    for fidx in range(5):
                        if self.freecells[fidx] is None:
                            def do_move(col=col, fidx=fidx, card=card):
                                self.freecells[fidx] = self.tableau[col].pop()
                            self.animate_move(
                                card,
                                'tableau', (col, row),
                                'freecell', fidx,
                                do_move
                            )
                            return
                    return
        # At the end of handle_click, after any move, trigger auto move
        self.auto_move_to_foundation(pygame.display.get_surface())
        return

    def animate_move(self, card, from_zone, from_idx, to_zone, to_idx, on_complete):
        start = self.get_card_screen_pos(from_zone, from_idx)
        end = self.get_card_screen_pos(to_zone, to_idx)
        self.animations.append((card, start, end, on_complete, from_zone, from_idx))
        self.animating = True
        self.animating_card_info = (from_zone, from_idx)

    def get_card_screen_pos(self, zone, idx):
        # Returns the (x, y) pixel position for a card in a given zone
        if zone == 'freecell':
            x = MARGIN + idx * (CARD_WIDTH + FREECELL_GAP)
            y = MARGIN
            return (x, y)
        elif zone == 'foundation':
            x = MARGIN + (idx + 5) * (FOUNDATION_WIDTH + FOUNDATION_GAP)
            y = MARGIN + 10
            return (x, y)
        elif zone == 'tableau':
            col, row = idx
            x = MARGIN + col * (CARD_WIDTH + TABLEAU_GAP)
            y = MARGIN + CARD_HEIGHT + 60 + row * 30
            return (x, y)
        return (0, 0)

    def can_move_tableau_to_tableau(self, from_col, to_col):
        if not self.tableau[from_col]:
            return False
        card = self.tableau[from_col][-1]
        if not self.tableau[to_col]:
            return True
        top = self.tableau[to_col][-1]
        if top.suit in ['♠', '♣']:
            valid = card.suit in ['♥', '♦']
        else:
            valid = card.suit in ['♠', '♣']
        return valid and card.value == top.value - 1

    def can_move_tableau_to_foundation(self, t_col):
        if not self.tableau[t_col]:
            return False
        card = self.tableau[t_col][-1]
        foundation = self.foundations[card.suit]
        return (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)

    def can_move_freecell_to_tableau(self, f_idx, t_col):
        card = self.freecells[f_idx]
        if card is None:
            return False
        if not self.tableau[t_col]:
            return True
        top = self.tableau[t_col][-1]
        if top.suit in ['♠', '♣']:
            valid = card.suit in ['♥', '♦']
        else:
            valid = card.suit in ['♠', '♣']
        return valid and card.value == top.value - 1

    def can_move_freecell_to_foundation(self, f_idx):
        card = self.freecells[f_idx]
        if card is None:
            return False
        foundation = self.foundations[card.suit]
        return (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)

    def auto_move_to_foundation(self, screen=None):
        while True:
            moved = False
            # Check tableau tops
            for col in range(8):
                if self.tableau[col]:
                    card = self.tableau[col][-1]
                    suit = card.suit
                    foundation = self.foundations[suit]
                    can_move_to_foundation = (
                        (not foundation and card.rank == 'A') or
                        (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)
                    )
                    if can_move_to_foundation:
                        row = len(self.tableau[col]) - 1
                        def do_move(col=col, suit=suit, card=card):
                            self.foundations[suit].append(self.tableau[col].pop())
                            self.check_win()
                        self.animate_move(
                            card,
                            'tableau', (col, row),
                            'foundation', SUITS.index(suit),
                            do_move
                        )
                        moved = True
                        break  # Only one move per call
            if moved and screen:
                while self.animations:
                    self.process_animations(screen)
                continue
            if moved:
                continue
            # Check freecells
            for i, card in enumerate(self.freecells):
                if card:
                    suit = card.suit
                    foundation = self.foundations[suit]
                    can_move_to_foundation = (
                        (not foundation and card.rank == 'A') or
                        (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1)
                    )
                    if can_move_to_foundation:
                        def do_move(i=i, suit=suit, card=card):
                            self.foundations[suit].append(self.freecells[i])
                            self.freecells[i] = None
                            self.check_win()
                        self.animate_move(
                            card,
                            'freecell', i,
                            'foundation', SUITS.index(suit),
                            do_move
                        )
                        moved = True
                        break  # Only one move per call
            if moved and screen:
                while self.animations:
                    self.process_animations(screen)
                continue
            if not moved:
                break

def draw_back_arrow(surface):
    # Draw a back arrow at the top left (same as launcher)
    arrow_rect = pygame.Rect(18, 18, 48, 48)
    pygame.draw.circle(surface, (230, 230, 230), arrow_rect.center, 24)
    pygame.draw.circle(surface, (180, 180, 180), arrow_rect.center, 24, 2)
    pts = [
        (arrow_rect.x + 32, arrow_rect.y + 12),
        (arrow_rect.x + 16, arrow_rect.y + 24),
        (arrow_rect.x + 32, arrow_rect.y + 36)
    ]
    pygame.draw.polygon(surface, (60, 60, 60), pts)
    return arrow_rect

def main():
    screen = pygame.display.set_mode((MARGIN*2 + 8*(CARD_WIDTH+TABLEAU_GAP)-TABLEAU_GAP, 700), pygame.RESIZABLE)
    pygame.display.set_caption('Freecell (5 Freecells)')
    game = PygameFreecellGame()
    clock = pygame.time.Clock()
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_p:
                    game.undo()
                elif event.key == pygame.K_ESCAPE:
                    game.running = False
        if game.animations:
            game.process_animations(screen)
        else:
            game.draw(screen)
        fps = clock.get_fps()
        pygame.display.set_caption(f'Freecell (5 Freecells) - FPS: {fps:.1f}')
        clock.tick(60)  # Cap the game loop at 60 FPS
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
    main()
