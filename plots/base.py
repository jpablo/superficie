import operator
import itertools
from math import *
from PyQt4 import QtGui, QtCore
from pivy.coin import *
from superficie.viewer.Viewer import Viewer
from superficie.animations.animation import Animation
from superficie.base import MaterialNode
from superficie.util import conecta, intervalPartition, Range, malla, make_hideable
from superficie.utils import fluid
from superficie.widgets import Slider
from superficie.plots.parametrized_function import ParametrizedFunction


def genVarsVals(vars, args):
    return ";".join([v + "=" + str(a) for v, a in zip(vars, args)])


def func2param(func):
    """
    Transforms a function f:R^2 -> R into f(x,y) => (x,y,f(x,y))
    @param func:
    """

    def param(x, y, *args, **kwargs):
        return x, y, func(x, y, *args, **kwargs)

    return param


def func2revolution_param(func):
    """
    Transforms a function f:R^2 -> R into f(r,t) => (r cos(t), r sin(t),f(r,t))
    @param func:
    """

    def param(r, t, *args, **kwargs):
        return r * cos(t), r * sin(t), func(r, t, *args, **kwargs)

    return param


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

    def __init__(self, func=None, nx=10, ny=10, extraVars=()):
        self.function = ParametrizedFunction(func, extraVars)
        if self.function.argCount() < 2:
            raise (TypeError, "function %s needs at least 2 arguments" % func)
        self.vectorFieldFunc = None
        self.coordinates = SoCoordinate3()
        self.mesh = make_hideable(SoQuadMesh())
        self.mesh.verticesPerColumn = nx
        self.mesh.verticesPerRow = ny
        normal_binding = SoNormalBinding()
        normal_binding.value = SoNormalBinding.PER_VERTEX_INDEXED
        ## ============================
        self.scale = SoScale()
        self.lineSetX = make_hideable(SoLineSet(), show=False)
        self.lineSetY = make_hideable(SoLineSet(), show=False)
        self.linesetYcoor = SoCoordinate3()
        self.lineColor = SoMaterial()
        self.lineColor.diffuseColor = (1, 0, 0)
        ## ============================
        self.root = SoSeparator()
        self.root.addChild(normal_binding)
        self.root.addChild(self.scale)
        self.root.addChild(self.coordinates)
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

    def addVectorField(self, func):
        self.vectorFieldFunc = func

    def update(self, rangeX, rangeY):
        vertices = range(len(rangeX) * len(rangeY))
        malla(vertices, self.function, rangeX.min, rangeX.dt, len(rangeX), rangeY.min, rangeY.dt, len(rangeY))
        self.coordinates.point.setValues(0, len(vertices), vertices)
        ## ============================
        ## the lines
        vpc = self.verticesPerColumn
        vpr = self.verticesPerRow
        lstX = tuple(itertools.repeat(vpr, vpc))
        lstY = tuple(itertools.repeat(vpc, vpr))
        self.lineSetX.numVertices.setValues(lstX)  # we need the "transpose of the first list
        verticesY = []
        for i in range(vpr):
            for j in range(vpc):
                verticesY.append(vertices[j * vpr + i])
        self.linesetYcoor.point.setValues(0, len(verticesY), verticesY)
        self.lineSetY.numVertices.setValues(lstY)


class Mesh(MaterialNode):
    """A Set of Quads which share the same generating function"""

    def __init__(self, rangeX=(0, 1, 40), rangeY=(0, 1, 40), name=''):
        super(Mesh, self).__init__()
        self.name = name
        ## ============================
        self.sHints = SoShapeHints()
        self.sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        self.sHints.creaseAngle = 0.0
        self.separator.addChild(self.sHints)
        ## ============================
        self.quads = {}
        self.parameters = {}
        self.rangeX = Range(*rangeX)
        self.rangeY = Range(*rangeY)
        self.setupGui()
        self.animation = Animation(lambda x: x, (1000, 1, 2))

    def __len__(self):
        return len(self.rangeX) * len(self.rangeY)

    def setupGui(self):
        # TODO: factorize gui code out of BaseObject subtypes as much as possible.
        layout = QtGui.QVBoxLayout()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        if self.name != "":
            layout.addWidget(QtGui.QLabel("<center><h1>%s</h1></center>" % self.name))

    def getGui(self):
        return self.widget

    def addWidget(self, widget):
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
    def setMeshDiffuseColor(self, val):
        for quad in self.quads.values():
            quad.lineColor.diffuseColor = val

    meshDiffuseColor = property(fset=setMeshDiffuseColor)

    def setScaleFactor(self, vec3):
        for quad in self.quads.values():
            quad.scale.scaleFactor = vec3

    def setVerticesPerColumn(self, n):
        for quad in self.quads.values():
            quad.mesh.verticesPerColumn = int(round(n))

    def checkReturnValue(self, func, val):
        if not operator.isSequenceType(val) or len(val) != 3:
            raise TypeError, "function %s does not produces a 3-tuple" % func

    def getParametersValues(self):
        return dict((par.name, par.getValue()) for par in self.parameters.values())

    def addQuad(self, func, extraVars=()):
        """
        Adds a Quad object.
        @param func: the function used to generate the points
        """
        quad = Quad(func, len(self.rangeX), len(self.rangeY), extraVars)
        for v in sorted(quad.function.extraVariables):
            if not v in self.parameters:
                self.addParameter((v, 0, 1, 0))
            #     ## ============================
        d = self.getParametersValues()
        quad.function.updateExtraVariables(d)
        ## test the return value with valid values
        x_ini = self.rangeX[0]
        y_ini = self.rangeY[0]
        val = quad.function(x_ini, y_ini)
        self.checkReturnValue(quad.function, val)
        ## ============================
        self.quads[quad.function] = quad
        self.separator.addChild(quad.root)
        ## ============================
        self.updateAll()

    def updateParameters(self):
        d = self.getParametersValues()
        for function in self.quads:
            function.updateExtraVariables(d)

    def updateAll(self, val=0):
        if hasattr(self, "parameters"):
            self.updateParameters()
            self.updateMesh()

    def updateMesh(self):
        for quad in self.quads.values():
            quad.update(self.rangeX, self.rangeY)

    def addParameter(self, rangep=('w', 0, 1, 0), qlabel=None):
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
        # the equation is centered
        layout.addStretch()
        eqn.eval(layout)
        layout.addStretch()
        self.addWidget(w)