from logic import *
from utils import *

def setup_KB(base):
    base.tell(expr("Stench(X)"))
    base.tell(expr("Adjacent(X, Y)"))
    base.tell(expr("Breeze(X)"))
    base.tell(expr("Visited(X)"))
    base.tell(expr("Safe(X) <=> ~Wumpus(X) & ~Pit(X)"))
    base.tell(expr("Safe(X) <== Visited(X)"))
    base.tell(expr("Wumpus(X) <== ~Visited(X) & Stench(Y) & Adjacent(X, Y) & Stench(Z) & Adjacent(X, Z)"))
    base.tell(expr("Pit(X) <== ~Visited(X) & Breeze(Y) & Adjacent(X, Y) & Breeze(Z) & Breeze(X, Z)"))
    base.tell(expr("Pit(X) ==> ~Safe(X)"))
    base.tell(expr("Wumpus(X) ==> ~Safe(X)"))
    base.tell(expr("Danger(X) <== Breeze(Y) & Adjacent(X, Y)"))
    base.tell(expr("Danger(X) <== Stench(Y) & Adjacent(X, Y)"))

base = PropKB()
setup_KB(base)

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

    # NOTE: kb.ask_if_true(EXPR) is good for checking KB
    size = None
    # origin is always (0, 0)
    location = (0, 0)
    #TODO: Improve upon this agent!
    return "N"
