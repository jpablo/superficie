import sys
from PyQt4 import QtGui
from superficie.plots import Plot3D
from superficie.viewer import MinimalViewer
from superficie.util import _1

app = QtGui.QApplication(sys.argv)

viewer = MinimalViewer()
plot = Plot3D(lambda x, y: x ** 3 - 3 * x * y ** 2 + 2.5, (-1, 1), (-1, 1))
plot.setAmbientColor(_1(145, 61, 74)).setDiffuseColor(_1(127, 119, 20)).setSpecularColor(_1(145, 61, 74))
viewer.addChild(plot)

viewer.resize(400, 400)
viewer.show()
viewer.viewAll()

sys.exit(app.exec_())


