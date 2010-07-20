from pivy.coin import *
from PyQt4 import QtCore
from PyQt4 import QtGui
from superficie.util import wrap, malla2
from math import acos
from collections import Sequence

from superficie.util import intervalPartition, Vec3, segment
from superficie.util import Range
from superficie.base import GraphicObject
from superficie.Animation import Animation

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


indicesCubo = (
    0, 1, 2, 3, SO_END_FACE_INDEX,
    0, 4, 5, 1, SO_END_FACE_INDEX,
    1, 5, 6, 2, SO_END_FACE_INDEX,
    2, 6, 7, 3, SO_END_FACE_INDEX,
    3, 7, 4, 0, SO_END_FACE_INDEX,
    4, 5, 6, 7, SO_END_FACE_INDEX,
    )



class Cube(QtCore.QObject):
    def __init__(self, mincoord, maxcoord):
        QtCore.QObject.__init__(self)
        self.coords = list(mincoord)
        self.coords.extend(maxcoord)
        self.ptos = generaPuntos(self.coords)
        self.root = self.creaNodo()

    def creaNodo(self):
        root = SoSeparator()
        coords = SoCoordinate3()
        coords.point.setValues(0, len(self.ptos), self.ptos)
        root.addChild(coords)
        indices = SoIndexedFaceSet()
        indices.coordIndex.setValues(0, len(indicesCubo), indicesCubo)
        root.addChild(indices)
        return root

class Points(GraphicObject):
    def __init__(self, coords=[], colors=[(1, 1, 1)], name="", file=""):
        super(Points, self).__init__(name)
#        if file != "":
#            ## assume is an csv file
#            coords = lstToFloat(readCsv(file))
        ## ===============================
        self.root = SoSeparator()
        self.material = SoMaterial()
        self.materialBinding = SoMaterialBinding()
        self.materialBinding.value = SoMaterialBinding.PER_VERTEX
        ds = SoDrawStyle()
        ds.pointSize = 2
        self.coordinate = SoCoordinate3()
        ## ===============================
        self.root.addChild(self.material)
        self.root.addChild(self.materialBinding)
        self.root.addChild(self.coordinate)
        self.root.addChild(ds)
        self.root.addChild(SoPointSet())
        ## ===============================
        self.setCoords(coords)
        self.setColors(colors)

    def setPointSize(self, n):
        self.root[3].pointSize = n

#    def setHSVColors(self,vec=[],pos=[],file=""):
#        if file != "":
#            dprom = column(lstToFloat(readCsv(file)),0)
#            vec = [(c,1,1) for c in dprom]
#        self.setColors(vec,pos,True)


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
            self.material.diffuseColor.setHSVValues(0, len(colors), colors)
        else:
            self.material.diffuseColor.setValues(0, len(colors), colors)
        self.colors = colors

    def setCoords(self, coords, whichCoords=(0, 1, 2)):
        ## project the first 3 coordinates
        ## by default
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


class Point(Points):
    def __init__(self, coords, color=(1, 1, 1)):
        ## coords is a triple (x,y,z)
        Points.__init__(self, [coords], [color])

## examples:
## ps = Points([(0,0,0),(1,1,1),(2,2,2)])
## ps.setPointSize(1)
## ps.setHSVColors([(.5,1,1),(.6,1,1),(.9,1,1)])

class Polygon(QtCore.QObject):
    def __init__(self, coords, name=""):
        QtCore.QObject.__init__(self)
        self.name = name
        if self.name != "":
            self.getGui = lambda: QtGui.QLabel("<center><h1>%s</h1></center>" % self.name)
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
        self.root = SoSeparator()
        coor = SoCoordinate3()
        coor.point.setValues(0, len(self.coords), self.coords)

        
def Sphere2(p, radius=.05, mat=None):
    sep = SoSeparator()
    sep.setName("Sphere")
    tr = SoTranslation()
    sp = SoSphere()
    sp.radius = radius
    tr.translation = p
    if mat == None:
        mat = SoMaterial()
        mat.ambientColor.setValue(.33, .22, .27)
        mat.diffuseColor.setValue(.78, .57, .11)
        mat.specularColor.setValue(.99, .94, .81)
        mat.shininess = .28
    sep.addChild(tr)
    sep.addChild(mat)
    sep.addChild(sp)
    return sep

