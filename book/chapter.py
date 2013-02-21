from PyQt4 import QtGui, uic, QtCore
from pivy.coin import SoSeparator, SoSwitch
from page import Page
from superficie.util import nodeDict, connect, pegaNombres

changePage_fclass, base_class = uic.loadUiType(pegaNombres("viewer", "change-page.ui"))

class ChangePageUI(base_class, changePage_fclass):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)


class Chapter(QtCore.QObject):
    """A Chapter"""

    pageChanged = QtCore.pyqtSignal(Page,int)

    def __init__(self, name=""):
        super(Chapter, self).__init__()
        self.name = name
        self.book = None
        self.root = SoSeparator()
        self.root.setName("Chapter:root")
        self.pagesSwitch = SoSwitch()
        self.pagesSwitch.setName("Chapter:pages")
        self.root.addChild(self.pagesSwitch)

        self.__pages = nodeDict()
        ## ============================
        self.setupGui()

    def setupGui(self):
        ## self.wiget has next, prev buttons, plus a QStackedWidget for holding per page controls
        self.widget = ChangePageUI()
        ## the initial state
        self.widget.previa.hide()
        self.widget.siguiente.hide()
        connect(self.widget.siguiente, "clicked(bool)", self.nextPage)
        connect(self.widget.previa, "clicked(bool)", self.prevPage)
        ## ============================
        self.notasStack = QtGui.QStackedWidget()
        ## ============================

    def setBook(self,book):
        self.book = book


    @property
    def pages(self):
        """The list of pages"""
        return self.__pages

    def createPage(self):
        """
        Creates a new page and appends it to this chapter
        """
        page = Page()
        self.addPage(page)
        return page

    def addPage(self, page):
        """
        Adds 'page' to this chapter. page can be a Page or a SoNode. Searches
        page for a 'getGui' function, which should return a widget.
        @param page: Page | SoNode
        """
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
        ## only change the page if theres a book already
        if self.book is not None:
            self.whichPage = len(self.pagesSwitch) - 1
        ## ============================
        if hasattr(page, "getGui"):
            guiLayout.addWidget(page.getGui())
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
        """code to be executed whenever the chapter is displayed
        this is intended for global changes to the scenegraph that
        are needed by this chapter
        """
        print "chapterSpecificIn:", self
        pass

    def chapterSpecificOut(self):
        """code to be executed whenever another chapter is displayed
        restore the scenegraph to sane values
        """
        print "chapterSpecificOut", self
        pass


    @property
    def page(self):
        """the current page"""
        if self.whichPage < 0:
            return None
        return self.pages[self.pagesSwitch[self.whichPage]]


    def getWhichPage(self):
        """
        Returns the index of the current page
        """
        return self.pagesSwitch.whichChild.getValue()

    def setWhichPage(self, n):
        """
        Activates the n-th page
        @param n:
        """
        if len(self.pagesSwitch) > 0:
            self.page and self.onPageUnload(self.page)
            node = self.pagesSwitch.getChild(n)
            self.onPageEnter(self.pages[node])
            self.pagesSwitch.whichChild = n
            self.widget.pageStack.setCurrentIndex(n)
            self.notasStack.setCurrentIndex(n)
            self.pageChanged.emit(self.page, n)


    whichPage = property(getWhichPage, setWhichPage)

    def changePage(self, dir):
        self.whichPage = (self.whichPage + dir) % len(self.pagesSwitch)

    def nextPage(self):
        self.changePage(1)

    def prevPage(self):
        self.changePage(-1)

    def onPageUnload(self, page):
        if page.camera_position is not None and self.book is not None:
            self.book.viewer.cameraPosition = self.__camera_position

    def onPageEnter(self, page):
        if page.camera_position is not None and self.book is not None:
            self.__camera_position = self.book.viewer.cameraPosition
            self.book.viewer.cameraPosition = page.camera_position