#!/usr/bin/env python

import logging
from pivy.gui.soqt import SoQtExaminerViewer
from PyQt4.QtGui import QWidget
from PyQt4 import QtCore, QtGui, QtOpenGL

from pivy import coin
from pivy.quarter import QuarterWidget
from superficie.util import callback, readFile, filePath
from superficie.utils import fluid

coin.SoCamera.upVector = property(lambda self: self.orientation.getValue() * coin.SbVec3f(0, 1, 0))
coin.SoCamera.cameraDirection = property(lambda self: self.orientation.getValue() * coin.SbVec3f(0, 0, -1))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def newPointAt(self, vec):
    self.position = vec + -self.cameraDirection


coin.SoCamera.newPointAt = newPointAt

coin.SbVec3f.__repr__ = lambda self: "SbVec3f(%f,%f,%f)" % self.getValue()

TransparencyType = [
    'SCREEN_DOOR, ADD',
    'DELAYED_ADD',
    'SORTED_OBJECT_ADD',
    'BLEND, DELAYED_BLEND',
    'SORTED_OBJECT_BLEND',
    'SORTED_OBJECT_SORTED_TRIANGLE_ADD',
    'SORTED_OBJECT_SORTED_TRIANGLE_BLEND',
    'NONE',
    'SORTED_LAYERS_BLEND'
]


class MinimalViewer(QWidget):
    """
    A QWidget which contains a child QuarterWidget
    """

    def __init__(self, colorLights=True):
        QWidget.__init__(self)
        self.setupSoQt()
        # camera defaults
        self.camera_point_at = [coin.SbVec3f(0, 0, 0), coin.SbVec3f(0, 0, 1)]
        self.camera_position = (7, 7, 7)
        # call viewAll when switching to a new page
        self.camera_viewAll = True
        # the scene root

        self.initializeViewer()
        self.setInitialCameraPosition()
        self.mouseEventCB = coin.SoEventCallback()
        self.getSRoot().addChild(self.mouseEventCB)
        if colorLights:
            self.addLights()
            self.setColorLightOn(True)
            # no need the default headlight in this case
            self.examiner.setHeadlight(False)

    def setupSoQt(self):
        self.root = self.getRoot()
        self.examiner = SoQtExaminerViewer(self)
        self.examiner.setSceneGraph(self.root)
        for attr in ["viewAll", "setDecoration", "setHeadlight", "setTransparencyType"]:
            setattr(self, attr, getattr(self.examiner, attr))

    def getRoot(self):
        return coin.SoSeparator()

    @fluid
    def addChild(self, node):
        self.root.addChild(getattr(node, "root", node))

    @property
    def camera(self):
        return self.examiner.getCamera()

    def setCameraPosition(self, position):
        self.__camera_position = self.camera.position
        self.camera.position = position
        logger.debug('setCameraPosition: %s, %s, %s', position, self.getCameraPosition(), self.camera)

    def getCameraPosition(self):
        return self.camera.position.getValue()

    cameraPosition = property(getCameraPosition, setCameraPosition)

    def setInitialCameraPosition(self):
        """Chose an adequate initial pov"""
        logger.debug('setInitialCameraPosition')
        self.setCameraPosition(self.camera_position)
        self.camera.pointAt(*self.camera_point_at)
        self.camera.farDistance = 25
        self.camera.nearDistance = .01

    def trackCameraPosition(self, val):
        if val:
            if not hasattr(self, "cameraSensor"):
                def print_pos(camera, sensor):
                    print "position:", camera.position.getValue()

                def print_or(camera, sensor):
                    print "orientation:", camera.orientation.getValue().getAxisAngle()

                self.cameraSensor = callback(self.camera.position, print_pos, self.camera)
                self.cameraSensor2 = callback(self.camera.orientation, print_or, self.camera)
            else:
                self.cameraSensor.attach(self.camera.position)
                self.cameraSensor2.attach(self.camera.orientation)
        elif hasattr(self, "cameraSensor"):
            self.cameraSensor.detach()
            self.cameraSensor2.detach()

    def addLights(self):
        self.colorLights = readFile(filePath("viewer", "lights.iv")).getChild(0)
        self.insertLight(self.colorLights)
        self.colorLights.whichChild = coin.SO_SWITCH_ALL

    def setColorLightOn(self, val):
        if self.colorLights:
            self.colorLights.whichChild = coin.SO_SWITCH_ALL if val else coin.SO_SWITCH_NONE

    def insertLight(self, luz):
        self.getSRoot().insertChild(luz, 0)

    def buildRotor(self):
        rotor = coin.SoRotor()
        rotor.on = False
        rotor.setName("rotor")
        rotor.speed = 0.005
        rotor.rotation = (0, 0, 1, 0)
        return rotor

    def initializeViewer(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setAlpha(True)
        QtOpenGL.QGLFormat.setDefaultFormat(fmt)
        self.rotor = self.buildRotor()
        hints = coin.SoShapeHints()
        hints.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = coin.SoShapeHints.SOLID
        hints.faceType = coin.SoShapeHints.CONVEX
        self.root.addChild(self.rotor)
        self.root.addChild(hints)

    def getSRoot(self):
        return self.examiner.getSceneManager().getSceneGraph()

    def toText(self, root):
        wa = coin.SoWriteAction()
        return wa.apply(root)

    def setStereoAdjustment(self, val):
        self.camera.setStereoAdjustment(val)


if __name__ == "__main__":
    import sys
    from pivy.gui.soqt import SoQt

    SoQt.init(None)
    app = QtGui.QApplication(sys.argv)
    visor = MinimalViewer()
    ## ============================
    visor.root.addChild(coin.SoCone())
    ## ============================
    visor.resize(400, 400)
    visor.show()
    visor.viewAll()

    sys.exit(app.exec_())
