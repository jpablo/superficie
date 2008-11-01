# -*- coding: utf-8 -*-
from math import sqrt, pow
from pivy.coin import SoInput, SoDB,  SoSearchAction,  SbVec3f, SoSFVec3f, SoSFFloat, SoCalculator, SoSwitch, SoOneShot, SoFieldSensor
from PyQt4 import QtCore
from random import random
import os

mods =  os.getcwd()+"\\modulos"
SoInput.addDirectoryFirst(mods)

#def partial(f,a):
#    return lambda *b:f(a,*b)

Vec3 = SbVec3f


###### Functions ######################

class partial(object):
    def __init__(*args, **kw):
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)
    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)

def conectaParcial(emisor, signal, metodo,  *args):
#    conecta(emisor, QtCore.SIGNAL(signal),  partial(metodo, arg))
    ## si lo anterior no funciona, entonces usamos esto:
    if not hasattr(emisor, "__parciales"):
        emisor.__parciales = []
    emisor.__parciales.append(partial(metodo, *args))
    conecta(emisor, QtCore.SIGNAL(signal),  emisor.__parciales[-1])

def conecta(ob, signal,  func):
#    if type(signal) == str:
#        signal = QtCore.SIGNAL(signal)
    QtCore.QObject.connect(ob, signal, func)

    
def evalIfDef(ob, fn, arg):
    if hasattr(ob, fn):
        ob.fn(arg)
    
def identity(x): return x

class dictRepr(dict):
    "a dictionary which uses string representation of keys instead of keys themselves"
    def __init__(self, **args):
        dict.__init__(self, args)
    def __setitem__(self, key, val):
        dict.__setitem__(self, str(key), val)
    def __getitem__(self, key):
        return dict.__getitem__(self, str(key))
    def __contains__(self, arg):
        sarg = str(arg)
        return self.has_key(sarg)
    def __delitem__(self, key):
        dict.__delitem__(self, str(key))
    def fromitem(self, item):
        ## es la función inversa de __getitem__
        ## (mas o menos, regresa el primer elemento)
        index = self.values().index(item)
        return self.items()[index][0]

        
def callback(field, func, data=None):
    ## the function will be called as:
    ## func(field,sensor)
    if data == None:
        data = field
    sensor = SoFieldSensor(func, data)
    sensor.attach(field)
    return sensor


########## Segments, Intervals, Partitions

## este es un ejercicio no muy util
## en manejo de Engines
class SegmentoEngines(object):
    def __init__(self, p1, p2):
        self.v1 = SoSFVec3f()
        self.v2 = SoSFVec3f()
        self.v3 = SoSFVec3f()
        self.h = SoSFFloat()
        self.calc = SoCalculator()
        ## ============================
        self.calc.expression.set1Value(0,"oA=A-h*(A-B)")
        self.calc.A.connectFrom(self.v1)
        self.calc.B.connectFrom(self.v2)
        self.calc.h.connectFrom(self.h)
        self.v3.connectFrom(self.calc.oA)
        ## ============================
        self.v1.setValue(p1)
        self.v2.setValue(p2)
    def eval(self, t):
        self.h.setValue(t)
        return self.v3.getValue().getValue()

        
## esto es mucho mas conciso
## ¿será mas rápido?
class Segmento(object):
    def __init__(self, p1, p2):
        self.v1 = p1
        self.v2 = p2
    def eval(self, t):
        return self.v1 - t*(self.v1 - self.v2)
        
    def p1(self):
        return self.v1
    def p2(self):
        return self.v2

## probablemente solo esto sea suficiente        
def segment(p1,p2,t):
    return p1 - t * (p1 - p2)
        
