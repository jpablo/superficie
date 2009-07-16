__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore, QtGui
from pivy.coin import SoCoordinate3
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

    def setupPlanes(self):
        self.addChild(Planos(True))


class GraphicObject(SoSwitch):
    def __init__(self, visible=False, parent=None):
        SoSwitch.__init__(self)
        self.qobject = QtCore.QObject()
        self.parent = parent
        self.children = nodeDict()
        self.setVisible(visible)
        ## ============================
        if parent:
            parent.addChild(self)

    def addChild(self, node):
        root = getattr(node, "root", node)
        SoSwitch.addChild(self,root)
        self.children[root] = node

    def getChildren(self):
        return self.children.values()

    def show(self):
        self.setVisible(True)

    def hide(self):
        self.setVisible(False)

    def setVisible(self, visible):
        if visible:
            self.whichChild = SO_SWITCH_ALL
        else:
            self.whichChild = SO_SWITCH_NONE


class Plano(GraphicObject):
    """
    Documentation
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


class Planos(GraphicObject):
    def __init__(self, visible=False, parent=None):
        GraphicObject.__init__(self,visible,parent)
        self.addChild(Plano(0))
        self.addChild(Plano(1))
        self.addChild(Plano(2))


if __name__ == "__main__":
    print "Hello";