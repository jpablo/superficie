from pivy.coin import SoCoordinate3, SoLineSet
from superficie.animations.animation import Animation
from superficie.base import GeometryNode
from superficie.util import Vec3
from superficie.utils import fluid


class Line(GeometryNode):
    """A Line
    example: segments p1:p2, p3:p4
    [p1,p2,p3,p4] = [(0,0,0),(1,1,1),(-1,2,0),(-1,-1,1)]
    Line([p1,p2,p3,p4]).setNumVerticesPerSegment([2,2])
    """
    def __init__(self, points, color=(1, 1, 1), width=1, nvertices= -1):
        super(Line,self).__init__()
        self.width = width
        self.diffuseColor = color
        self.lineset = SoLineSet()
        self.setPoints(points, nvertices)
        self.separator.addChild(self.lineset)
        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))

    def __getitem__(self, i):
        return self.coordinates.point[i]

    def __len__(self):
        return len(self.coordinates.point)

    def __add__(self, other):
        """
        Combine the two lines
        """
        if not other:
            return self
        return Line(
            points = self.points + other.points,
            color = self.diffuseColor,
            width = self.width,
        ).setNumVerticesPerSegment(self.numVerticesPerSegment + other.numVerticesPerSegment)

    def __radd__(self, other):
        return self + other

    @fluid
    def setPoints(self, pts, nvertices= -1):
        ## sometimes we don't want to show all points
        if nvertices == -1:
            nvertices = len(pts)
        npts = len(pts)
        self.coordinates.point.setValues(0, npts, pts)
        self.coordinates.point.setNum(npts)
        self.setNumVertices(nvertices)

    def getPoints(self):
        return self.coordinates.point.getValues()

    points = property(getPoints, setPoints)

    @fluid
    def setNumVertices(self, n):
        """Defines the first n vertices to be drawn"""
        self.lineset.numVertices.setValue(n)

    @fluid
    def setNumVerticesPerSegment(self, lst):
        """Controls which vertices are drawn"""
        self.lineset.numVertices.setValues(lst)

    def getNumVerticesPerSegment(self):
        return self.lineset.numVertices.getValues()

    numVerticesPerSegment = property(getNumVerticesPerSegment, setNumVerticesPerSegment)

    @fluid
    def setWidth(self, width):
        self.drawStyle.lineWidth.setValue(width)

    def getWidth(self):
        return self.drawStyle.lineWidth.getValue()

    width = property(getWidth, setWidth)

    def resetObjectForAnimation(self):
        self.setNumVertices(1)

    def project(self, x=None, y=None, z=None, color=(1, 1, 1), width=1, nvertices= -1):
        """insert the projection on the given plane"""
        assert (x,y,z) != (None,None,None)
        pts = self.getPoints()
        if x is not None:
            ptosProj = [Vec3(x, p[1], p[2]) for p in pts]
        elif y is not None:
            ptosProj = [Vec3(p[0], y, p[2]) for p in pts]
        elif z is not None:
            ptosProj = [Vec3(p[0], p[1], z) for p in pts]
        return Line(ptosProj, color, width, nvertices)