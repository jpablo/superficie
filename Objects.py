from pivy.coin import *
from PyQt4 import QtCore
from PyQt4 import QtGui

from util import wrap, malla2
from math import acos, pi, sqrt
from collections import Sequence
from MinimalViewer import MinimalViewer

from util import intervalPartition, Vec3, segment
from util import Range
from BaseObject import GraphicObject, fluid, CompositeObject, BaseObject
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
    """A collection of points"""

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
        
        self.addChild(coor)


############ portar ##########
class Point(Points):
    def __init__(self, coords, color=(1, 1, 1)):
        ## coords is a triple (x,y,z)
        Points.__init__(self, [coords], [color])

## examples:
## ps = Points([(0,0,0),(1,1,1),(2,2,2)])
## ps.setPointSize(1)
## ps.setHSVColors([(.5,1,1),(.6,1,1),(.9,1,1)])

#def Cylinder(col, length, radius = 0.98):
#    sep = SoSeparator()
#
#    cyl = SoCylinder()
#    cyl.radius.setValue(radius)
#    cyl.height.setValue(length)
#    cyl.parts = SoCylinder.SIDES
#
#    light = SoShapeHints()
##    light.VertexOrdering = SoShapeHints.COUNTERCLOCKWISE
##    light.ShapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
##    light.FaceType  = SoShapeHints.UNKNOWN_FACE_TYPE
#
#    mat = SoMaterial()
#    mat.emissiveColor = col
#    mat.diffuseColor = col
#    mat.transparency.setValue(0.5)
#
#    rot = SoRotationXYZ()
#    rot.axis = SoRotationXYZ.X
#    rot.angle = pi / 2
#
#    trans = SoTransparencyType()
##    trans.value = SoTransparencyType.DELAYED_BLEND
#    trans.value = SoTransparencyType.SORTED_OBJECT_BLEND
##    trans.value = SoTransparencyType.SORTED_OBJECT_SORTED_TRIANGLE_BLEND
#
#    sep.addChild(light)
#    sep.addChild(rot)
#    sep.addChild(trans)
#    sep.addChild(mat)
#    sep.addChild(cyl)
#
#    return sep
#
#
#def Sphere2(p, radius=.05, mat=None):
#    sep = SoSeparator()
#    sep.setName("Sphere")
#    tr = SoTranslation()
#    sp = SoSphere()
#    sp.radius = radius
#    tr.translation = p
#    if mat == None:
#        mat = SoMaterial()
#        mat.ambientColor.setValue(.33, .22, .27)
#        mat.diffuseColor.setValue(.78, .57, .11)
#        mat.specularColor.setValue(.99, .94, .81)
#        mat.shininess = .28
#    sep.addChild(tr)
#    sep.addChild(mat)
#    sep.addChild(sp)
#    return sep
#
#
#
#

class Sphere(GraphicObject):

    def __init__(self, center, radius=.05, color=(1, 1, 1), name=''):
        super(Sphere,self).__init__(name)
        self.sp = SoSphere()
        self.sp.radius = radius
#        ## ===================
        self.root.addChild(self.sp)
        self.origin = center
        self.color = color

    def getRadius(self):
        return self.sp.radius.getValue()

    def setRadius(self, radius):
        self.sp.radius = radius

    radius = property(getRadius, setRadius)
    

class Arrow(BaseObject):
    def __init__(self, p1, p2, scale=0.01, escalaVertice=2.0):
        """p1,p2: Vec3"""
        super(Arrow,self).__init__(name)
        self.base = None
        self.p1 = p1
        self.p2initial = self.p2 = p2
        self.scale = scale
        self.escalaVertice = escalaVertice
        self.lengthFactor = 1
        self.widthFactor = 1
        ## ============================
        sep = SoSeparator()
        sep.setName("Tube")
        self.sphere = Sphere(p1, scale * escalaVertice)
        self.base = self.addChild(self.sphere)
        self.tr1 = SoTransform()
        self.tr2 = SoTransform()

