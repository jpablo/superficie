# -*- coding: utf-8 -*-
__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore, QtGui, uic
from pivy.coin import SoCoordinate3
from pivy.coin import *
from superficie.util import nodeDict, connect, write
from superficie.util import malla2, Range, pegaNombres
from superficie.Animation import Animation
from superficie.gui import Button

changePage_fclass, base_class = uic.loadUiType(pegaNombres("Viewer","change-page.ui"))

class ChangePageUI(base_class, changePage_fclass):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)


class Chapter(QtCore.QObject):
    "A Chapter"


#    pageChanged = QtCore.pyqtSignal(int)

    def __init__(self, name = ""):
        QtCore.QObject.__init__(self)
        self.name = name
        self.viewer = None
        self.root = SoSeparator()
        self.root.setName("Chapter:root")
        self.pagesSwitch = SoSwitch()
        self.pagesSwitch.setName("Chapter:pages")
        self.root.addChild(self.pagesSwitch)

        self.__pages = nodeDict()
        ## ============================
        self.widget = ChangePageUI()
        self.widget.setStyleSheet("QWidget { background:white }")
        connect(self.widget.siguiente, "clicked(bool)", self.nextPage)
        connect(self.widget.previa, "clicked(bool)", self.prevPage)
        ## ============================
        ## the initial sate
        self.widget.previa.hide()
        self.widget.siguiente.hide()


    @property
    def pages(self):
        "The list of pages"
        return self.__pages

    def createPage(self):
        page = Page()
        self.addPage(page)
        return page

    def addPage(self, page):
        "add a page"
#        print "Chapter.addPage:", ob
        page.viewer = self.viewer
        ## ============================
        ## page can be a Page or SoNode
        root = getattr(page, "root", page)
        self.pages[root] = page
        self.pagesSwitch.addChild(root)
        ## ============================
        layout  =  QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        widget = QtGui.QWidget()
        widget.setObjectName("PageGui")
        widget.setLayout(layout)
        self.widget.pageStack.addWidget(widget)
        ## ============================
        ## this sets both self.pagesSwitch and self.widget.pageStack
        self.whichPage = len(self.pagesSwitch) - 1
        ## ============================
        if hasattr(page,  "getGui"):
            layout.addWidget(page.getGui())
        ## ============================
        if len(self.pagesSwitch) == 2:
            self.widget.previa.show()
            self.widget.siguiente.show()


    def getGui(self):
        return self.widget

    def chapterSpecificIn(self):
        "code to be executed whenever the chapter is displayed"
        "this is intended for global changes to the scenegraph that"
        "are needed by this chapter"
        print "chapterSpecificIn:", self
        pass

    def chapterSpecificOut(self):
        "code to be executed whenever another chapter is displayed"
        "restore the scenegraph to sane values"
        print "chapterSpecificOut", self
        pass

    def getViewer(self):
        return self.viewer
    
    def setViewer(self,parent):
        self.viewer = parent
        for ob in self.pages:
            ob.viewer = self.viewer

    @property
    def page(self):
        "the current page"
        if self.whichPage < 0:
            return None
        return self.pages[self.pagesSwitch[self.whichPage]]


    @property
    def whichPage(self):
        return self.pagesSwitch.whichChild.getValue()

    @whichPage.setter
    def whichPage(self,n):
        if len(self.pagesSwitch) > 0:
            self.pagesSwitch.whichChild = n
            self.widget.pageStack.setCurrentIndex(n)
#            self.pageChanged.emit(n)
#        self.getCamera().viewAll(self.getPage(), self.viewer.getViewportRegion())
#        self.viewAll()

    def changePage(self,dir):
        self.whichPage = (self.whichPage + dir) % len(self.pagesSwitch)

    def nextPage(self):
        self.changePage(1)

    def prevPage(self):
        self.changePage(-1)

