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

cambia_figura_fclass, base_class = uic.loadUiType(pegaNombres("Viewer","change-page.ui"))

class ChangeChapterUI(base_class, cambia_figura_fclass):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)


class Book(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.__previousChapter = None
        self.root = SoSeparator()
        self.root.setName("Book:root")
        self.chapters = SoSwitch()
        self.chapters.setName("Book:chapters")
        self.root.addChild(self.chapters)
        ## this dictionary contains the chapters python objects
        ## not only the SoSeparator
        self.chaptersObjects = nodeDict()
        self.chaptersStack = QtGui.QStackedWidget()

    def changePage(self,dir):
        self.whichPage = (self.whichPage + dir) % self.numPages()
        self.emit(QtCore.SIGNAL("cambiaFigura(int)"), self.whichPage)

    def next(self):
        self.changePage(1)

    def prev(self):
        self.changePage(-1)


    def createChapter(self):
        chapter = Chapter()
        self.addChapter(chapter)
        return chapter

    def addChapter(self, chapter):
        "A chapter contains several pages"
        chapterRoot = SoSeparator()
        chapterRoot.setName("Chapter:root")
        chapter.root = chapterRoot
        ## Every chapter has its own "prolog"
        ## which permits set up common nodes for the chapter
        ## ¿para que sirve este grupo??
#        chapterRoot.addChild(SoGroup())
        pages = SoSwitch()
        pages.setName("Chapter:pages")
        chapterRoot.addChild(pages)
        self.chapters.addChild(chapterRoot)
        self.chapters.whichChild = len(self.chapters) - 1
        self.chaptersObjects[pages] = chapter
        ## ============================
        ## setup the UI
        ui = ChangeChapterUI()
        ui.setStyleSheet("QWidget { background:white }")
        self.chaptersStack.addWidget(ui)
        self.chaptersStack.setCurrentWidget(ui)
        connect(ui.siguiente, "clicked(bool)", self.next)
        connect(ui.previa, "clicked(bool)", self.prev)
        ## ============================
        ## the initial sate
        ui.previa.hide()
        ui.siguiente.hide()
        ## ============================
        if hasattr(chapter, "getProlog"):
            self.addChapterProlog(chapter.getProlog())
        for page in chapter.getPages():
            self.addPage(page)


    def addChapterProlog(self, node):
        ## node tiene que ser derivado de SoNode
        self.chapters[self.whichChapter][0].addChild(node)

    @property
    def chapter(self):
        "chapter is the switch 0-child of the separator 'root'"
        if self.whichChapter < 0:
            return None
        chapi = self.whichChapter
        ##
        return self.chapters[chapi][0]

    @property
    def chapterObject(self):
        """returns: base.Chapter"""
        if self.whichChapter < 0:
            return None
        return self.chaptersObjects[self.chapter]

    @property
    def whichChapter(self):
        return self.chapters.whichChild.getValue()

    @whichChapter.setter
    def whichChapter(self,n):
        ## only the == operator test for identity of the underlying
        ## OpenInventor object (the python proxy object is changed every time)
        chapterChanged = not(self.__previousChapter == self.chapter)
        if self.__previousChapter != None and chapterChanged:
            obAnterior = self.chaptersObjects[self.__previousChapter]
            if hasattr(obAnterior, "chapterSpecificOut"):
                obAnterior.chapterSpecificOut()
        self.chapters.whichChild = n
        self.chaptersStack.setCurrentIndex(n)
        chapterob = self.chapterObject
        if hasattr(chapterob, "chapterSpecificIn") and chapterChanged:
            chapterob.chapterSpecificIn()
        self.__previousChapter = self.chapter
#        self.viewer.viewAll()

    def numPages(self):
        return len(self.chapter)

    def getChapterWidget(self):
        return self.chaptersStack.widget(self.whichChapter)

    def createPage(self):
        page = superficie.base.Page()
        self.addPage(page)
        return page

    def addPage(self, page):
        "Add a page to the current chapter"
        print "Book.addPage:", page
        ## ============================
        if not self.chapter:
            self.createChapter()
        ## ============================
        root = getattr(page, "root", page)
        ## chapter es un SoSwitch!!
        ## no un objeto "Chapter"
        self.chapter.addChild(root)
        print "self.whichPage = ", self.numPages() - 1
        self.whichPage = self.numPages() - 1
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

#        self.viewAll()


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
#        self.objetos = dictRepr()

    @property
    def whichPage(self):
        return self.chapter.whichChild.getValue() if self.chapter else -1

    @whichPage.setter
    def whichPage(self,n):
#        print "setWhichPage:", n
        self.setWhichPageWidget(n)
        if self.chapter and len(self.chapter) > 0:
            self.chapter.whichChild = n
            pages = self.chapterObject.getPages()
            pOb = pages[n]
            ## execute some function
            if hasattr(pOb, "pre"):
                pOb.pre()
#        self.getCamera().viewAll(self.getPage(), self.viewer.getViewportRegion())
#        self.viewAll()


    def getPage(self):
        "returns a Separator"
        if self.chapter:
            return self.chapter[self.whichPage]

    def getPageWidget(self):
        "get the page's wiget"
#        print "getPageWidget:"
        return self.getChapterWidget().parametrosStack.widget(self.whichPage)

    def setWhichPageWidget(self, index):
        "set which page widget to show"
#        print "setWhichPageWidget:", index
        self.getChapterWidget().parametrosStack.setCurrentIndex(index)

    def addPageGui(self, widget):
        self.getPageWidget().layout().addWidget(widget)


class Chapter(QtCore.QObject):
    "A Chapter"
    def __init__(self, name = ""):
        QtCore.QObject.__init__(self)
        self.viewer = None
        self.root = None
        self.name = name
        ## the relation between the chapter and the pages
        ## is left to the viewer
        ## In particular, it doesn't have a SoSeparator or a self.root
        self.pages = []

    def getPages(self):
        "The list of pages"
        return self.pages

    def addPage(self, ob):
        "add a page"
#        print "Chapter.addPage:", ob
        self.pages.append(ob)
        ob.viewer = self.viewer
        

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