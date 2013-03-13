import sys
import unittest
from superficie.base import MaterialNode

class TestBaseObject(unittest.TestCase):

    def test_MaterialNode(self):
        node = MaterialNode()
        node.diffuseColor = (100,0,0)
        self.assertListEqual(map(tuple,node.diffuseColor), [(100,0,0)])

        node.transparency = 0.5
        self.assertListEqual(node.transparency, [0.5])



if __name__ == '__main__':
    unittest.main()

