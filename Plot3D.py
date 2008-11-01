#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import util
from pivy.gui.soqt import *
from pivy.coin import *
from PyQt4 import QtGui, QtCore, uic
from math import sqrt, pi
from Parametro import Parametro
from util import lee,  GenIntervalo, partial,  conecta
import logging
#from numpy import *
#import psyco
#import pp

#job_server = pp.Server()
#print job_server.get_ncpus()

log = logging.getLogger("MallaBase")
log.setLevel(logging.DEBUG)


def malla2(puntos, func,xmin, xinc,nx,ymin, yinc, ny):
    for x in xrange(nx):
        for y in xrange(ny):
            puntos.append( func(xmin+xinc*x,ymin+yinc*y) )
#psyco.bind(malla2)

def malla(puntos, func,xmin, xinc,nx,ymin, yinc, ny):
    for x in xrange(nx):
        for y in xrange(ny):
            puntos[ny*x+y] = func(xmin+xinc*x,ymin+yinc*y)
#psyco.bind(malla)

def processIter(iter, defpts ,  defname):
    if len(iter) == 2 and callable(iter[1]):
        return GenIntervalo(iter[1], name=iter[0])
    else:
        iter = list(iter)
        name = defname
        npoints = defpts
        if type(iter[0]) == str:
            name = iter[0]
            del iter[0]
        if len(iter) == 3:
            npoints = iter[2]
            del iter[2]
        ## at this point, len(iter) == 2
        vmin, vmax = iter
        return GenIntervalo((vmin, vmax, npoints), name=name)



class MallaBase(QtCore.QObject):
    name = "Mesh"
    defaultViewer = None
    def __init__(self, rangoX=(0,1),  rangoY=(0,1)):
        ## rangoX = ([name], min,max, [points]) | func parms -> (min,max,points)
        QtCore.QObject.__init__(self)
        self.parent = None
        ## ============================
        self.rangoX = processIter(rangoX, 40, 'x')
        self.rangoY = processIter(rangoY, 40, 'y')
        self.rangoX.end()
        self.rangoY.end()
        ## ============================
        self.drawStyle = 0
        self.parametros = {}
        self.__parciales = []
        self.funcion = None
        self.quads = {}
        self.root = self.creaRoot()
        if hasattr(self, "func"):
            self.creaQuad(self.root,self.func)
        self.setupGui()
        ## esto deberia estar al final del proceso
        if MallaBase.defaultViewer != None:
            MallaBase.defaultViewer.addChild(self)
        ## al llegar aquí, todavía no se han creado los puntos

    def creaRoot(self):
        self.drawStyle = SoDrawStyle()
