#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic
import logging
from pivy.quarter import QuarterWidget
from pivy.coin import *
from pivy.gui.soqt import *
import superficie.base
from superficie.util import callback
from superficie.util import conecta
from superficie.util import nodeDict
from superficie.util import main
from superficie.util import pegaNombres
from superficie.util import readFile

#modulosPath = "superficie"


log = logging.getLogger("Viewer")
log.setLevel(logging.DEBUG)

cambia_figura_fclass, base_class = uic.loadUiType(pegaNombres("Viewer","change-page.ui"))

## para no tener que cargar el mismo archivo varias veces
class CambiaFigura(base_class, cambia_figura_fclass):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)


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

class Viewer(QtGui.QWidget):
    "Viewer"
    def __init__(self,parent=None,uiLayout=None,luces=True):
        QtGui.QWidget.__init__(self,parent)
        # ============================
        self.direccion = 1
        self.moviendo = False
        self.moviendoOb = None
        ## ============================
        self.inicializarVisor(luces)
        self.inicializarUi(uiLayout)
        ## por el momento cada figura es unicamente un SoSeparator
        self.objetos = nodeDict()
        self.chaptersObjects = nodeDict()
        ## ============================

    def getCamera(self):
        return self.viewer.getSoRenderManager().getCamera()

    
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
        self.lucesColor = readFile(pegaNombres("Viewer","lights.iv")).getChild(0)
        self.getSRoot().insertChild(self.lucesColor,0)
        self.lucesColor.whichChild = SO_SWITCH_ALL
        ## ============================
        self.lucesBlanca = SoDirectionalLight()
        self.getSRoot().insertChild(self.lucesBlanca,0)
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
        root = self.root = SoSeparator()
        self.__previousChapter = None
        ## ============================
#        self.viewer = SoQtExaminerViewer(self)
        ## ============================
        ## si usamos:
        self.viewer = QuarterWidget()
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.viewer)
        ## metodos disponibles:
        # viewAll
        # setTransparencyType
        # setSceneGraph
        ## ============================
        ## copy some attributes
#        for attr in ["viewAll", "setDecoration", "setHeadlight", "setTransparencyType"]:
        for attr in ["viewAll", "setTransparencyType"]:
            setattr(self, attr, getattr(self.viewer, attr))
        ## ============================
        
#        self.viewer.setAlphaChannel(True)
        self.viewer.setSceneGraph(root)
#        self.viewer.setTransparencyType(SoGLRenderAction.SORTED_LAYERS_BLEND)
#        self.viewer.setTransparencyType(SoGLRenderAction.SORTED_OBJECT_BLEND)
#        self.viewer.setAntialiasing(True, 0)
#        self.viewer.setWireframeOverlayColor(SbColor(0.5, 0, 0))
        ## en la sala ixtli
#        self.viewer.setStereoType(SoQtViewer.STEREO_QUADBUFFER)
        ## en el resto del mundo
#        self.viewer.setStereoType(SoQtViewer.STEREO_ANAGLYPH)
        ## esto es principalmente por los poliedros
#        if not noestiloIni:
#        self.setDrawStyle(SoQtViewer.VIEW_WIREFRAME_OVERLAY)
#        self.viewer.setHeadlight(False)
#        self.viewer.setFeedbackVisibility(False)
#        self.viewer.setDecoration(False)
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
        root.addChild(rotor)
        self.rotor = rotor
        ## ============================
        self.rotacionInicial()
        self.setStereoAdjustment(.2)
        ## ===========================
        if luces:
            self.agregaLuces(root)
        hints = SoShapeHints()
        hints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        hints.shapeType = SoShapeHints.SOLID
        hints.faceType = SoShapeHints.CONVEX
        root.addChild(hints)
        ## ============================
        self.prolog = SoSeparator()
        root.addChild(self.prolog)
        ## ============================
        self.chapters = SoSwitch()
        ## ============================
        root.addChild(self.chapters)
        
        ## ============================