#class Segmento(object):
#    "calcula el punto p1 - t (p1 - p2)"
#    def __init__(self,  p1,  p2):
#        self.x1,  self.y1, self.z1 = p1
#        self.x2,  self.y2, self.z2 = p2
#        self.dx = self.x2-self.x1
#        self.dy = self.y2-self.y1
#        self.dz = self.z2-self.z1
#
#    def eval(self, t):
#        x = t*self.dx + self.x1
#        y = t*self.dy + self.y1
#        z = t*self.dz + self.z1
#        return (x, y, z)
#    
#    def p1(self):
#        return (self.x1, self.y1, self.z1)
#
#    def p2(self):
#        return (self.x2, self.y2, self.z2)

        
#def param(p2,p1,t):
#    "calcula el punto p2 - t (p2 - p1)"
#    (x1,y1) = p1
#    (x2,y2) = p2
#    return (x2 - t*(x2 - x1), y2 - t*(y2 - y1))

#def param3(p2,p1,t):
#    "calcula el punto p2 - t (p2 - p1)"
#    (x1,y1, z1) = p1
#    (x2,y2, z2) = p2
#    return (x2 - t*(x2 - x1), y2 - t*(y2 - y1), z2 - t*(z2 - z1))

        
class GenIntervalo(object):
    def __init__(self, iter, func = None,  tipo='t', name="I"):
        ## tipo = n | t
        ## iter = (min,max,n)
        self.name = name
        if callable(iter):  
            self.vmin, self.vmax, self.npoints = iter()
            self.iterFunc = iter
        else:
            self.vmin, self.vmax, self.npoints = iter
            self.iterFunc = None
        self.dt = float(self.vmax - self.vmin) / ( self.npoints - 1 )
        if not func:
            self.func = lambda x:x
        else:
            self.func = func
        self.tipo = tipo
        ## direccion = 1 | -1
        self.direccion = 1
        self.begin()
    
    def update(self, *vals):
        if self.iterFunc != None:
            prev_points = self.npoints
            self.vmin, self.vmax, self.npoints = self.iterFunc(*vals)
            self.dt = float(self.vmax - self.vmin) / ( self.npoints - 1 )
            ## this could leave self.t or self.n in an inconsistent state
            ## (out of range)
            ## so, better calculate the corresponding n and t
            nprop = self.n / float(prev_points)
            self.n = int(round(nprop * self.npoints))
            self.t = self.n * self.dt  + self.vmin
#            print "update:",  self.name,  self.vmax,  self.vmin +  self.dt * (self.npoints-1)
            
    def iter(self):
        return (self.name, self.vmin, self.vmax, self.npoints)
    
    def begin(self):
        self.reset(n=0)
    
    def end(self):
        ## the last valid n-value is npoints-1
        self.reset(n=self.npoints-1)
        
    def reset(self, n=None,  t=None):
        ## n es un entero entre 0 y npoints - 1
        ## t es un real entre vmin y vmax        
        if n != None:
            self.n = int(n)
        elif t != None:
            self.n = int(round((t-self.vmin) / self.dt))
        self.t = self.n * self.dt  + self.vmin
        
    def next(self):
        if 0 <= self.n < self.npoints:
            self.t = self.vmin + self.n * self.dt
            ## a veces nos interesa el valor t y a veces solamente el entero
            ret = (self.t if self.tipo == 't' else self.n)
            self.func(ret)
            self.n += self.direccion
        else:
            ## esto pone a self.n dentro del rango de iteracion
            if self.direccion == 1:
                self.n = self.npoints - 1
            elif self.direccion == -1:
                self.n = 0
            raise StopIteration, self.direccion
    
def genIntervalPartition(iter,  func = None):
    "evalua una funcion en los puntos del interval dado"
    vmin, vmax, npoints = iter
    dt = float(vmax - vmin) / ( npoints - 1 )
    n = 0
    if not func: func = lambda x:x
    while n < npoints:
        yield func(vmin + n * dt)
        n += 1

def intervalPartition(iter, func=None):
    return list(genIntervalPartition(iter, func))

#def intervalPartition(a,b,n):
#    l = b - a
#    return [l*(i/(n-1.)) + a for i in range(n)]

def genCircular(lst): 
    n = 0
    while 1:
        if len(lst) == 0:
            return
        yield lst[n]
        n = (n + 1) % len(lst)

########## Geometry ##################        
    
