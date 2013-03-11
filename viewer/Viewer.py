#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PyQt4.QtGui import QWidget
from PyQt4 import QtCore, QtGui, QtOpenGL

from pivy.coin import *
from pivy.quarter import QuarterWidget
from superficie.book import Book

from superficie.util import callback, pegaNombres, readFile
from superficie import globals

SoCamera.upVector = property(lambda self: self.orientation.getValue() * SbVec3f(0,1,0))
SoCamera.cameraDirection = property(lambda self: self.orientation.getValue() * SbVec3f(0,0,-1))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def newPointAt(self, vec):
    self.position = vec + -self.cameraDirection

SoCamera.newPointAt = newPointAt

SbVec3f.__repr__ = lambda self: "SbVec3f(%f,%f,%f)" % self.getValue()

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


class Viewer(QWidget):

    def __init__(self, parent=None, uiLayout=None, notasLayout=None, luces=True):
        super(Viewer, self).__init__(parent)
        globals.ViewerInstances.append(self)
        # camera defaults
        self.camera_point_at = [SbVec3f(0, 0, 0), SbVec3f(0, 0, 1)]
        self.camera_position = (7, 7, 7)
        # call viewAll when switching to a new page
        self.camera_viewAll = True
        self.book = Book()
        # copy some attributes from book
        self.root = self.book.root
        self.createChapter = self.book.createChapter
        self.addChapter = self.book.addChapter
        self.chaptersStack = self.book.chaptersStack
        self.notasStack = self.book.notasStack
        #=======================================================================
        self.initializeViewer(luces)
        self.initializeUI(uiLayout, notasLayout)
        #=======================================================================
        self.book.pageChanged.connect(self.adjustCameraForPage)
        # self.book.chapterChanged.connect(self.onChapterChanged)

    def slot(self):
        print "Viewer.slot"

    def getWhichPage(self):
        return self.chapter.whichPage

    def setWhichPage(self, n):
        self.chapter.whichPage = n

    whichPage = property(getWhichPage, setWhichPage)

    @property
    def chapter(self):
        return self.book.chapter

    def getWhichChapter(self):
        """returns the selected chapter"""
        return self.book.whichChapter

    def setWhichChapter(self, n):
        self.book.whichChapter = n

    whichChapter = property(getWhichChapter, setWhichChapter)

    @property
    def page(self):
        return self.book.page

    @staticmethod
    def Instance():
        return globals.ViewerInstances[-1]

    def adjustCameraForPage(self, page, n):
        logger.debug('adjustCameraForPage %s', n)
        if page.camera_position:
            self.setCameraPosition(page.camera_position)
        else:
            self.setCameraPosition(self.camera_position)
        if page.camera_point_at:
            self.camera.pointAt(*page.camera_point_at)
        else:
            self.camera.pointAt(*self.camera_point_at)
        if page.camera_viewAll:
            self.viewAll()

    # def onChapterChanged(self, c):
    #     logger.debug('onChapterChanged %s', c)
    #     self.viewAll()

#    @property
#    def camera(self):
#        """Gets the camera"""
#        return self.viewer.getSoRenderManager().getCamera()

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
#                    axis,angle = camera.orientation.getValue().getAxisAngle()
#                    print "rotation: {"
#                    print "\taxis:", axis
#                    print "\tvalue:", angle
#                    print "}"
                self.cameraSensor = callback(self.camera.position, ppos, self.camera)
                self.cameraSensor2 = callback(self.camera.orientation, por, self.camera)
            else:
                self.cameraSensor.attach(self.camera.position)
                self.cameraSensor2.attach(self.camera.orientation)
        elif hasattr(self, "cameraSensor"):
            self.cameraSensor.detach()
            self.cameraSensor2.detach()

    def addLights(self):
        self.lucesColor = readFile(pegaNombres("viewer", "lights.iv")).getChild(0)
        self.insertLight(self.lucesColor)
        self.lucesColor.whichChild = SO_SWITCH_ALL
        ## ============================
        self.lucesBlanca = SoDirectionalLight()
        self.insertLight(self.lucesBlanca)
        self.lucesBlanca.on = False

    def setColorLightOn(self, val):
        if val:
            self.lucesColor.whichChild = SO_SWITCH_ALL
        else:
            self.lucesColor.whichChild = SO_SWITCH_NONE

    def setWhiteLightOn(self, val):
        self.lucesBlanca.on = val

    def insertLight(self, luz):
        self.getSRoot().insertChild(luz, 0)

    def viewAll(self):
        # logger.debug('Viewer.viewAll')
        self.viewer.viewAll()

    def setTransparencyType(self, tr_type):
        self.viewer.setTransparencyType(tr_type)

    def initializeViewer(self, lights):
        # ============================
        fmt = QtOpenGL.QGLFormat()
        fmt.setAlpha(True)
        QtOpenGL.QGLFormat.setDefaultFormat(fmt)
        # ============================
        self.viewer = QuarterWidget()
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.viewer)
        ## ============================
        self.viewer.setSceneGraph(self.root)
        ## ============================
        self.mouseEventCB = SoEventCallback()
        self.getSRoot().addChild(self.mouseEventCB)
        ## ============================
        rotor = SoRotor()
        rotor.on = False
        rotor.setName("rotor")
        rotor.speed = 0.005
        rotor.rotation = (0, 0, 1, 0)
        self.root.addChild(rotor)
        self.rotor = rotor
        ## ============================
        self.camera = self.viewer.getSoRenderManager().getCamera()
        self.setInitialCameraPosition()
        ## ===========================
        if lights:
            self.addLights()
        hints = SoShapeHints()
        hints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = SoShapeHints.SOLID
        hints.faceType = SoShapeHints.CONVEX
        self.root.addChild(hints)

    def initializeUI(self, uiLayout, notasLayout):
        if uiLayout is not None:
            uiLayout.addWidget(self.chaptersStack)
        if notasLayout is not None:
            notasLayout.addWidget(self.notasStack)

    @QtCore.pyqtSignature("bool")
    def on_axisButton_clicked(self, b):
        self.ejes.show(b)

    def getSRoot(self):
        return self.viewer.getSoRenderManager().getSceneGraph()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    viewer = Viewer()
    ## ============================
    viewer.createChapter()
    ## ============================
    viewer.chapter.createPage()
    sep = SoSeparator()
    sep.getGui = lambda: QtGui.QLabel("<center><h1>Sphere+Cone</h1></center>")
    sphere = SoSphere()
    cone = SoCone()
    sep.addChild(sphere)
    sep.addChild(cone)
    viewer.page.addChild(sep)
    ## ============================
    viewer.chapter.createPage()
    cube = SoCube()
    cube.getGui = lambda: QtGui.QLabel("<center><h1>Cubo</h1></center>")
    viewer.page.addChild(cube)
    ## ============================
    viewer.whichPage = 0
    viewer.resize(400, 400)
    viewer.show()
    viewer.chaptersStack.show()

    sys.exit(app.exec_())
