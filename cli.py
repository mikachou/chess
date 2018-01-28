# cli interface to play chess

from elements import *
import re

def printGame(game):
    "print game"
    lines = []
    lines.append('  A B C D E F G H ')

    for i in char_range('1', '8'):
        line = i + ' '
        for j in char_range('a', 'h'):
            piece = game.board.squares[(j, i)].piece
            if type(piece).__name__ is 'Knight':
                letter = 'N' if piece.color is Color.WHITE else 'n'
            elif piece is not None:
                name = type(piece).__name__
                letter = name.upper()[0] if piece.color is Color.WHITE else name.lower()[0]
            else:
                letter = '.'
            line += letter + ' '
        lines.append(line)

    print(*list(reversed(lines)), sep='\n')


def inputMove(game):
    "input moves during game"
    move = input('Enter move : ')

    # matches
    matches = re.search(r"^\s*([a-h])\s*([1-8])\s*\-\s*([a-h])\s*([1-8])\s*$", move, re.IGNORECASE)

    if matches is None:
        return False

    try:
        game.move((matches.group(1).lower(), matches.group(2)), (matches.group(3).lower(), matches.group(4)))
    except ValueError as e:
        print(e)
        return False

    return True

game = Game()

end = False
while not end:
    print()
    printGame(game)
    print()
    move = False
    while not end and not move:
        if game.currentPlayerCheckmated():
            print(('White' if game.hasToMove is Color.WHITE else 'Black') + ' player is checkmated!')
            print(('Black' if game.hasToMove is Color.WHITE else 'White') + ' player wins!')
            end = True
            break
        if game.currentPlayerInCheck():
            print(('White' if game.hasToMove is Color.WHITE else 'Black') + ' player in check!')
        move = inputMove(game)