class Sphere(GraphicObject):
    def __init__(self, center, radius=.05, color=(1, 1, 1), visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        sp = SoSphere()
        sp.radius = radius
#        ## ===================
        self.addChild(sp)
        self.setOrigin(center)


class Tube(object):
    def __init__(self, p1, p2, escala=0.01, escalaVertice=2.0, mat=None, extremos=False):
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.escala = 0.01
        self.escalaVertice = escalaVertice
        ## ============================
        sep = SoSeparator()
        sep.setName("Tube")
        if extremos:
            sep.addChild(Sphere(p1, escala * escalaVertice))
            #~ sep.addChild(esfera(p2, escala*escalaVertice))
        self.tr1 = SoTransform()
        self.tr2 = SoTransform()
        if mat == None:
            mat = SoMaterial()
            mat.ambientColor.setValue(.0, .0, .0)
            mat.diffuseColor.setValue(.4, .4, .4)
            mat.specularColor.setValue(.8, .8, .8)
            mat.shininess = .1
        self.cil = wrap(SoCylinder())
        self.cil.setName("segmento")
        ## ==========================
        conoSep = SoSeparator()
        self.conoTr = SoTransform()
        cono = SoCone()
        cono.bottomRadius = .025
        cono.height = .1
        mat2 = SoMaterial()
        mat2.ambientColor.setValue(.33, .22, .27)
        mat2.diffuseColor.setValue(.78, .57, .11)
        mat2.specularColor.setValue(.99, .94, .81)
        mat2.shininess = .28
        conoSep.addChild(mat2)
        conoSep.addChild(self.conoTr)
        conoSep.addChild(cono)
        ## ==========================
        sep.addChild(self.tr2)
        sep.addChild(self.tr1)
        sep.addChild(mat)
        sep.addChild(self.cil)
        sep.addChild(conoSep)
        ## ============================
        self.calcTransformation()
        self.root = sep

    def calcTransformation(self):
        vec = self.p2 - self.p1
        t = vec.length() if vec.length() != 0 else .00001
        self.tr1.translation = (0, t / 2.0, 0)
        self.conoTr.translation = (0, t / 2.0, 0)
        self.cil[0].radius = self.escala
        self.cil[0].height = t
        self.tr2.translation = self.p1
        zt = Vec3(0, t, 0)
        ejeRot = zt.cross(vec)
        ang = acos(zt.dot(vec) / t ** 2)
        if ejeRot.length() < .0001:
            ejeRot = Vec3(1, 0, 0)
        self.tr2.rotation.setValue(ejeRot, ang)

    def setRadius(self, r):
        self.cil[0].radius = r

    def setPoints(self, p1, p2):
        """Documentation"""
        self.p1 = p1
        self.p2 = p2
        self.calcTransformation()
    
    def setP2(self, pt):
        self.p2 = pt
        self.calcTransformation()
    
    def setLengthFactor(self, factor):
        self.lengthFactor = factor
        self.setP2(segment(self.p1, self.p2inicial, factor))


class Arrow(GraphicObject):
    def __init__(self, p1, p2, escala=0.01, escalaVertice=2.0, extremos=False, visible=False, parent=None):
        "p1,p2: Vec3"
        GraphicObject.__init__(self, visible, parent)
        self.base = None
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.escala = escala
        self.escalaVertice = escalaVertice
        ## ============================
        sep = SoSeparator()
        sep.setName("Tube")
        if extremos:
            self.base = self.addChild(Sphere(p1, escala * escalaVertice, visible=True))
        self.tr1 = SoTransform()
        self.tr2 = SoTransform()

        self.setAmbientColor((.0, .0, .0))
        self.setDiffuseColor((.4, .4, .4))
        self.setSpecularColor((.8, .8, .8))
        self.setShininess(.1)
        self.cil = wrap(SoCylinder())
        self.cil.setName("segmento")
        ## ==========================
        conoSep = SoSeparator()
        self.conoTr = SoTransform()
        self.cono = SoCone()
        self.cono.bottomRadius = self.escala * 2
        self.cono.height = .1
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
#        sep.addChild(self.matBase)
        sep.addChild(self.cil)
        sep.addChild(conoSep)
        ## ============================
        self.calcTransformation()
        self.addChild(sep)

    def calcTransformation(self):
        vec = self.p2 - self.p1
        t = vec.length() if vec.length() != 0 else .00001
        self.tr1.translation = (0, t / 2.0, 0)
        self.conoTr.translation = (0, t / 2.0, 0)
        self.cil[0].radius = self.escala
        self.cil[0].height = t
        self.tr2.translation = self.p1
        if self.base:
            self.base.setOrigin(self.p1)
        zt = Vec3(0, t, 0)
        ejeRot = zt.cross(vec)
        ang = acos(zt.dot(vec) / t ** 2)
        if ejeRot.length() < .0001:
            ejeRot = Vec3(1, 0, 0)
        self.tr2.rotation.setValue(ejeRot, ang)

    def setRadius(self, r):
        self.cil[0].radius = r

    def setPoints(self, p1, p2):
        "p1, p2: Vec3d"
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.calcTransformation()

    def setP2(self, pt):
        self.p2 = pt
        self.calcTransformation()

    def setLengthFactor(self, factor):
        self.lengthFactor = factor
        self.setP2(segment(self.p1, self.p2inicial, factor))


class Line(GraphicObject):
    def __init__(self, ptos, color=(1, 1, 1), width=1, nvertices= -1, name="Line", visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        sep = SoSeparator()
        sep.setName("Line")
        self.coords = SoCoordinate3()
        self.lineset = SoLineSet()
        draw = SoDrawStyle()
        ## ============================
        self.setCoordinates(ptos, nvertices)
        draw.lineWidth.setValue(width)
        self.material.diffuseColor = color
        ## ============================
        sep.addChild(self.coords)
        sep.addChild(draw)
        sep.addChild(self.lineset)
        self.addChild(sep)
        self.whichChild = 0
        ## ============================
        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))

    def resetObjectForAnimation(self):
        self.setNumVertices(1)

    def __getitem__(self, i):
        "overwrite GraphicObject.__getitem__"
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
        return Line(ptosProj, color, width, nvertices, parent=self.parent)


