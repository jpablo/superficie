import sys
from PyQt4 import QtGui
from superficie.plots import Plot3D
from superficie.viewer import MinimalViewer


app = QtGui.QApplication(sys.argv)

viewer = MinimalViewer()
plot = Plot3D(lambda x, y: .5 * x ** 3 - .5 * 3 * x * y ** 2 + 2.5, (-1, 1), (-1, 1))
viewer.addChild(plot)
viewer.resize(400, 400)
viewer.show()
viewer.viewAll()

sys.exit(app.exec_())