#        self.setAmbientColor((.0, .0, .0))
#        self.setDiffuseColor((.4, .4, .4))
#        self.setSpecularColor((.8, .8, .8))
#        self.setShininess(.1)
        self.cil = make_hideable(SoCylinder())
        self.cil.setName("segmento")
        ## ==========================
        conoSep = SoSeparator()
        self.conoTr = SoTransform()
        self.cono = SoCone()
        self.cono.bottomRadius = self.scale * 2
        self.matHead = SoMaterial()
        self.matHead.ambientColor = (.33, .22, .27)
        self.matHead.diffuseColor = (.78, .57, .11)
        self.matHead.specularColor = (.99, .94, .81)
        self.matHead.shininess = .28
        conoSep.addChild(self.matHead)
        conoSep.addChild(self.conoTr)
        conoSep.addChild(self.cono)
        ## ==========================
        sep.addChild(self.tr2)
        sep.addChild(self.tr1)
        sep.addChild(self.cil.parent_switch)
        sep.addChild(conoSep)
        ## ============================
        self.calcTransformation()
        #self.cono.height = self.cil.height.getValue() * .2
        self.setWidthFactor(.1)
        self.addChild(sep)


    def calcTransformation(self):
        scaledP2 = segment(self.p1, self.p2initial, self.lengthFactor)
        vec = scaledP2 - self.p1
        t = vec.length() if vec.length() != 0 else .00001
        self.tr1.translation = (0, t / 2.0, 0)
        self.conoTr.translation = (0, t / 2.0, 0)
        self.cil.height = t ##?
        self.tr2.translation = self.p1
        if self.base:
            self.base.setOrigin(self.p1)

        ## TODO: pasar a util
        def ajustaArg(arg):
            if arg > 1.0:
                return 1.0
            elif arg < -1.0:
                return -1.0
            return arg

        zt = Vec3(0, t, 0)
        ejeRot = zt.cross(vec)
        ang = acos(ajustaArg(zt.dot(vec) / t ** 2))
        arg = zt.dot(vec) / t ** 2
        ang = acos(ajustaArg(arg))
        if ejeRot.length() < .0001:
            ejeRot = Vec3(1, 0, 0)
        self.tr2.rotation.setValue(ejeRot, ang)

    @fluid
    def setRadius(self, r):
        self.cil.radius = r
        rr = r * 1.5
        self.sphere.radius = rr
        self.cono.bottomRadius = rr
        self.cono.height = 3*sqrt(3)*r
        coneHeight = self.cono.height.getValue()
        self.cil.height = self.cil.height.getValue() - coneHeight /2.0

    @fluid
    def setPoints(self, p1, p2):
        "p1, p2: Vec3d"
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.calcTransformation()

    @fluid
    def setP2(self, pt):
        self.p2 = pt
        self.calcTransformation()

    @fluid
    def setLengthFactor(self, factor):
        self.lengthFactor = factor
        self.calcTransformation()

    @fluid
    def setWidthFactor(self, factor):
        self.widthFactor = factor
        r = self.cil.radius.getValue() * factor
        self.setRadius(r)


