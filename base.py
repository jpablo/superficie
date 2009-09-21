__author__="jpablo"
__date__ ="$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore, QtGui
from pivy.coin import SoCoordinate3
from pivy.coin import *
from superficie.util import nodeDict
from superficie.Animation import Animation
from superficie.gui import Button

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
        self.animations = []
        self.objectsForAnimate = []
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
        if hasattr(node, "updateAll"):
            node.updateAll()

    def addWidgetChild(self, arg):
        widget, node = arg
        self.addWidget(widget)
        self.addChild(node)

    def getChildren(self):
        return self.children.values()

    def setupPlanes(self):
        self.addChild(Planes(True))

    def setupAnimations(self,objects):
        self.objectsForAnimate = objects
        self.animations = [ ob.getAnimation() for ob in objects ]
        Animation.chain(self.animations, pause=1000)

        Button("inicio", self.animate, parent=self)

    def animate(self):
        for ob in self.objectsForAnimate:
            ob.resetObjectForAnimation()
        self.animations[0].start()


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




class Plane(GraphicObject):
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


class Planes(GraphicObject):
    def __init__(self, visible=False, parent=None):
        GraphicObject.__init__(self,visible,parent)
        self.addChild(Plane(0))
        self.addChild(Plane(1))
        self.addChild(Plane(2))


if __name__ == "__main__":
    print "Hello";