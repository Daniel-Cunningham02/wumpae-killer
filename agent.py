from logic import *
from utils import *
from time import sleep
from random import seed

class WumpusHunter():
    def __init__(self):
        self.base = FolKB([expr("Unvisited(x) & Adjacent(x, y) & Breeze(y) ==> Maybepit(x)"),
            expr('Unvisited(x) & Adjacent(x, y) & Breeze(y) & Adjacent(x, z) & Breeze(z) ==> Pit(x)'),
            expr("Unvisited(x) & Adjacent(x, y) & Stench(y) ==> Wumpus(x)"),
            expr("Wumpus(x) & Pit(x) ==> Unsafe(x)"),
            expr("Visited(x) ==> Safe(x)")])
        self.location = (0, 0)
        self.history = []
        self.yTopBound, self.yBotBound = None, None
        self.xLeftBound, self.xRightBound = None, None
        self.justShot = False

hunter = WumpusHunter()


def locToString(loc):
    """
    Takes location and returns the Square_{}_{} String
    """
    x, y = loc
    if x < 0:
        x = 'n' + str(abs(x))
    if y < 0:
        y = 'n' + str(abs(y))
    return "Square_{}_{}".format(x, y)

def stench(loc):
    """
    Returns Stench expression using loc
    """
    return expr("Stench({})".format(locToString(loc)))

def breeze(loc):
    """
    Returns Breeze expression using loc
    """
    return expr("Breeze({})".format(locToString(loc)))

def visited(loc):
    """
    Returns Visited expression using loc
    """
    return expr("Visited({})".format(locToString(loc)))

def unvisited(loc):
    """
    Returns Unvisited expression using loc
    """
    return expr("Unvisited({})".format(locToString(loc)))

def visit(base, loc):
    """
    Asks if loc is unvisited if so retract and make visited
    """
    if base.ask(unvisited(loc)) == {}:
      base.retract(unvisited(loc))
    base.tell(visited(loc))

def adjacent(src, dest):
    """
    Makes the squares at src and dest adjacent both ways
    """
    srcSquare = locToString(src)
    destSquare = locToString(dest)
    hunter.base.tell(expr("Adjacent({}, {})".format(srcSquare, destSquare)))
    hunter.base.tell(expr("Adjacent({}, {})".format(destSquare, srcSquare)))

def left(loc):
    """
    Returns the square west of the location provided
    """
    x, y = loc
    return (x - 1), y

def right(loc):
    """
    Returns the square east of the location provided
    """
    x, y = loc
    return (x + 1), y

def up(loc):
    """
    Returns the square north of the location provided
    """
    x, y = loc
    return x, (y + 1)

def down(loc):
    """
    Returns the square south of the location provided
    """
    x, y = loc
    return x, (y - 1)

def oppositeMove(loc, move):
    """
    Returns the opposite of a move. None if firing move
    """
    if move == None:
        return None
    if move[0] == 'F':
        return None
    if move == 'N':
        hunter.location = down(loc)
        return 'S'
    elif move == 'S':
        hunter.location = up(loc)
        return 'N'
    elif move == 'W':
        hunter.location = right(loc)
        return 'E'
    else:
        hunter.location = left(loc)
        return 'W'
    
def find_adjacent(loc):
    """
    Finds the adjacent squares within the known bounds
    """
    adjacentSquares = []
    adjacentSquares.append(left(loc))
    adjacentSquares.append(up(loc))
    adjacentSquares.append(right(loc))
    adjacentSquares.append(down(loc))

    for i in adjacentSquares:
        if not checkKnownBounds(i):
            adjacentSquares.remove(i)
    return adjacentSquares
    
def UpdateVisited(square):
    """
    Update the square that just became visited
    """
    visit(hunter.base, square)

    # Make adjacent squares adjacent in KB
    for i in find_adjacent(square):
        adjacent(square, i)

    # Make unvisited squares unvisited in KB
    for i in find_adjacent(square):
        if hunter.base.ask(visited(i)) == False:
            hunter.base.tell(unvisited(i))

def findSquareShot(loc, move):
    """
    Returns the square that was shot at from a location and direction
    """
    if move == 'FN':
        return up(loc)
    elif move == 'FW':
        return left(loc)
    elif move == 'FE':
        return right(loc)
    else:
        return down(loc)
    
def makeBound(loc, move):
    """
    Changes the bounds
    """
    if move == 'N':
        (_, hunter.yTopBound) = loc
    elif move == 'W':
        (hunter.xLeftBound, _) = loc
    elif move == 'E':
        (hunter.xRightBound, _) = loc
    elif move == 'S':
        (_, hunter.yBotBound) = loc

def checkKnownBounds(loc):
    """
    Checks all known bounds and returns a True value if the loc is inside
    """
    xLoc, yLoc = loc
    if hunter.xLeftBound != None:
        if xLoc <= hunter.xLeftBound:
            return False
    
    if hunter.xRightBound != None:
        if xLoc >= hunter.xRightBound:
            return False
        
    if hunter.yTopBound != None:
        if yLoc >= hunter.yTopBound:
            return False
    
    if hunter.yBotBound != None:
        if yLoc <= hunter.yBotBound:
            return False
        
    return True

    
