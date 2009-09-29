from pivy.coin import *
from PyQt4 import QtCore,QtGui
from superficie.util import wrap
from math import acos
from superficie.util import intervalPartition, Vec3, segment
from superficie.util import genIntervalPartition
from superficie.util import nodeDict
from superficie.base import Page
from superficie.base import GraphicObject
from superficie.Animation import Animation

def generaPuntos(coords):
    c = coords
    return (
        (c[0],c[1],c[5]),
        (c[3],c[1],c[5]),
        (c[3],c[4],c[5]),
        (c[0],c[4],c[5]),
        (c[0],c[1],c[2]),
        (c[3],c[1],c[2]),
        (c[3],c[4],c[2]),
        (c[0],c[4],c[2]))


indicesCubo = (
    0,1,2,3,SO_END_FACE_INDEX,
    0,4,5,1,SO_END_FACE_INDEX,
    1,5,6,2,SO_END_FACE_INDEX,
    2,6,7,3,SO_END_FACE_INDEX,
    3,7,4,0,SO_END_FACE_INDEX,
    4,5,6,7,SO_END_FACE_INDEX,
    )



class Cube(QtCore.QObject):
    def __init__(self, mincoord,maxcoord):
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

class Points(Page):
    def __init__(self,coords=[],colors = [(1,1,1)],name="",file=""):
        Page.__init__(self,name)
        if file != "":
            ## assume is an csv file
            coords = lstToFloat(readCsv(file))
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

    def setPointSize(self,n):
        self.root[3].pointSize = n

    def setHSVColors(self,vec=[],pos=[],file=""):
        if file != "":
            dprom = column(lstToFloat(readCsv(file)),0)
            vec = [(c,1,1) for c in dprom]
        self.setColors(vec,pos,True)


    def setColors(self,vec,pos=[],hsv = False):
        ## valid values:
        ## vec == (r,g,b) | [(r,g,b)]
        ## pos == []  ==> pos == range(len(self))
        ## if pos != [] and len(pos) <= len(vec)
        ##      ==> point[pos[i]] of color vec[i]
        ## if pos != [] and len(pos) > len(vec)
        ##      ==> colors are cycled trough positions
        ##      ==> the rest will be white
        n = len(self)
        if isinstance(vec[0],int):
            vec = [vec]
        if pos == []:
            colors = [vec[i % len(vec)] for i in range(n)]
        else:
            colors = [(1,1,1) for i in range(n)]
            if len(pos) <= len(vec):
                for c,p in zip(vec,pos):
                    colors[p] = c
            else:
                for i,p in enumerate(pos):
                    colors[p] = vec[i % len(vec)]
        if hsv:
            self.material.diffuseColor.setHSVValues(0,len(colors),colors)
        else:
            self.material.diffuseColor.setValues(0,len(colors),colors)
        self.colors = colors

    def setCoords(self,coords,whichCoords=(0,1,2)):
        ## project the first 3 coordinates
        ## by default
        dim = len(coords[0])
        if  dim == 2:
            self.coords = [p+(0,) for p in coords]
        else:
            self.coords = coords
        self.setWhichCoorsShow(whichCoords)

    def setWhichCoorsShow(self, whichCoords):
        ## this only make sense if dim >= 3
        ## whichCoords is a 3-tuple
        coords3 = [tuple(p[c] for c in whichCoords) for p in self.coords]
        self.coordinate.point.deleteValues(0)
        self.coordinate.point.setValues(0,len(coords3),coords3)

    def __len__(self):
        return len(self.coordinate.point)

    def __getitem__(self,key):
        return self.coordinate.point[key].getValue()


class Point(Points):
    def __init__(self,coords,color = (1,1,1)):
        ## coords is a triple (x,y,z)
        Points.__init__(self,[coords],[color])

## examples:
## ps = Points([(0,0,0),(1,1,1),(2,2,2)])
## ps.setPointSize(1)
## ps.setHSVColors([(.5,1,1),(.6,1,1),(.9,1,1)])

