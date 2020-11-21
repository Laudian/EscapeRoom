from enum import Enum

class Position(object):
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.name = name

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x+other.x, self.y+other.y)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __repr__(self):
        return "X = " + str(self.x) + ", Y = " + str(self.y)

    def __hash__(self):
        return hash((self.x, self.y))


class Direction(Enum):
    LEFT  = Position(-1,  0, name="links")
    RIGHT = Position( 1,  0, name="rechts")
    UP    = Position( 0,  1, name="oben")
    DOWN  = Position( 0, -1, name="unten")


# Settings
startpos = Position(1, 1)
startdir = Direction.RIGHT


class Network(object):
    def showMessage(self, message):
        print(message)


class BoardObject(object):
    def blocked(self):
        return True

    def inspect(self):
        return "The inspect method is not set for this object."

    def __repr__(self):
        return "Err"


class Player(BoardObject):
    def __init__(self):
        self.pos = startpos
        self.dir = startdir

    def __repr__(self):
        return "SPI"

    def inspect(self):
        return "This is you."

    def setDir(self, dir):
        self.dir = dir

    def setPos(self, pos):
        self.pos = pos

    def getPos(self):
        return self.pos

    def getDir(self):
        return self.dir.value


class EmptySquare(BoardObject):
    def blocked(self):
        return False

    def inspect(self):
        return "There is nothing in front of you."

    def __repr__(self):
        return "EMP"


class Wall(BoardObject):
    def inspect(self):
        return "This is a wall."

    def __repr__(self):
        return "WAL"


class GameBoard(object):
    def __init__(self, network):
        self.network = network
        self.board = {}
        self.player = Player()

        # Fill Gameboard with empty Fields
        for x in range(1, 11):
            for y in range(1, 11):
                pos = Position(x,y)
                self.board[pos] = EmptySquare()

        # Put player on the board
        self.board[self.player.pos] = self.player

        # TODO Surround the Baord with Walls

        # Spiel startet
        self.network.showMessage("Das Spiel beginnt nun. Hier steht irgendeine Einleitung")

    def turn(self, dir: Direction):
        self.player.setDir(dir)
        self.network.showMessage("Du guckst jetzt nach "+ dir.value.name + ".")

    def move(self, steps):
        path = []
        pos = self.player.getPos()
        dir = self.player.getDir()

        while steps > 0:
            pos = pos + dir
            path.append(self.board.get(pos, Wall()))
            steps -= 1

        for square in path:
            if square.blocked():
                self.network.showMessage("Der Weg ist versperrt.")
                return
        self.player.setPos(pos)
        self.network.showMessage("Du befindest dich jetzt an folgender Position: " + str(pos) + ".")

if __name__ == "__main__":
    network = Network()
    test = GameBoard(network)