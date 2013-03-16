from base import Mesh, toList, func2param
from parametrized_function import getExtraVariables


class Plot3D(Mesh):
    def __init__(self, funcs, rangeX=(0, 1, 40), rangeY=(0, 1, 40), name=''):
        super(Plot3D, self).__init__(rangeX, rangeY, name)
        map(self.addFunction, toList(funcs))

    def addFunction(self, func):
        self.addQuad(func2param(func), getExtraVariables(func))