class Polygon(QtCore.QObject):
    def __init__(self, coords,name=""):
        QtCore.QObject.__init__(self)
        self.name = name
        if self.name != "":
            self.getGui = lambda: QtGui.QLabel("<center><h1>%s</h1></center>" % self.name)
        ## is a 2d point
        dim = len(coords[0])
        if  dim == 2:
            self.coords = [p+(0,) for p in coords]
        elif dim == 3:
            self.coords = coords
        ## just project to the first 3 coordinates
        elif dim > 3:
            self.coords = [(p[0],p[1],p[2]) for p in coords]
        ## ===============================
        self.root = SoSeparator()
        coor = SoCoordinate3()
        coor.point.setValues(0,len(self.coords),self.coords)

        
def Sphere2(p, radius=.05, mat = None):
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
    def __init__(self,center,radius = .05,color=(1,1,1),visible = False,parent=None):
        GraphicObject.__init__(self,visible,parent)
        sp = SoSphere()
        sp.radius = radius
        ## ===================
        mat = SoMaterial()
        mat.ambientColor.setValue(.33, .22, .27)
        mat.diffuseColor.setValue(.78, .57, .11)
        mat.specularColor.setValue(.99, .94, .81)
        mat.shininess = .28
        ## ===================
        self.addChild(mat)
        self.addChild(sp)
        self.setOrigin(center)


class Tube(object):
    def __init__(self, p1, p2, escala = 0.01, escalaVertice = 2.0, mat = None, extremos = False):
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.escala = 0.01
        self.escalaVertice = escalaVertice
        ## ============================
        sep = SoSeparator()
        sep.setName("Tube")
        if extremos:
            sep.addChild(Sphere(p1, escala*escalaVertice))
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
        vec = self.p2-self.p1
        t = vec.length() if vec.length() != 0 else .00001
        self.tr1.translation = (0, t/2.0, 0)
        self.conoTr.translation = (0, t/2.0, 0)
        self.cil[0].radius = self.escala
        self.cil[0].height = t
        self.tr2.translation = self.p1
        zt = Vec3(0,t,0)
        ejeRot = zt.cross(vec)
        ang = acos(zt.dot(vec)/t**2)
        if ejeRot.length() < .0001:
            ejeRot = Vec3(1, 0, 0)
        self.tr2.rotation.setValue(ejeRot, ang)

    def setRadius(self, r):
        self.cil[0].radius = r

    def setPoints(self,p1,p2):
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
    def __init__(self, p1, p2, escala = 0.01, escalaVertice = 2.0, mat = None, extremos = False,visible = False,parent=None):
        GraphicObject.__init__(self,visible,parent)
        self.p1 = p1
        self.p2inicial = self.p2 = p2
        self.escala = escala
        self.escalaVertice = escalaVertice
        ## ============================
        sep = SoSeparator()
        sep.setName("Tube")
        if extremos:
            self.addChild(Sphere(p1, escala*escalaVertice))
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
        self.cono = SoCone()
        self.cono.bottomRadius = self.escala * 2
        self.cono.height = .1
        mat2 = SoMaterial()
        mat2.ambientColor.setValue(.33, .22, .27)
        mat2.diffuseColor.setValue(.78, .57, .11)
        mat2.specularColor.setValue(.99, .94, .81)
        mat2.shininess = .28
        conoSep.addChild(mat2)
        conoSep.addChild(self.conoTr)
        conoSep.addChild(self.cono)
        ## ==========================
        sep.addChild(self.tr2)
        sep.addChild(self.tr1)
        sep.addChild(mat)
        sep.addChild(self.cil)
        sep.addChild(conoSep)
        ## ============================
        self.calcTransformation()
        self.addChild(sep)

    def calcTransformation(self):
        vec = self.p2-self.p1
        t = vec.length() if vec.length() != 0 else .00001
        self.tr1.translation = (0, t/2.0, 0)
        self.conoTr.translation = (0, t/2.0, 0)
        self.cil[0].radius = self.escala
        self.cil[0].height = t
        self.tr2.translation = self.p1
        zt = Vec3(0,t,0)
        ejeRot = zt.cross(vec)
        ang = acos(zt.dot(vec)/t**2)
        if ejeRot.length() < .0001:
            ejeRot = Vec3(1, 0, 0)
        self.tr2.rotation.setValue(ejeRot, ang)

    def setRadius(self, r):
        self.cil[0].radius = r

    def setPoints(self,p1,p2):
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
    def __init__(self,ptos,color=(1,1,1),width=1,nvertices = -1,name="Line",visible = False,parent=None):
        GraphicObject.__init__(self,visible,parent)
        sep = SoSeparator()
        sep.setName("Line")
        self.coords = SoCoordinate3()
        self.lineset = SoLineSet()
        draw = SoDrawStyle()
        mat = SoMaterial()
        ## ============================
        self.setCoordinates(ptos, nvertices)
        draw.lineWidth.setValue(width)
        mat.diffuseColor = color
        ## ============================
        sep.addChild(self.coords)
        sep.addChild(mat)
        sep.addChild(draw)
        sep.addChild(self.lineset)
        self.addChild(sep)
        self.whichChild = 0
        ## ============================
        self.animation = Animation(self.setNumVertices,(4000,1,len(ptos)))

    def resetObjectForAnimation(self):
        self.setNumVertices(1)

    def __getitem__(self, i):
        "overwrite GraphicObject.__getitem__"
        ## this makes more sense in this case
        return self.coords.point[i]

    def __len__(self):
        return len(self.coords.point)
        
    def setNumVertices(self, n):
