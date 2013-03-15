import sys
from math import pi, sin, cos
from PyQt4 import QtGui
from superficie.plots import RevolutionPlot3D
from superficie.viewer import MinimalViewer

app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()

plot = RevolutionPlot3D(lambda r, t: r ** 2 + z, (0.0001, 1), (0, 2 * pi))

viewer.addChild(plot).viewAll().resize(400, 400)
viewer.show()
sys.exit(app.exec_())


