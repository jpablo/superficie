import sys
from math import pi, sin, cos
from PyQt4 import QtGui
from superficie.plots import ParametricPlot3D
from superficie.viewer import MinimalViewer

app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()

a = 1
b = 0.5
c = .505


def torus(u, v):
    return (a + b * cos(v)) * cos(u), (a + b * cos(v)) * sin(u), b * sin(v)

plot = ParametricPlot3D(torus, (0, 2 * pi, 150), (0, 2 * pi, 100))

viewer.addChild(plot).viewAll().resize(400, 400)
viewer.show()
sys.exit(app.exec_())


