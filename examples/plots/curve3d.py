import sys
from math import exp, sin, cosh, tanh, cos, tan, pi
from PyQt4 import QtGui
from superficie.nodes import Curve3D
from superficie.viewer import MinimalViewer

app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()

r = 3
m = tan(pi / 60)
t0 = pi / 2


def sigmoid(t):
    return abs(2.0/(1+exp(-(t/15.0)))-1)


def loxodrome(t):
    t = t * sigmoid(t)
    return r * cos(-t) / cosh(m * (-t - t0)), r * sin(-t) / cosh(m * (-t - t0)), r * tanh(m * (-t - t0))

# max_distance and max_angle are hints for the refinement algorithm (optionals)
curve = Curve3D(loxodrome, (-75, 60, 10), width=1, max_distance=.3, max_angle=.2)

viewer.addChild(curve).viewAll().resize(400, 400)
viewer.show()
sys.exit(app.exec_())


