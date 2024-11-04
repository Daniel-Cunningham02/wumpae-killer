from logic import *
from utils import *

base = FolKB([expr("Adjacent(x, y) ==> Adjacent(y, x)"),
            expr("Unvisited(x) & Adjacent(x, y) & Breeze(y) & Breeze(x, z) & Breeze(z) ==> Pit(x)"),
            expr("Unvisited(x) & Adjacent(x, y) & Stench(y) & Notwumpus(x) ==> Wumpus(x)"),
            expr("Wumpus(x) & Pit(x) ==> Unsafe(x)"),
            expr("Visited(x) ==> Safe(x)"),
            expr("Breeze(y) & Adjacent(x, y) ==> Danger(x)"),
            expr("Stench(y) & Adjacent(x, y) ==> Danger(x)")])
location = (0, 0)
history = []

def locToString(location):
    x, y = location
    return "Square_{}_{}".format(x, y)

def stench(loc):
    return expr("Stench({})".format(locToString(loc)))

def breeze(loc):
    return expr("Breeze({})".format(locToString(loc)))

def visited(loc):
    return expr("Visited({})".format(locToString(loc)))

def unvisited(loc):
    return expr("Unvisited({})".format(locToString(loc)))

def danger(loc):
    return expr("Danger({})".format(locToString(loc)))

def visit(base, loc):
    if base.ask(unvisited(loc)) == {}:
      base.retract(unvisited(loc))
    base.tell(visited(loc))

def adjacent(src, dest):
    srcSquare = locToString(src)
    destSquare = locToString(dest)
    return expr("Adjacent({}, {})".format(srcSquare, destSquare))

def left(location):
    x, y = location
    return (x - 1), y

def right(location):
    x, y = location
    return (x + 1), y

def up(location):
    x, y = location
    return x, (y + 1)

def down(location):
    x, y = location
    return x, (y - 1)

def oppositeMove(move):
    if move[0] == 'F':
        return None
    if move == 'N':
        location = down(location)
        return 'S'
    elif move == 'S':
        location = up(location)
        return 'N'
    elif move == 'W':
        location = right(location)
        return 'E'
    else:
        location = left(location)
        return 'W'
    
def find_adjacent(location):
      adjacentSquares = []
      adjacentSquares.append(left(location))
      adjacentSquares.append(up(location))
      adjacentSquares.append(right(location))
      adjacentSquares.append(down(location))
      return adjacentSquares
    
def UpdateVisited(square):
    visit(base, square)

    # Make adjacent squares adjacent in KB
    for i in find_adjacent(square):
        base.tell(adjacent(square, i))

    # Make unvisited squares unvisited in KB
    for i in find_adjacent(square):
        if base.ask(visited(i)) == False:
            base.tell(unvisited(i))

def updateKB(percepts, square):
    # Deal with Percepts
    # Percept Strings:
    #   O - Bump
    #   S - Smell Wumpus
    #   B - Breeze
    #   Y - Scream of a Dying Wumpus
    for i in percepts:
        if i == 'O':
            # TODO: Deal with Bump
            pass
        elif i == 'S':
            if base.ask(stench(square)) == False:
              base.tell(stench(square))
        elif i == 'B':
            if base.ask(breeze(square)) == False:
              base.tell(breeze(square))
        elif i == 'Y':
            #TODO: Deal with Yell
            pass
        
def check_if_visited(location):
    if base.ask(visited(location)) == {}:
      return True
    return False

def checkForWumpae(location):
    if base.ask(expr('Stench(x)')) == False:
        return None
    
    for i in find_adjacent(location):
        if(base.ask(expr("Wumpus({})".format(locToString(i))))):
            return i
    return None

def addToHistory(move):
    history.append(move)
    return move

def shootWumpus(location, wumpusLocation):
    if left(location) == wumpusLocation:
        return 'FW'
    elif up(location) == wumpusLocation:
        return 'FN'
    elif right(location) == wumpusLocation:
        return 'FE'
    else:
        return 'FS'
    
def findSafeSquare(location):
    print(base.ask(expr('Danger(x)')))
    if base.ask(expr('Danger(x)')) == False:
        return None
    for i in find_adjacent(location):
        if base.ask(expr('Danger({})'.format(locToString(i)))) == False:
            return i
    return None

def makeMove(location, safe_square):
    if left(location) == safe_square:
        location = left(location)
        return 'W'
    elif up(location) == safe_square:
        location = up(location)
        return 'N'
    elif right(location) == safe_square:
        location = right(location)
        return 'E'
    else:
        location = down(location)
        return 'S'

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
    print(percept)
    if check_if_visited(location) == False:
        UpdateVisited(location)
    updateKB(percept, location)

    # Check for Wumpae to shoot
    WumpusLocation = checkForWumpae(location)
    if WumpusLocation != None:
        return addToHistory(shootWumpus(location, WumpusLocation))
    
    safe_square = findSafeSquare(location)
    if safe_square == None:
        return oppositeMove(history.pop(0))
    
    return addToHistory(makeMove(location, safe_square))