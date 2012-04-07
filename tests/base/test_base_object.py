__author__ = 'jpablo'

import sys
import unittest
from superficie.base import BaseObject

class TestBaseObject(unittest.TestCase):

    def test_BaseObject(self):
        ob = BaseObject()

        ob.show()
        self.assertTrue(ob.visible)

        ob.hide()
        self.assertFalse(ob.visible)

        ob.origin = (1,1,1)
        self.assertTupleEqual(tuple(ob.origin), (1,1,1))


if __name__ == '__main__':
    unittest.main()

