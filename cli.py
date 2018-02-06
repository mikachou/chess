# cli interface to play chess

from elements import *
import re
import getopt
import sys

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
    coords = getMove(input('Enter move: '))

    if not coords:
        return False

    return move(game, coords)


def getMove(moveStr):
    matches = re.search(r"^\s*([a-h])([1-8])([a-h])([1-8])\s*$", moveStr, re.IGNORECASE)

    if matches is None:
        return False

    return (matches.group(1), matches.group(2)), (matches.group(3), matches.group(4))


def move(game, coords):
    try:
        game.move(coords[0], coords[1])
    except ValueError as e:
        print(e)
        return False

    return True


def validateMovesSyntax(movesString):
    moves = [ getMove(move) for move in movesString.split(' ') if move is not '' ]

    return False if False in moves else moves


def usage():
    print ('Help message : -h or --help' )
    print ('Play moves : -m "e2e4 e7e5 g1f3…"  or  --moves="e2e4 e7e5 g1f3…"]' )


def printError():
    print ('Wrong syntax')
    usage()


# parse options
try:
    opts, arg = getopt.getopt(sys.argv[1:], "hm:", ["--help", "--moves="])
except getopt.GetoptError:
    printError()
    sys.exit(2)

manualInput = True

for opt, arg in opts:
    if opt in [ '-h', '--help' ]:
        usage()
        sys.exit(0)
    if opt in [ '-m', '--moves' ]:
        moves = validateMovesSyntax(arg)

        if not moves:
            printError()
            sys.exit(2)

        manualInput = False


game = Game()

end = False
nMove = 0
while not end:
    print()
    printGame(game)
    print()
    moved = False
    while not end and not moved:
        if game.currentPlayerCheckmated():
            print(('White' if game.hasToMove is Color.WHITE else 'Black') + ' player is checkmated!')
            print(('Black' if game.hasToMove is Color.WHITE else 'White') + ' player wins!')
            end = True
            break
        if game.currentPlayerInCheck():
            print(('White' if game.hasToMove is Color.WHITE else 'Black') + ' player in check!')

        if not manualInput and nMove == len(moves):
            print('This is the last defined move')
            print()
            manualInput = True

        if manualInput:
            moved = inputMove(game)
        else:
            print('Move: {}{}-'.format(*moves[nMove][0]) + '{}{}'.format(*moves[nMove][1]))
            moved = move(game, moves[nMove])

        if moved:
            game.opponentToPlay()
            nMove += 1
        elif not manualInput:
            print ('Some moves are wrong. Exit.')
            sys.exit(2)