#    def removePage(self,n):
#        ## TODO: hay que borrar todos los objetos (en self.objetos) asociados a la figura!
#        self.switch.removeChild(n)
#        stack = self.ui.pageStack
#        stack.removeWidget(stack.widget(n))
#
#    def removeAllPages(self):
#        self.switch.removeAllChildren()
#        stack = self.ui.pageStack
#        while stack.count() > 0:
#            stack.removeWidget(stack.widget(0))
##        self.objetos = dictRepr()
#
#
#
#    def getPage(self):
#        "returns a Separator"
#        if self.chapter:
#            return self.chapter[self.whichPage]
#


class Page(QtCore.QObject):
    "The base class of a container node"
    def __init__(self,name = ""):
        QtCore.QObject.__init__(self)
        self.viewer = None
        self.name = name
        self.root = SoSeparator()
        self.root.setName("Page:root")
        self.children = nodeDict()
        ## =========================
        self.animations = []
        self.objectsForAnimate = []
        ## =========================
        layout  =  QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            layout.addWidget(QtGui.QLabel("<center><h1>%s</h1></center>" % self.name))
        ## ============================
        self.coordPlanes = {}

    def getGui(self):
        return self.widget

    def addWidget(self,widget):
        self.widget.layout().addWidget(widget)

    def addLayout(self,layout):
        self.widget.layout().addLayout(layout)

    def addChild(self, node):
        root = getattr(node, "root", node)
        self.root.addChild(root)
        self.children[root] = node
        if hasattr(node,  "getGui"):
            self.addWidget(node.getGui())
        if hasattr(node, "updateAll"):
            node.updateAll()

    def addWidgetChild(self, arg):
        widget, node = arg
        self.addWidget(widget)
        self.addChild(node)

    def getChildren(self):
        return self.children.values()

    def setupPlanes(self,r0 = (-1,1,5)):
        self.coordPlanes["xy"] = BasePlane(plane="xy",parent=self)
        self.coordPlanes["xz"] = BasePlane(plane="xz",parent=self)
        self.coordPlanes["yz"] = BasePlane(plane="yz",parent=self)

        for p in self.coordPlanes.values():
            p.setRange(r0)
            p.setHeight(r0[0])


    def setupAnimations(self,objects):
        self.objectsForAnimate = objects
        self.animations = [ ob.getAnimation() for ob in objects ]
        Animation.chain(self.animations, pause=1000)

        Button("inicio", self.animate, parent=self)

    def animate(self):
        for ob in self.objectsForAnimate:
            ob.resetObjectForAnimation()
        self.animations[0].start()


    def pre(self):
        print "pre"


class GraphicObject(SoSwitch):
    def __init__(self, visible=False, parent=None):
        SoSwitch.__init__(self)
        self.qobject = QtCore.QObject()
        self.parent = parent
        self.children = nodeDict()
        ## this permits get at children by position
        self.childrenList = []
        self.setVisible(visible)
        ## ============================
        self.separator = SoSeparator()
        SoSwitch.addChild(self,self.separator)
        ## ============================
        self.translation = SoTranslation()
        self.translation.translation = (0,0,0)
        self.separator.addChild(self.translation)
        self.animation = None
        ## ============================
        self.material = SoMaterial()
        self.transType = SoTransparencyType()
        self.separator.addChild(self.material)
        self.separator.addChild(self.transType)
        ## ============================
        self.drawStyle = SoDrawStyle()
        self.separator.addChild(self.drawStyle)
        ## ============================
        if parent:
            parent.addChild(self)

    def __getitem__(self,key):
        return self.childrenList[key]

    def addChild(self, node):
        root = getattr(node, "root", node)
        self.separator.addChild(root)
        self.children[root] = node
        self.childrenList.append(node)

    def getChildren(self):
        return self.children.values()

    def show(self):
        self.setVisible(True)

    def hide(self):
        self.setVisible(False)

    def setDrawStyle(self,style):
        self.drawStyle.style = style

    def setVisible(self, visible):
        if visible:
            self.whichChild = SO_SWITCH_ALL
        else:
            self.whichChild = SO_SWITCH_NONE

    def setOrigin(self,pos):
        """Documentation"""
        self.translation.translation = pos
    def getOrigin(self):
        return self.translation.translation.getValue()

    def getAnimation(self):
        return self.animation

    def resetObjectForAnimation(self):
        pass

    def setColor(self, val):
        self.setDiffuseColor(val)
        self.setEmissiveColor(val)
        self.setAmbientColor(val)
        self.setSpecularColor(val)

    def setTransparency(self, val):
        self.material.transparency.setValue(val)

    def setEmissiveColor(self, val):
        self.material.emissiveColor.setValue(val)

    def setDiffuseColor(self, val):
        self.material.diffuseColor.setValue(val)

    def setAmbientColor(self, val):
        self.material.ambientColor.setValue(val)

    def setSpecularColor(self, val):
        self.material.specularColor.setValue(val)

    def setShininess(self,val):
        self.material.shininess = val

    def setTransparencyType(self, trans):
        self.transType.value = trans


