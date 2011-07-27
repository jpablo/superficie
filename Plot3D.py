#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pivy.coin import *

from superficie.Viewer import Viewer

from Animation import Animation
Quarter = True

from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4 import QtGui, QtCore
import operator
import itertools

from util import  conecta, intervalPartition, Range, malla,make_hideable
from BaseObject import GraphicObject, fluid
from gui import Slider
from Objects import Arrow
from FreeVariableFunction import FreeVariableFunction

## TODO: el código necesita averiguar qué símbolos están definidos
## en el bloque que llama a *Plot3D, para que este código
## use las funciones ya definidas, y no tener que definirlas aquí
from math import *


def genVarsVals(vars, args):
    return ";".join([v+"="+str(a) for v, a in zip(vars, args)])

def func2param(func):
    """
    Transforms a function f:R^2 -> R into f(x,y) => (x,y,f(x,y)
    @param func:
    """
    return lambda x,y: (x,y,func(x,y))

def func2revolution_param(func):
    """
    Transforms a function f:R^2 -> R into f(r,t) => (r cos(t), r sin(t),f(r,t)
    @param func:
    """
    return lambda r,t: (r*cos(t),r*sin(t),func(r,t))
    
def toList(obj_or_lst):
    """
    if obj_or_lst is not a list, converts it; return it otherwise
    @param obj_or_lst:
    """
    
    if not type(obj_or_lst) in (list, tuple):
        obj_or_lst = [obj_or_lst]
    return obj_or_lst
    
        
class Quad(object):
    """A Mesh"""
    def __init__(self, func = None, nx = 10, ny = 10):
        self.function = FreeVariableFunction(func)
#        print self.function.usedFreeVariables
        if self.function.argCount() < 2:
            raise TypeError, "function %s needs at least 2 arguments" % func
        self.vectorFieldFunc = None
        self.coords = SoCoordinate3()
        self.mesh = make_hideable(SoQuadMesh())
        self.mesh.verticesPerColumn = nx
        self.mesh.verticesPerRow = ny
        normal_binding = SoNormalBinding()
        normal_binding.value = SoNormalBinding.PER_VERTEX_INDEXED
        ## ============================
        self.scale = SoScale()
        self.lineSetX = make_hideable(SoLineSet(),show=False)
        self.lineSetY = make_hideable(SoLineSet(),show=False)
        self.linesetYcoor = SoCoordinate3()
        self.lineColor = SoMaterial()
        self.lineColor.diffuseColor = (1,0,0)
        ## ============================
        self.root = SoSeparator()
        self.root.addChild(normal_binding)
        self.root.addChild(self.scale)
        self.root.addChild(self.coords)
        self.root.addChild(self.mesh.root)
        self.root.addChild(self.lineColor)
        self.root.addChild(self.lineSetX.root)
        self.root.addChild(self.linesetYcoor)
        self.root.addChild(self.lineSetY.root)

    def getLinesVisible(self):
        return self.lineSetX.visible

    def setLinesVisible(self, visible):
        self.lineSetX.visible = visible
        self.lineSetY.visible = visible
    
    linesVisible = property(getLinesVisible, setLinesVisible)

    @property
    def verticesPerColumn(self):
        return self.mesh.verticesPerColumn.getValue()

    @property
    def verticesPerRow(self):
        return self.mesh.verticesPerRow.getValue()

    def addVectorField(self,func):
        self.vectorFieldFunc = func

    def update(self, rangeX, rangeY):
        vertices = range(len(rangeX) * len(rangeY))
        malla(vertices, self.function, rangeX.min, rangeX.dt, len(rangeX), rangeY.min, rangeY.dt, len(rangeY))
        self.coords.point.setValues(0, len(vertices), vertices)
        ## ============================
        ## the lines
        vpc = self.verticesPerColumn
        vpr = self.verticesPerRow
        lstX = tuple(itertools.repeat(vpr,vpc))
        lstY = tuple(itertools.repeat(vpc,vpr)) 
        self.lineSetX.numVertices.setValues(lstX) ## we need the "transpose of the first list
        verticesY = []
        for i in range(vpr):
            for j in range(vpc):
                verticesY.append(vertices[j * vpr + i])        
        self.linesetYcoor.point.setValues(0, len(verticesY), verticesY)
        self.lineSetY.numVertices.setValues(lstY)
            ## ============================
            ## the vector field
