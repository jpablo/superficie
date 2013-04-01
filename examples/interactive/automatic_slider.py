import sys
from PyQt4 import QtGui
from superficie.plots import ParametricPlot3D, Plot3D
from superficie.viewer import Viewer
from superficie.util import _1

app = QtGui.QApplication(sys.argv)
viewer = Viewer()
viewer.book.createChapter()
viewer.chapter.createPage()

z = 1.5

# the graph of an hyperbolic paraboloid
surface = Plot3D(
    lambda x, y: x ** 2 - y ** 2 + z,
    (-1, 1), (-1, 1)
)
# the third argument 'h' will be noticed and assumed to be a parameter
# a slider will be generated
chart = Plot3D(
    lambda x, y, h: h * (x ** 2 - y ** 2 + z),
    (-1, 1), (-1, 1)
).setLinesVisible(True).setMeshVisible(False)

viewer.page.addChild(surface)
viewer.page.addChild(chart)
viewer.viewAll()
viewer.resize(400, 400)
viewer.show()
viewer.chaptersStack.show()
sys.exit(app.exec_())