class Line(BaseObject):
    def __init__(self, ptos, color=(1, 1, 1), width=1, nvertices= -1, name="Line", visible=False, parent=None):
        BaseObject.__init__(self, visible, parent)
        sep = SoSeparator()
        sep.setName("Line")
        self.coords = SoCoordinate3()
        self.lineset = SoLineSet()
        self.draw = SoDrawStyle()
        ## ============================
        self.setCoordinates(ptos, nvertices)
        self.setWidth(width)
        self.material.diffuseColor = color
        ## ============================
        sep.addChild(self.coords)
        sep.addChild(self.draw)
        sep.addChild(self.lineset)
        self.addChild(sep)
        #        self.whichChild = 0
        ## ============================
        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))

    @fluid
    def setWidth(self, width):
        self.draw.lineWidth.setValue(width)

    width = property(fset=setWidth)

    def resetObjectForAnimation(self):
        self.setNumVertices(1)

    def __getitem__(self, i):
        "overwrite BaseObject.__getitem__"
        ## this makes more sense in this case
        return self.coords.point[i]

    def __len__(self):
        return len(self.coords.point)

    def setNumVertices(self, n):
        "Defines the first n vertices to be drawn"
        self.lineset.numVertices.setValue(n)

    def setVertexIndexes(self, lst):
        "Controls which vertices are drawn"
        self.lineset.numVertices.setValues(lst)

    def setCoordinates(self, ptos, nvertices= -1):
        ## sometimes we don't want to show all points
        if nvertices == -1:
            nvertices = len(ptos)
        self.coords.point.setValues(0, len(ptos), ptos)
        self.setNumVertices(nvertices)

    def getCoordinates(self):
        """return the points"""
        return self.coords.point.getValues()

    def project(self, x=None, y=None, z=None, color=(1, 1, 1), width=1, nvertices= -1):
        """insert the projection on the given plane"""
        pts = self.getCoordinates()
        if x != None:
            ptosProj = [Vec3(x, p[1], p[2]) for p in pts]
        elif y != None:
            ptosProj = [Vec3(p[0], y, p[2]) for p in pts]
        elif z != None:
            ptosProj = [Vec3(p[0], p[1], z) for p in pts]
        return Line(ptosProj, color, width, nvertices, visible=True, parent=self.parent)
