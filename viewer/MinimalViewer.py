#!/usr/bin/env python

import logging
from PyQt4.QtGui import QWidget
from PyQt4 import QtCore, QtGui, QtOpenGL

from pivy import coin
from pivy.quarter import QuarterWidget
from superficie.util import callback, readFile, pegaNombres


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
    def __init__(self):
        QWidget.__init__(self)
        # camera defaults
        self.camera_point_at = [coin.SbVec3f(0, 0, 0), coin.SbVec3f(0, 0, 1)]
        self.camera_position = (7, 7, 7)
        # call viewAll when switching to a new page
        self.camera_viewAll = True

        self.root = coin.SoSeparator()
        self.initializeViewer(True)

    def setCameraPosition(self, position):
        self.__camera_position = self.camera.position
        self.camera.position = position
        logger.debug('setCameraPosition: %s, %s, %s', position, self.getCameraPosition(), self.camera)

    def getCameraPosition(self):
        return self.camera.position.getValue()

    cameraPosition = property(getCameraPosition, setCameraPosition)

    def setInitialCameraPosition(self):
        """Chose an adecuate initial pov"""
        logger.debug('setInitialCameraPosition')
        self.setCameraPosition(self.camera_position)
        self.camera.pointAt(*self.camera_point_at)
        self.camera.farDistance = 25
        self.camera.nearDistance = .01

    def trackCameraPosition(self, val):
        if val:
            if not hasattr(self, "cameraSensor"):
                def ppos(camera, sensor):
                    print "position:", camera.position.getValue()

                def por(camera, sensor):
                    print "orientation:", camera.orientation.getValue().getAxisAngle()

                self.cameraSensor = callback(self.camera.position, ppos, self.camera)
                self.cameraSensor2 = callback(self.camera.orientation, por, self.camera)
            else:
                self.cameraSensor.attach(self.camera.position)
                self.cameraSensor2.attach(self.camera.orientation)
        elif hasattr(self, "cameraSensor"):
            self.cameraSensor.detach()
            self.cameraSensor2.detach()

    def addLights(self):
        self.colorLights = readFile(pegaNombres("viewer", "lights.iv")).getChild(0)
        self.insertLight(self.colorLights)
        self.colorLights.whichChild = coin.SO_SWITCH_ALL
        ## ============================
        self.whiteLight = coin.SoDirectionalLight()
        self.insertLight(self.whiteLight)
        self.whiteLight.on = False

    def setColorLightOn(self, val):
        if val:
            self.colorLights.whichChild = coin.SO_SWITCH_ALL
        else:
            self.colorLights.whichChild = coin.SO_SWITCH_NONE

    def setWhiteLightOn(self, val):
        self.whiteLight.on = val

    def insertLight(self, luz):
        self.getSRoot().insertChild(luz, 0)

    def viewAll(self):
        self.viewer.viewAll()

    def setTransparencyType(self, tr_type):
        self.viewer.setTransparencyType(tr_type)

    def initializeViewer(self, lights):
        fmt = QtOpenGL.QGLFormat()
        fmt.setAlpha(True)
        QtOpenGL.QGLFormat.setDefaultFormat(fmt)
        self.viewer = QuarterWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.viewer)
        self.setLayout(layout)
        self.viewer.setSceneGraph(self.root)
        self.mouseEventCB = coin.SoEventCallback()
        self.getSRoot().addChild(self.mouseEventCB)
        rotor = coin.SoRotor()
        rotor.on = False
        rotor.setName("rotor")
        rotor.speed = 0.005
        rotor.rotation = (0, 0, 1, 0)
        self.root.addChild(rotor)
        self.rotor = rotor
        self.camera = self.viewer.getSoRenderManager().getCamera()
        self.setInitialCameraPosition()
        if lights:
            self.addLights()
        hints = coin.SoShapeHints()
        hints.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = coin.SoShapeHints.SOLID
        hints.faceType = coin.SoShapeHints.CONVEX
        self.root.addChild(hints)

    def getSRoot(self):
        return self.viewer.getSoRenderManager().getSceneGraph()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    visor = MinimalViewer()
    ## ============================
    visor.root.addChild(coin.SoCone())
    ## ============================
    visor.resize(400, 400)
    visor.show()
    visor.viewAll()

    sys.exit(app.exec_())
