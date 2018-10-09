import os
import sys
import time
from msvcrt import getch
from msvcrt import kbhit
from colorama import init
from colorama import Fore, Back, Style

init()  # for colors

BlackTokenColor = Fore.RED
WhiteTokenColor = Fore.WHITE

TokenTypeNameList = {'K': 'K',
                     'Q': 'Q',
                     'B': 'B',
                     'N': 'N',
                     'R': 'R',
                     'WP': 'P',
                     'BP': 'P'
                     }

PawnPromotionOptions = ['Q', 'N', 'B', 'R']

HighlightCells = []
HighlightRules = {'K': [[(-1, 0)], [(-1, 1)], [(0, 1)], [(1, 1)], [(1, 0)], [(1, -1)], [(0, -1)], [(-1, -1)]],
                  'Q': [[(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                        [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                        [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                        [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                        [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                        [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                        [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                        [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]],
                  'B': [[(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)],
                        [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                        [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                        [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]],
                  'N': [[(-2, 1)], [(-1, 2)], [(1, 2)], [(2, 1)], [(2, -1)], [(1, -2)], [(-1, -2)], [(-2, -1)]],
                  'R': [[(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                        [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                        [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                        [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)]],
                  'WP': [[(0, 1), (0, 2)], [(-1, 1)], [(1, 1)]],
                  'BP': [[(0, -1), (0, -2)], [(-1, -1)], [(1, -1)]]
                  }


class Grid:
    def __init__(self, x_size, y_size, refresh_rate, cursor, alt_cursor):
        self.Board = {}
        self.x_size = x_size
        self.y_size = y_size
        self.cursor = cursor
        self.alt_cursor = alt_cursor
        self.refresh_rate = refresh_rate
        self.WhiteTileColor = Back.LIGHTBLACK_EX
        self.BlackTileColor = Back.BLACK
        self.HighlightColor = Back.LIGHTBLUE_EX
        self.build_board()

    def build_board(self):
        color_build_toggle = self.BlackTileColor
        for y in range(self.y_size - 1, -1, -1):
            for x in range(self.x_size):
                tile = Tile((x, y), None, color_build_toggle, self)
                self.Board[x, y] = tile
                color_build_toggle = self.toggle_color(color_build_toggle)
            # make the color switch an extra time for each line
            color_build_toggle = self.toggle_color(color_build_toggle)

    def toggle_color(self, color_build_toggle):
        if color_build_toggle == self.BlackTileColor:
            return self.WhiteTileColor
        else:
            return self.BlackTileColor

    def keyboard_controls(self, key):
        if key == 120:  # x
            print("Exit")
            quit(0)
        elif key == 32:  # space - for debugging
            print("Pause")
        elif key == 113:  # q - select
            self.select_tile_token()
            draw_screen(self)
            self.display_tile_info(MainCursor.position()[0], MainCursor.position()[1])
        elif key == 101:  # e - cycle highlight
            self.cycle_highlight()
        elif key == 97:  # a - Left
            MainCursor.cursor_move('left')
            AltCursor.reset()
            HighlightCells.clear()
            draw_screen(self)
        elif key == 100:  # d - Right
            MainCursor.cursor_move('right')
            AltCursor.reset()
            HighlightCells.clear()
            draw_screen(self)
        elif key == 119:  # w - Up
            MainCursor.cursor_move('up')
            AltCursor.reset()
            HighlightCells.clear()
            draw_screen(self)
        elif key == 115:  # s - Down
            MainCursor.cursor_move('down')
            AltCursor.reset()
            HighlightCells.clear()
            draw_screen(self)

    def display_tile_info(self, x, y):
        # Tile Information
        print("\n")
        print(str(self.Board[x, y].color) + "Tile" + str(self.Board[x, y].position))

        # Token Information
        if self.Board[x, y].token is not None:
            print(str(self.Board[x, y].token.color) + "Token: " + self.Board[x, y].token.name)
        sys.stdout.write(Style.RESET_ALL + " ")

    def move_token(self, _from, _to):
        _to.token = _from.token
        _from.token = None
        _to.token.parent_tile = _to

    def select_tile_token(self):
        HighlightCells.clear()
        cursor_pos = self.cursor.position()
        alt_cursor_pos = self.alt_cursor.position()

        if self.alt_cursor.active:
            if self.alt_cursor.mode == 'move':
                self.move_token(self.Board[cursor_pos], self.Board[alt_cursor_pos])
                self.alt_cursor.reset()
                self.pawn_check_change(self.Board[alt_cursor_pos])
                return
            else:
                self.alt_cursor.mode = 'move'
                self.alt_cursor.active = False
                self.cursor.active = True

        try:
            self.cursor.selection.token.find_available_moves()
        except AttributeError:
            print('Nothing to select here.')
            return

        if len(HighlightCells) > 0:
            self.alt_cursor.active = True
            self.alt_cursor.selection = self.Board[HighlightCells[0]]
        # time.sleep(2)

    def cycle_highlight(self):
        if self.alt_cursor.active:
            if self.alt_cursor.mode == 'move':
                if self.alt_cursor.counter >= len(HighlightCells):
                    self.alt_cursor.counter = 0
                self.alt_cursor.selection = self.Board[HighlightCells[self.alt_cursor.counter]]
            elif self.alt_cursor.mode == 'pawn':
                token_options = PawnPromotionOptions
                if self.alt_cursor.counter >= len(token_options):
                    self.alt_cursor.counter = 0
                self.Board[self.cursor.position()].token.token_type = token_options[self.alt_cursor.counter]
                self.Board[self.cursor.position()].token.name = TokenTypeNameList[token_options[self.alt_cursor.counter]]

            self.alt_cursor.counter += 1
            draw_screen(Grid)

    def pawn_check_change(self, _tile):
        token_type = _tile.token.token_type
        y = _tile.position[1]
        if token_type == 'BP' or token_type == 'WP':
            if (token_type == 'BP' and y == 0) or (token_type == 'WP' and y == 7):
                self.alt_cursor.active = True
                self.alt_cursor.mode = 'pawn'
                self.cursor.active = False
                self.cursor.selection = _tile
                HighlightCells.clear()
                HighlightCells.append(_tile.position)
                self.alt_cursor.counter = 0
                self.cycle_highlight()


class Cursor:
    def __init__(self, active, mode, back_color, text_color):
        self.active = active
        self.mode = mode
        self.counter = 1
        self.back_color = back_color
        self.text_color = text_color
        self.selection = None
        self.parent_grid = None

    def attach_to_grid(self, grid):
        self.parent_grid = grid
        self.selection = grid.Board[(0, 0)]

    def position(self):
        return self.selection.position[0], self.selection.position[1]

    def cursor_move(self, direction):
        dx, dy = 0, 0
        if direction == 'left':
            dx -= 1
        elif direction == 'right':
            dx += 1
        elif direction == 'up':
            dy += 1
        elif direction == 'down':
            dy -= 1
        else:
            print('Unknown Cursor Move Command: ' + direction)

        new_x = self.position()[0] + dx
        new_y = self.position()[1] + dy

        if new_x > 7:
            new_x = 7
        if new_x < 0:
            new_x = 0
        if new_y > 7:
            new_y = 7
        if new_y < 0:
            new_y = 0

        self.selection = self.parent_grid.Board[(new_x, new_y)]

        self.mode = 'move'
        self.active = True

    def reset(self):
        self.active = False
        self.counter = 1


class Tile:
    def __init__(self, position, token, color, parent_grid):
        self.position = position
        self.token = token
        self.color = color
        self.parent_grid = parent_grid


class Token:
    def __init__(self, name, token_type, color, parent_tile):
        self.name = name
        self.token_type = token_type
        self.color = color
        self.parent_tile = parent_tile

    def find_available_moves(self):
        # figure out which cells to highlight

        x = self.parent_tile.position[0]
        y = self.parent_tile.position[1]
        grid = self.parent_tile.parent_grid.Board

        for row in HighlightRules[self.token_type]:
            row_blocked = False
            own_token_blocking = False
            for cell in row:
                temp_cell = (cell[0] + x, cell[1] + y)
                print(str(temp_cell) + ' tested, applying' + str(cell))

                # if the cell is on the board
                if 0 <= temp_cell[0] <= 7 and 0 <= temp_cell[1] <= 7:
                    # check if cell has your own token
                    if grid[temp_cell].token is not None:
                        row_blocked = True
                        if grid[temp_cell].token.color == self.color:
                            own_token_blocking = True
                else:
                    # print('Off Board')
                    break

                if self.token_type == 'BP' or self.token_type == 'WP':
                    row_blocked, own_token_blocking = self.pawn_move_rules(x, temp_cell[0], y, temp_cell[1],
                                                                      row_blocked, own_token_blocking, self.token_type)

                if own_token_blocking:
                    # print('own token')
                    break
                else:
                    # print('available')
                    HighlightCells.append(temp_cell)

                if row_blocked:
                    # print('Opposition token blocking')
                    break

    def pawn_move_rules(self, _from_x, _to_x, _from_y, _to_y, _row_blocked, _own_token_blocking, _token_type):
        # if in same column
        if _from_x == _to_x:
            if _row_blocked:
                # cannot capture forward act like own token in the way
                _own_token_blocking = True
        elif not _row_blocked:
            # if diag is open treat it as blocked
            _row_blocked = True
            _own_token_blocking = True

        # only allow double move from starting row
        if abs(_from_y - _to_y) > 1:
            if (_token_type == 'BP' and _from_y != 6) or (_token_type == 'WP' and _from_y != 1):
                _row_blocked = True
                _own_token_blocking = True
        return _row_blocked, _own_token_blocking


def place_tokens(_board):
    global WhiteTokenColor, BlackTokenColor
    Grid.Board[0, 7].token = Token("R", "R", BlackTokenColor, Grid.Board[0, 7])
    Grid.Board[1, 7].token = Token("N", "N", BlackTokenColor, Grid.Board[1, 7])
    Grid.Board[2, 7].token = Token("B", "B", BlackTokenColor, Grid.Board[2, 7])
    Grid.Board[3, 7].token = Token("K", "K", BlackTokenColor, Grid.Board[3, 7])
    Grid.Board[4, 7].token = Token("Q", "Q", BlackTokenColor, Grid.Board[4, 7])
    Grid.Board[5, 7].token = Token("B", "B", BlackTokenColor, Grid.Board[5, 7])
    Grid.Board[6, 7].token = Token("N", "N", BlackTokenColor, Grid.Board[6, 7])
    Grid.Board[7, 7].token = Token("R", "R", BlackTokenColor, Grid.Board[7, 7])
    Grid.Board[0, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[0, 6])
    Grid.Board[1, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[1, 6])
    Grid.Board[2, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[2, 6])
    Grid.Board[3, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[3, 6])
    Grid.Board[4, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[4, 6])
    Grid.Board[5, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[5, 6])
    Grid.Board[6, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[6, 6])
    Grid.Board[7, 6].token = Token("P", "BP", BlackTokenColor, Grid.Board[7, 6])

    Grid.Board[0, 0].token = Token("R", "R", WhiteTokenColor, Grid.Board[0, 0])
    Grid.Board[1, 0].token = Token("N", "N", WhiteTokenColor, Grid.Board[1, 0])
    Grid.Board[2, 0].token = Token("B", "B", WhiteTokenColor, Grid.Board[2, 0])
    Grid.Board[3, 0].token = Token("Q", "Q", WhiteTokenColor, Grid.Board[3, 0])
    Grid.Board[4, 0].token = Token("K", "K", WhiteTokenColor, Grid.Board[4, 0])
    Grid.Board[5, 0].token = Token("B", "B", WhiteTokenColor, Grid.Board[5, 0])
    Grid.Board[6, 0].token = Token("N", "N", WhiteTokenColor, Grid.Board[6, 0])
    Grid.Board[7, 0].token = Token("R", "R", WhiteTokenColor, Grid.Board[7, 0])
    Grid.Board[0, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[0, 1])
    Grid.Board[1, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[1, 1])
    Grid.Board[2, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[2, 1])
    Grid.Board[3, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[3, 1])
    Grid.Board[4, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[4, 1])
    Grid.Board[5, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[5, 1])
    Grid.Board[6, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[6, 1])
    Grid.Board[7, 1].token = Token("P", "WP", WhiteTokenColor, Grid.Board[7, 1])


def draw_screen(_grid):
    global WhiteTokenColor
    os.system("cls")

    for y in range(_grid.y_size - 1, -1, -1):
        for x in range(_grid.x_size):

            text = ''
            cell = ''

            try:
                cursor_token_name = _grid.cursor.selection.token.name
            except AttributeError:
                cursor_token_name = ''  # no selected token for cursor
            # set text color for the tokens
            if _grid.Board[x, y].token is not None:
                text = _grid.Board[x, y].token.color

            # colors for the cursor cell
            if _grid.cursor.active and _grid.cursor.position() == (x, y):
                text = _grid.cursor.text_color
                cell = _grid.cursor.back_color

            # colors for the Alt Cursor
            elif _grid.alt_cursor.active and _grid.alt_cursor.position() == (x, y):
                text = _grid.alt_cursor.text_color
                cell = _grid.alt_cursor.back_color

            # when a token is selected show the available options in green
            elif cursor_token_name != '' and (x, y) in HighlightCells:
                cell = _grid.HighlightColor

                # otherwise use the default "tile" color
            else:
                cell = _grid.Board[x, y].color

            sys.stdout.write(text)
            sys.stdout.write(cell)

            # ForeGround "Token" color& Name Or an Empty Space if none
            if _grid.Board[x, y].token is not None:
                sys.stdout.write(_grid.Board[x, y].token.name)
            else:
                sys.stdout.write(" ")

            sys.stdout.write(Style.RESET_ALL+" ")
        sys.stdout.write("\n")
        sys.stdout.flush()


MainCursor = Cursor(1, 'move', Back.WHITE, Fore.BLACK)
AltCursor = Cursor(0, 'move', Back.GREEN, Fore.WHITE)
Grid = Grid(8, 8, .1, MainCursor, AltCursor)
MainCursor.attach_to_grid(Grid)
AltCursor.attach_to_grid(Grid)
Grid.build_board()
place_tokens(Grid.Board)
draw_screen(Grid)
while True:
    time.sleep(Grid.refresh_rate)
    if kbhit():
        Grid.keyboard_controls(ord(getch()))


