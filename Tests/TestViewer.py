import superficie
from superficie.Viewer2 import Viewer
from PyQt4 import QtGui
import sys
import unittest


class TestViewer(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.viewer = Viewer()

    def tearDown(self):
        del self.viewer
        del self.app

    def testInit(self):
        ## to force execution of setUp
        pass




if __name__ == '__main__':
    unittest.main()