class CurveVectorField(GraphicObject):
    '''
    Holds data needed to draw an arrow along a vector field
    '''
    def __init__(self, function, domain_points, base_arrow_points, visible=True, parent=None):
        GraphicObject.__init__(self, visible, parent)
        self.function = function
        self.domain_points = domain_points
        self.base_arrow_points = base_arrow_points
        self.end_points = map(self.function, self.domain_points)
        self.arrow = None
        self.animation = None
        
        self.arrow = Arrow(self.base_arrow_points[0], self.base_arrow_points[0] + self.end_points[0], escala=0.1, escalaVertice=2, extremos=True, visible=True)
        self.arrow.setDiffuseColor((1, 0, 0))
        self.arrow.cono.height = .5
        self.arrow.base.setDiffuseColor((1, 1, 0))
        self.addChild(self.arrow)

        def animate_field(i):
            self.arrow.setPoints(self.base_arrow_points[i], self.base_arrow_points[i] + self.end_points[i])
            
        self.animation = Animation(animate_field, (8000, 0, len(self.base_arrow_points) - 1))


class Curve3D(GraphicObject):
    """
    A curve in 3D. It is composed of one or several Lines
    """
    def __init__(self, func, iter, color=(1, 1, 1), width=1, nvertices= -1, parent=None, domTrans=None):
        GraphicObject.__init__(self, True, parent)
        self.__derivative = None
        self.fields = {}
        self.lines = []
        c = lambda t: Vec3(func(t))
        ## ============================
        if domTrans:
            ptsTr = intervalPartition(iter, domTrans)
            print max(ptsTr), min(ptsTr)
            points = map(c, ptsTr)

        self.iter = iter
        self.func = func

        if not isinstance(iter[0], Sequence):
            self.iter = [iter]
            
        for it in self.iter:
            points = intervalPartition(it, c)
            self.lines.append(Line(points, color, width, nvertices, parent=self))

        self.lengths = map(len, self.lines)
        self.animation = Animation(self.setNumVertices, (4000, 1, len(self)))

    def setField(self, name, function):
        '''
        Creates an arrow along each of the points of the field
        @param function: callable
        @param name: string
        '''
        self.fields[name] = CurveVectorField(function, self.domainPoints, self.Points,parent=self)
    
    def getDerivative(self):
        return self.__derivative
    
    def setDerivative(self, func):
        self.__derivative = func
        end_points = map(self.__derivative, self.domainPoints)
        self.tangent_vector = Arrow(self.Points[0], self.Points[0] + end_points[0], visible=False, escala=0.1, escalaVertice=2, extremos=True, parent=self)
        self.tangent_vector.setDiffuseColor((1, 0, 0))
        self.tangent_vector.cono.height = .5
        self.tangent_vector.base.setDiffuseColor((1, 1, 0))
        
        def animate_tangent(i):
            self.tangent_vector.setPoints(self.Points[i], self.Points[i] + end_points[i])
            
        self.tangent_vector.animation = Animation(animate_tangent, (8000, 0, len(self) - 1))
            
    derivative = property(getDerivative, setDerivative)
        
        
    def __len__(self):
        return sum(self.lengths)
    
    def setNumVertices(self, n):
        "shows only the first n vertices"
