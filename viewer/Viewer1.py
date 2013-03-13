#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtOpenGL
#import logging

from pivy.coin import *
try:
    from pivy.quarter import QuarterWidget
    Quarter = True
except ImportError:
    from pivy.gui.soqt import *
    Quarter = False
from superficie.util import callback
from superficie.util import conecta
from superficie.util import filePath
from superficie.util import readFile
from superficie.Book import Book

#modulosPath = "superficie"
#log = logging.getLogger("Viewer")
#log.setLevel(logging.DEBUG)


def getPickedPoint(root, myPickAction, cursorPosition):
    myPickAction.setPoint(cursorPosition)
    myPickAction.setRadius(8.0)
    myPickAction.setPickAll(True)
    myPickAction.apply(root)
    return myPickAction.getPickedPointList()

TransparencyType= [
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

class Viewer(Book,QWidget):
    "Viewer"

    ## this should be on Book, but then we couldn't derive
    ## from it because PyQt only suppor one base clase derived
    ## from QObject
    chapterChanged = QtCore.pyqtSignal(int)

    def __init__(self,parent=None,uiLayout=None,luces=True):
        QWidget.__init__(self,parent)
        Book.__init__(self)
        # ============================
        fmt = QtOpenGL.QGLFormat()
        fmt.setAlpha(True)
        QtOpenGL.QGLFormat.setDefaultFormat(fmt)
        self.moviendo = False
        self.moviendoOb = None
        ## ============================
        self.inicializarVisor(luces)
        self.inicializarUi(uiLayout)

    ## TODO: investigate why this function is never called
    @property
    def whichChapter(self):
        print "Viewer.whichChapter.getter"
        return Book.whichChapter.fget(self)

    @Book.whichChapter.setter
    def whichChapter(self,n):
        self.chapterChanged.emit(n)
        Book.whichChapter.fset(self,n)


    def getCamera(self):
        if Quarter:
            return self.viewer.getSoRenderManager().getCamera()
        else:
            return self.viewer.getCamera()


    def setStereoAdjustment(self, val):
        camera = self.getCamera()
        camera.setStereoAdjustment(val)

    def rotacionInicial(self):
        "Chose an adecuate initial pov"
        camera = self.getCamera()
        camera.position = (7,7,7)
        camera.pointAt(SbVec3f(0, 0, 0),  SbVec3f(0, 0, 1))
        camera.farDistance = 25
        camera.nearDistance = .01

    def trackCameraPosition(self, val):
        if val:
            camera = self.getCamera()
            if not hasattr(self, "cameraSensor"):
                def fn(camera, sensor):
                    print camera.position.getValue().getValue()
                self.cameraSensor = callback(camera.position, fn, camera)
            else:
                self.cameraSensor.attach(camera.position)
        elif hasattr(self, "cameraSensor"):
            self.cameraSensor.detach()

    def agregaLuces(self, root):
        self.lucesColor = readFile(filePath("Viewer","lights.iv")).getChild(0)
        self.insertaLuz(self.lucesColor)
        self.lucesColor.whichChild = SO_SWITCH_ALL
        ## ============================
        self.lucesBlanca = SoDirectionalLight()
        self.insertaLuz(self.lucesBlanca)
        self.lucesBlanca.on = False

    def setColorLightOn(self, val):
        if val:
            self.lucesColor.whichChild = SO_SWITCH_ALL
        else:
            self.lucesColor.whichChild = SO_SWITCH_NONE

    def setWhiteLightOn(self, val):
        self.lucesBlanca.on = val

    def insertaLuz(self, luz):
        self.getSRoot().insertChild(luz, 0)

    def inicializarVisor(self, luces):
        if Quarter:
            self.viewer = QuarterWidget()
            layout = QtGui.QVBoxLayout()
            self.setLayout(layout)
            layout.addWidget(self.viewer)
        else:
            self.viewer = SoQtExaminerViewer(self)
        ## metodos disponibles:
        # viewAll
        # setTransparencyType
        # setSceneGraph
        ## ============================
        ## copy some attributes
        if Quarter:
            for attr in ["viewAll", "setTransparencyType"]:
                setattr(self, attr, getattr(self.viewer, attr))
        else:
            for attr in ["viewAll", "setDecoration", "setHeadlight", "setTransparencyType"]:
                setattr(self, attr, getattr(self.viewer, attr))
        ## ============================
        self.viewer.setSceneGraph(self.root)
        if not Quarter:
            self.viewer.setAlphaChannel(True)
            self.viewer.setTransparencyType(SoGLRenderAction.SORTED_LAYERS_BLEND)
            self.viewer.setTransparencyType(SoGLRenderAction.SORTED_OBJECT_BLEND)
            self.viewer.setAntialiasing(True, 0)
            self.viewer.setWireframeOverlayColor(SbColor(0.5, 0, 0))
            self.viewer.setHeadlight(False)
            self.viewer.setFeedbackVisibility(False)
            self.viewer.setDecoration(False)
        ## en la sala ixtli
#        self.viewer.setStereoType(SoQtViewer.STEREO_QUADBUFFER)
        ## en el resto del mundo
#        self.viewer.setStereoType(SoQtViewer.STEREO_ANAGLYPH)
        ## esto es principalmente por los poliedros
#        if not noestiloIni:
#        self.setDrawStyle(SoQtViewer.VIEW_WIREFRAME_OVERLAY)
        ## ============================
        self.mouseEventCB = SoEventCallback()
        self.getSRoot().addChild(self.mouseEventCB)
        ## ============================
        ## esto es un poco pesado
        rotor = SoRotor()
        rotor.on = False
        rotor.setName("rotor")
        rotor.speed = 0.005
        rotor.rotation = (0,0,1,0)
        self.root.addChild(rotor)
        self.rotor = rotor
        ## ============================
        self.rotacionInicial()
        self.setStereoAdjustment(.2)
        ## ===========================
        if luces:
            self.agregaLuces(self.root)
        hints = SoShapeHints()
        hints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = SoShapeHints.SOLID
        hints.faceType = SoShapeHints.CONVEX
        self.root.addChild(hints)
        ## ============================
#        self.capturaMouseClicked(self.mouse1Clicked, self.mouse2Clicked)
#        self.capturaMouseMoved(self.mouseMoved)


    def inicializarUi(self,uilayout):
        self.chaptersStack = QtGui.QStackedWidget()
#        self.chaptersStack.setStyleSheet("QWidget { background:green }")
        if uilayout:
            uilayout.addWidget(self.chaptersStack)
        ## ========================================
#        self.options = QWidget()
#        uic.loadUi(modulosPath + "Visor/options-visor.ui",self)
#        self.visorPropertiesFrame.setParent(self.options)

    @QtCore.pyqtSignature("bool")
    def on_axisButton_clicked(self,b):
        self.ejes.show(b)

    def getSRoot(self):
        if Quarter:
            return self.viewer.getSoRenderManager().getSceneGraph()
        else:
            return self.viewer.getSceneManager().getSceneGraph()

    def mouseMoved(self, pickedList):
        chapterob = self.getChapterObject()
        if hasattr(chapterob, "mouseMoved"):
            chapterob.mouseMoved(pickedList)

    def mouse1Clicked(self, pickedList):
        chapterob = self.getChapterObject()
        if hasattr(chapterob, "mouse1Clicked"):
            chapterob.mouse1Clicked(pickedList)

    def mouse2Clicked(self, pickedList):
        chapterob = self.getChapterObject()
        if hasattr(chapterob, "mouse2Clicked"):
            chapterob.mouse2Clicked(pickedList)


    def capturaMouseClicked(self, slot1,  slot2 = None):
        "target es el objeto en el que estamos interesados"
        self.mouseEventCB.addEventCallback(SoMouseButtonEvent.getClassTypeId(),self.mousePressCB)
        conecta(self, QtCore.SIGNAL("mouse1Clicked"), slot1)
        if slot2 != None:
            conecta(self, QtCore.SIGNAL("mouse2Clicked"), slot2)

    def mousePressCB(self, userData,  eventCB):
        sroot = self.getSRoot()
        event = eventCB.getEvent()
        viewport = eventCB.getAction().getViewportRegion()
        cursorPosition = event.getPosition(viewport)
        ## ============================
        pickAction = SoRayPickAction(viewport)
        myPickedPointList = getPickedPoint(sroot, pickAction, cursorPosition)
        ## ============================
        if myPickedPointList.getLength() == 0:
            return FALSE
        if SoMouseButtonEvent.isButtonPressEvent(event, SoMouseButtonEvent.BUTTON1):
            self.emit(QtCore.SIGNAL("mouse1Clicked"), myPickedPointList)
            self.toggleEventMouseMoved(True)
            self.moviendo = True
            eventCB.setHandled()
        elif SoMouseButtonEvent.isButtonReleaseEvent(event, SoMouseButtonEvent.BUTTON1):
            self.moviendo = False
            self.moviendoOb = None
            self.toggleEventMouseMoved(False)
            eventCB.setHandled()
        elif SoMouseButtonEvent.isButtonPressEvent(event, SoMouseButtonEvent.BUTTON2):
            self.emit(QtCore.SIGNAL("mouse2Clicked"), myPickedPointList)
            eventCB.setHandled()

    def toggleEventMouseMoved(self, val):
        "Activa/desactiva el rastreo del movimiento del mouse"
        ## TODO: arreglar esto
        if val:
            self.mouseEventCB.addEventCallback(SoLocation2Event.getClassTypeId(),self.mouseMoveCB)
        else:
            ## esto marca un error, no tengo idea porqué
            self.mouseEventCB.removeEventCallback(SoLocation2Event.getClassTypeId(),self.mouseMoveCB)

    def mouseMoveCB(self, userData,  eventCB):
        print "mouseMoveCB"
        if self.moviendo:
            event = eventCB.getEvent()
            viewport = eventCB.getAction().getViewportRegion()
            cursorPosition = event.getPosition()
            sroot = self.getSRoot()
            pickAction = SoRayPickAction(viewport)
            myPickedPointList = getPickedPoint(sroot, pickAction, cursorPosition)
            if myPickedPointList.getLength() == 0:
                return FALSE
            self.emit(QtCore.SIGNAL("mouseMoved"), myPickedPointList)
            eventCB.setHandled()

    def capturaMouseMoved(self, slot):
        "Esta funcion es utilizada por el usuario"
        conecta(self, QtCore.SIGNAL("mouseMoved"), slot)

    def setDrawStyle(self,type):
        print "not implemented"
        return
#        self.viewer.setDrawStyle(SoQtExaminerViewer.STILL, type)

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

    if Quarter:
        sys.exit(app.exec_())
    else:
        SoQt.mainLoop()
