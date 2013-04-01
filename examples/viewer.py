import sys
from PyQt4 import QtGui
from superficie.viewer import MinimalViewer
from superficie.util import readFile


app = QtGui.QApplication(sys.argv)
viewer = MinimalViewer()
input = readFile('sample.iv')
viewer.addChild(input)
viewer.toText(viewer.getSRoot())
viewer.resize(400, 400)
viewer.show()
viewer.viewAll()

sys.exit(app.exec_())

