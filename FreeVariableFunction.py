'''
Created on 25/04/2010

@author: jpablo
'''

from random import random
from types import FunctionType

class FreeVariableFunction(object):
    '''
    A function-like object which can handle free variables
    '''
    def __init__(self, func):
        self.func = func 
        self.freeVariables = {}
        self.findInnerFreeVariables()

    def __call__(self,*args):
        return self.func(*args)
    
    @staticmethod
    def getFreeVariables(func):
        '''
        extract the variable names that aren't in the global namespace
        @param func:
        '''
        return filter(lambda n: n not in func.func_globals, func.func_code.co_names) 
        
    def updateGlobals(self, dvals={}):
        '''
        update the globals dictionary of each function with the values in dvals
        @param dvals: dictionary of values
        '''
        for var,func in self.freeVariables.items():
            func.func_globals[var] = dvals[var]

    def argCount(self):
        return self.func.func_code.co_argcount

    def findInnerFreeVariables(self):        
        '''
        create a map of free variables within each inner function of self.func
        '''
        def _findFunctions(func):
            for fv in FreeVariableFunction.getFreeVariables(func): 
                self.freeVariables[fv] = func
            if not func.func_closure:
                return 
            for closure in func.func_closure:
                obj = closure.cell_contents
                if isinstance(obj, FunctionType):
                    _findFunctions(obj)
        _findFunctions(self.func)
                
        
    
#def bindFreeVariables(func, dvals={}):
#    dvals.update(globals())
#    f = FunctionType(func.func_code, dvals, closure=func.func_closure)
#    f.func_defaults = func.func_defaults
#    return f
#
#def getFreeVariables(func):
#    nargs = func.func_code.co_argcount
#    vars1 = []
#    while True:
#        try:
#            d = dict(zip(vars1,[random() for j in vars1]))
#            print "d:", d
#            f = bindFreeVariables(func, d)
#            args = [random() for j in range(nargs)]
#            val = f(*args)
#            break
#        except NameError, error:
#            freevar = error.args[0].split(" ")[2].replace("'","")
#            ## this occurs when func has an inner function with
#            ## free variables
#            if freevar in vars1:
#                raise NameError, error
#            vars1.append(freevar)
#    return vars1
#
#    
#
#class FreeVariableFunction2(object):
#    '''
#    A function-like object which can handle free variables
#    '''
#    def __init__(self, func):
#        self.func = func
#        self.freeVariables = filter(lambda n: n not in func.func_globals, func.func_code.co_names)
#
#    def __call__(self,*args):
#        return self.func(*args) 
#        
#    def updateGlobals(self, dvals={}):
#        self.func.func_globals.update(dvals)
#
#    def argCount(self):
#        return self.func.func_code.co_argcount

if __name__ == "__main__":
    from math import sin 
    from Plot3D import func2param
    par = func2param(lambda u,v: h* u + sin(v)-w)
    fvf = FreeVariableFunction(par)
    print fvf.freeVariables
    fvf.updateGlobals({'h':1, 'w':0})
    print fvf(1,1)
    