#        self.lineset.numVertices.setValue(n)
        ## find out on which line n lies
        for line in self.lines:
            nl = len(line)
            if n < nl:
                line.setNumVertices(n)
                break
            else:
                ## draw the whole line
                line.setNumVertices(nl)
                n -= nl

    def getCoordinates(self):
        '''
        returns the joined coordinates of all the lines
        '''
        coord = []
        for line in self.lines:
            #------------"l += i" it's the same that "l = l + i"
            #------------coord = coord + line.getCoordinates()
            coord += line.getCoordinates()
        return coord

    def project(self, x=None, y=None, z=None, color=(1, 1, 1), width=1, nvertices= -1):    
        for line in self.lines:
            line.project(x, y, z, color, width, nvertices)
        return line.project(x, y, z, color, width, nvertices)


    def __getitem__(self, i):
        '''
        returns the i-th point 
        @param i: the index
        '''
        for line in self.lines:
            nl = len(line)
            if i < nl:
                return line[i]
            else:
                i -= nl

    def updatePoints(self, func):
        '''
        recalculates points according to the function func
        @param func: a function  R -> R^3
        '''
        self.func = func
        c = lambda t: Vec3(func(t))
        for it, line in zip(self.iter, self.lines):
            points = intervalPartition(it, c)
            line.setCoordinates(points)

    @property
    def domainPoints(self):
        '''
        returns the preimages of the points
        '''
        ret = []
        for it in self.iter:
            ret += intervalPartition(it)
        return ret

    @property
    def Points(self):
        ret = []
        for line in self.lines:
            ret += line.getCoordinates()
        return ret


class Bundle3(GraphicObject):
    def __init__(self, curve, cp, factor=1, name="", visible=False, parent=None):
        """curve is something derived from Line"""
        GraphicObject.__init__(self, visible, parent)
        self.curve = curve
        self.cp = cp
        self.factor = factor
        self.line = Line(())
        ## ============================
        self.coords = SoCoordinate3()
        self.mesh = SoQuadMesh()
        self.mesh.verticesPerColumn = len(curve)
        self.mesh.verticesPerRow = 2
        nb = SoNormalBinding()
#        nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        sHints = SoShapeHints()
        sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE

        self.generateArrows()
        ## ============================
        self.scale = SoScale()
        ## ============================
        sep = SoSeparator()
        sep.addChild(nb)
        sep.addChild(sHints)
        sep.addChild(self.scale)
        sep.addChild(self.coords)
        sep.addChild(self.mesh)
