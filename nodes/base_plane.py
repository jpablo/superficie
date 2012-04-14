from pivy.coin import SoCoordinate3, SoQuadMesh, SoShapeHints
from superficie.base import GeometryNode
from superficie.util import Range, mesh2

__author__ = 'jpablo'

class BasePlane(GeometryNode):
    def __init__(self, plane="xy"):
        super(BasePlane,self).__init__()
        ## ============================
        self.plane = plane
        self.setDiffuseColor((.5, .5, .5))
        self.setAmbientColor((.5, .5, .5))
        ## ============================
        self.mesh = SoQuadMesh()
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.setRange((-2, 2, 7), plane)
        self.setTransparency(0.5)
        self.setTransparencyType(8)
        ## ============================
        self.separator.addChild(self.sHints)
        self.separator.addChild(self.mesh)

    def setHeight(self, val):
        oldVal = list(self.translation.translation.getValue())
        oldVal[self.constantIndex] = val
        self.translation.translation = oldVal

    def setRange(self, r0, plane=""):
        if plane == "":
            plane = self.plane
        self.plane = plane
        r = Range(*r0)
        self.points = []
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
        mesh2(self.points, self.func, r.min, r.dt, len(r), r.min, r.dt, len(r))
        self.coordinates.point.setValues(0, len(self.points), self.points)
        self.mesh.verticesPerColumn = len(r)
        self.mesh.verticesPerRow = len(r)