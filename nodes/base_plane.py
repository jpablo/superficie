from pivy.coin import SoCoordinate3, SoQuadMesh, SoShapeHints
from BaseObject import GraphicObject
from util import Range, malla2

__author__ = 'jpablo'

class BasePlane(GraphicObject):
    def __init__(self, plane="xy"):
        super(BasePlane,self).__init__()
        ## ============================
        self.plane = plane
        self.setDiffuseColor((.5, .5, .5))
        self.setAmbientColor((.5, .5, .5))
        ## ============================
        self.coords = SoCoordinate3()
        self.mesh = SoQuadMesh()
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.setRange((-2, 2, 7), plane)
        self.setTransparency(0.5)
        self.setTransparencyType(8)
        ## ============================
        self.addChild(self.sHints)
        self.addChild(self.coords)
        self.addChild(self.mesh)

    def setHeight(self, val):
        oldVal = list(self.translation.translation.getValue())
        oldVal[self.constantIndex] = val
        self.translation.translation = oldVal

    def setRange(self, r0, plane=""):
        if plane == "":
            plane = self.plane
        self.plane = plane
        r = Range(*r0)
        self.ptos = []
        if plane == "xy":
            self.func = lambda x, y:(x, y, 0)
            ## this will be used to determine which coordinate to modify
            ## in setHeight
            self.constantIndex = 2
        elif plane == "yz":
            self.func = lambda y, z:(0, y, z)
            self.constantIndex = 0
        elif plane == "xz":
            self.func = lambda x, z:(x, 0, z)
            self.constantIndex = 1
        elif type(plane) == type(lambda :0):
            self.func = plane
        malla2(self.ptos, self.func, r.min, r.dt, len(r), r.min, r.dt, len(r))
        self.coords.point.setValues(0, len(self.ptos), self.ptos)
        self.mesh.verticesPerColumn = len(r)
        self.mesh.verticesPerRow = len(r)