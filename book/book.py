from PyQt4 import QtGui, uic, QtCore
from pivy.coin import SoSeparator, SoSwitch
from chapter import Chapter
from page import Page
from superficie.util import nodeDict


class Book(QtCore.QObject):
    """Implemens a Book-like object"""

    chapterChanged = QtCore.pyqtSignal(int)
    pageChanged = QtCore.pyqtSignal(Page, int)

    def __init__(self, viewer):
        super(Book, self).__init__()
        self.viewer = viewer
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
        """Creates a new empty Chapter"""
        chapter = Chapter()
        self.addChapter(chapter)
        return chapter

    def addChapter(self, chapter):
        """
        Appends chapter to this book
        @param chapter: Chapter
        """
        ## we probably should check that chapter is derived
        ## from base.Chapter
        self.chaptersObjects[chapter.pagesSwitch] = chapter
        self.chapters.addChild(chapter.root)
        if hasattr(chapter, 'setBook'):
            chapter.setBook(self)
        ## ============================
        ## setup the UI
        self.chaptersStack.addWidget(chapter.getGui())
        self.notasStack.addWidget(chapter.getNotas())
        self.whichChapter = len(self.chapters) - 1
        #=======================================================================
        chapter.pageChanged.connect(self._pageChangedCB)

    def _pageChangedCB(self, page, n):
        self.pageChanged.emit(page, n)

    @property
    def chapterSwitch(self):
        """the switch of the current chapter"""
        if self.whichChapter < 0:
            return None
        return self.chapters[self.whichChapter][0]

    @property
    def chapter(self):
        """returns the current chapter"""
        if self.whichChapter < 0:
            return None
        return self.chaptersObjects[self.chapterSwitch]

    @property
    def page(self):
        """returns the current page in the chapter"""
        return self.chapter.page if self.whichChapter >= 0 else None

    def getWhichChapter(self):
        """returns the selected chapter"""
        return self.chapters.whichChild.getValue()

    def setWhichChapter(self, n):
        """
        Sets the current chapter
        @param n: int
        """
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