class BasePlane(GraphicObject):
    def __init__(self, plane = "xy", visible = True, parent = None):
        GraphicObject.__init__(self,visible,parent)
        ## ============================
        self.plane = plane
        self.setDiffuseColor((.5,.5,.5))
        self.setAmbientColor((.5,.5,.5))
        ## ============================
        self.translation = SoTranslation()
        ## ============================
        self.coords = SoCoordinate3()
        self.mesh = SoQuadMesh()
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.separator.addChild(self.translation)
        self.separator.addChild(self.sHints)
        self.separator.addChild(self.coords)
        self.separator.addChild(self.mesh)
        self.setRange((-2,2,7),plane)
        self.setTransparency(0.5)
        self.setTransparencyType(8)

    def setHeight(self,val):
        oldVal = list(self.translation.translation.getValue())
        oldVal[self.constantIndex] = val
        self.translation.translation = oldVal

    def setRange(self,r0,plane=""):
        if plane == "":
            plane = self.plane
        self.plane = plane
        r = Range(*r0)
        self.ptos = []
        if plane=="xy":
            func = lambda x,y:(x,y,0)
            ## this will be used to determine which coordinate to modify
            ## in setHeight
            self.constantIndex = 2
        elif plane=="yz":
            func = lambda y,z:(0,y,z)
            self.constantIndex = 0
        elif plane=="xz":
            func = lambda x,z:(x,0,z)
            self.constantIndex = 1
        elif type(plane) == type(lambda :0):
            func = plane
        malla2(self.ptos,func, r.min, r.dt, len(r),r.min, r.dt, len(r))
        self.coords.point.setValues(0,len(self.ptos),self.ptos)
        self.mesh.verticesPerColumn = len(r)
        self.mesh.verticesPerRow = len(r)





class Plane(GraphicObject):
    """
    """
    def __init__(self, pos, visible=True, parent=None):
        GraphicObject.__init__(self,visible,parent)
        self.altura = -1
        vertices = [[-1,1],[1,1],[-1,-1],[1,-1]]
        for p in vertices:
            p.insert(pos,self.altura)
        sh = SoShapeHints()
        sh.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        sh.faceType = SoShapeHints.UNKNOWN_FACE_TYPE
        sh.shapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
        coords = SoCoordinate3()
        coords.point.setValues(0,len(vertices),vertices)
        mesh = SoQuadMesh()
        mesh.verticesPerColumn = 2
        mesh.verticesPerRow = 2
        nb = SoNormalBinding()
#            nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        mat = SoMaterial()
        mat.transparency = 0.5
        self.setTransparencyType(8)
        ## ============================
        root = SoSeparator()
        root.addChild(sh)
        root.addChild(mat)
        root.addChild(nb)
        root.addChild(coords)
        root.addChild(mesh)
        self.addChild(root)

    def setAltura(val):
        pass


class Planes(GraphicObject):
    def __init__(self, visible=False, parent=None):
        GraphicObject.__init__(self,visible,parent)
        self.addChild(Plane(0))
        self.addChild(Plane(1))
        self.addChild(Plane(2))


if __name__ == "__main__":
    print "Hello";