#        if quad.vectorFieldFunc:
#            for v in vertices:
#                vf = quad.vectorFieldFunc(Vec3(v))
#                self.addChild(Arrow(Vec3(v), vf, visible=True, escala=.005, extremos=True))


        
class Mesh(GraphicObject):
    """A Set of Quads which share the same generating function"""
    ## ============================
    autoAdd = False

    def __init__(self, rangeX=(0,1,40),  rangeY=(0,1,40), name=''):
        super(Mesh,self).__init__()
        self.name = name
        ## ============================
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.sHints.creaseAngle = 0.0
        self.addChild(self.sHints)
        ## ============================
        self.quads = {}
        self.parameters = {}
        self.rangeX = Range(*rangeX)
        self.rangeY = Range(*rangeY)
        ## ============================
        # TODO: factorize gui code out of BaseObject subtypes as much as possible.
        layout  =  QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            layout.addWidget(QtGui.QLabel("<center><h1>%s</h1></center>" % self.name))
        if Mesh.autoAdd:
            viewer = Viewer.Instance()
            viewer.chapter.createPage()
            viewer.page.addChild(self)
        ## ===============================
        self.animation = Animation(lambda x:x, (1000, 1, 2))



    def __len__(self):
        return len(self.rangeX) * len(self.rangeY)
            
    def getGui(self):
        return self.widget

    def addWidget(self,widget):
        self.widget.layout().addWidget(widget)

    def addVectorField(self, func):
        for quad in self.quads.values():
            quad.addVectorField(func)

    @fluid
    def setMeshVisible(self, visible):
        for quad in self.quads.values():
            quad.mesh.visible = visible
            
    meshVisible = property(fset=setMeshVisible)

    @fluid
    def setLinesVisible(self, visible):
        for quad in self.quads.values():
            quad.linesVisible = visible
            
    linesVisible = property(fset=setLinesVisible)

    @fluid
    def setMeshDiffuseColor(self,val):
        for quad in self.quads.values():
            quad.lineColor.diffuseColor = val
            
    meshDiffuseColor = property(fset=setMeshDiffuseColor)

    def setScaleFactor(self,vec3):
        for quad in self.quads.values():
            quad.scale.scaleFactor = vec3

    def setVerticesPerColumn(self,n):
        for quad in self.quads.values():
            quad.mesh.verticesPerColumn = int(round(n))
            
    def checkReturnValue(self, func, val):
        if not operator.isSequenceType(val) or len(val) != 3:
            raise TypeError, "function %s does not produces a 3-tuple" % func
    
    def getParametersValues(self):
        return dict((par.name, par.getValue()) for par in self.parameters.values())
    
    def addQuad(self,func):
        """
        Adds a Quad object.
        @param func: a callable
        """
        quad = Quad(func, len(self.rangeX), len(self.rangeY))
        for v in sorted(quad.function.freeVariables):
            self.addParameter((v, 0, 1, 0))
        ## ============================
        d = self.getParametersValues()
        quad.function.updateGlobals(d)
        ## test the return value with valid values
        xini = self.rangeX[0]
        yini = self.rangeY[0]
        val = quad.function(xini,yini)
        self.checkReturnValue(quad.function, val)
        ## ============================
        self.quads[quad.function] = quad
        self.addChild(quad)
        ## ============================
        self.updateAll()        
        
        
    def updateParameters(self):
        d = self.getParametersValues()
        for function in self.quads:
            function.updateGlobals(d)
        
    def updateAll(self, val = 0):
        if hasattr(self,"parameters"):
            self.updateParameters()
            self.updateMesh()


    def updateMesh(self):
        for quad in self.quads.values():
            quad.update(self.rangeX, self.rangeY)

    def addParameter(self, rangep=('w', 0, 1, 0), qlabel = None):
        """
        @param rangep: (name, vmin, vmax, vini) | (name, vmin, vmax)
        """
        if len(rangep) == 3:
            rangep += rangep[1:2]
        sliderNpoints = 20
        rangep += (sliderNpoints,)
        ## ============================
        slider = Slider(rangep=rangep, func=self.updateAll)
        self.addWidget(slider)
        self.parameters[slider.name] = slider
        ## ============================
        if qlabel is not None:
            if not (type(qlabel) == list or type(qlabel) == tuple):
                qlabel = [qlabel]
            slider.qlabel = qlabel
            for lab in qlabel:
                conecta(slider, QtCore.SIGNAL("labelChanged(float)"), lab.setParamValue)
        ## ============================
        return slider

    def getParameter(self, name):
        return self.parameters[name]
        
    def setRange(self, name, rangep):
        if name == "x":
            pass
        elif name == "y":
            pass
        else:
            self.getParameter(name).updateRange(rangep)
            
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
        self.widget.layout().insertWidget(1,w,0, QtCore.Qt.AlignTop)



