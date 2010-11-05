# -*- coding: utf-8 -*-
__author__ = "jpablo"
__date__ = "$18/05/2009 12:47:43 AM$"

from PyQt4 import QtGui, QtCore, uic
from pivy.coin import SoSeparator, SoSwitch
from superficie.util import nodeDict, connect, Vec3
from superficie.util import pegaNombres
from superficie.VariousObjects import Arrow, BasePlane
from superficie.Animation import Animation
from superficie.gui import Button

changePage_fclass, base_class = uic.loadUiType(pegaNombres("Viewer", "change-page.ui"))

class ChangePageUI(base_class, changePage_fclass):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)



class Book(QtCore.QObject):
    "Implemens a Book-like object"
    
    chapterChanged = QtCore.pyqtSignal(int)
    #===========================================================================
    # The chapter and the page
    #===========================================================================
    pageChanged = QtCore.pyqtSignal(int, int)
    
    def __init__(self):
        super(Book, self).__init__()
        self.__previousChapter = None
        self.root = SoSeparator()
        self.root.setName("Book:root")
        self.chapters = SoSwitch()
        self.chapters.setName("Book:chapters")
        self.root.addChild(self.chapters)
        ## this dictionary contains the chapters python objects
        ## not only the SoSeparator
        self.chaptersObjects = nodeDict()
        ## chapterStack has one widget (of controls) per chapter
        self.chaptersStack = QtGui.QStackedWidget()
        self.notasStack = QtGui.QStackedWidget()

    def __len__(self):
        """The number of chapters"""
        return len(self.chapters)

    def createChapter(self):
        "Creates a new empty Chapter"
        chapter = Chapter()
        self.addChapter(chapter)
        return chapter
    
    def _pageChangedCB(self, n):
        self.pageChanged.emit(self.whichChapter, n)

    def addChapter(self, chapter):
        '''
        Appends chapter to this book
        @param chapter: Chapter
        '''
        ## we probably should check that chapter is derived
        ## from base.Chapter
        self.chaptersObjects[chapter.pagesSwitch] = chapter
        self.chapters.addChild(chapter.root)
        ## ============================
        ## setup the UI
        self.chaptersStack.addWidget(chapter.getGui())
        self.notasStack.addWidget(chapter.getNotas())
        self.whichChapter = len(self.chapters) - 1
        #=======================================================================
        chapter.pageChanged.connect(self._pageChangedCB)

    @property
    def chapterSwitch(self):
        "the switch of the current chapter"
        if self.whichChapter < 0:
            return None
        return self.chapters[self.whichChapter][0]

    @property
    def chapter(self):
        "returns the current chapter"
        if self.whichChapter < 0:
            return None
        return self.chaptersObjects[self.chapterSwitch]

    @property
    def page(self):
        "returns the current page in the chapter"
        return self.chapter.page if self.whichChapter >= 0 else None

    def getWhichChapter(self):
        "returns the selected chapter"
        return self.chapters.whichChild.getValue()

    def setWhichChapter(self, n):
        '''
        Sets the current chapter
        @param n: int
        '''
        ## only the == operator test for identity of the underlying
        ## OpenInventor object (the python proxy object is changed every time)
        chapterChanged = not(self.__previousChapter == self.chapterSwitch)
        if self.__previousChapter != None and chapterChanged:
            obAnterior = self.chaptersObjects[self.__previousChapter]
            if hasattr(obAnterior, "chapterSpecificOut"):
                obAnterior.chapterSpecificOut()
        self.chapters.whichChild = n
        self.chaptersStack.setCurrentIndex(n)
        self.notasStack.setCurrentIndex(n)
        chapterob = self.chapter
        if hasattr(chapterob, "chapterSpecificIn") and chapterChanged:
            chapterob.chapterSpecificIn()
        self.__previousChapter = self.chapterSwitch
        self.chapterChanged.emit(n)
        
    whichChapter = property(getWhichChapter, setWhichChapter)


