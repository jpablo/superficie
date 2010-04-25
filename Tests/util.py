from superficie.util import SupHideable
from pivy.coin import SoGroup
import sys

from PyQt4 import QtGui
import unittest


class  UtilTestCase(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_SupHideable(self):
        group = SoGroup()
        h = SupHideable(group)
        print h

if __name__ == '__main__':
    unittest.main()