class ParametricPlot3D(Mesh):
    def __init__(self, funcs, rangeX=(0,1,40), rangeY=(0,1,40), name = ''):
        super(ParametricPlot3D,self).__init__(rangeX,rangeY,name)
        funcs = toList(funcs)
        for fn in funcs:
            self.addQuad(fn)

    def addFunction(self,func):
        self.addQuad(func)            

class Plot3D(Mesh):
    def __init__(self, funcs, rangeX=(0,1,40), rangeY=(0,1,40), name = ''):
        super(Plot3D,self).__init__(rangeX,rangeY,name)
        funcs = toList(funcs)
        params = map(func2param, funcs)
        for par in params:
            self.addQuad(par)

    def addFunction(self,func):
        self.addQuad(func2param(func))            
        
#    def checkReturnValue(self, func, val):
#        if not operator.isNumberType(val):
#            raise TypeError, "function %s does not produces a number" % func
        
            
class RevolutionPlot3D(Mesh):
    def __init__(self, funcs, rangeX=(0,1,40), rangeY=(0,2*pi,40), name = ''):
        super(RevolutionPlot3D,self).__init__(rangeX,rangeY,name)
        funcs = toList(funcs)
        params = map(func2revolution_param, funcs)
        for par in params:
            self.addQuad(par)

    def addFunction(self,func):
        self.addQuad(func2revolution_param(func))            
        
#    def checkReturnValue(self, func, val):
#        if not operator.isNumberType(val):
#            raise TypeError, "function %s does not produces a number" % func
            

#class RevolutionParametricPlot3D(ParametricPlot3D):
#    def __init__(self, funcs, rangeX=(0,1,40), rangeY=(0,1,40), name = '', eq = None,visible = True, parent = None):
#        ParametricPlot3D.__init__(self,funcs,rangeX=rangeX,rangeY=rangeY,name=name,visible=visible,parent=parent)



class VectorField3D(GraphicObject):
    def __init__(self, curve, cp, col, factor=1, name="", visible = False, parent = None):
        """curve is something derived from Line"""
        GraphicObject.__init__(self,visible,parent)
        comp = SoComplexity()
        comp.value.setValue(.1)
        self.separator.addChild(comp)
        ## ============================
        points = curve.getPoints()
        pointsp = [curve[i]+cp(t)*factor for i,t in enumerate(intervalPartition(curve.iter))]
        for p,pp in zip(points,pointsp):
            self.addChild(Arrow(p,pp,visible=True,escala=.005,extremos=True))

        self.animation = Animation(lambda num: self[num-1].show(),(4000,1,len(points)))

    def setMaterial(self,mat):
        for c in self.getChildren():
            c.material.ambientColor  = mat.ambientColor
            c.material.diffuseColor  = mat.diffuseColor
            c.material.specularColor = mat.specularColor
            c.material.shininess     = mat.shininess

    def setHeadMaterial(self,mat):
        for c in self.getChildren():
            c.matHead.ambientColor  = mat.ambientColor
            c.matHead.diffuseColor  = mat.diffuseColor
            c.matHead.specularColor = mat.specularColor
            c.matHead.shininess     = mat.shininess

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



if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    Mesh.autoAdd = True
    viewer = Viewer()
    viewer.createChapter()
    #===========================================================================
    # Mesh
    #===========================================================================
    m = Mesh((-1, 1, 20), (-1, 1, 20))
    m.addQuad(lambda x, y:(x,y,   u*x**2 - v*y**2))
    m.addQuad(lambda x, y:(x,y, - sin(x)**2 - y**2))

    #===========================================================================
    # ParametricPlot3D
    #===========================================================================
    pp = ParametricPlot3D(lambda x,y:(x,y, a*x**2 + b*y**2),(-1,1),(-1,1),name="pp")

    for t in intervalPartition((0, 3, 4)):
        pp.addQuad(lambda x,y,t=t:(x,y, x**2 + b*y**2 + t))

    pp.setRange("a", (-1, 1, 0))
    pp.setRange("b", (-1, 1, 0))

    #===========================================================================
    # Plot3D
    #===========================================================================
    Plot3D(lambda x,y: h*(x**2+y**2+z),(-1,1),(-1,1), name="p2")
    #===========================================================================
    # RevolutionPlot3D
    #===========================================================================
    RevolutionPlot3D(lambda r,t: 1/r ,(.2,1),(.1,2*pi), name="p3")
    ## ============================
    viewer.whichPage = 0
    viewer.resize(400, 400)
    viewer.show()
    viewer.chaptersStack.show()
    viewer.viewAll()

    sys.exit(app.exec_())
    
