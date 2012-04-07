#from pivy.gui.soqt import *
from Animation import Animation

modulosPath = "superficie"

def setWhichChildCB(switch, n):
    if not n:
        switch.whichChild = -1
    elif n == 2:
        switch.whichChild = 0



