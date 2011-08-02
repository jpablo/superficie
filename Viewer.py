#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget
from PyQt4 import QtCore, QtGui, QtOpenGL

from pivy.coin import *
from pivy.quarter import QuarterWidget
Quarter = True
from util import callback, pegaNombres, readFile
from Book import Book
from superficie import globals


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
        self.book = Book(self)
        #=======================================================================
        # Copiamos algunos atributos de book
        #=======================================================================
        self.root = self.book.root
        self.createChapter = self.book.createChapter
        self.addChapter = self.book.addChapter
        self.chaptersStack = self.book.chaptersStack
        self.notasStack = self.book.notasStack
        #=======================================================================
        self.initializeViewer(luces)
        self.initializeUI(uiLayout,notasLayout)
        #=======================================================================
        self.book.pageChanged.connect(self.onPageChanged)
        self.book.chapterChanged.connect(self.onChapterChanged)


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
        
    def onPageChanged(self, c, n):
        self.viewAll()
        
    def onChapterChanged(self, c):
        self.viewAll()

    @property
    def camera(self):
        """Gets the camera"""
        return self.viewer.getSoRenderManager().getCamera()

    def setCameraPosition(self, position):
        self.camera.position = position

    def getCameraPosition(self):
        return self.camera.position.getValue().getValue()

    cameraPosition = property(getCameraPosition, setCameraPosition)

    def setInitialCameraPosition(self):
        """Chose an adecuate initial pov"""
        self.camera.position = (7, 7, 7)
        self.camera.pointAt(SbVec3f(0, 0, 0), SbVec3f(0, 0, 1))
        self.camera.farDistance = 25
        self.camera.nearDistance = .01

    def trackCameraPosition(self, val):
        if val:
            if not hasattr(self, "cameraSensor"):
                def fn(camera, sensor):
                    print camera.position.getValue().getValue()
                self.cameraSensor = callback(self.camera.position, fn, self.camera)
            else:
                self.cameraSensor.attach(self.camera.position)
        elif hasattr(self, "cameraSensor"):
            self.cameraSensor.detach()

    def addLights(self):
        self.lucesColor = readFile(pegaNombres("Viewer", "lights.iv")).getChild(0)
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

    def initializeViewer(self, luces):
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
        ## copy some attributes
        for attr in ["viewAll", "setTransparencyType"]:
            setattr(self, attr, getattr(self.viewer, attr))
        ## ============================
        self.viewer.setSceneGraph(self.root)
        ## ============================
        self.mouseEventCB = SoEventCallback()
        self.getSRoot().addChild(self.mouseEventCB)
        ## ============================
        ## esto es un poco pesado
        rotor = SoRotor()
        rotor.on = False
        rotor.setName("rotor")
        rotor.speed = 0.005
        rotor.rotation = (0, 0, 1, 0)
        self.root.addChild(rotor)
        self.rotor = rotor
        ## ============================
        self.setInitialCameraPosition()
        ## ===========================
        if luces:
            self.addLights()
        hints = SoShapeHints()
        hints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = SoShapeHints.SOLID
        hints.faceType = SoShapeHints.CONVEX
        self.root.addChild(hints)


    def initializeUI(self, uilayout,notasLayout):
        if uilayout is not None:
            uilayout.addWidget(self.chaptersStack)
        if notasLayout is not None:
            notasLayout.addWidget(self.notasStack)

    @QtCore.pyqtSignature("bool")
    def on_axisButton_clicked(self, b):
        self.ejes.show(b)

    def getSRoot(self):
        if Quarter:
            return self.viewer.getSoRenderManager().getSceneGraph()
        else:
            return self.viewer.getSceneManager().getSceneGraph()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    visor = Viewer()
    ## ============================
    visor.createChapter()
    ## ============================
    visor.chapter.createPage()
    sep = SoSeparator()
    sep.getGui = lambda: QtGui.QLabel("<center><h1>Esfera+Cono</h1></center>")
    esfera = SoSphere()
    cono = SoCone()
    sep.addChild(esfera)
    sep.addChild(cono)
    visor.page.addChild(sep)
    ## ============================
    visor.chapter.createPage()
    cubo = SoCube()
    cubo.getGui = lambda: QtGui.QLabel("<center><h1>Cubo</h1></center>")
    visor.page.addChild(cubo)
    ## ============================
    visor.whichPage = 0
    visor.resize(400, 400)
    visor.show()
    visor.chaptersStack.show()
    
    sys.exit(app.exec_())