#
#
#class CurveVectorField(Arrow):
#    '''
#    Holds data needed to draw an arrow along a vector field
#    '''
#    def __init__(self, function, domain_points, base_arrow_points, visible=True, parent=None):
#        super(CurveVectorField, self).__init__(Vec3(0,0,0), Vec3(0,0,0), escala=0.1, escalaVertice=2, extremos=True, visible=True, parent=parent)
#        self.function = function
#        self.domain_points = None
#        self.base_arrow_points = None
#        self.end_points = None
#        self.animation = None
#        self.last_i = 0
#        self.updatePoints(domain_points, base_arrow_points)
#        self.setDiffuseColor((1, 0, 0))
#        self.cono.height = .5
#        self.base.setDiffuseColor((1, 1, 0))
#        self.animation = Animation(self.animate_field, (8000, 0, len(self.base_arrow_points) - 1))
#
#
#    def animate_field(self, i):
#        self.setPoints(self.base_arrow_points[i], self.base_arrow_points[i] + self.end_points[i])
#        self.last_i = i
#
#    def updatePoints(self, domain_points, base_arrow_points):
#        self.domain_points = domain_points
#        self.base_arrow_points = base_arrow_points
#        self.end_points = map(self.function, self.domain_points)
#        self.animate_field(self.last_i)
#
#
#class CurveVectorField2(BaseObject):
#    '''
#    Holds data needed to draw an arrow along a vector field
#    '''
#    def __init__(self, function, domain_points, base_arrow_points, visible=True, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        self.function = function
#        self.domain_points = None
#        self.base_arrow_points = None
#        self.end_points = None
#        self.arrow = None
#        self.animation = None
#        self.last_i = 0
#        self.arrow = Arrow(Vec3(0,0,0), Vec3(0,0,0), escala=0.1, escalaVertice=2, extremos=True, visible=True)
#        self.updatePoints(domain_points, base_arrow_points)
#        self.arrow.setDiffuseColor((1, 0, 0))
#        self.arrow.cono.height = .5
#        self.arrow.base.setDiffuseColor((1, 1, 0))
#        self.addChild(self.arrow)
#        self.animation = Animation(self.animate_field, (8000, 0, len(self.base_arrow_points) - 1))
#
#
#    def animate_field(self, i):
#        self.arrow.setPoints(self.base_arrow_points[i], self.base_arrow_points[i] + self.end_points[i])
#        self.last_i = i
#
#
#    @fluid
#    def setLengthFactor(self, factor):
#        self.arrow.setLengthFactor(factor)
#
#    @fluid
#    def setWidthFactor(self, factor):
#        self.arrow.setWidthFactor(factor)
#
#    def updatePoints(self, domain_points, base_arrow_points):
#        self.domain_points = domain_points
#        self.base_arrow_points = base_arrow_points
#        self.end_points = map(self.function, self.domain_points)
#        self.animate_field(self.last_i)
#
#class Curve3D(BaseObject):
#    """
#    A curve in 3D. It is composed of one or several Lines
#    """
#    def __init__(self, func, iter, color=(1, 1, 1), width=1, nvertices= -1, visible=True, parent=None, domTrans=None):
#        BaseObject.__init__(self, visible, parent)
#        self.__derivative = None
#        self.fields = {}
#        self.lines = []
#        self.iter = iter
#        c = lambda t: Vec3(func(t))
#        ## ============================
#        if domTrans:
#            ptsTr = intervalPartition(self.iter, domTrans)
#            print max(ptsTr), min(ptsTr)
#            points = map(c, ptsTr)
#
#        self.func = func
#        if not isinstance(self.iter[0], Sequence):
#            self.iter = [self.iter]
#        for it in self.iter:
#            points = intervalPartition(it, c)
#            self.lines.append(Line(points, color, width, nvertices, visible=True, parent=self))
#
#        self.lengths = map(len, self.lines)
#        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))
#
#    def setField(self, name, function):
#        '''
#        Creates an arrow along each of the points of the field
#        @param function: callable
#        @param name: string
#        '''
#        field = self.fields[name] = CurveVectorField(function, self.domainPoints, self.Points,parent=self)
#        return field
#
#    def getDerivative(self):
#        return self.__derivative
#
#    def setDerivative(self, func):
#        self.__derivative = func
#        end_points = map(self.__derivative, self.domainPoints)
#        self.tangent_vector = Arrow(self.Points[0], self.Points[0] + end_points[0], visible=False, escala=0.1, escalaVertice=2, extremos=True, parent=self)
#        self.tangent_vector.setDiffuseColor((1, 0, 0))
#        self.tangent_vector.cono.height = .5
#        self.tangent_vector.base.setDiffuseColor((1, 1, 0))
#
#        def animate_tangent(i):
#            self.tangent_vector.setPoints(self.Points[i], self.Points[i] + end_points[i])
#
#        self.tangent_vector.animation = Animation(animate_tangent, (8000, 0, len(self) - 1))
#
#    derivative = property(getDerivative, setDerivative)
#
#
#    def __len__(self):
#        return sum(self.lengths)
#
#    def setNumVertices(self, n):
#        "shows only the first n vertices"
##        self.lineset.numVertices.setValue(n)
#        ## find out on which line n lies
#        for line in self.lines:
#            nl = len(line)
#            if n < nl:
#                line.setNumVertices(n)
#                break
#            else:
#                ## draw the whole line
#                line.setNumVertices(nl)
#                n -= nl
#
#    def getCoordinates(self):
#        '''
#        returns the joined coordinates of all the lines
#        '''
#        coord = []
#        for line in self.lines:
#            #------------"l += i" it's the same that "l = l + i"
#            #------------coord = coord + line.getCoordinates()
#            coord += line.getCoordinates()
#        return coord
#
#    def project(self, x=None, y=None, z=None, color=(1, 1, 1), width=1, nvertices= -1):
#        for line in self.lines:
#            line.project(x, y, z, color, width, nvertices)
#        return line.project(x, y, z, color, width, nvertices)
#
#
#    def __getitem__(self, i):
#        '''
#        returns the i-th point
#        @param i: the index
#        '''
#        for line in self.lines:
#            nl = len(line)
#            if i < nl:
#                return line[i]
#            else:
#                i -= nl
#
#    def updatePoints(self, func = None):
#        '''
#        recalculates points according to the function func
#        @param func: a function  R -> R^3
#        '''
#        if func is not None:
#            self.func = func
#        #c = lambda t: Vec3(self.func(t))
#        for it, line in zip(self.iter, self.lines):
#            line.setCoordinates(intervalPartition(it, self.func))
#        #-----------------------------------------------------------------------
#        for f in self.fields.values():
#            f.updatePoints(self.domainPoints, self.Points)
#
#
#    @property
#    def domainPoints(self):
#        '''
#        returns the preimages of the points
#        '''
#        ret = []
#        for it in self.iter:
#            ret += intervalPartition(it)
#        return ret
#
#    @property
#    def Points(self):
#        ret = []
#        for line in self.lines:
#            ret += line.getCoordinates()
#        return ret
#
#
#class Bundle3(BaseObject):
#    def __init__(self, curve, cp, factor=1, name="", visible=False, parent=None):
#        """curve is something derived from Line"""
#        BaseObject.__init__(self, visible, parent)
#        self.curve = curve
#        self.cp = cp
#        self.factor = factor
#        self.line = Line(())
#        ## ============================
#        self.coords = SoCoordinate3()
#        self.mesh = SoQuadMesh()
#        self.mesh.verticesPerColumn = len(curve)
#        self.mesh.verticesPerRow = 2
#        nb = SoNormalBinding()
##        nb.value = SoNormalBinding.PER_VERTEX_INDEXED
#        sHints = SoShapeHints()
#        sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
#
#        self.generateArrows()
#        ## ============================
#        self.scale = SoScale()
#        ## ============================
#        sep = SoSeparator()
#        sep.addChild(nb)
#        sep.addChild(sHints)
#        sep.addChild(self.scale)
#        sep.addChild(self.coords)
#        sep.addChild(self.mesh)
##        self.addChild(self.line)
#        self.addChild(sep)
#
#        self.animation = Animation(lambda num: float(num) / len(curve) * self.material.transparency.getValue(), (4000, 1, len(curve)))
#
#    def __len__(self):
#        "the same lengh as the base curve"
#        return len(self.curve)
#
#    def setFactor(self, factor):
#        '''
#        Set multiplicative factor for arrow length
#        @param factor:
#        '''
#        self.factor = factor
#        self.generateArrows()
#
#    def generateArrows(self):
#        '''
#        create the arrows
#        '''
#        points = self.curve.getCoordinates()
#        #pointsp = [self.curve[i]+self.cp(t)*self.factor for i,t in enumerate(intervalPartition(self.curve.iter))]
#        pointsp = [self.curve[i] + self.cp(t) * self.factor for i, t in enumerate(self.curve.domainPoints)]
#        pointsRow = zip(map(tuple, points), map(tuple, pointsp))
#
#        pointsRowFlatten = []
#        vertexIndexes = []
#        for p, pp in pointsRow:
#            ## TODO: triangular!!
#            pointsRowFlatten.append(p)
#            pointsRowFlatten.append(pp)
#            vertexIndexes.append(2)
#        ## ============================
#        self.line.setCoordinates(pointsRowFlatten)
#        self.line.setVertexIndexes(vertexIndexes)
#        self.coords.point.setValues(0, len(pointsRowFlatten), pointsRowFlatten)
#
#
#    def setTransparency(self, val):
#        BaseObject.setTransparency(self, val)
##        self.line.setTransparency(val)
#
#    def setTransparencyType(self, trans):
#        BaseObject.setTransparencyType(self, trans)
##        self.line.setTransparencyType(trans)
#
#    def setNumVisibleArrows(self, num):
#        """set the number of arrow to show"""
#        self.mesh.verticesPerColumn = num
#
#
#class Bundle2(BaseObject):
#    def __init__(self, curve, cp, col, factor=1, name="", visible=False, parent=None):
#        """curve is something derived from Curve3D"""
#        BaseObject.__init__(self, visible, parent)
#        comp = SoComplexity()
#        comp.value.setValue(.1)
#        self.root.addChild(comp)
#        ## ============================
#        points = curve.getCoordinates()
#        pointsp = [curve[i] + cp(t) * factor for i, t in enumerate(curve.domainPoints)]
#        for p, pp in zip(points, pointsp):
#            self.addChild(Arrow(p, pp, visible=True, escala=.005, extremos=True))
#
#        self.animation = Animation(lambda num: self[num - 1].show(), (4000, 1, len(points)))
#
#    def setMaterial(self, mat):
#        for c in self.getChildren():
#            c.material.ambientColor = mat.ambientColor
#            c.material.diffuseColor = mat.diffuseColor
#            c.material.specularColor = mat.specularColor
#            c.material.shininess = mat.shininess
#
#    def setHeadMaterial(self, mat):
#        for c in self.getChildren():
#            c.matHead.ambientColor = mat.ambientColor
#            c.matHead.diffuseColor = mat.diffuseColor
#            c.matHead.specularColor = mat.specularColor
#            c.matHead.shininess = mat.shininess
#
#    def resetObjectForAnimation(self):
#        self.hideAllArrows()
#
#    def setRadius(self, r):
#        for c in self.getChildren():
#            c.setRadius(r)
#
#    def setLengthFactor(self, factor):
#        for c in filter(lambda c: isinstance(c, Arrow), self.getChildren()):
#            c.setLengthFactor(factor)
#
#    def hideAllArrows(self):
#        for arrow in self.getChildren():
#            arrow.hide()
#
#    def setNumVisibleArrows(self, num):
#        """set the number of arrow to show"""
#        print "setNumVisibleArrows:", num
#
#
#
#
#class Bundle(BaseObject):
#    def __init__(self, c, cp, partition, col, factor=1, name="", visible=False, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        tmin, tmax, n = partition
#        puntos = [c(t) for t in intervalPartition([tmin, tmax, n])]
#        puntosp = [c(t) + cp(t) * factor for t in intervalPartition([tmin, tmax, n])]
#        for p, pp in zip(puntos, puntosp):
#            self.addChild(Arrow(p, pp, extremos=True, escalaVertice=3, visible=True))
#
#        self.animation = Animation(lambda num: self[num - 1].show(), (4000, 1, n))
#
#    def setMaterial(self, mat):
#        for c in self.getChildren():
#            c.material.ambientColor = mat.ambientColor
#            c.material.diffuseColor = mat.diffuseColor
#            c.material.specularColor = mat.specularColor
#            c.material.shininess = mat.shininess
#
#    def setHeadMaterial(self, mat):
#        for c in self.getChildren():
#            c.matHead.ambientColor = mat.ambientColor
#            c.matHead.diffuseColor = mat.diffuseColor
#            c.matHead.specularColor = mat.specularColor
#            c.matHead.shininess = mat.shininess
#
#    def resetObjectForAnimation(self):
#        self.hideAllArrows()
#
#    def setRadius(self, r):
#        for c in self.getChildren():
#            c.setRadius(r)
#
#    def setLengthFactor(self, factor):
#        for c in self.getChildren():
#            if hasattr(c, "setLengthFactor"):
#                c.setLengthFactor(factor)
#
#    def hideAllArrows(self):
#        for arrow in self.getChildren():
#            arrow.hide()
#
#
#class TangentPlane(BaseObject):
#    def __init__(self, param, par1, par2, pt, color, visible=False, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        ve = par1(pt[0])
#        ve.normalize()
#        ue = par2(pt[1])
#        ue.normalize()
#        def planePar(h, t):
#            return tuple(Vec3(param(*pt)) + h * ve + t * ue)
#        baseplane = BasePlane()
#        baseplane.setRange((-.5, .5, 30), plane=planePar)
#        baseplane.setTransparency(0)
#        baseplane.setDiffuseColor(color)
#        baseplane.setEmissiveColor(color)
#        self.addChild(baseplane)
#
#class TangentPlane2(BaseObject):
#    def __init__(self, param, par1, par2, (xorig,yorig), color, visible=False, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        self.par1 = par1
#        self.par2 = par2
#        self.param = param
#        self.localOrigin = (xorig,yorig)
#        self.r0 = (-1, 1, 30)
#
#        self.baseplane = BasePlane()
#        self.baseplane.setTransparency(.4).setDiffuseColor(color).setEmissiveColor(color)
#        self.addChild(self.baseplane)
#        self.localOriginSphere = Sphere(param(*self.localOrigin), radius=.03, color=(1,0,0), visible=True)
#        self.addChild(self.localOriginSphere)
#
#        self.localXAxis = Line([], color=(1,0,0), visible=False)
#        self.localYAxis = Line([], color=(1,0,0), visible=False)
#        self.addChild(self.localXAxis)
#        self.addChild(self.localYAxis)
#        ## ============================
#        self.setLocalOrigin(self.localOrigin)
#
#
#    def setLocalOrigin(self, pt):
#        self.localOrigin = pt
#        ve = self.par1(*pt)
#        ve.normalize()
#        ue = self.par2(*pt)
#        ue.normalize()
#        orig = Vec3(self.param(*pt))
#        self.planeParam = lambda h, t: tuple(orig + h * ve + t * ue)
#        self.baseplane.setRange(self.r0, plane=self.planeParam)
#        self.localOriginSphere.setOrigin(orig)
#        self.localXAxis.setCoordinates([self.planeParam(*pt) for pt in [(self.r0[0],0),(self.r0[1],0)]])
#        self.localYAxis.setCoordinates([self.planeParam(*pt) for pt in [(0,self.r0[0]),(0,self.r0[1])]])
#
#    def setU(self, val):
#        self.setLocalOrigin((val, self.localOrigin[1]))
#
#    def setV(self, val):
#        self.setLocalOrigin((self.localOrigin[0], val))
#
#    def setRange(self, r0):
#        self.r0 = r0
#        self.baseplane.setRange(self.r0)
#

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
        self.root.addChild(self.translation)
        self.root.addChild(self.sHints)
        self.root.addChild(self.coords)
        self.root.addChild(self.mesh)
        self.setRange((-2, 2, 7), plane)
        self.setTransparency(0.5)
        self.setTransparencyType(8)

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