def border(p1,p2,k):
    "calcula la intersección con un círculo de radio k"
    (x1,y1) = p1
    (x2,y2) = p2
    x2mx1 = x2 - x1
    y2my1 = y2 - y1
    a = 2*x2*x2mx1 + 2*y2*y2my1
    b = sqrt(pow(4*k,2)*(pow(-x2mx1,2) + pow(-y2my1,2)) - 4*pow(x2*y1 - x1*y2,2))
    c = (2*(pow(-x2mx1,2) + pow(-y2my1,2)))
    t1 = (a - b) / c
    t2 = (a + b) / c
    xini = x2 - t1 * x2mx1
    yini = y2 - t1 * y2my1
    xfin = x2 - t2 * x2mx1
    yfin = y2 - t2 * y2my1
    return [(xini, yini), (xfin, yfin)]

def projection(q, p1, p2):
    (x1,y1) = p1
    (x2,y2) = p2
    (x3,y3) = q
    c = ((x1 - x2) * (x2 - x3) + (y1 - y2) * (y2 - y3)) / ( pow(x1-x2,2) + pow(y1-y2,2) )
    x = x2 + (x2-x1) * c
    y = y2 + (y2-y1) * c
    return (x,y)

def projectionVecs(a, u):  
    ## segun mathworld la formula es:
    ## proj_v (a) = (a.u)/|u|^2 * u
    return mult( dot(a, u)/pow(norma(u) , 2),  u )
    
def mirror(q, p1, p2):
    m = proyeccion(q, p1, p2)
    return param(q,m,2)


########### Open Inventor ##################    

def readBuffer(texto):
    input = SoInput()
    input.setBuffer(texto)
    return SoDB.readAll(input)

def readFile(file):
    myInput = SoInput()
    myInput.openFile(file)
    return SoDB.readAll(myInput)

def searchAll(nodo,label):
    if nodo.getName().getString() == label:
        return nodo
    childList = nodo.getChildren()
    if type(childList) == type(None):
        return None
    if childList.getLength() > 0:
        for n in nodo.getChildren():
            ret = buscaTodo(n, label)
            if ret != None:
                return n
    ## in any other case
    return None

def search(nodo,label):
    for c in nodo.getChildren():
        if c.getName().getString() == label:
            return c
    return None
    
def searchByName(root, name, default = None):
    sa = SoSearchAction()
    sa.setName(name)
    sa.setInterest(SoSearchAction.FIRST)
    sa.apply(root)
    if sa.getPath() != None:
        return sa.getPath().getTail()
    else:
        return default

def searchByNodeType(root, type, default = None, interest = SoSearchAction.FIRST):
    sa = SoSearchAction()
    sa.setType(type.getClassTypeId())
    sa.setInterest(interest)
    sa.apply(root)
    if interest != SoSearchAction.ALL and sa.getPath() != None:
        return sa.getPath().getTail()
    elif interest == SoSearchAction.ALL and len(list(sa.getPaths())) > 0:
        return [path.getTail() for path in  sa.getPaths()]
    else:
        return default


def wrap(node, show = True):
    if hasattr(node, "root"):
        node = node.root
    switch = SoSwitch()
    switch.addChild(node)
    if show:
        switch.whichChild = 0
    else:
        switch.whichChild = -1
    return switch
        
   
def main(args=None):
    if args == None:
        import sys
        args = sys.argv
    from pivy.gui.soqt import SoQt
    from PyQt4 import QtCore, QtGui
    app = QtGui.QApplication(args)
    SoQt.init(None)
    app.connect(app, QtCore.SIGNAL('lastWindowClosed()'), app, QtCore.SLOT('quit()'))
    return app
    

def main2(args=None):
    if args == None:
        import sys
        args = sys.argv
    from pivy.gui.soqt import SoQt
    from PyQt4 import QtCore, QtGui
    SoQt.init(args)
    app = QtGui.QApplication(args)
    app.connect(app, QtCore.SIGNAL('lastWindowClosed()'), app, QtCore.SLOT('quit()'))
    return app

def fn(strfunc):
    var = "var"+str(random()).split(".")[-1]
    fbody = strfunc.replace('#',var)
    exec ("ret = lambda %s: %s" % (var, fbody))
    return ret

def prueba():
    return globals()
    
