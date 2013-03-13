# -*- coding: utf-8 -*-
from pivy.coin import SO_SWITCH_ALL
from pivy.coin import SO_SWITCH_NONE
from math import sqrt, pow
from pivy.coin import SoInput, SoDB, SoSearchAction, SbVec3f, SoSFVec3f, SoSFFloat, SoCalculator, SoSwitch, SoOneShot, SoFieldSensor, SoWriteAction
from PyQt4 import QtCore
from random import random
import os
from os.path import join
import collections
from itertools import izip

import util

modulosPath = os.path.dirname(util.__file__)


def filePath(folder, archivo):
    return join(modulosPath, folder, archivo)


mods = os.getcwd() + "\\modulos"
SoInput.addDirectoryFirst(mods)

#def partial(f,a):
#    return lambda *b:f(a,*b)

v = Vec3 = SbVec3f


###### vector arithmetic ######################

def vsum(lst1, lst2):
    """term-by-term sum
    >>> vsum([1,2,3],[1,2,3])
    [2,4,6]
    """
    return map(lambda (x, y): x + y, izip(lst1, lst2))


def mmap(fn):
    """ A variant of map
    allows this sintax:
    >>> mmap(lambda x: x+1)([1,2,3])
    [2,3,4]
    """
    return lambda lst: map(fn, lst)

###### Functions ######################

class partial(object):
    def __init__(*args, **kw): #@NoSelf
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)

    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)


def connectPartial(emisor, signal, metodo, *args):
#    conecta(emisor, QtCore.SIGNAL(signal),  partial(metodo, arg))
    ## si lo anterior no funciona, entonces usamos esto:
    if not hasattr(emisor, "__parciales"):
        emisor.__parciales = []
    emisor.__parciales.append(partial(metodo, *args))
    connect(emisor, signal, emisor.__parciales[-1])


def conecta(ob, signal, func):
#    if type(signal) == str:
#        signal = QtCore.SIGNAL(signal)
    QtCore.QObject.connect(ob, signal, func)


def connect(ob, signal, func):
    QtCore.QObject.connect(ob, QtCore.SIGNAL(signal), func)


def evalIfDef(ob, fn, arg):
    if hasattr(ob, fn):
        ob.fn(arg)


def identity(x): return x


