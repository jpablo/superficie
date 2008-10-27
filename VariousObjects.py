from pivy.coin import *
from PyQt4 import QtCore,QtGui
from superficie.PuntoReflejado import creaPunto
from superficie.util import wrap
from math import acos
#from superficie.util import lstToFloat,readCsv, column

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


class Base(QtCore.QObject):
    def __init__(self,name = ""):
        QtCore.QObject.__init__(self)
        self.name = name
        ## =========================
        layout  =  QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            layout.addWidget(QtGui.QLabel("<center><h1>%s</h1></center>" % self.name))

    def getGui(self):
        return self.widget

    def addWidget(self,widget):
        self.widget.layout().addWidget(widget)

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

class Points(Base):
    def __init__(self,coords=[],colors = [(1,1,1)],name="",file=""):
        Base.__init__(self,name)
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

        
def Sphere(p, radius=.05, mat = None):
    sep = SoSeparator()
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

def Tube(p1, p2, escala = 0.01, escalaVertice = 2.0, mat = None, extremos = False):
    sep = SoSeparator()
    if extremos:
        sep.addChild(Sphere(p1, escala*escalaVertice))
        #~ sep.addChild(esfera(p2, escala*escalaVertice))
    tr1 = SoTransform()
    tr2 = SoTransform()
    if mat == None:
        mat = SoMaterial()
        mat.ambientColor.setValue(.0, .0, .0)
        mat.diffuseColor.setValue(.4, .4, .4)
        mat.specularColor.setValue(.8, .8, .8)
        mat.shininess = .1
    cil = wrap(SoCylinder())
    cil.setName("segmento")
    ## ==========================
    conoSep = SoSeparator()
    conoTr = SoTransform()
    cono = SoCone()
    cono.bottomRadius = .025
    cono.height = .1
    mat2 = SoMaterial()
    mat2.ambientColor.setValue(.33, .22, .27)
    mat2.diffuseColor.setValue(.78, .57, .11)
    mat2.specularColor.setValue(.99, .94, .81)
    mat2.shininess = .28
    conoSep.addChild(mat2)
    conoSep.addChild(conoTr)
    conoSep.addChild(cono)
    ## ==========================
    sep.addChild(tr2)
    sep.addChild(tr1)
    sep.addChild(mat)
    sep.addChild(cil)
    sep.addChild(conoSep)
    vec = p2-p1
    t = vec.length()
    tr1.translation = (0, t/2.0, 0)
    conoTr.translation = (0, t/2.0, 0)
    cil[0].radius = escala
    cil[0].height = t
    tr2.translation = p1
    zt = SbVec3f(0,t,0)
    ejeRot = zt.cross(vec)
    ang = acos(zt.dot(vec)/t**2)
    if ejeRot.length() < .0001:
        ejeRot = (1, 0, 0)
    tr2.rotation.setValue(ejeRot, ang)
    return sep

    

def Line(ptos,col = (1, 1, 1),width=1):
    coords = SoCoordinate3()
    coords.point.setValues(0,len(ptos),ptos)
    linea = SoLineSet()
    linea.numVertices.setValue(len(ptos))
    draw = SoDrawStyle()
    draw.lineWidth.setValue(width)
    mat = SoMaterial()
    mat.diffuseColor = col
    sep = SoSeparator()
    sep.addChild(mat)
    sep.addChild(coords)
    sep.addChild(draw)
    sep.addChild(linea)
    return sep

    
def Bundle(c, cp, particion, col, factor=1):
    tmin, tmax, n = particion
    puntos = [c(t) for t in intervalPartition([tmin,tmax,n])]
    puntosp = [c(t)+cp(t)*factor for t in intervalPartition([tmin,tmax,n])]
    sep = SoSeparator()
    for p,pp in zip(puntos,puntosp):
        sep.addChild(Tube(p,pp,extremos=True,escalaVertice=3))
    return sep

