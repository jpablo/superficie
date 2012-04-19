from pivy.coin import SoMaterialBinding, SoCoordinate3, SoPointSet

from superficie.utils import fluid
from superficie.base import GeometryNode

## examples:
## ps = Points([(0,0,0),(1,1,1),(2,2,2)])
## ps.setPointSize(1)
## ps.setHSVColors([(.5,1,1),(.6,1,1),(.9,1,1)])


class PointSet(GeometryNode):
    """A collection of points"""

    def __init__(self, points=None, colors=None, name='', file=''):
        if not colors: colors = [(1, 1, 1)]
        super(PointSet, self).__init__()
        self.points = points or []
        self.colors = colors or [(1,1,1)]
#        if file != "":
#            ## assume is an csv file
#            coords = lstToFloat(readCsv(file))
        ## ===============================
        self.materialBinding = SoMaterialBinding()
        self.materialBinding.value = SoMaterialBinding.PER_VERTEX
        ## ===============================
        self.separator.addChild(self.materialBinding)
        self.separator.addChild(SoPointSet())
        ## ===============================
        self.setPoints(points)
        self.setColors(colors)
        self.setPointSize(2)


    def __len__(self):
        return len(self.coordinates.point)

    def __getitem__(self, key):
        return self.coordinates.point[key].getValue()

    @fluid
    def setPointSize(self, n):
        self.drawStyle.pointSize = n

#    def setHSVColors(self,vec=[],pos=[],file=""):
#        if file != "":
#            dprom = column(lstToFloat(readCsv(file)),0)
#            vec = [(c,1,1) for c in dprom]
#        self.setColors(vec,pos,True)


    @fluid
    def setColors(self, vec, pos=None, hsv=False):
        ## valid values:
        ## vec == (r,g,b) | [(r,g,b)]
        ## pos == []  ==> pos == range(len(self))
        ## if pos != [] and len(pos) <= len(vec)
        ##      ==> point[pos[i]] of color vec[i]
        ## if pos != [] and len(pos) > len(vec)
        ##      ==> colors are cycled trough positions
        ##      ==> the rest will be white
        n = len(self)
        if isinstance(vec[0], int):
            vec = [vec]
        if not pos:
            colors = [vec[i % len(vec)] for i in xrange(n)]
        else:
            colors = [(1, 1, 1) for i in xrange(n)]
            if len(pos) <= len(vec):
                for c, p in zip(vec, pos):
                    colors[p] = c
            else:
                for i, p in enumerate(pos):
                    colors[p] = vec[i % len(vec)]
        if hsv:
            self.diffuseColor.setHSVValues(0, len(colors), colors)
        else:
            self.diffuseColor.setValues(0, len(colors), colors)
        self.colors = colors

    def setPoints(self, points, axis=(0, 1, 2)):
        ## project the first 3 coordinates
        ## by default
        if not len(points):
            return
        dim = len(points[0])
        if  dim == 2:
            self.points = [p + (0,) for p in points]
        else:
            self.points = points
        self.setWhichCoorsShow(axis)

    def setWhichCoorsShow(self, axis):
        ## this only make sense if dim >= 3
        ## points_3d is a 3-tuple
        points_3d = [tuple(p[c] for c in axis) for p in self.points]
        self.coordinates.point.deleteValues(0)
        self.coordinates.point.setValues(0, len(points_3d), points_3d)
