__author__ = 'jpablo'

import sys
import unittest
from superficie.nodes import Curve3D

class TestLine(unittest.TestCase):

    def test_Curve3(self):
        fn = lambda t: (t,0,0)
        start, end, npoints = (0,1,10)
        curve = Curve3D(fn,(start,end,npoints))

        self.assertEqual(len(curve.lines),1)
        self.assertEqual(len(curve),npoints)
        self.assertEqual(tuple(curve[0]), fn(start))
        self.assertEqual(tuple(curve[npoints-1]), fn(end))


    def test_intervals(self):
        fn = lambda t: (t,0,0)
        start1, end1, npoints1 = (0,1,5)
        start2, end2, npoints2 = (2,3,7)
        ntotal = npoints1 + npoints2
        curve = Curve3D(fn, [(start1,end1,npoints1), (start2,end2,npoints2)])

        self.assertEqual(len(curve.lines), 2)
        self.assertEqual(len(curve), ntotal)
        self.assertEqual(len(curve.points), ntotal)
        self.assertEqual(len(curve.domainPoints), ntotal)
        self.assertEqual(tuple(curve[0]), fn(start1))
        self.assertEqual(tuple(curve[npoints1 + npoints2-1]), fn(end2))

