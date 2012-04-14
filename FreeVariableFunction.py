from types import FunctionType

class FreeVariableFunction(object):
    """
    A function-like object which can handle free variables
    """
    usedFreeVariables = set()
    
    def __init__(self, func):
        self.func = func
        self.freeVariables = {}
        self.findInnerFreeVariables()
        FreeVariableFunction.usedFreeVariables.update(self.freeVariables.keys())

    def __call__(self,*args):
        return self.func(*args)
        
    @staticmethod
    def getFreeVariables(func):
        """
        extract the variable names that aren't in the global namespace
        @param func:
        """
        return filter(lambda n: n not in func.func_globals, func.func_code.co_names)
        
    def updateGlobals(self, dvals={}):
        """
        update the globals dictionary of each function with the values in dvals
        @param dvals: dictionary of values
        """
        for var,func in self.freeVariables.items():
            func.func_globals[var] = dvals[var]

    def argCount(self):
        return self.func.func_code.co_argcount

    def findInnerFreeVariables(self):        
        """
        create a map of free variables within each inner function of self.func
        """
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

if __name__ == "__main__":
    from math import sin 
    from Plot3D import func2param
    par = func2param(lambda u,v: h* u + sin(v)-w)
    fvf = FreeVariableFunction(par)
    print fvf.freeVariables
    fvf.updateGlobals({'h':1, 'w':0})
    print fvf(1,1)
    