import os
import sys
import time
from msvcrt import getch
from msvcrt import kbhit
from colorama import init
from colorama import Fore, Back, Style
init()

Grid = {}
GridSizeX = 8
GridSizeY = 8
Cursor = [0, 7]
CursorActive = 1
AltCursorPosition = (0, 7)
AltCursorActive = 0
AltCursorCount = 0
AltCursorMode = 'move'
RefreshRate = .1

HighlightColor = Back.LIGHTBLUE_EX
AltCursorColor = Back.GREEN
BlackTileColor = Back.BLACK
BlackTokenColor = Fore.RED
WhiteTileColor = Back.LIGHTBLACK_EX
WhiteTokenColor = Fore.WHITE

TokenTypeNameList = {'K': 'K',
                     'Q': 'Q',
                     'B': 'B',
                     'N': 'N',
                     'R': 'R',
                     'WP': 'P',
                     'BP': 'P'
                     }

SelectedTokenName = ''
SelectedTokenPosition = (0, 0)
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


class Tile:
    def __init__(self, position, token, color):
        self.position = position
        self.token = token
        self.color = color


class Token:
    def __init__(self, name, token_type, color):
        self.name = name
        self.token_type = token_type
        self.color = color


def build_board():
    color_build_toggle = BlackTileColor  # defaults first tile to black
    for y in range(GridSizeY-1, -1, -1):
        for x in range(GridSizeX):
            tile = Tile((x, y), None, color_build_toggle)
            Grid[x, y] = tile
            color_build_toggle = toggle_color(color_build_toggle)
        color_build_toggle = toggle_color(color_build_toggle)  # make the color switch an extra time for each line


def toggle_color(_color_build_toggle):
    if _color_build_toggle == BlackTileColor:
        return WhiteTileColor
    else:
        return BlackTileColor


