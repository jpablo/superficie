from collections import Sequence
from superficie.animations.animation import Animation
from superficie.util import Vec3, intervalPartition

#from nodes.curvevectorfield import CurveVectorField
from superficie.nodes.line import Line
from superficie.base import BaseObject


def fix_interval(it):
    """
    >>> fix_interval( (-1,1,20) )
    [(-1, 1, 20)]
    >>> fix_interval( [(-1,1,20)] )
    [(-1, 1, 20)]
    """
    return [it] if not isinstance(it[0], Sequence) else it

def fix_function(func,test_point):
    val = func(test_point)
    if isinstance(val,Vec3):
        return func
    else:
        ## not the most efficient, but...
        return lambda t: Vec3(func(t))


def find_line_index(lengths,i):
    """
    return the line index and the offset
    [2, 3] => ( [ 0 | 1 ] [ 0 | 1 | 2 ] )
                      ^             ^
    >>> find_line_index([2,3],1)
    (0, 1)
    >>> find_line_index([2,3],4)
    (1, 2)
    """
    for index,n in enumerate(lengths):
        if i < n:
            return index, i
        else:
            i -= n

class Curve3D(BaseObject):
    """
    A (possible broken) curve in 3D.
    examples:
    Curve3D(lambda x: (0,x,x**2),(-1,1,20))
    Curve3D(lambda x: (0,x,x**2),[(-1,0,20),(0.2,1,20)])
    """
    def __init__(self, func, interval, color=(1, 1, 1), width=1, nvertices= -1, domTrans=None):
        super(Curve3D,self).__init__()
        self.__derivative = None
        self.fields = {}
        self.lines = []
        self.intervals = fix_interval(interval)
        ## self.interval[0][0] is the start of the first interval
        ## should be a valid value, anyway
        self.function = fix_function(func,self.intervals[0][0])
#        ## ============================
#        if domTrans:
#            ptsTr = intervalPartition(self.interval, domTrans)
#            points = map(c, ptsTr)

        for it in self.intervals:
            points = intervalPartition(it, self.function)
            self.lines.append(Line(points, color, width, nvertices))
            self.separator.addChild(self.lines[-1].root) ## <--- container feature!!

        self.lengths = map(len, self.lines)
        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))

    def __len__(self):
        return sum(self.lengths)

    def __getitem__(self, i):
        """
        returns the i-th point
        """
        index, offset = find_line_index(self.lengths,i)
        return self.lines[index][offset]


    def setField(self, name, function):
        """
        Creates an arrow along each of the points of the field
        """
        return None
        field = self.fields[name] = CurveVectorField(function, self.domainPoints, self.points)
        self.addChild(field)
        return field

    def getDerivative(self):
        return self.__derivative

    def setDerivative(self, func):
        self.__derivative = func
        self.end_points = map(self.__derivative, self.domainPoints)
        self.tangent_vector = Arrow(self.points[0], self.points[0] + self.end_points[0])
        self.tangent_vector.setDiffuseColor((1, 0, 0))
        self.tangent_vector.head.height = .5

        def animate_tangent(i):
            self.tangent_vector.setPoints(self.points[i], self.points[i] + self.end_points[i])

        self.tangent_vector.animation = Animation(animate_tangent, (8000, 0, len(self) - 1))

    derivative = property(getDerivative, setDerivative)


    def setNumVertices(self, i):
        """shows only the first n vertices"""

        index, offset = find_line_index(self.lengths,i)

        for j in range(index-1):
            ## draw the whole line
            self.lines[j].setNumVertices(self.lengths[j])
        else:
            ## just the requested points
            self.lines[index].setNumVertices(offset)


    def project(self, x=None, y=None, z=None, color=(1, 1, 1), width=1, nvertices= -1):
        """
        Join the projections into a single Line object
        """
        return sum([line.project(x, y, z, color, width, nvertices) for line in self.lines])


    def updatePoints(self, func = None):
        """
        recalculates points according to the function func
        @param func: a function  R -> R^3
        """
        if func is not None:
            self.function = fix_function(func,self.intervals[0][0])
        for it, line in zip(self.intervals, self.lines):
            line.setPoints(intervalPartition(it, self.function))
        #-----------------------------------------------------------------------
        for f in self.fields.values():
            f.updatePoints(self.domainPoints, self.points)


    @property
    def domainPoints(self):
        """
        returns the preimages of the points
        """
        return sum(map(intervalPartition, self.intervals),[])

    @property
    def points(self):
        return sum([line.points for line in self.lines],[])
