from PyQt4 import QtCore
from PyQt4 import QtGui
from pivy.coin import SoSeparator
from superficie.animations.animation import Animation
from superficie.widgets.button import Button
from superficie.nodes import Arrow, BasePlane
from superficie.util import nodeDict, Vec3


class Page(QtCore.QObject):
    """The base class of a container node"""

    def __init__(self, name=""):
        QtCore.QObject.__init__(self)
        self.name = name
        self.root = SoSeparator()
        self.root.setName("Page:root")
        self.children = nodeDict()
        self.camera_position = None
        self.camera_point_at = None
        self.camera_viewAll = True
        ## =========================
        self.animations = []
        self.objectsForAnimate = []
        self.coordPlanes = {}
        ## =========================
        self.setupGui()
        self.setupAxis()
        self.showAxis(False)

    def setupGui(self):
        layout = QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            title = QtGui.QLabel("<center><h1>%s</h1></center>" % self.name)
            title.setWordWrap(True)
            layout.addWidget(title)
            layout.addStretch()
            ## ============================
        notes = QtGui.QLabel(self.__doc__)
        notes.setWordWrap(True)
        notes.setTextFormat(QtCore.Qt.RichText)
        notes_layout = QtGui.QVBoxLayout()
        notes_layout.addWidget(notes)
        notes_layout.addStretch()
        self.notesWidget = QtGui.QWidget()
        self.notesWidget.setLayout(notes_layout)

    def getGui(self):
        return self.widget

    def getNotes(self):
        return self.notesWidget

    def addWidget(self, widget):
        self.widget.layout().addWidget(widget)

    def addLayout(self, layout):
        self.widget.layout().addLayout(layout)

    def addChild(self, node):
        # if `node` has an attribute root, we assume it is the OpenInventor root object
        # otherwise node is assumed to be an OI object
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
        self.coordPlanes = {
            'xy': BasePlane(plane="xy").setDiffuseColor((1, 1, 0)),
            'xz': BasePlane(plane="xz").setDiffuseColor((1, 0, 1)),
            'yz': BasePlane(plane="yz").setDiffuseColor((0, 1, 1))
        }
        for p in self.coordPlanes.values():
            p.setRange(r0)
            p.setHeight(r0[0])
            self.addChild(p)

    def showAxis(self, show):
        """
        @param show: bool
        """
        self.axis_x.setVisible(show)
        self.axis_y.setVisible(show)
        self.axis_z.setVisible(show)

    def setupAxis(self):
        self.axis_x = Arrow(Vec3(-5, 0, 0), Vec3(5, 0, 0))
        self.axis_y = Arrow(Vec3(0, -5, 0), Vec3(0, 5, 0))
        self.axis_z = Arrow(Vec3(0, 0, -5), Vec3(0, 0, 5))
        self.axis_x.setDiffuseColor((1, 0, 0)).setWidthFactor(.2)
        self.axis_y.setDiffuseColor((0, 1, 0)).setWidthFactor(.2)
        self.axis_z.setDiffuseColor((0, 0, 1)).setWidthFactor(.2)
        self.addChildren([self.axis_x, self.axis_y, self.axis_z ])

    def setupAnimations(self, objects):
        """
        Extracts the 'animation' property of the objects and chains them
        """
        self.objectsForAnimate = objects
        self.animations = [ getattr(ob, 'animation', ob) for ob in objects ]
        Animation.chain(self.animations, pause=1000)

        Button("inicio", self.animate, parent=self)

    def animate(self):
        for ob in self.objectsForAnimate:
            ob.resetObjectForAnimation()
        self.animations[0].start()