def place_tokens():
    Grid[0, 7].token = Token("R", "R", BlackTokenColor)
    Grid[1, 7].token = Token("N", "N", BlackTokenColor)
    Grid[2, 7].token = Token("B", "B", BlackTokenColor)
    Grid[3, 7].token = Token("K", "K", BlackTokenColor)
    Grid[4, 7].token = Token("Q", "Q", BlackTokenColor)
    Grid[5, 7].token = Token("B", "B", BlackTokenColor)
    Grid[6, 7].token = Token("N", "N", BlackTokenColor)
    Grid[7, 7].token = Token("R", "R", BlackTokenColor)
    Grid[0, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[1, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[2, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[3, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[4, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[5, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[6, 6].token = Token("P", "BP", BlackTokenColor)
    Grid[7, 6].token = Token("P", "BP", BlackTokenColor)

    Grid[0, 0].token = Token("R", "R", WhiteTokenColor)
    Grid[1, 0].token = Token("N", "N", WhiteTokenColor)
    Grid[2, 0].token = Token("B", "B", WhiteTokenColor)
    Grid[3, 0].token = Token("Q", "Q", WhiteTokenColor)
    Grid[4, 0].token = Token("K", "K", WhiteTokenColor)
    Grid[5, 0].token = Token("B", "B", WhiteTokenColor)
    Grid[6, 0].token = Token("N", "N", WhiteTokenColor)
    Grid[7, 0].token = Token("R", "R", WhiteTokenColor)
    Grid[0, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[1, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[2, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[3, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[4, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[5, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[6, 1].token = Token("P", "WP", WhiteTokenColor)
    Grid[7, 1].token = Token("P", "WP", WhiteTokenColor)


def draw_screen(_grid):
    global HighlightColor, AltCursorColor, AltCursorActive
    os.system("cls")

    for y in range(GridSizeY-1, -1, -1):
        for x in range(GridSizeX):
            #  Background "Tile" color

            # If this is the cursor make it white
            if CursorActive and Cursor[0] == x and Cursor[1] == y:
                sys.stdout.write(Back.WHITE)

            # if this is the Alt Cursor Make it green
            elif AltCursorActive == 1 and AltCursorPosition[0] == x and AltCursorPosition[1] == y:
                sys.stdout.write(AltCursorColor)

            # when a token is selected show it's options in green
            elif SelectedTokenName != '' and (x, y) in HighlightCells:
                sys.stdout.write(HighlightColor)

            # otherwise use the default "tile" color
            else:
                sys.stdout.write(_grid[x, y].color)

            # ForeGround "Token" color& Name Or an Empty Space if none
            if _grid[x, y].token is not None:
                sys.stdout.write(_grid[x, y].token.color)
                sys.stdout.write(_grid[x, y].token.name)
            else:
                sys.stdout.write(" ")

            sys.stdout.write(Style.RESET_ALL+" ")
        sys.stdout.write("\n")
        sys.stdout.flush()


def find_available_moves(token_type, token_color, x, y):
    global AltCursorActive, AltCursorPosition
    # figure out which cells to highlight
    if SelectedTokenName != '':
        for row in HighlightRules[token_type]:
            row_blocked = False
            own_token_blocking = False
            for cell in row:
                temp_cell = (cell[0] + x, cell[1] + y)
                print(str(temp_cell) + ' tested, applying' + str(cell))

                # if the cell is on the board
                if 0 <= temp_cell[0] <= 7 and 0 <= temp_cell[1] <= 7:
                    # check if cell has your own token
                    if Grid[temp_cell].token is not None:
                        row_blocked = True
                        if Grid[temp_cell].token.color == token_color:
                            own_token_blocking = True
                else:
                    # print('Off Board')
                    break

                if token_type == 'BP' or token_type == 'WP':
                    blocking = pawn_move_rules(x, temp_cell[0], y, temp_cell[1], row_blocked, own_token_blocking, token_type)
                    row_blocked = blocking[0]
                    own_token_blocking = blocking[1]

                if own_token_blocking:
                    # print('own token')
                    break
                else:
                    # print('available')
                    HighlightCells.append(temp_cell)

                if row_blocked:
                    # print('Opposition token blocking')
                    break

        if len(HighlightCells) > 0:
            AltCursorActive = True
            AltCursorPosition = HighlightCells[0]
        # time.sleep(2)


def select_tile_token(x, y):
    global SelectedTokenName, AltCursorActive, AltCursorPosition, AltCursorMode, CursorActive
    HighlightCells.clear()
    if AltCursorActive == 1:
        if AltCursorMode == 'move':
            move_token(Grid[x, y], Grid[AltCursorPosition[0], AltCursorPosition[1]])
            AltCursorActive = 0
            pawn_check_change(Grid[AltCursorPosition[0], AltCursorPosition[1]])
            return
        else:
            AltCursorMode = 'move'
            AltCursorActive = 0
            CursorActive = 1


    try:
        SelectedTokenName = Grid[x, y].token.name
    except AttributeError:
        print('Nothing to select here.')
        return

    token_color = Grid[x, y].token.color
    token_type = Grid[x, y].token.token_type

    find_available_moves(token_type, token_color, x, y)


def pawn_move_rules(_from_x, _to_x, _from_y, _to_y, _row_blocked, _own_token_blocking, _token_type ):
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


def move_token(_from, _to):
    _to.token = _from.token
    _from.token = None


def pawn_check_change(_tile):
    global AltCursorPosition, AltCursorActive, AltCursorCount, AltCursorMode, Cursor, CursorActive, SelectedTokenName
    token_type = _tile.token.token_type
    y = _tile.position[1]
    if token_type == 'BP' or token_type == 'WP':
        if (token_type == 'BP' and y == 0) or (token_type == 'WP' and y == 7):
            SelectedTokenName = 'P'
            AltCursorPosition = _tile.position
            AltCursorActive = 1
            AltCursorMode = 'pawn'
            CursorActive = 0
            Cursor[0] = _tile.position[0]
            Cursor[1] = _tile.position[1]
            HighlightCells.clear()
            HighlightCells.append(_tile.position)
            cycle_highlight()


def cycle_highlight():
    global AltCursorPosition, AltCursorActive, AltCursorCount, AltCursorMode

    if AltCursorActive == 1:
        if AltCursorMode == 'move':
            if AltCursorCount >= len(HighlightCells):
                AltCursorCount = 0
            AltCursorPosition = HighlightCells[AltCursorCount]
        elif AltCursorMode == 'pawn':
            token_options = list(HighlightRules)
            if AltCursorCount >= len(token_options):
                AltCursorCount = 0
            Grid[Cursor[0], Cursor[1]].token.token_type = token_options[AltCursorCount]
            Grid[Cursor[0], Cursor[1]].token.name = TokenTypeNameList[token_options[AltCursorCount]]

        AltCursorCount += 1
        draw_screen(Grid)


def display_tile_info(x, y):
    # Tile Information
    print("\n")
    print(str(Grid[x, y].color) + "Tile" + str(Grid[x, y].position))

    # Token Information
    if Grid[x, y].token is not None:
        print(str(Grid[x, y].token.color) + "Token: " + Grid[x, y].token.name)
    sys.stdout.write(Style.RESET_ALL + " ")


def cursor_move(direction):
    global AltCursorActive, AltCursorCount
    if direction == 'left':
        Cursor[0] -= 1
    elif direction == 'right':
        Cursor[0] += 1
    elif direction == 'up':
        Cursor[1] += 1
    elif direction == 'down':
        Cursor[1] -= 1
    else:
        print('Unknown Cursor Move Command: ' + direction)
    AltCursorActive = 0
    AltCursorCount = 1


def keyboard_controls(key):
    global AltCursorPosition, AltCursorActive, AltCursorCount
    if key == 120:  # x
        print("Exit")
        quit(0)
    elif key == 32:  # space - for debugging
        print("Pause")
        print(AltCursorPosition)
    elif key == 113:  # q - select
        select_tile_token(Cursor[0], Cursor[1])
        draw_screen(Grid)
        display_tile_info(Cursor[0], Cursor[1])
    elif key == 101:  # e - cycle highlight
        cycle_highlight()
    elif key == 97:  # a - Left
        cursor_move('left')
        HighlightCells.clear()
        draw_screen(Grid)
    elif key == 100:  # d - Right
        cursor_move('right')
        HighlightCells.clear()
        draw_screen(Grid)
    elif key == 119:  # w - Up
        cursor_move('up')
        HighlightCells.clear()
        draw_screen(Grid)
    elif key == 115:  # s - Down
        cursor_move('down')
        HighlightCells.clear()
        draw_screen(Grid)


build_board()
place_tokens()
draw_screen(Grid)
while True:
    time.sleep(RefreshRate)
    if kbhit():
        keyboard_controls(ord(getch()))