#        self.addChild(self.line)
        self.addChild(sep)

        self.animation = Animation(lambda num: float(num) / len(curve) * self.material.transparency.getValue(), (4000, 1, len(curve)))

    def __len__(self):
        "the same lengh as the base curve"
        return len(self.curve)

    def setFactor(self, factor):
        '''
        Set multiplicative factor for arrow length
        @param factor:
        '''
        self.factor = factor
        self.generateArrows()

    def generateArrows(self):
        '''
        create the arrows
        '''
        points = self.curve.getCoordinates()
        #pointsp = [self.curve[i]+self.cp(t)*self.factor for i,t in enumerate(intervalPartition(self.curve.iter))]
        pointsp = [self.curve[i] + self.cp(t) * self.factor for i, t in enumerate(self.curve.domainPoints)]
        pointsRow = zip(map(tuple, points), map(tuple, pointsp))

        pointsRowFlatten = []
        vertexIndexes = []
        for p, pp in pointsRow:
            ## TODO: triangular!!
            pointsRowFlatten.append(p)
            pointsRowFlatten.append(pp)
            vertexIndexes.append(2)
        ## ============================
        self.line.setCoordinates(pointsRowFlatten)
        self.line.setVertexIndexes(vertexIndexes)
        self.coords.point.setValues(0, len(pointsRowFlatten), pointsRowFlatten)


    def setTransparency(self, val):
        GraphicObject.setTransparency(self, val)
#        self.line.setTransparency(val)

    def setTransparencyType(self, trans):
        GraphicObject.setTransparencyType(self, trans)
#        self.line.setTransparencyType(trans)

    def setNumVisibleArrows(self, num):
        """set the number of arrow to show"""
        self.mesh.verticesPerColumn = num


class Bundle2(GraphicObject):
    def __init__(self, curve, cp, col, factor=1, name="", visible=False, parent=None):
        """curve is something derived from Curve3D"""
        GraphicObject.__init__(self, visible, parent)
        comp = SoComplexity()
        comp.value.setValue(.1)
        self.separator.addChild(comp)
        ## ============================
        points = curve.getCoordinates()
        pointsp = [curve[i] + cp(t) * factor for i, t in enumerate(curve.domainPoints)]
        for p, pp in zip(points, pointsp):
            self.addChild(Arrow(p, pp, visible=True, escala=.005, extremos=True))

        self.animation = Animation(lambda num: self[num - 1].show(), (4000, 1, len(points)))

    def setMaterial(self, mat):
        for c in self.getChildren():
            c.material.ambientColor = mat.ambientColor
            c.material.diffuseColor = mat.diffuseColor
            c.material.specularColor = mat.specularColor
            c.material.shininess = mat.shininess

    def setHeadMaterial(self, mat):
        for c in self.getChildren():
            c.matHead.ambientColor = mat.ambientColor
            c.matHead.diffuseColor = mat.diffuseColor
            c.matHead.specularColor = mat.specularColor
            c.matHead.shininess = mat.shininess

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)

    def setLengthFactor(self, factor):
        for c in filter(lambda c: isinstance(c, Arrow), self.getChildren()):
            c.setLengthFactor(factor)

    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()

    def setNumVisibleArrows(self, num):
        """set the number of arrow to show"""
        print "setNumVisibleArrows:", num




class Bundle(GraphicObject):
    def __init__(self, c, cp, partition, col, factor=1, name="", visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        tmin, tmax, n = partition
        puntos = [c(t) for t in intervalPartition([tmin, tmax, n])]
        puntosp = [c(t) + cp(t) * factor for t in intervalPartition([tmin, tmax, n])]
        for p, pp in zip(puntos, puntosp):
            self.addChild(Arrow(p, pp, extremos=True, escalaVertice=3, visible=True))

        self.animation = Animation(lambda num: self[num - 1].show(), (4000, 1, n))

    def setMaterial(self, mat):
        for c in self.getChildren():
            c.material.ambientColor = mat.ambientColor
            c.material.diffuseColor = mat.diffuseColor
            c.material.specularColor = mat.specularColor
            c.material.shininess = mat.shininess

    def setHeadMaterial(self, mat):
        for c in self.getChildren():
            c.matHead.ambientColor = mat.ambientColor
            c.matHead.diffuseColor = mat.diffuseColor
            c.matHead.specularColor = mat.specularColor
            c.matHead.shininess = mat.shininess

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)

    def setLengthFactor(self, factor):
        for c in self.getChildren():
            if hasattr(c, "setLengthFactor"):
                c.setLengthFactor(factor)
    
    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()


