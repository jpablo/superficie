__author__ = 'jpablo'

from superficie.Objects import Arrow
from superficie.util import Vec3

import unittest



class  ObjectsTestCase(unittest.TestCase):

    def test_Arrow(self):
        a = Arrow(Vec3(1,1,1),Vec3(0,0,0))
        b = Arrow(Vec3(1,1,1),Vec3(0,0,1))
        b.setPoints(Vec3(1,1,1),Vec3(0,0,0))

        self.assertEqual(list(a.p1), list(b.p1))
        self.assertEqual(list(a.p2), list(b.p2))
        self.assertEqual(a.body.height.getValue(), b.body.height.getValue())



if __name__ == '__main__':
    unittest.main()

