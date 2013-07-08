#!/usr/bin/env python

import logging

from PyQt4 import QtGui
from pivy.coin import SbVec3f

from superficie.book import Book
from superficie import globals
# from superficie.viewer.MinimalViewer import MinimalViewer
from superficie.viewer.MinimalViewerSoQt import MinimalViewer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BookProxy(object):
    """
    Proxy methods for managing the current chapter and page
    """

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


class Viewer(MinimalViewer, BookProxy):
    """
    Extends MinimalViewer with a Book-like structure
    """

    def __init__(self, parent=None, uiLayout=None, notesLayout=None, lights=True):
        self.book = Book()
        # copy some attributes from book
        self.chaptersStack = self.book.chaptersStack
        self.notesStack = self.book.notesStack
        self.initializeUI(uiLayout, notesLayout)
        self.book.pageChanged.connect(self.adjustCameraForPage)
        # initialize the MinimalViewer
        MinimalViewer.__init__(self)

    def getRoot(self):
        return self.book.root

    @staticmethod
    def Instance():
        return globals.ViewerInstances[-1]

    def adjustCameraForPage(self, page, n):
        logger.debug('adjustCameraForPage %s', n)
        if page.camera_position:
            self.setCameraPosition(page.camera_position)
        else:
            self.setCameraPosition(self.camera_position)
        if page.camera_point_at:
            self.camera.pointAt(*page.camera_point_at)
        else:
            self.camera.pointAt(*self.camera_point_at)
        if page.camera_viewAll:
            self.viewAll()

    def initializeUI(self, uiLayout, notesLayout):
        if uiLayout is not None:
            uiLayout.addWidget(self.chaptersStack)
        if notesLayout is not None:
            notesLayout.addWidget(self.notesStack)


if __name__ == "__main__":
    import sys
    from PyQt4 import QtGui
    from pivy.coin import SoSeparator, SoCone, SoSphere, SoCube
    # from pivy.gui.soqt import SoQt
    # SoQt.init(None)

    app = QtGui.QApplication(sys.argv)
    viewer = Viewer(lights=False)
    ## ============================
    viewer.book.createChapter()
    ## ============================
    viewer.chapter.createPage()
    sep = SoSeparator()
    sep.getGui = lambda: QtGui.QLabel("<center><h1>Sphere+Cone</h1></center>")
    sphere = SoSphere()
    cone = SoCone()
    sep.addChild(sphere)
    sep.addChild(cone)
    viewer.page.addChild(sep)
    ## ============================
    viewer.chapter.createPage()
    cube = SoCube()
    cube.getGui = lambda: QtGui.QLabel("<center><h1>Cubo</h1></center>")
    viewer.page.addChild(cube)
    ## ============================
    viewer.whichPage = 0
    viewer.resize(400, 400)
    viewer.show()
    viewer.chaptersStack.show()

    sys.exit(app.exec_())
