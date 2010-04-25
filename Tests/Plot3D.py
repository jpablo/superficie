import sys

from pivy.coin import SoGroup
from pivy.coin import SoNode
from superficie.Plot3D import Mesh

from PyQt4 import QtGui
from pivy.coin import SO_SWITCH_NONE
from superficie.Plot3D import Quad
import unittest

class  Plot3DTestCase(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
    

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def testQuad(self):
        func = lambda x,y: 0
        quad = Quad(func, 2, 2)
        self.assertEqual(2,quad.verticesPerColumn)
        self.assertEqual(2,quad.verticesPerRow)
        
    def testMesh(self):
        """Documentation"""
        rangeX = (0,1,2)
        rangeY = (0,1,2)
        func = lambda x,y: (0,0,0)
        mesh = Mesh(rangeX,rangeY,"testMesh")
        mesh.addQuad(func)
        mesh.meshVisible = False
        mesh.linesVisible = False

        quad = mesh.quads.values()[0]
        
        self.assertEqual(False, quad.meshVisible)
        self.assertEqual(False, quad.linesVisible)


if __name__ == '__main__':
    unittest.main()

