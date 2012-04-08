__author__ = 'jpablo'

import sys
import unittest
import math
from superficie.nodes import Arrow
from superficie.nodes.arrow import calc_transformations
from superficie.util import Vec3

class TestArrow(unittest.TestCase):

    def test_transformations(self):
        angle, rot_axis, length = calc_transformations(Vec3(0,0,0),Vec3(0,0,1),1)
        self.assertEqual(length, 1)
        ## the default orientation is along the positive y axis
        self.assertEqual(angle, math.pi / 2)
        self.assertTupleEqual(tuple(rot_axis), (1,0,0))

    def test_Arrow(self):
        p1, p2 = (0,0,0),(1,1,1)
        arrow = Arrow(p1,p2)


if __name__ == '__main__':
    unittest.main()

