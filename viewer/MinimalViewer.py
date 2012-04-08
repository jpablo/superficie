from PyQt4.QtGui import QWidget
from PyQt4 import QtCore, QtGui, QtOpenGL

from pivy.coin import *
from pivy.quarter import QuarterWidget
from superficie.util import callback, readFile, pegaNombres



class MinimalViewer(QWidget):

    def __init__(self):
        super(MinimalViewer, self).__init__()
        self.root = SoSeparator()
        self.initializeViewer(True)

    def initializeViewer(self, lights):
        # ============================
        fmt = QtOpenGL.QGLFormat()
        fmt.setAlpha(True)
        QtOpenGL.QGLFormat.setDefaultFormat(fmt)
        self.viewer = QuarterWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.viewer)
        self.setLayout(layout)
        ## ============================
        ## copy some attributes
        for attr in ["viewAll", "setTransparencyType"]:
            setattr(self, attr, getattr(self.viewer, attr))
        ## ============================
        self.viewer.setSceneGraph(self.root)
        self.setInitialCameraPosition()
        if lights:
            self.addLights()
        hints = SoShapeHints()
        hints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = SoShapeHints.SOLID
        hints.faceType = SoShapeHints.CONVEX
        self.root.addChild(hints)

    @property
    def camera(self):
        return self.viewer.getSoRenderManager().getCamera()

    def setInitialCameraPosition(self):
        """Chose an adecuate initial pov"""
        self.camera.position = (7, 7, 7)
        self.camera.pointAt(SbVec3f(0, 0, 0), SbVec3f(0, 0, 1))
        self.camera.farDistance = 25
        self.camera.nearDistance = .01


    def addLights(self):
#        self.lucesColor = readFile(pegaNombres("Viewer", "lights.iv")).getChild(0)
#        self.insertLight(self.lucesColor)
#        self.lucesColor.whichChild = SO_SWITCH_ALL
        ## ============================
        self.whiteLight = SoDirectionalLight()
        self.insertLight(self.whiteLight)
        self.whiteLight.on = False


    def insertLight(self, light):
        self.getSRoot().insertChild(light, 0)

    def getSRoot(self):
        return self.viewer.getSoRenderManager().getSceneGraph()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    visor = MinimalViewer()
    ## ============================
    visor.root.addChild(SoCone())
    ## ============================
    visor.resize(400, 400)
    visor.show()
    visor.viewAll()

    sys.exit(app.exec_())
