'''
Created on 25/04/2010

@author: jpablo
'''

class FreeVariableFunction(object):
    '''
    A function-like object which can handle free variables
    '''
    def __init__(self, func):
        self.func = func
        self.freeVariables = filter(lambda n: n not in func.func_globals, func.func_code.co_names)

    def __call__(self,*args):
        return self.func(*args) 
        
    def updateGlobals(self, dvals={}):
        self.func.func_globals.update(dvals)

    def argCount(self):
        return self.func.func_code.co_argcount
    