from enum import Enum

def char_range(c1, c2):
    "Generates the characters from c1 to c2 inclusive"
    for i in [chr(j) for j in range(ord(c1), ord(c2) + 1)]:
        yield i

class Color(Enum):
    BLACK = 1
    WHITE = 0

    def __int__(self):
        return self.value

    def opponent(color):
        return Color.BLACK if color is Color.WHITE else Color.WHITE

class Square:
    def __init__(self, board, color, coords):
        self.board = board
        self.color = color
        self.coords = coords
        self.piece = None

    def controlledBy(self, set, excludeKing = False):
        "Check whether a square is controlled by a set"
        return set.controls(self, excludeKing)

class Chessboard:
    def __init__(self):
        self.squares = {}
        for i in char_range('a', 'h'):
            for j in char_range('1', '8'):
                self.squares[(i, j)] = Square(self, (ord(i) + int(j) + 1) % 2, (i, j))

class Piece:
    def __init__(self, game, color, coords):
        self.game = game
        self.board = game.board
        self.color = color
        self.square = self.board.squares[coords]
        self.square.piece = self
        self.nbMoves = 0

    def moveTo(self, coords):
        possibleMoves = self.possibleMoves()

        if possibleMoves is None or self.board.squares[coords] not in self.possibleMoves():
            return False

        self.square.piece = None
        self.square = self.board.squares[coords]
        # delete piece if there is a piece of the square
        if self.square.piece:
            self.game.sets[Color.opponent(self.color)].remove(self.square.piece)
            self.square.piece = None
        self.square.piece = self
        self.nbMoves += 1

        return True

    def newCoords(self, move, origin=None):
        column = chr(ord(self.square.coords[0] if origin is None else origin[0]) + move[0])
        row = str(int(self.square.coords[1] if origin is None else origin[1]) + move[1])

        # return False if new_coord do n
        if 'abcdefgh'.find(column) == -1 or '12345678'.find(row) == -1:
            return False

        return (column, row)

    def recursiveAddCoords(self, list, coords, move, control = False):
        "Add coords to a list of possible moves while squares are free"
        newCoords = self.newCoords(move, coords)

        # returns list if there is no further existing square, or if square is occupied
        # by a piece of a same color
        if not newCoords:
            return list

        # returns list if square is occupied by a piece of the same color
        piece = self.board.squares[newCoords].piece
        if piece:
            if control or piece.color is not self.color:
                list.append(newCoords)

            return list

        list.append(newCoords)

        return self.recursiveAddCoords(list, newCoords, move, control)


class King(Piece):
    def possibleMoves(self, control = False):
        opponentColor = Color.opponent(self.color)

        # filter among adjacent squares
        possibleMoves = self.adjacentSquares()

        # keep only free squares and squares occupied par an opponent piece (or friend pieces too if control)
        possibleMoves = [ square for square in possibleMoves if not square.piece \
            or (square.piece and control) \
            or (square.piece and square.piece.color is opponentColor) \
        ]

        # check whether squares are controlled by opponent. Exclude king from computation to avoid infinite recursion loop
        possibleMoves = [
            square for square in possibleMoves if not square.controlledBy(self.game.sets[opponentColor], True)
        ]

        # exclude squares adjacent from opponent king
        possibleMoves = [
            square for square in possibleMoves if not square in self.game.sets[opponentColor].king().adjacentSquares()
        ]

        return possibleMoves

    def inCheck(self, opponentSet):
        for piece in opponentSet.pieces:
            if self.square in piece.possibleMoves():
                return True

        return False

    def checkmated(self, opponentSet):
        return self.inCheck(opponentSet) and not self.possibleMoves()

    def adjacentSquares(self):
        # search for theorical possibles squares
        adjacents = [
            self.newCoords((0, 1)),
            self.newCoords((1, 1)),
            self.newCoords((1, 0)),
            self.newCoords((1, -1)),
            self.newCoords((0, -1)),
            self.newCoords((-1, -1)),
            self.newCoords((-1, 0)),
            self.newCoords((-1, 1)),
        ]

        # remove non existent squares
        adjacents = [ coords for coords in adjacents if coords ]

        # change coords into squares
        return [ self.board.squares[coords] for coords in adjacents ]

class Queen(Piece):
    def possibleMoves(self, control = False):
        return Rook.possibleMoves(self, control) + Bishop.possibleMoves(self, control)

class Bishop(Piece):
    def possibleMoves(self, control = False):
        coords = self.square.coords
        possibleMoves = []
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (1, 1), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (1, -1), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (-1, -1), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (-1, 1), control)

        possibleMoves = [ self.board.squares[coords] for coords in possibleMoves ]

        return possibleMoves

