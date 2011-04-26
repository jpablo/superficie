from pivy.coin import *
from PyQt4 import QtCore
from PyQt4 import QtGui
from superficie.util import wrap, malla2
from math import acos, pi, sqrt
from collections import Sequence

from util import intervalPartition, Vec3, segment
from util import Range
from BaseObject import GraphicObject, fluid
from superficie.Animation import Animation
from util import make_hideable, _1

def generaPuntos(coords):
    c = coords
    return (
        (c[0], c[1], c[5]),
        (c[3], c[1], c[5]),
        (c[3], c[4], c[5]),
        (c[0], c[4], c[5]),
        (c[0], c[1], c[2]),
        (c[3], c[1], c[2]),
        (c[3], c[4], c[2]),
        (c[0], c[4], c[2]))



class Points(GraphicObject):
    'A collection of points'

    def __init__(self, coords=[], colors=[(1, 1, 1)], name='', file=''):
        super(Points, self).__init__(name)
#        if file != "":
#            ## assume is an csv file
#            coords = lstToFloat(readCsv(file))
        ## ===============================
        self.materialBinding = SoMaterialBinding()
        self.coordinate = SoCoordinate3()

        self.materialBinding.value = SoMaterialBinding.PER_VERTEX
        ## ===============================
        self.root.addChild(self.materialBinding)
        self.root.addChild(self.coordinate)
        self.root.addChild(SoPointSet())
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



class Polygon(GraphicObject):
    def __init__(self, coords, name=""):
        super(Polygon, self).__init__(name)
        
        ## is a 2d point
        dim = len(coords[0])
        if  dim == 2:
            self.coords = [p + (0,) for p in coords]
        elif dim == 3:
            self.coords = coords
        ## just project to the first 3 coordinates
        elif dim > 3:
            self.coords = [(p[0], p[1], p[2]) for p in coords]
        ## ===============================
        coor = SoCoordinate3()
        coor.point.setValues(0, len(self.coords), self.coords)
        
        self.root.addChild(coor)


if __name__ == "__main__":

    p = Points()
    p.toText()