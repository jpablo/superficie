import sys
from PyQt4 import QtGui
from superficie.plots import Plot3D
from superficie.viewer import Viewer
from superficie.util import _1

app = QtGui.QApplication(sys.argv)
viewer = Viewer()
viewer.book.createChapter()
viewer.chapter.createPage()

z = 1.5
surface = Plot3D(lambda x, y: x ** 2 - y ** 2 + z, (-1, 1), (-1, 1))
chart = Plot3D(lambda x, y: h * (x ** 2 - y ** 2 + z), (-1, 1), (-1, 1))
surface.setAmbientColor(_1(145, 61, 74)).setDiffuseColor(_1(127, 119, 20)).setSpecularColor(_1(145, 61, 74))
chart.setLinesVisible(True).setMeshVisible(False)

viewer.page.addChild(surface)
viewer.page.addChild(chart)
viewer.viewAll()
viewer.resize(400, 400)
viewer.show()
viewer.chaptersStack.show()
sys.exit(app.exec_())