#        self.drawStyle.style = SoDrawStyle.LINES
        root = SoSeparator()
        #  ======================
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.sHints.creaseAngle = 0.0
        root.addChild(self.sHints)
        root.addChild(self.drawStyle)
        return root

    def rangeXpoints(self):
        ## n is an *index*, but there are n+1 points
        return self.rangoX.n+1

    def rangeYpoints(self):
        return self.rangoY.n+1

    def getGui(self):
        return self.paramW

    def setupGui(self):
        "agrega el widget para los parámetros + el título"
        self.paramW = QtGui.QWidget()
        self.paramW.setObjectName("MallaBaseGui")
        self.paramWlayout  =  QtGui.QVBoxLayout()
        self.paramWlayout.setMargin(0)
        self.paramWlayout.setSpacing(20)
        self.paramW.setLayout(self.paramWlayout)
        ## ============================
        ##      the label
        label = QtGui.QLabel("<h2>"+self.name+"</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.paramWlayout.insertWidget(0,label,0, QtCore.Qt.AlignTop)
        self.paramWlayout.addStretch()

    def addEqn(self, eqn):
        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        w = QtGui.QWidget()
        w.setLayout(layout)
        layout.addStretch()
        ## ============================
        eqn.eval(layout)
        ## ============================
        layout.addStretch()
        self.paramWlayout.insertWidget(1,w,0, QtCore.Qt.AlignTop)


    def finalizaGui(self):
        log.debug(self.paramWlayout.count())
        self.paramWlayout.addStretch()

    def addQuad(self, func,col=None):
        def func2(*args):
            if args == ():
                return func
            else:
                return partial(func, *args)
        self.creaQuad(self.root, func2,col)

    def creaQuad(self,root,func,col=None):
        quad = {}
        quad["coords"] = SoCoordinate3()
        quad["mesh"] = SoQuadMesh()
        quad["mesh"].verticesPerColumn = self.rangeXpoints()
        quad["mesh"].verticesPerRow = self.rangeYpoints()
        nb = SoNormalBinding()
        nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        ## ============================
        ## ¿porqué uso un SoSwitch en lugar de un SoSeparator?
        quad["switch"] = SoSwitch()
        quad["switch"].whichChild = SO_SWITCH_ALL
        quad["switch"].addChild(nb)
        quad["switch"].addChild(quad["coords"])
        quad["switch"].addChild(quad["mesh"])
        if col != None:
            mat = SoMaterial()
            mat.diffuseColor = col
            quad["switch"].insertChild(mat,0)
        ## ============================
        self.quads[func] = quad
        root.addChild(quad["switch"])
        ## ============================
        if hasattr(self, "rangoYparam"):
            quad["edgeY"] = self.createEdge()
            root.addChild(quad["edgeY"])
        if hasattr(self, "rangoXparam"):
            quad["edgeX"] = self.createEdge()
            root.addChild(quad["edgeX"])
        ## ============================
        ## oculta la malla cuando hay muy pocos puntos
        if self.rangeYpoints() < 2 or self.rangeXpoints() < 2:
            quad["switch"].whichChild = SO_SWITCH_NONE
        else:
            quad["switch"].whichChild = SO_SWITCH_ALL


    def addParameter(self, iter=(0, 1), tini=0, qlabel = None):
        rango = processIter(iter, 100,'w')
        name = rango.name
        self.__parciales.append(partial(self.setParam,name))
        par = self.__parciales[-1]
        p = self.parametros[name] = Parametro2(rango.iter(),tini=tini,func=par)
        if tini > 0:
            p.slider.setMinimum(1)
        ## el indice count()-1 inserta el el widget en la penultima posicion
        ## en la ultima esta un spacer
        self.paramWlayout.insertWidget(self.paramWlayout.count()-1, p)
        ## ============================
        if qlabel != None:
            if not (type(qlabel) == list or type(qlabel) == tuple):
                qlabel = [qlabel]
            p.qlabel = qlabel
            for lab in qlabel:
                conecta(p, QtCore.SIGNAL("actualiza(float)"), lab.setParamValue)
        ## ============================
        return p

    def setParam(self, name, val):
#        print "setParam", name, val
        "actualiza el valor del parametro"
        if self.parametros.has_key(name):
            self.parametros[name].val = val
            self.updateAll()

    def updateAll(self):
        self.regeneraFuncion()
        self.genera()

    def regeneraFuncion(self):
        "evalua la funcion en los parametros"
        parVals = [p.getValue() for p in self.parametros.values()]
        ## ============================
        if self.rangoX.iterFunc != None:
            self.rangoX.update(*parVals)
        if self.rangoY.iterFunc != None:
            self.rangoY.update(*parVals)
        ## ============================
        for func,q in self.quads.items():
            q["funcion"] = func(*parVals)
            if q.has_key("edgeX"):
                self.calculateEdge("X", q)
            if q.has_key("edgeY"):
                self.calculateEdge("Y", q)

    def genera(self):
        "genera los puntos de la malla"
        for q in self.quads.values():
            vertices = range(self.rangeXpoints()*self.rangeYpoints())
            malla(vertices, q["funcion"], self.rangoX.vmin, self.rangoX.dt, self.rangeXpoints(),  self.rangoY.vmin, self.rangoY.dt, self.rangeYpoints())
            q["coords"].point.setValues(0,len(vertices),vertices)

    def generaPrueba(self,nx,ny,num = 0):
        ## solo para pruebas
        self.rangoX.reset(t=nx)
        self.rangoY.reset(t=ny)
        for q in self.quads.values():
            if num == 0:
                vertices = []
                malla2(vertices, q["funcion"], self.rangoX.vmin, self.rangoX.dt, self.rangeXpoints(),  self.rangoY.vmin, self.rangoY.dt, self.rangeYpoints())
            elif num == 1:
                vertices = range(self.rangeXpoints()*self.rangeYpoints())
                malla(vertices, q["funcion"], self.rangoX.vmin, self.rangoX.dt, self.rangeXpoints(),  self.rangoY.vmin, self.rangoY.dt, self.rangeYpoints())

    def addParameterX(self, delta = 0):
#        print "addParameterX", self.quads
        ## TODO: Repensar  la interaccion de estos dos parametros
        if delta == 0:
            xmax = self.rangoX.vmax
        else:
            delta = max(delta, self.rangoX.dt)
            xmax = self.rangoX.vmin# + delta
            self.setNpoints(nx=xmax, update=False)
#            self.rangoX.reset(t=xmax)
#            for q in self.quads.values():
#                q["mesh"].verticesPerColumn = self.rangeXpoints()
        self.rangoXparam = Parametro2(self.rangoX.iter(),tini=xmax,func=lambda x: self.setNpoints(nx=x))
        ## esto evita que la malla desaparezca completamente
        if delta > 0:
            self.rangoXparam.slider.setMinimum(0)
        self.paramWlayout.insertWidget(self.paramWlayout.count()-1,  self.rangoXparam)

    def addParameterY(self, delta = 0):
        if delta == 0:
            ymax = self.rangoY.vmax
        else:
            delta = max(delta, self.rangoY.dt)
            ymax = self.rangoY.vmin# + delta
            self.setNpoints(ny=ymax, update=False)
        self.rangoYparam = Parametro2(self.rangoY.iter(),tini=ymax,func=lambda y: self.setNpoints(ny=y))
        if delta > 0:
            self.rangoYparam.slider.setMinimum(0)
        self.paramWlayout.insertWidget(self.paramWlayout.count()-1, self.rangoYparam)

    def calculateEdge(self, eje, quad):
        f = quad["funcion"]
        r1 = getattr(self, "rango"+eje)
        r2 = (self.rangoX if eje == "Y" else self.rangoY)
        if eje == "X":
            r2 = self.rangoY
            fn = util.partial(f, r1.vmin)
        else:
            r2 = self.rangoX
            fn = util.partial(lambda t: f(t, r1.vmin))
        fi = list(util.genIntervalo(r2.iter()[1:], fn))
        sep = quad["edge"+eje]
        sep[0].point.setValues(0, len(fi), fi)
        sep[1].coordIndex.setValues(0, len(fi), range(len(fi)))

    def createEdge(self):
        coord3 = SoCoordinate3()
        lineSet = SoIndexedLineSet()
        sep = SoSeparator()
        sep.addChild(coord3)
        sep.addChild(lineSet)
        return sep


    def setNpoints(self, nx = None, ny = None, update = True):
        ## changes de (x|y)range limit. This is acomplished by drawing more or less
        ## points at the *same* increment (which is self.rangoX.dt)
        if nx != None:
            self.rangoX.reset(t=nx)
        if ny != None:
            self.rangoY.reset(t=ny)
        ## este código es un desmadre
        for q in self.quads.values():
            if nx != None:
                q["mesh"].verticesPerColumn = self.rangeXpoints()
            if ny != None:
                q["mesh"].verticesPerRow = self.rangeYpoints()
            if self.rangeYpoints() < 2 or self.rangeXpoints() < 2:
                q["switch"].whichChild = SO_SWITCH_NONE
            else:
                q["switch"].whichChild = SO_SWITCH_ALL
        if update:
            self.genera()
        if self.parent != None:
            self.parent.viewer.viewAll()

    def final(self,mp):
        ## que hace esto?
        return (self.rangoX,self.rangoY,self.componentes(1))



class ParametricPlot3D(MallaBase):
    def __init__(self,  func,  xrange,  yrange,  addXdelta=None,  addYdelta=None,  extraParms = (),  name = '', eq = None):
        ## ejemplo: extraParms=[("w",(0,1),0.8)]
        ## addXdelta = 0.02 | (0.02, 'z')
        self.name = name
        ## ============================
        ## TODO: arreglar esto:
#        if 0:
#        #~ if type(func) == str:
#            ## Esto no funciona en otros modulos!!
#            ## en este caso xrange es de la forma ('var',xmin,xmax)
#            xvar = xrange[0]
#            yvar = yrange[0]
#            pvars = [p[0] for p in extraParms]
#            ## en primer lugar tiene que ir los parametros extras
#            vars = pvars + [xvar, yvar]
#            self.__func = eval("lambda " + ",".join(vars) + ":" + func)
#            ## xrange debe ser de la forma (xmin,xmax)
#            ## igual para yrange
#            xrange = xrange[1:]
#            yrange = yrange[1:]
#        else:
#            self.__func = func
        ## ============================
        MallaBase.__init__(self, xrange, yrange)
        if addXdelta != None:
            self.addParameterX(addXdelta)
        if addYdelta != None:
            self.addParameterY(addYdelta)
        for p in extraParms:
            self.addParameter(*p)
        self.addQuad(func)
        ## ============================
        if eq != None:
            self.addEqn(eq)
        ## ============================



def grande(txt):
    return "<font size=+3 face=Serif>%s</font>" % txt

class Eq(object):
    def __init__(self, expr):
        self.expr = expr

    def update(self, val):
        print val

    def eval(self, layout):
        self.formato(layout, self)

    def __neg__(self):
        return Eq(('-',  self))

    def __add__(self, other):
        return Eq(('+',  self,  other))

    def __radd__(self, other):
        return Eq(('+',  other,  self))

    def __sub__(self, other):
        return Eq(('-',  self,  other))

    def __rsub__(self, other):
        return Eq(('-',  other,  self))

    def __mul__(self, other):
        return Eq(('*',  self,  other))

    def __rmul__(self, other):
        return Eq(('*',  other,   self))

    def __div__(self, other):
        return Eq(('/',  self,  other))

    def __rdiv__(self, other):
        return Eq(('/',  other, self))

    def __pow__(self, other):
        return Eq(('^',  self,  other))

    def __xor__(self, other):
        return Eq(('^',  self,  other))

    def __eq__(self, other):
        return Eq(('=',  self,  other))

    def  __call__(self, *others):
        return Eq(['func', self] +  list(others) )

## ============================
    @staticmethod
    def frac(layout, a, b):
            vboxlayout = QtGui.QVBoxLayout()
            vboxlayout.setMargin(0)
            vboxlayout.setSpacing(0)

            num = QtGui.QHBoxLayout()
            num.setMargin(0)
            num.setSpacing(0)
            Eq.formato(num, a)
            vboxlayout.addLayout(num)

            line = QtGui.QFrame()
            line.setFrameShape(QtGui.QFrame.HLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            vboxlayout.addWidget(line)

            denom = QtGui.QHBoxLayout()
            denom.setMargin(0)
            denom.setSpacing(0)
            Eq.formato(denom, b)
            vboxlayout.addLayout(denom)

            layout.addLayout(vboxlayout)

    @staticmethod
    def pow(layout, x, n):
        Eq.formato(layout, x)
        layout.addWidget(QtGui.QLabel(grande("<sup>%s</sup>" % n)))

    @staticmethod
    def plus(layout, *expr):
        op = expr[0]
        for a in expr[1:-1]:
            Eq.formato(layout, a)
            layout.addWidget(QtGui.QLabel(grande(" "+op+"")))
        else:
            Eq.formato(layout, expr[-1])

    @staticmethod
    def mult(layout,  a,  b):
        Eq.formato(layout, a)
        layout.addWidget(QtGui.QLabel(" "))
        Eq.formato(layout, b)

    @staticmethod
    def func(layout, args):
        fn = args[0].expr
        layout.addWidget(QtGui.QLabel(grande(fn + '(')))
        for a in args[1:]:
            Eq.formato(layout, a)
        layout.addWidget(QtGui.QLabel(grande(')')))

    @staticmethod
    def var(layout, expr):
        if len(unicode(expr)) == 1 and unicode(expr).isalpha():
            expr = '<em>%s</em>' % expr
        label = QtGui.QLabel(grande(expr))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

    @staticmethod
    def operacion(layout, ob):
        expr = ob.expr[1]
#        if len(unicode(expr)) == 1 and unicode(expr).isalpha():
        ## en general el valor inicial es 0
#        num = eval(ob.expr[1].replace(ob.expr[2], "0"))
        if not hasattr(ob,  "labels"):
            ob.labels = []
        exprRoja = '<em style="color:red">%s</em>' % ob.expr[1]
        label = QtGui.QLabel(grande(exprRoja))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        ob.labels.append(label)

    @staticmethod
    def param(layout, ob):
        name = ob.expr[1]
        ## puede haber varias etiquetas asociadas al mismo parámetro
        if not hasattr(ob,  "labels"):
            ob.labels = []
        ## en general el valor inicial es 0
        ## hacer esto mas general!
        ob.labels.append(QtGui.QLabel(grande('<em style="color:red">%s</em>' % name)))
        layout.addWidget(ob.labels[-1])

    def setParamValue(self, val):
        valstr = "%.2f" % val
        if valstr == "1.00":
            valstr = "1"
        elif valstr == "0.00":
            valstr = "0"
        if self.expr[0] == "par":
            for label in self.labels:
                label.setText(grande('<span style="color:red">%s</span>' % valstr))
        elif self.expr[0] == "operacion":
            ## self.expr == ("operacion", expr, val)
            num = eval(self.expr[1].replace(self.expr[2], valstr))
            for label in self.labels:
                label.setText(grande('<span style="color:red">%s</span>' % num))

    @staticmethod
    def formato(layout, ob):
        ## ob puede ser de tipo  Eq, o número, o cadena
        if hasattr(ob, "expr"):
            expr = ob.expr
        else:
            expr = ob
        t = type(expr)
        if t == tuple or t == list:
            head = expr[0]
        if t  == str or t == unicode or t == int or t == float:
            Eq.var(layout, expr)
        elif head == "func":
            Eq.func(layout, expr[1:])
        elif head == "+" or head == "-" or head == "=":
            Eq.plus(layout, *expr)
        elif head == "^":
            Eq.pow(layout, expr[1], expr[2])
        elif head == "/":
            Eq.frac(layout, expr[1],  expr[2])
        elif head == "*":
            Eq.mult(layout, expr[1],  expr[2])
        elif head == "par":
            Eq.param(layout, ob)
        elif head == "operacion":
            Eq.operacion(layout, ob)


def defVars(*args):
    ## no funciona
    for a in args:
        exec("%s = Eq('%s')" % (a, a))

def creaVars(*args):
    return map(Eq,  *args)

def creaVarParam(name):
    return Eq(('par', name))

def creaOpParam(expr, var):
    return Eq(('operacion', expr, var))

if __name__ == "__main__":
    from util import  main
    from math import  cos,  sin,  pi
    from Visor import Visor

    app = main()
    visor = Visor()
    ## ============================
    class Hiperboloide(MallaBase):
        name = "Hiperboloide<br>de una hoja"
        def __init__(self):
            MallaBase.__init__(self,('u', -pi, pi), (0, 1))
            self.addParameterX()
            self.addParameterY()
            self.addParameter(('w', 0,1), tini=0.8)
            self.addQuad(lambda w, u, t: ((1 - t)* cos(u) + t *cos(u + w*pi), (1 - t) *sin(u) + t *sin(u + w*pi), -1 + 2* t))
#    hip = Hiperboloide()
    ## ============================
    fhip =  lambda w, u, t: ((1 - t)* cos(u) + t *cos(u + w*pi), (1 - t) *sin(u) + t *sin(u + w*pi), -1 + 2* t)
    hip = ParametricPlot3D(fhip,  ('u', -pi, pi), (0, 1),  addYdelta=0.1,  extraParms=[(('w', 0,1),0.8)],  name = "Hiperboloide<br>de una hoja")
    x, y, z, a, c, seno = creaVars( ['x', 'y', 'z', 'a', 'c', 'seno'])
    hip.addEqn(  (x^2) / (a^2) + (y^2) / (a^2) - (z^2) / (c^2) == 1 )
#    hip.addEqn(seno(x+y))
    ## ============================
    visor.addPageChild(hip)
    ## ============================
    visor.resize(400, 400)
    visor.show()
    visor.ui.show()
    SoQt.mainLoop()