#        self.capturaMouseClicked(self.mouse1Clicked, self.mouse2Clicked)
#        self.capturaMouseMoved(self.mouseMoved)
        

    def inicializarUi(self,uilayout):
        self.chaptersStack = QtGui.QStackedWidget()
#        self.chaptersStack.setStyleSheet("QWidget { background:green }")
        if uilayout:
            uilayout.addWidget(self.chaptersStack)
        ## ========================================
#        self.options = QtGui.QWidget()
#        uic.loadUi(modulosPath + "Visor/options-visor.ui",self)
#        self.visorPropertiesFrame.setParent(self.options)

    @QtCore.pyqtSignature("bool")
    def on_axisButton_clicked(self,b):
        self.ejes.show(b)

    def getSRoot(self):
        return self.viewer.getSoRenderManager().getSceneGraph()
#        return self.viewer.getSceneManager().getSceneGraph()
        
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

    def cambiaFigura(self,sentido):
        self.whichPage = (self.whichPage + sentido) % self.numPages()
        self.emit(QtCore.SIGNAL("cambiaFigura(int)"), self.whichPage)

    def siguiente(self):
        self.cambiaFigura(1)

    def previa(self):
        self.cambiaFigura(-1)

    def createChapter(self):
        chapter = superficie.base.Chapter()
        self.addChapter(chapter)

    def addChapter(self, chapter):
        "A chapter contains several pages"
        chapter.setViewer(self)
        sep = SoSeparator()
        ## el "prologo"
        sep.addChild(SoGroup())
        switch = SoSwitch()
        switch.setName("switch")
        sep.addChild(switch)
        self.chapters.addChild(sep)
        self.chapters.whichChild = len(self.chapters) - 1
        self.chaptersObjects[switch] = chapter
        ## ============================
        ui = CambiaFigura()
        ui.setStyleSheet("QWidget { background:white }")
        self.chaptersStack.addWidget(ui)
        self.chaptersStack.setCurrentWidget(ui)
        conecta(ui.siguiente, QtCore.SIGNAL("clicked(bool)"), self.siguiente)
        conecta(ui.previa, QtCore.SIGNAL("clicked(bool)"), self.previa)
        ## ============================
        ui.previa.hide()
        ui.siguiente.hide()
        ## ============================
        if hasattr(chapter, "getProlog"):
            self.addChapterProlog(chapter.getProlog())
        for page in chapter.getPages():
            self.addPage(page)

    
    def addChapterProlog(self, node):
        ## node tiene que ser derivado de SoNode
        self.chapters[self.whichChapter()][0].addChild(node)
    
    def whichChapter(self):
        return self.chapters.whichChild.getValue()
        
    def getChapter(self):
        """returns: SoSeparator"""
        if self.whichChapter() < 0:
            return None
        ## self.chapters[i] tiene dos elementos: el "prólogo" y el switch
        return self.chapters[self.whichChapter()][1]
    
    def getChapterObject(self):
        if self.whichChapter() < 0:
            return None
        return self.chaptersObjects[self.getChapter()]
        
    def setWhichChapter(self,n):
        ## only the == operator test for identity of the underlying
        ## OpenInventor object (the python proxy object is changed every time)
        chapterChanged = not(self.__previousChapter == self.getChapter())
        if self.__previousChapter != None and chapterChanged:
            obAnterior = self.chaptersObjects[self.__previousChapter]
            if hasattr(obAnterior, "chapterSpecificOut"):
                obAnterior.chapterSpecificOut()
        self.chapters.whichChild = n
        self.chaptersStack.setCurrentIndex(n)
        chapterob = self.getChapterObject()
        if hasattr(chapterob, "chapterSpecificIn") and chapterChanged:
            chapterob.chapterSpecificIn()
        self.__previousChapter = self.getChapter()
        self.viewer.viewAll()

        
    def setWhichPageWidget(self, index):
        self.getChapterWidget().parametrosStack.setCurrentIndex(index)

        
    def numPages(self):
        return len(self.getChapter())
    
    def getChapterWidget(self):
        return self.chaptersStack.widget(self.whichChapter())

    def createPage(self):
        page = superficie.base.Page()
        self.addPage(page)
        return page
    
    def addPage(self, page):
        ""
        ## ============================
        if not self.getChapter():
            self.createChapter()
        ## ============================
        ## esto es lo que regresa self.getPage()
        root = getattr(page, "root", page)
        ## chapter es un SoSwitch!!
        self.getChapter().addChild(root)
        self.whichPage = self.numPages() - 1
        self.objetos[root] = page
        ## ============================
        layout  =  QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        widget = QtGui.QWidget()
        widget.setObjectName("PageGui")
        widget.setLayout(layout)
        ui = self.getChapterWidget()
        ui.parametrosStack.addWidget(widget)
        ui.parametrosStack.setCurrentWidget(widget)
        ## ============================
        if hasattr(page,  "getGui"):
            self.addPageGui(page.getGui())
        ## ============================
        if self.numPages() == 2:
            ui.previa.show()
            ui.siguiente.show()

    def removePage(self,n):
        ## TODO: hay que borrar todos los objetos (en self.objetos) asociados a la figura!
        self.switch.removeChild(n)
        stack = self.ui.parametrosStack
        stack.removeWidget(stack.widget(n))

    def removeAllPages(self):
        self.switch.removeAllChildren()
        stack = self.ui.parametrosStack
        while stack.count() > 0:
            stack.removeWidget(stack.widget(0))
        self.objetos = dictRepr()

    def setWhichPage(self,n):
        if self.getChapter():
            self.getChapter().whichChild = n
            self.setWhichPageWidget(n)
