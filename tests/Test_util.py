import sys
from PyQt4 import QtGui
from pivy.coin import SoGroup
from superficie import util
import unittest



class  UtilTestCase(unittest.TestCase):
#    def setUp(self):
#        self.app = QtGui.QApplication(sys.argv)

    def test_make_hideable(self):
        group = SoGroup()
        util.make_hideable(group)

        self.assertTrue(hasattr(group,'parent_switch'))
        self.assertEqual(list(group.parent_switch.getChildren()),[group])

    def test_intervalPartition(self):
        p = util.intervalPartition([0,1,3])
        self.assertEquals(p,[0.0,0.5,1.0])

        p2 = util.intervalPartition([0,1,3], lambda x: x+1)
        self.assertEquals(p2,[1.0,1.5,2.0])


if __name__ == '__main__':
    unittest.main()

