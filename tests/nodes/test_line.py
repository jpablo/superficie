__author__ = 'jpablo'

import sys
import unittest
from superficie.nodes import Line

class TestLine(unittest.TestCase):

    def test_Line(self):
        points = [p1,p2,p3,p4] = [(0,0,0),(1,1,1),(-1,2,0),(-1,-1,1)]
        line = Line([p1,p2,p3,p4])
        self.assertEqual(tuple(line[0]), p1)
        self.assertEqual(tuple(line[3]), p4)
        self.assertEqual(map(tuple,line.points), points)
        self.assertEqual(len(line), len(points))

        line.setPoints([p2,p3])
        self.assertEqual(tuple(line[0]), p2)
        self.assertEqual(tuple(line[1]), p3)
        self.assertEqual(len(line), 2)
        self.assertEqual(map(tuple,line.points), [p2,p3])


    def test_Segments(self):
        [p1,p2,p3,p4] = [(0,0,0),(1,1,1),(-1,2,0),(-1,-1,1)]
        line = Line([p1,p2,p3,p4]).setNumVerticesPerSegment([2,2])
        self.assertEqual(tuple(line[0]),p1)
        self.assertEqual(tuple(line[3]),p4)
        self.assertEqual(line.getNumVerticesPerSegment(),[2,2])

    def test_sum(self):
        points = [p1,p2,p3,p4] = [(0,0,0),(1,1,1),(-1,2,0),(-1,-1,1)]

        line1 = Line([p1,p2])
        line2 = Line([p3,p4])
        line = line1 + line2

        self.assertEqual(len(line),4)
        self.assertEqual(tuple(line[0]),p1)
        self.assertEqual(tuple(line[3]),p4)
        self.assertEqual(line.numVerticesPerSegment, [2,2])


if __name__ == '__main__':
    unittest.main()