def updateKB(percepts, square):
    """
    Updates the knowledge base using the known percepts
    """
    # Deal with Percepts
    # Percept Strings:
    #   O - Bump
    #   S - Smell Wumpus
    #   B - Breeze
    #   Y - Scream of a Dying Wumpus
    wumpusYell = False
    for i in percepts:
        if i == 'O':
            makeBound(square, hunter.history[-1])
            oppositeMove(square, hunter.history[-1])
        elif i == 'S':
            if hunter.base.ask(stench(square)) == False:
              hunter.base.tell(stench(square))
        elif i == 'B':
            if hunter.base.ask(breeze(square)) == False:
              hunter.base.tell(breeze(square))
        elif i == 'Y':
            wumpusYell = True
    
    if hunter.justShot == True:
        move = hunter.history[-1]
        squareShot = findSquareShot(square, move)
        if wumpusYell == True:
            hunter.base.tell(expr(f"Wumpus({locToString(squareShot)})"))
            hunter.base.tell(expr(f'Deadwumpus({locToString(squareShot)})'))
        else:
            hunter.base.tell(expr(f"Notwumpus({locToString(squareShot)})"))


        
def check_if_visited(loc):
    """
    Returns True if the loc has been visited
    """
    if hunter.base.ask(unvisited(loc)) == False:
      return True
    return False

def checkForWumpae(loc):
    """
    Checks if there is a wumpus on an adjacent square 
        by seeing if it has been shot at already (Notwumpus expression)
        or if it is a dead wumpus (Deadwumpus expression)
    """
    for i in find_adjacent(loc):
        if hunter.base.ask(expr(f"Wumpus({locToString(i)})")) and hunter.base.ask(expr(f'Deadwumpus({locToString(i)})')) == False:
            if hunter.base.ask(expr(f"Notwumpus({locToString(i)})")) == False:
                return i
    return None

def addToHistory(move):
    """
    Adds a move to the history and returns the move
    """
    hunter.history.append(move)
    return move

def shootWumpus(loc, wumpusLocation):
    """
    Returns the move that allows the hunter at loc to shoot at wumpusLocation
    """
    if left(loc) == wumpusLocation:
        return 'FW'
    elif up(loc) == wumpusLocation:
        return 'FN'
    elif right(loc) == wumpusLocation:
        return 'FE'
    else:
        return 'FS'
    
def findSafeSquare(loc):
    """
    Finds a 
    """
    for i in find_adjacent(loc):
        if hunter.base.ask(expr(f'Pit({locToString(i)})')) == False:
            if hunter.base.ask(expr(f'Wumpus({locToString(i)})')) == False or hunter.base.ask(expr(f'Deadwumpus({locToString(i)})')) == {}:
                return i
    return None

def makeMove(loc, safe_square):
    if left(loc) == safe_square:
        hunter.location = left(loc)
        return 'W'
    elif up(loc) == safe_square:
        hunter.location = up(loc)
        return 'N'
    elif right(loc) == safe_square:
        hunter.location = right(loc)
        return 'E'
    else:
        hunter.location = down(loc)
        return 'S'
    
def GetRandomAdjacent(loc):
    """
    Get random adjacent square that is certainly not a pit or the previous square:
    """
    adjacent_squares = find_adjacent(loc)
    if len(adjacent_squares) == 1:
        return adjacent_squares[0]
    # Get last move (without moving)
    
    current_loc = loc
    previous_loc = None
    if hunter.history:
        opposite_move = oppositeMove(loc, hunter.history[-1])
        previous_loc = hunter.location
        move = makeMove(hunter.location, current_loc)
        
    for i in adjacent_squares:
        if i == previous_loc or hunter.base.ask(expr(f'Pit({locToString(i)})')):
            adjacent_squares.remove(i)


    return adjacent_squares[random.randint(0, len(adjacent_squares)) - 1]

def agent(percept):
    """
    Percept Strings:
      O - Bump
      S - Smell Wumpus
      B - Breeze
      Y - Scream of a Dying Wumpus

    Return a Wumpus action based on the percepts.
      N - Go north (up)
      S - Go south (down)
      E - Go east (right)
      W - Go west (left)
      FN - Fire the arrow north 
      FS - Fire the arrow south 
      FE - Fire the arrow east
      FW - Fire the arrow west
    """
    # origin is always (0, 0)
    # Update KB with percepts
    if hunter.history:
        print(f'Location: {hunter.location}, last move: {hunter.history[-1]}')
        if hunter.history[-1] != None:
            if hunter.history[-1][0] == 'F':
                hunter.justShot = True
            else:
                hunter.justShot = False
    print(percept)
    UpdateVisited(hunter.location)
    updateKB(percept, hunter.location)

    # Check for Wumpae to shoot
    WumpusLocation = checkForWumpae(hunter.location)
    if WumpusLocation != None:
        return addToHistory(shootWumpus(hunter.location, WumpusLocation))
    
    safe_square = findSafeSquare(hunter.location)
    if hunter.history and hunter.history[-1] != None and safe_square == None:
        return addToHistory(oppositeMove(hunter.location, hunter.history[-1]))
    elif safe_square == None:
        return addToHistory(makeMove(hunter.location, GetRandomAdjacent(hunter.location)))
    else:
        if check_if_visited(safe_square):
            return addToHistory(makeMove(hunter.location, GetRandomAdjacent(hunter.location)))
        else:
            return addToHistory(makeMove(hunter.location, safe_square))