# cli interface to play chess

from elements import *
import re
import getopt
import sys

tokens = {
    'p': Pawn,
    'r': Rook,
    'n': Knight,
    'b': Bishop,
    'q': Queen,
    'k': King
}

def printGame(game):
    "print game"
    lines = []
    lines.append('  A B C D E F G H ')

    for i in char_range('1', '8'):
        line = i + ' '
        for j in char_range('a', 'h'):
            piece = game.board.squares[(j, i)].piece
            if type(piece) is Knight:
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
    mv = getMove(input('{} to move. Enter move: '.format('White' if game.hasToMove is Color.WHITE else 'Black')))

    if not mv:
        return False

    return move(game, (mv[0], mv[1]), mv[2])


def getMove(moveStr):
    matches = re.search(r"^\s*([a-h])([1-8])([a-h])([1-8])([qbnr])?\s*$", moveStr, re.IGNORECASE)

    if matches is None:
        return False

    return (matches.group(1), matches.group(2)), (matches.group(3), matches.group(4)), \
        tokens[matches.group(5)] if matches.group(5) else None

def getPosition(positionStr):
    pieces = ''.join(list(tokens.keys()))
    matches = re.search(r"^\s*([bw])(?:([" + pieces + r"])([a-h])([1-8]))?\s*$", positionStr)

    if matches is None:
        return False

    if matches.lastindex == 1:
        return matches.group(1)

    return matches.group(1), matches.group(2), (matches.group(3), matches.group(4))

def move(game, coords, promote = None):
    try:
        game.move(coords[0], coords[1], promote)
    except ValueError as e:
        print(e)
        return False

    return True


def validateMovesSyntax(movesString):
    moves = [ getMove(move) for move in movesString.split(' ') if move is not '' ]

    return False if False in moves else moves

def validatePositionSyntax(positionsString):
    positions = [ getPosition(position)  for  position in positionsString.split(' ') if position is not '' ]

    return False if False in positions else positions

def usage():
    print ('Help message : -h or --help' )
    print ('Play moves : -m "e2e4 e7e5 g1f3…"  or  --moves="e2e4 e7e5 g1f3…"' )
    print ('Set initial position : -p "bka8 wqb6 wkc5 w"  or  --position="bka8 wqb6 wkc5 w"' )


def printError():
    print ('Wrong syntax')
    usage()


# parse options
try:
    opts, arg = getopt.getopt(sys.argv[1:], "hm:p:", ["help", "moves=", "position="])
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

    if opt in [ '-p', '--position' ]:
        positions = validatePositionSyntax(arg)

        if not positions:
            printError()
            sys.exit(2)

        game = Game(empty = True)

        for i in range(0, len(positions)):
            if i == len(positions) - 1:
                game.hasToMove = Color.WHITE if positions[i] is 'w' else Color.BLACK
            else:
                color = Color.WHITE if positions[i][0] is 'w' else Color.BLACK
                game.players[color].pieces.append(tokens[positions[i][1]](game, color, (positions[i][2])))

        pass

if not 'game' in locals():
    game = Game()

end = False
nMove = 0
while not end:
    print()
    printGame(game)
    print()
    moved = False
    while not end and not moved:
        if game.currentPlayerInStalemate():
            print(('White' if game.hasToMove is Color.WHITE else 'Black') + ' player in stalemate!')
            print("It's a draw")
            end = True
            break

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
            token = None
            for i, piece in tokens.items():
                if piece == moves[nMove][2]:
                    token = i
                    break

            print('Move: {}{}'.format(*moves[nMove][0]) \
                + '{}{}'.format(*moves[nMove][1]) \
                + ('{}'.format(token) if token else ''))
            moved = move(game, (moves[nMove][0], moves[nMove][1]), moves[nMove][2])

        if moved:
            game.opponentToPlay()
            nMove += 1
        elif not manualInput:
            print ('Some moves are wrong. Exit.')
            sys.exit(2)
