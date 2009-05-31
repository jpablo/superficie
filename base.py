__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore, QtGui
from pivy.coin import *
from superficie.util import nodeDict

class Chapter(QtCore.QObject):
    "A Chapter"
    def __init__(self, name = ""):
        QtCore.QObject.__init__(self)
        self.viewer = None
        self.root = None
        self.name = name
        ## the relation between the chapter and the pages
        ## is left to the viewer
        self.objects = []

    def getPages(self):
        "The list of pages"
        return self.objects

    def addPage(self, ob):
        "add a page"
        self.objects.append(ob)
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
        for ob in self.objects:
            ob.viewer = self.viewer

class Page(QtCore.QObject):
    "The base class of a container node"
    def __init__(self,name = ""):
        QtCore.QObject.__init__(self)
        self.viewer = None
        self.name = name
        self.root = SoSeparator()
        self.children = nodeDict()
        ## =========================
        layout  =  QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            layout.addWidget(QtGui.QLabel("<center><h1>%s</h1></center>" % self.name))

    def getGui(self):
        return self.widget

    def addWidget(self,widget):
        self.widget.layout().addWidget(widget)

    def addChild(self, node):
        root = getattr(node, "root", node)
        self.root.addChild(root)
        self.children[root] = node
        if hasattr(node,  "getGui"):
            self.addWidget(node.getGui())


    def addWidgetChild(self, arg):
        widget, node = arg
        self.addWidget(widget)
        self.addChild(node)

    def getChildren(self):
        return self.children.values()


if __name__ == "__main__":
    print "Hello";