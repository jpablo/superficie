from plots.Plot3D import Mesh, toList

__author__ = 'jpablo'

class ParametricPlot3D(Mesh):
    def __init__(self, funcs, rangeX=(0,1,40), rangeY=(0,1,40), name = ''):
        super(ParametricPlot3D,self).__init__(rangeX,rangeY,name)
        funcs = toList(funcs)
        for fn in funcs:
            self.addQuad(fn)

    def addFunction(self,func):
        self.addQuad(func)