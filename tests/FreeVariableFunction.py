'''
Created on 09/05/2010

@author: jpablo
'''
import unittest

from superficie.Plot3D import func2param
from superficie.FreeVariableFunction import FreeVariableFunction
from math import sin 

class Test(unittest.TestCase):


    def testFreeVariable(self):
        par = func2param(lambda u,v: h* u + sin(v)*w) #@UndefinedVariable
        fvf = FreeVariableFunction(par)
        vals = {'h':1, 'w':0}
        
        self.assertEqual(2,fvf.argCount())
        self.assertEqual(2, len(fvf.freeVariables))
        self.assertEqual(vals.keys(), fvf.freeVariables.keys())
        
        fvf.updateGlobals(vals)
        res = fvf(0,0)
        self.assertEqual((0,0,0.0), res)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFreeVariable']
    unittest.main()