class Chapter(QtCore.QObject):
    "A Chapter"

    pageChanged = QtCore.pyqtSignal(int)

    def __init__(self, name=""):
        super(Chapter, self).__init__()
        self.name = name
        self.viewer = None
        self.root = SoSeparator()
        self.root.setName("Chapter:root")
        self.pagesSwitch = SoSwitch()
        self.pagesSwitch.setName("Chapter:pages")
        self.root.addChild(self.pagesSwitch)

        self.__pages = nodeDict()
        ## ============================
        ## self.wiget has next, prev buttons, plus a QStackedWidget for holding per page controls
        self.widget = ChangePageUI()
        self.widget.setStyleSheet("QWidget { background:white }")
        connect(self.widget.siguiente, "clicked(bool)", self.nextPage)
        connect(self.widget.previa, "clicked(bool)", self.prevPage)
        ## ============================
        self.notasStack = QtGui.QStackedWidget()
        ## ============================
        ## the initial sate
        self.widget.previa.hide()
        self.widget.siguiente.hide()


    @property
    def pages(self):
        "The list of pages"
        return self.__pages

    def createPage(self):
        '''
        Creates a new page and appends it to this chapter
        '''
        page = Page()
        self.addPage(page)
        return page

    def addPage(self, page):
        '''
        Adds 'page' to this chapter. page can be a Page or a SoNode. Searches
        page for a 'getGui' function, which should return a widget.
        @param page: Page | SoNode
        '''
        page.viewer = self.viewer
        ## ============================
        ## page can be a Page or SoNode
        root = getattr(page, "root", page)
        self.pages[root] = page
        self.pagesSwitch.addChild(root)
        ## ============================
        guiLayout = QtGui.QVBoxLayout()
        guiLayout.setMargin(0)
        guiLayout.setSpacing(0)
        widget = QtGui.QWidget()
        widget.setObjectName("PageGui")
        widget.setLayout(guiLayout)
        self.widget.pageStack.addWidget(widget)
        ## ============================
        notasLayout = QtGui.QVBoxLayout()
        notasLayout.setMargin(0)
        notasLayout.setSpacing(0)
        widget = QtGui.QWidget()
        widget.setObjectName("PageNotas")
        widget.setLayout(notasLayout)
        self.notasStack.addWidget(widget)
        ## ============================
        ## this sets self.pagesSwitch, self.widget.pageStack, self.notasStack
        self.whichPage = len(self.pagesSwitch) - 1
        ## ============================
        if hasattr(page, "getGui"):
            guiLayout.addWidget(page.getGui())
        ## ============================
        if hasattr(page, "getNotas"):
            notasLayout.addWidget(page.getNotas())
        ## ============================
        if len(self.pagesSwitch) == 2:
            self.widget.previa.show()
            self.widget.siguiente.show()


    def getGui(self):
        return self.widget

    def getNotas(self):
        return self.notasStack

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
    
    def setViewer(self, parent):
        self.viewer = parent
        for ob in self.pages:
            ob.viewer = self.viewer

    @property
    def page(self):
        "the current page"
        if self.whichPage < 0:
            return None
        return self.pages[self.pagesSwitch[self.whichPage]]


    def getWhichPage(self):
        '''
        Returns the index of the current page
        '''
        return self.pagesSwitch.whichChild.getValue()

    def setWhichPage(self, n):
        '''
        Activates the n-th page
        @param n:
        '''
        if len(self.pagesSwitch) > 0:
            self.page and self.page.post()
            node = self.pagesSwitch.getChild(n)
            self.pages[node].pre()
            self.pagesSwitch.whichChild = n
            self.widget.pageStack.setCurrentIndex(n)
            self.notasStack.setCurrentIndex(n)
            self.pageChanged.emit(n)
            
    whichPage = property(getWhichPage, setWhichPage)
    
    def changePage(self, dir):
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
    def __init__(self, name=""):
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
        layout = QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            titulo = QtGui.QLabel("<center><h1>%s</h1></center>" % self.name)
            titulo.setWordWrap(True)
            layout.addWidget(titulo)
            layout.addStretch()
        ## ============================
        layout = QtGui.QVBoxLayout()
        self.notasWidget = QtGui.QWidget()
        self.notasWidget.setLayout(layout)
        notas = QtGui.QLabel(self.__doc__)
        notas.setWordWrap(True)
        notas.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(notas)
        layout.addStretch()
        ## ============================
        self.coordPlanes = {}
        self.setupAxis()

    def getGui(self):
        return self.widget

    def getNotas(self):
        return self.notasWidget

    def addWidget(self, widget):
        self.widget.layout().addWidget(widget)

    def addLayout(self, layout):
        self.widget.layout().addLayout(layout)

    def addChild(self, node):
        root = getattr(node, "root", node)
        self.root.addChild(root)
        self.children[root] = node        
        if hasattr(node, "getGui"):
            self.addWidget(node.getGui())
        if hasattr(node, "updateAll"):
            node.updateAll()

    def addChildren(self, lst):
        for c in lst:
            self.addChild(c)

    def addWidgetChild(self, arg):
        widget, node = arg
        self.addWidget(widget)
        self.addChild(node)

    def getChildren(self):
        return self.children.values()

    def setupPlanes(self, r0=(-1, 1, 5)):
        self.coordPlanes["xy"] = BasePlane(plane="xy", parent=self)
        self.coordPlanes["xz"] = BasePlane(plane="xz", parent=self)
        self.coordPlanes["yz"] = BasePlane(plane="yz", parent=self)

        for p in self.coordPlanes.values():
            p.setRange(r0)
            p.setHeight(r0[0])
            
    
    def showAxis(self,show):
        '''
        @param show: bool
        '''
        self.axis_x.setVisible(show)
        self.axis_y.setVisible(show)
        self.axis_z.setVisible(show)
    
    def setupAxis(self):
        self.axis_x = Arrow(Vec3(-5, 0, 0), Vec3(5, 0, 0), parent=self)
        self.axis_x.setDiffuseColor((1, 0, 0))
        self.axis_y = Arrow(Vec3(0, -5, 0), Vec3(0, 5, 0), parent=self)
        self.axis_y.setDiffuseColor((0, 1, 0))
        self.axis_z = Arrow(Vec3(0, 0, -5), Vec3(0, 0, 5), parent=self)
        self.axis_z.setDiffuseColor((0, 0, 1))


    def setupAnimations(self, objects):
        self.objectsForAnimate = objects
        self.animations = [ getattr(ob, 'animation', ob) for ob in objects ]
        Animation.chain(self.animations, pause=1000)

        Button("inicio", self.animate, parent=self)

    def animate(self):
        for ob in self.objectsForAnimate:
            ob.resetObjectForAnimation()
        self.animations[0].start()


    def pre(self):
        '''
        Called before settis this page as current for the chapter
        '''
        pass
        
    def post(self):
        '''
        Called upon whichPage changed, but before next page's 'pre'
        '''
        pass
