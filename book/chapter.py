import logging
from PyQt4 import QtGui, uic, QtCore
from pivy.coin import SoSeparator, SoSwitch
from page import Page
from superficie.util import nodeDict, connect, filePath

changePage_fclass, base_class = uic.loadUiType(filePath("viewer", "change-page.ui"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()


class ChangePageUI(base_class, changePage_fclass):
    def __init__(self, *args):
        # noinspection PyCallByClass
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)


class Chapter(QtCore.QObject):
    """A Chapter"""

    pageChanged = QtCore.pyqtSignal(Page, int)

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
        ## self.widget has next, prev buttons, plus a QStackedWidget for holding per page controls
        self.widget = ChangePageUI()
        ## the initial state
        self.widget.previous.hide()
        self.widget.next.hide()
        connect(self.widget.next, "clicked(bool)", self.nextPage)
        connect(self.widget.previous, "clicked(bool)", self.prevPage)
        ## ============================
        self.notasStack = QtGui.QStackedWidget()
        ## ============================

    def setBook(self, book):
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
            self.widget.previous.show()
            self.widget.next.show()

    def getGui(self):
        return self.widget

    def getNotas(self):
        return self.notasStack

    def chapterSpecificIn(self):
        """code to be executed whenever the chapter is displayed
        this is intended for global changes to the scenegraph that
        are needed by this chapter
        """
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
            self.pagesSwitch.getChild(n)
            self.pagesSwitch.whichChild = n
            self.widget.pageStack.setCurrentIndex(n)
            self.notasStack.setCurrentIndex(n)
            self.pageChanged.emit(self.page, n)

    whichPage = property(getWhichPage, setWhichPage)

    def changePage(self, direction):
        self.whichPage = (self.whichPage + direction) % len(self.pagesSwitch)

    def nextPage(self):
        self.changePage(1)

    def prevPage(self):
        self.changePage(-1)
