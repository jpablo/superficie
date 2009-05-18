__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore, QtGui
from pivy.coin import *
from superficie.util import dictRepr

class Chapter(QtCore.QObject):
    "An empty Chapter"
    def __init__(self,parent = None, name = ""):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.name = name
        self.objects = []

    def getPages(self):
        "The list of pages"
        return self.objects

    def addPage(self, ob):
        "add a page"
        self.objects.append(ob)

    def chapterSpecificIn(self):
        pass

    def chapterSpecificOut(self):
        pass


class PageContainer(QtCore.QObject):
    "The base class of a container node"
    def __init__(self,name = ""):
        QtCore.QObject.__init__(self)
        self.name = name
        ## =========================
        self.root = SoSeparator()
        self.children = dictRepr()
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

    def addWidgetChild(self, arg):
        widget, node = arg
        self.addWidget(widget)
        self.addChild(node)

    def getChildren(self):
        return self.children.values()


if __name__ == "__main__":
    print "Hello";