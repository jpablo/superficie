# -*- coding: utf-8 -*-
__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtGui, QtCore
from pivy.coin import SoSeparator, SoSwitch
from superficie.util import nodeDict
from superficie.base import Chapter

class Book(QtCore.QObject):
    "Implemens a Book-like object"
    
    chapterChanged = QtCore.pyqtSignal(int)
    #===========================================================================
    # The chapter and the page
    #===========================================================================
    pageChanged = QtCore.pyqtSignal(int,int)
    
    def __init__(self):
        super(Book,self).__init__()
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

    def __len__(self):
        """The number of chapters"""
        return len(self.chapters)

    def createChapter(self):
        "Creates a new empty Chapter"
        chapter = Chapter()
        self.addChapter(chapter)
        return chapter
    
    def _pageChangedCB(self,n):
        self.pageChanged.emit(self.whichChapter,n)

    def addChapter(self, chapter):
        "Appends a chapter"
        "A chapter contains several pages"
        ## we probably should check that chapter is derived
        ## from base.Chapter
        self.chaptersObjects[chapter.pagesSwitch] = chapter
        self.chapters.addChild(chapter.root)
        ## ============================
        ## setup the UI
        ui = chapter.getGui()
        self.chaptersStack.addWidget(ui)
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
        "returns: base.Chapter"
        if self.whichChapter < 0:
            return None
        return self.chaptersObjects[self.chapterSwitch]

    @property
    def page(self):
        "convenience function"
        return self.chapter.page if self.whichChapter >= 0 else None

    @property
    def whichChapter(self):
        "returns the selected chapter"
        return self.chapters.whichChild.getValue()

    @whichChapter.setter
    def whichChapter(self,n):
        "Sets the current chapter"
        ## only the == operator test for identity of the underlying
        ## OpenInventor object (the python proxy object is changed every time)
        chapterChanged = not(self.__previousChapter == self.chapterSwitch)
        if self.__previousChapter != None and chapterChanged:
            obAnterior = self.chaptersObjects[self.__previousChapter]
            if hasattr(obAnterior, "chapterSpecificOut"):
                obAnterior.chapterSpecificOut()
        self.chapters.whichChild = n
        self.chaptersStack.setCurrentIndex(n)
        chapterob = self.chapter
        if hasattr(chapterob, "chapterSpecificIn") and chapterChanged:
            chapterob.chapterSpecificIn()
        self.__previousChapter = self.chapterSwitch
        self.chapterChanged.emit(n)
#        self.viewer.viewAll()
