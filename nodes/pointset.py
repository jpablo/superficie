from pivy.coin import SoMaterialBinding, SoCoordinate3, SoPointSet
from BaseObject import GraphicObject, fluid

__author__ = 'jpablo'


## examples:
## ps = Points([(0,0,0),(1,1,1),(2,2,2)])
## ps.setPointSize(1)
## ps.setHSVColors([(.5,1,1),(.6,1,1),(.9,1,1)])


class Points(GraphicObject):
    """A collection of points"""

    def __init__(self, coords=[], colors=[(1, 1, 1)], name='', file=''):
        super(Points, self).__init__()
#        if file != "":
#            ## assume is an csv file
#            coords = lstToFloat(readCsv(file))
        ## ===============================
        self.materialBinding = SoMaterialBinding()
        self.coordinate = SoCoordinate3()
        self.materialBinding.value = SoMaterialBinding.PER_VERTEX
        ## ===============================
        self.addChild(self.materialBinding)
        self.addChild(self.coordinate)
        self.addChild(SoPointSet())
        ## ===============================
        self.setCoords(coords)
        self.setColors(colors)
        self.setPointSize(2)

    @fluid
    def setPointSize(self, n):
        self.drawStyle.pointSize = n

#    def setHSVColors(self,vec=[],pos=[],file=""):
#        if file != "":
#            dprom = column(lstToFloat(readCsv(file)),0)
#            vec = [(c,1,1) for c in dprom]
#        self.setColors(vec,pos,True)


    @fluid
    def setColors(self, vec, pos=[], hsv=False):
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
        if pos == []:
            colors = [vec[i % len(vec)] for i in range(n)]
        else:
            colors = [(1, 1, 1) for i in range(n)]
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

    def setCoords(self, coords, whichCoords=(0, 1, 2)):
        ## project the first 3 coordinates
        ## by default
        if len(coords) == 0:
            return
        dim = len(coords[0])
        if  dim == 2:
            self.coords = [p + (0,) for p in coords]
        else:
            self.coords = coords
        self.setWhichCoorsShow(whichCoords)

    def setWhichCoorsShow(self, whichCoords):
        ## this only make sense if dim >= 3
        ## whichCoords is a 3-tuple
        coords3 = [tuple(p[c] for c in whichCoords) for p in self.coords]
        self.coordinate.point.deleteValues(0)
        self.coordinate.point.setValues(0, len(coords3), coords3)

    def __len__(self):
        return len(self.coordinate.point)

    def __getitem__(self, key):
        return self.coordinate.point[key].getValue()