#        self.getCamera().viewAll(self.getPage(), self.viewer.getViewportRegion())
#        self.viewer.viewAll()

    def getWhichPage(self):
        return self.getChapter().whichChild.getValue() if self.getChapter() else -1

    whichPage = property(getWhichPage,setWhichPage)

    def getPage(self):
        "returns a SoSwitch"
        if self.getChapter():
            return self.getChapter()[self.whichPage]

    def getPageWidget(self):
        return self.getChapterWidget().parametrosStack.widget(self.whichPage)

    def addPageGui(self, widget):
        self.getPageWidget().layout().addWidget(widget)

    def addChildren(self, obs, viewAll = True):
        for o in obs:
            self.addChild(o, viewAll)

    def addChild(self,ob, viewAll = True):
        "inserta ob en la página actual o en una página nueva"
        if not self.getPage():
            self.createPage()
        separator = self.getPage()
        pageOb = self.objetos[separator]
        pageOb.addChild(ob)
        if viewAll:
            self.viewAll()


    def removeChild(self, ob):
        ## como en addChild() se tiene la construcción:
        ## root = getattr(ob, "root", ob)
        ## self.objetos[root] = ob
        ## entonces aquí tenemos que hacer algo parecido:
        root = getattr(ob, "root", ob)
        del self.objetos[root]
        self.switch.getChild(self.whichPage).removeChild(root)

    def setDrawStyle(self,type):
        print "not implemented"
        return
#        self.viewer.setDrawStyle(SoQtExaminerViewer.STILL, type)
    
    def viewAll(self):
        self.viewer.viewAll()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    visor = Viewer()
    ## ============================
    visor.createChapter()
    visor.createPage()
    esfera = SoSphere()
    esfera.getGui = lambda: QtGui.QLabel("<center><h1>Esfera+Cono</h1></center>")
    visor.addChild(esfera)
    visor.addChild(SoCone())
    ## ============================
    visor.createPage()
    cubo = SoCube()
    cubo.getGui = lambda: QtGui.QLabel("<center><h1>Cubo</h1></center>")
    visor.addChild(cubo)
   ## ============================
    visor.whichPage = 0
    visor.resize(400, 400)
    visor.show()
    visor.chaptersStack.show()
#    SoQt.mainLoop()
    sys.exit(app.exec_())
