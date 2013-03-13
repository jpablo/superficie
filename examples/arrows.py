import sys
from PyQt4 import QtGui
from superficie.nodes.arrow import Arrow
from superficie.nodes.line import Line

from superficie.viewer import MinimalViewer

x = [(0, 0, 0), (1, 0, 0)]
y = [(0, 0, 0), (0, 1, 0)]
z = [(0, 0, 0), (0, 0, 1)]

lx = Line(x, width=5).setColor((1, 0, 0))
ly = Line(y, width=7).setColor((0, 1, 0))
lz = Line(z, width=5).setColor((0, 0, 1))

ob = Arrow((0, .05, 0), (1, .05, 0))
# ob.toText()
ob2 = Arrow(*y).setWidthFactor(.5)
ob3 = Arrow(*z)

app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()
viewer.addChild(ob)
viewer.addChild(ob2)
viewer.addChild(ob3)
viewer.addChild(lx)
viewer.addChild(ly)
viewer.addChild(lz)

viewer.resize(400, 400)
viewer.show()
viewer.viewAll()

sys.exit(app.exec_())

