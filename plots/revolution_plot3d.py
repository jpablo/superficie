from math import pi
from base import Mesh, toList, func2revolution_param


class RevolutionPlot3D(Mesh):
    def __init__(self, funcs, rangeX=(0, 1, 40), rangeY=(0, 2 * pi, 40), name=''):
        super(RevolutionPlot3D, self).__init__(rangeX, rangeY, name)
        funcs = toList(funcs)
        params = map(func2revolution_param, funcs)
        for par in params:
            self.addQuad(par)

    def addFunction(self, func):
        self.addQuad(func2revolution_param(func))

#    def checkReturnValue(self, func, val):
