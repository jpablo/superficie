from math import pi
from base import Mesh, toList, func2revolution_param
from parametrized_function import getExtraVariables


class RevolutionPlot3D(Mesh):
    def __init__(self, funcs, rangeX=(0, 1, 40), rangeY=(0, 2 * pi, 40), name=''):
        super(RevolutionPlot3D, self).__init__(rangeX, rangeY, name)
        map(self.addFunction, toList(funcs))

    def addFunction(self, func):
        self.addQuad(func2revolution_param(func), getExtraVariables(func))