#
#
#
#class Plane(BaseObject):
#    """
#    """
#    def __init__(self, pos, visible=True, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        self.altura = -1
#        vertices = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
#        for p in vertices:
#            p.insert(pos, self.altura)
#        sh = SoShapeHints()
#        sh.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
#        sh.faceType = SoShapeHints.UNKNOWN_FACE_TYPE
#        sh.shapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
#        coords = SoCoordinate3()
#        coords.point.setValues(0, len(vertices), vertices)
#        mesh = SoQuadMesh()
#        mesh.verticesPerColumn = 2
#        mesh.verticesPerRow = 2
#        nb = SoNormalBinding()
##            nb.value = SoNormalBinding.PER_VERTEX_INDEXED
#        mat = SoMaterial()
#        mat.transparency = 0.5
#        self.setTransparencyType(8)
#        ## ============================
#        root = SoSeparator()
#        root.addChild(sh)
#        root.addChild(mat)
#        root.addChild(nb)
#        root.addChild(coords)
#        root.addChild(mesh)
#        self.addChild(root)
#
#    def setAltura(self, val):
#        pass
#
#
#class Planes(BaseObject):
#    def __init__(self, visible=False, parent=None):
#        BaseObject.__init__(self, visible, parent)
#        self.addChild(Plane(0))
#        self.addChild(Plane(1))
#        self.addChild(Plane(2))
#


#if __name__ == "__main__":
#
#    p = Points()
#    p.toText()
#

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    viewer = MinimalViewer()
    viewer.root.addChild(Sphere((0,0,0),1).root)
    viewer.resize(400, 400)
    viewer.show()
    viewer.viewAll()

    sys.exit(app.exec_())

