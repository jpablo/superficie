import sys
from PyQt4 import QtGui
from superficie.plots import Plot3D
from superficie.viewer import MinimalViewer

app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()

function = lambda x, y: .5 * x ** 3 - .5 * 3 * x * y ** 2 + 2.5
x_range = (-1, 1)
y_range = (-1, 1)
plot = Plot3D(function, x_range, y_range)

# add the object to the scene
viewer.addChild(plot)
# adjust the camera and rotation center
viewer.viewAll()
viewer.resize(400, 400)
viewer.show()
sys.exit(app.exec_())