#        print "setNumVertices:", n
        self.lineset.numVertices.setValue(n)
        
    def setCoordinates(self, ptos, nvertices = -1):
        ## sometimes we don't want to show all points
        if nvertices == -1:
            nvertices = len(ptos)
        self.coords.point.setValues(0,len(ptos),ptos)
        self.setNumVertices(nvertices)

    def getCoordinates(self):
        """return the points"""
        return self.coords.point.getValues()

    def project(self, x = None, y = None, z = None, color = (1,1,1), width=1, nvertices = -1):
        """insert the projectio on the given plane"""
        pts = self.getCoordinates()
        if x != None:
            ptosProj = [Vec3(x,p[1],p[2]) for p in pts]
        elif y != None:
            ptosProj = [Vec3(p[0],y,p[2]) for p in pts]
        elif z != None:
            ptosProj = [Vec3(p[0],p[1],z) for p in pts]
        return Line(ptosProj,color,width,nvertices,parent=self.parent)


class Curve3D(Line):
    """
    """
    def __init__(self,iter,func,  color = (1,1,1), width=1, nvertices = -1, parent = None):
        c   = lambda t: Vec3(func(t))
        ## ============================
        points = intervalPartition(iter, c)
        Line.__init__(self, points, color, width, nvertices, parent=parent)
        self.func = func
        self.iter = iter

    def updatePoints(self,func):
        self.func = func
        c = lambda t: Vec3(func(t))
        points = intervalPartition(self.iter, c)
        self.setCoordinates(points)


class Bundle2(GraphicObject):
    def __init__(self, curve, cp, col, factor=1, name="", visible = False, parent = None):
        """"""
        GraphicObject.__init__(self,visible,parent)
        points = curve.getCoordinates()
        pointsp = [curve[i]+cp(t)*factor for i,t in enumerate(intervalPartition(curve.iter))]
        for p,pp in zip(points,pointsp):
            self.addChild(Arrow(p,pp,visible=True,escala=.005,extremos=True))

        self.animation = Animation(lambda num: self[num-1].show(),(4000,1,len(points)))

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)
    
    def setLengthFactor(self, factor):
        for c in filter(lambda c: isinstance(c,Arrow), self.getChildren()):
            c.setLengthFactor(factor)

    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()

    def setNumVisibleArrows(self, num):
        """set the number of arrow to show"""
        print "setNumVisibleArrows:", num




class Bundle(GraphicObject):
    def __init__(self, c, cp, partition, col, factor=1, name="", visible = False, parent = None):
        GraphicObject.__init__(self,visible,parent)
        tmin, tmax, n = partition
        puntos = [c(t) for t in intervalPartition([tmin,tmax,n])]
        puntosp = [c(t)+cp(t)*factor for t in intervalPartition([tmin,tmax,n])]
        for p,pp in zip(puntos,puntosp):
            self.addChild(Arrow(p,pp,extremos=True,escalaVertice=3,visible=True))

        self.animation = Animation(lambda num: self[num-1].show(),(4000,1,n))

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)

    def setLengthFactor(self, factor):
        for c in self.getChildren():
            if hasattr(c,"setLengthFactor"):
                c.setLengthFactor(factor)
    
    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()