class TangentPlane(GraphicObject):
    def __init__(self, param, par1, par2, pt, color, visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        ve = par1(pt[0])
        ve.normalize()
        ue = par2(pt[1])
        ue.normalize()
        def planePar(h, t):
            return tuple(Vec3(param(*pt)) + h * ve + t * ue)
        baseplane = BasePlane()
        baseplane.setRange((-.5, .5, 30), plane=planePar)
        baseplane.setTransparency(0)
        baseplane.setDiffuseColor(color)
        baseplane.setEmissiveColor(color)
        self.addChild(baseplane)

class TangentPlane2(GraphicObject):
    def __init__(self, param, par1, par2, origin, color, visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        self.par1 = par1
        self.par2 = par2
        self.param = param
        self.origin = origin
        self.r0 = (-.5, .5, 30)

        self.baseplane = BasePlane()
        self.setOrigin(origin)

        self.baseplane.setTransparency(0)
        self.baseplane.setDiffuseColor(color)
        self.baseplane.setEmissiveColor(color)
        self.addChild(self.baseplane)

    def setOrigin(self, pt):
        self.origin = pt
        ve = self.par1(*pt)
        ve.normalize()
        ue = self.par2(*pt)
        ue.normalize()
        orig = Vec3(self.param(*pt))
        def planePar(h, t):
            return tuple(orig + h * ve + t * ue)
        self.baseplane.setRange(self.r0, plane=planePar)

    def setU(self, val):
        self.setOrigin((val, self.origin[1]))

    def setV(self, val):
        self.setOrigin((self.origin[0], val))
        
    def setRange(self, r0):
        self.r0 = r0
        self.baseplane.setRange(self.r0)

class BasePlane(GraphicObject):
    def __init__(self, plane="xy", visible=True, parent=None):
        GraphicObject.__init__(self, visible, parent)
        ## ============================
        self.plane = plane
        self.setDiffuseColor((.5, .5, .5))
        self.setAmbientColor((.5, .5, .5))
        ## ============================
        self.translation = SoTranslation()
        ## ============================
        self.coords = SoCoordinate3()
        self.mesh = SoQuadMesh()
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.separator.addChild(self.translation)
        self.separator.addChild(self.sHints)
        self.separator.addChild(self.coords)
        self.separator.addChild(self.mesh)
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
            func = lambda x, y:(x, y, 0)
            ## this will be used to determine which coordinate to modify
            ## in setHeight
            self.constantIndex = 2
        elif plane == "yz":
            func = lambda y, z:(0, y, z)
            self.constantIndex = 0
        elif plane == "xz":
            func = lambda x, z:(x, 0, z)
            self.constantIndex = 1
        elif type(plane) == type(lambda :0):
            func = plane
        malla2(self.ptos, func, r.min, r.dt, len(r), r.min, r.dt, len(r))
        self.coords.point.setValues(0, len(self.ptos), self.ptos)
        self.mesh.verticesPerColumn = len(r)
        self.mesh.verticesPerRow = len(r)





class Plane(GraphicObject):
    """
    """
    def __init__(self, pos, visible=True, parent=None):
        GraphicObject.__init__(self, visible, parent)
        self.altura = -1
        vertices = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
        for p in vertices:
            p.insert(pos, self.altura)
        sh = SoShapeHints()
        sh.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        sh.faceType = SoShapeHints.UNKNOWN_FACE_TYPE
        sh.shapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
        coords = SoCoordinate3()
        coords.point.setValues(0, len(vertices), vertices)
        mesh = SoQuadMesh()
        mesh.verticesPerColumn = 2
        mesh.verticesPerRow = 2
        nb = SoNormalBinding()
#            nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        mat = SoMaterial()
        mat.transparency = 0.5
        self.setTransparencyType(8)
        ## ============================
        root = SoSeparator()
        root.addChild(sh)
        root.addChild(mat)
        root.addChild(nb)
        root.addChild(coords)
        root.addChild(mesh)
        self.addChild(root)

    def setAltura(self, val):
        pass


class Planes(GraphicObject):
    def __init__(self, visible=False, parent=None):
        GraphicObject.__init__(self, visible, parent)
        self.addChild(Plane(0))
        self.addChild(Plane(1))
        self.addChild(Plane(2))

