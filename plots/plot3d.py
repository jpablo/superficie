from base import Mesh, toList, func2param

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