class Knight(Piece):
    def possibleMoves(self, control = False):
        coords = self.square.coords

        # search for theorical possibles squares
        possibleMoves = [
            self.newCoords((1, 2)),
            self.newCoords((2, 1)),
            self.newCoords((2, -1)),
            self.newCoords((1, -2)),
            self.newCoords((-1, -2)),
            self.newCoords((-2, -1)),
            self.newCoords((-2, 1)),
            self.newCoords((-1, 2)),
        ]

        # remove non existent squares
        possibleMoves = [ move for move in possibleMoves if move ]

        # change coords into squares
        possibleMoves = [ self.board.squares[coords] for coords in possibleMoves ]

        # keep only free squares and squares occupied par an opponent piece (or friend pieces too if control)
        possibleMoves = [ square for square in possibleMoves if not square.piece \
            or (square.piece and control) \
            or (square.piece and square.piece.color != self.color) ]

        return possibleMoves


class Rook(Piece):
    def possibleMoves(self, control = False):
        coords = self.square.coords
        possibleMoves = []
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (0, 1), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (1, 0), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (0, -1), control)
        possibleMoves = self.recursiveAddCoords(possibleMoves, coords, (-1, 0), control)

        possibleMoves = [ self.board.squares[coords] for coords in possibleMoves ]

        return possibleMoves

class Pawn(Piece):
    def possibleMoves(self, control = False):
        coords = self.square.coords
        possibleMoves = []
        direction = 1 if self.color is Color.WHITE else -1

        up = self.newCoords((0, 1 * direction))

        if up and self.board.squares[up].piece is None:
            possibleMoves.append(self.board.squares[up])

        up2 = self.newCoords((0, 2 * direction))

        if self.nbMoves == 0 and up2 and self.board.squares[up2].piece is None:
            possibleMoves.append(self.board.squares[up2])

        for move in [(-1, 1 * direction), (1, 1 * direction)]:
            newCoords = self.newCoords(move)
            if newCoords and self.board.squares[newCoords].piece and \
                (control or self.board.squares[newCoords].piece.color != self.color):
                possibleMoves.append(self.board.squares[newCoords])

        return possibleMoves

    def moveTo(self, coords):
        move = Piece.moveTo(self, coords)

        if self.square.coords[1] in ['1', '8']:
            "promote"

        return move

class Set:
    def __init__(self, game, color):
        "initialize a new set at the beginning of a game"
        piecesLine = '1' if color is Color.WHITE else '8' # whites => 1, blacks => 8
        self.pieces = []
        self.pieces.append (King (game, color, ('e', piecesLine)))
        self.pieces.append (Queen (game, color, ('d', piecesLine)))
        self.pieces.append (Bishop (game, color, ('c', piecesLine)))
        self.pieces.append (Bishop (game, color, ('f', piecesLine)))
        self.pieces.append (Knight (game, color, ('b', piecesLine)))
        self.pieces.append (Knight (game, color, ('g', piecesLine)))
        self.pieces.append (Rook (game, color, ('a', piecesLine)))
        self.pieces.append (Rook (game, color, ('h', piecesLine)))

        pawnsLine = '2' if color is Color.WHITE else '7' # whites => 2, blacks => 7
        self.pawns = []
        for i in char_range('a', 'h'):
            self.pieces.append (Pawn (game, color, (i, pawnsLine)))

    def king(self):
        for piece in self.pieces:
            if type(piece).__name__ == 'King':
                return piece

    def inCheck(self, opponentSet):
        return self.king().inCheck(opponentSet)

    def checkmated(self, opponentSet):
        return self.king().checkmated(opponentSet)

    def controlledSquares(self, excludeKing = False):
        # ability to exclude king from computation to avoid infinite recursion loop
        squares = []
        for piece in self.pieces:
            if excludeKing and type(piece).__name__ == 'King':
                continue
            squares += piece.possibleMoves(True)

        return list(set(squares))

    def controls(self, square, excludeKing = False):
        # ability to exclude king from computation to avoid infinite recursion loop
        return square in self.controlledSquares(excludeKing)

    def remove(self, piece):
        self.pieces.remove(piece)

class Game:
    def __init__(self):
        "initialize a new game, with all pieces on each side"
        self.board = Chessboard()
        self.sets = {}
        self.sets[Color.WHITE]  = Set(self, Color.WHITE)
        self.sets[Color.BLACK] = Set(self, Color.BLACK)
        self.hasToMove = Color.WHITE

    def move(self, origin, destination):
        piece = self.board.squares[origin].piece

        if piece is None:
            raise ValueError('empty square')

        if piece.color is not self.hasToMove:
            raise ValueError('bad color')

        if not piece.moveTo(destination):
            raise ValueError('movement not allowed')

        self.hasToMove = Color.opponent(self.hasToMove)

    def currentPlayerInCheck(self):
        "Check whether the current player in check"
        return self.sets[self.hasToMove].inCheck(self.sets[Color.opponent(self.hasToMove)])

    def currentPlayerCheckmated(self):
        return self.sets[self.hasToMove].checkmated(self.sets[Color.opponent(self.hasToMove)])