class nodeDict(dict):
    """a dictionary which searches keys using comparison operator =="""

    def __init__(self, **args):
        dict.__init__(self, **args)

    #    def __setitem__(self,key,value):
    #        super(nodeDict,self).__setitem__(key,value)

    def __getitem__(self, key):
        """this is what diferentiates nodeDic from a regular dict"""
        for k, v in self.items():
            if k == key:
                return v
        raise KeyError, key

    def has_key(self, key):
        return any(k == key for k in self.keys())

    def __contains__(self, key):
        return self.has_key(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

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
        self.calc.expression.set1Value(0, "oA=A-h*(A-B)")
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
        return self.v1 - t * (self.v1 - self.v2)

    def p1(self):
        return self.v1

    def p2(self):
        return self.v2


def segment(p1, p2, t):
    return p1 - t * (p1 - p2)


class GenIntervalo(object):
    def __init__(self, iter, func=None, tipo='t', name="I"):
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
            self.func = lambda x: x
        else:
            self.func = func
        self.tipo = tipo
        ## direccion = 1 | -1
        self.direccion = 1
        self.begin()

    def update(self, *vals):
        if self.iterFunc is not None:
            prev_points = self.npoints
            self.vmin, self.vmax, self.npoints = self.iterFunc(*vals)
            self.dt = float(self.vmax - self.vmin) / ( self.npoints - 1 )
            ## this could leave self.t or self.n in an inconsistent state
            ## (out of range)
            ## so, better calculate the corresponding n and t
            nprop = self.n / float(prev_points)
            self.n = int(round(nprop * self.npoints))
            self.t = self.n * self.dt + self.vmin

    def iter(self):
        return (self.name, self.vmin, self.vmax, self.npoints)

    def begin(self):
        self.reset(n=0)

    def end(self):
        ## the last valid n-value is npoints-1
        self.reset(n=self.npoints - 1)

    def reset(self, n=None, t=None):
        ## n es un entero entre 0 y npoints - 1
        ## t es un real entre vmin y vmax        
        if n is not None:
            self.n = int(n)
        elif t is not None:
            self.n = int(round((t - self.vmin) / self.dt))
        self.t = self.n * self.dt + self.vmin

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


def genIntervalPartition((vmin, vmax, npoints), func=None):
    """evaluate a function on the points of the interval partition, returns a generator
    >>> list(genIntervalPartition([0,1,3]))
    [0.0, 0.5, 1.0]
    >>> list(genIntervalPartition([0,1,3], lambda x: x+1))
    [1.0, 1.5, 2.0]
    """
    dt = float(vmax - vmin) / ( npoints - 1 )
    n = 0
    if not func:
        func = lambda x: x
    while n < npoints:
        yield func(vmin + n * dt)
        n += 1


def intervalPartition((vmin, vmax, npoints), func=None):
    """evaluate a function on the points of the interval partition"""
    return list(genIntervalPartition((vmin, vmax, npoints), func))


class Range(object):
    """Similar to xrange() but for float values"""

    def __init__(self, vmin, vmax, npoints=30):
        self.min = vmin
        self.max = vmax
        self.xrange = xrange(npoints)
        self.dt = float(self.max - self.min) / (npoints - 1)

    def __len__(self):
        return len(self.xrange)

    def __getitem__(self, i):
        ival = self.xrange[i]
        return self.min + self.dt * ival


def genCircular(lst):
    n = 0
    while True:
        if not len(lst):
            return
        yield lst[n]
        n = (n + 1) % len(lst)

########## Geometry ##################        

def border(p1, p2, k):
    """calcula la intersección con un círculo de radio k"""
    (x1, y1) = p1
    (x2, y2) = p2
    x2mx1 = x2 - x1
    y2my1 = y2 - y1
    a = 2 * x2 * x2mx1 + 2 * y2 * y2my1
    b = sqrt(pow(4 * k, 2) * (pow(-x2mx1, 2) + pow(-y2my1, 2)) - 4 * pow(x2 * y1 - x1 * y2, 2))
    c = (2 * (pow(-x2mx1, 2) + pow(-y2my1, 2)))
    t1 = (a - b) / c
    t2 = (a + b) / c
    xini = x2 - t1 * x2mx1
    yini = y2 - t1 * y2my1
    xfin = x2 - t2 * x2mx1
    yfin = y2 - t2 * y2my1
    return [(xini, yini), (xfin, yfin)]


def projection(q, p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    (x3, y3) = q
    c = ((x1 - x2) * (x2 - x3) + (y1 - y2) * (y2 - y3)) / ( pow(x1 - x2, 2) + pow(y1 - y2, 2) )
    x = x2 + (x2 - x1) * c
    y = y2 + (y2 - y1) * c
    return x, y

#def projectionVecs(a, u):  
#    ## segun mathworld la formula es:
#    ## proj_v (a) = (a.u)/|u|^2 * u
#    return mult( dot(a, u)/pow(norma(u) , 2),  u )
#    
#def mirror(q, p1, p2):
#    m = proyeccion(q, p1, p2)
#    return param(q,m,2)


########### Open Inventor ##################    

def write(node):
    """returns the OI text representation for node"""
    wa = SoWriteAction()
    wa.apply(node)


def readBuffer(texto):
    input = SoInput()
    input.setBuffer(texto)
    return SoDB.readAll(input)


def readFile(file):
    myInput = SoInput()
    myInput.openFile(file)
    return SoDB.readAll(myInput)

#def searchAll(nodo,label):
#    if nodo.getName().getString() == label:
#        return nodo
#    childList = nodo.getChildren()
#    if type(childList) == type(None):
#        return None
#    if childList.getLength() > 0:
#        for n in nodo.getChildren():
#            ret = buscaTodo(n, label)
#            if ret != None:
#                return n
#    ## in any other case
#    return None

def search(nodo, label):
    for c in nodo.getChildren():
        if c.getName().getString() == label:
            return c
    return None


def searchByName(root, name, default=None):
    sa = SoSearchAction()
    sa.setName(name)
    sa.setInterest(SoSearchAction.FIRST)
    sa.apply(root)
    if sa.getPath() != None:
        return sa.getPath().getTail()
    else:
        return default


def searchByNodeType(root, type, default=None, interest=SoSearchAction.FIRST):
    sa = SoSearchAction()
    sa.setType(type.getClassTypeId())
    sa.setInterest(interest)
    sa.apply(root)
    if interest != SoSearchAction.ALL and sa.getPath() != None:
        return sa.getPath().getTail()
    elif interest == SoSearchAction.ALL and len(list(sa.getPaths())) > 0:
        return [path.getTail() for path in sa.getPaths()]
    else:
        return default


def malla(puntos, func, xmin, xinc, nx, ymin, yinc, ny):
    for x in xrange(nx):
        for y in xrange(ny):
            puntos[ny * x + y] = func(xmin + xinc * x, ymin + yinc * y)


def mesh2(puntos, func, xmin, xinc, nx, ymin, yinc, ny):
    for x in xrange(nx):
        for y in xrange(ny):
            puntos.append(func(xmin + xinc * x, ymin + yinc * y))


def malla3(puntos, func, rangex, rangey):
    ny = len(rangey)
    for ix, x in enumerate(rangex):
        for iy, y in enumerate(rangey):
            puntos[ny * ix + iy] = func(x, y)


def wrap(node, show=True):
    """wrap node with a SoSwitch, returns the switch"""
    switch = SoSwitch()
    switch.addChild(getattr(node, 'root', node))
    switch.whichChild = SO_SWITCH_ALL if show else SO_SWITCH_NONE
    return switch


def make_hideable(node, show=True):
    """
    Creates a SoSwitch with node as children, and puts it in property node.root
    """
    switch = SoSwitch()
    switch.addChild(node)
    node.root = switch

    def getVisible(self):
        return self.root.whichChild.getValue() != SO_SWITCH_NONE

    def setVisible(self, val):
        self.root.whichChild = SO_SWITCH_ALL if val else SO_SWITCH_NONE

    node.__class__.visible = property(getVisible, setVisible)
    node.visible = show
    return node


def _1(r, g, b):
    """Converts colors from 0-255 to 0-1"""
    vmax = 255.
    return (r / vmax, g / vmax, b / vmax)


def main(chapter_cls=None):
    # to run interactively with ipython:
    # ipython -i --gui=qt script.py
    # in this case, QtGui.QApplication.instance() will be prebuilt
    from PyQt4 import QtGui
    from superficie.viewer.Viewer import Viewer

    app = QtGui.QApplication.instance()
    run_exec = False
    if not app:
        import sys

        app = QtGui.QApplication(sys.argv)
        run_exec = True
    visor = Viewer()
    if chapter_cls:
        visor.book.addChapter(chapter_cls())
        ## ============================
    visor.whichPage = 0
    visor.resize(400, 400)
    visor.show()
    visor.trackCameraPosition(True)
    visor.viewAll()
    visor.chaptersStack.show()
    #    visor.notasStack.show()
    if run_exec:
        sys.exit(app.exec_())
    return visor


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
    var = "var" + str(random()).split(".")[-1]
    fbody = strfunc.replace('#', var)
    exec ("ret = lambda %s: %s" % (var, fbody))
    return ret #@UndefinedVariable

#===========================================================================
# varios 
#===========================================================================

def manipulate(*args, **kwargs):
    print args
    print kwargs


def tuplize(arg):
    """returns arg if it is already a sequence, (arg,) otherwise"""
    return arg if isinstance(arg, collections.Sequence) else (arg,)


if __name__ == "__main__":
    from PyQt4 import QtGui, QtCore
    import sys
    from superficie.Plot3D import Plot3D, RevolutionPlot3D, ParametricPlot3D, Mesh
    from superficie.Viewer import Viewer
    from math import sin

    app = QtGui.QApplication(sys.argv)
    Mesh.autoAdd = True
    viewer = Viewer()
    viewer.createChapter()

    class MiPlot3D(Plot3D):
        def __init__(self, *args, **kwargs):
            super(MiPlot3D, self).__init__(*args, **kwargs)

        def With(self, param_lst):
            print param_lst

    def setupParameter(self, param):
        self.addParameter(('v', 0, 1, 0))
        ## ============================
        d = self.getParametersValues()
        for quad in self.quads.values():
            quad.function.updateGlobals(d)
            ## test the return value
            val = quad.function(1, 1)
            self.checkReturnValue(quad.function, val)
            ## ============================
            self.quads[quad.function] = quad
            self.addChild(quad)
            ## ============================
        self.updateAll()

    class F(object):
        def __init__(self, func):
            self.func = func
            func2 = lambda x, y: x + y
            self.wrapper = lambda: func2
            print self.wrapper.func_code.co_freevars
            eval(self.wrapper.func_code)

        def __call__(self, *args):
            return eval(self.wrapper.func_code)


    func = F(lambda x, y: x + y)
    #    print func(1,1)

    MiPlot3D(lambda x, y: (-x - sin(y)) * f, (-1, 1), (-1, 1))

    viewer.resize(400, 400)
    viewer.show()
    viewer.chaptersStack.show()
    viewer.viewAll()
    sys.exit(app.exec_())
