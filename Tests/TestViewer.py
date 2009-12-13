import superficie
from superficie.Viewer import Viewer
from PyQt4 import QtGui
import sys
import unittest


class TestViewer(unittest.TestCase):
    def setUp(self):
        print Viewer.mro()
        self.app = QtGui.QApplication(sys.argv)
        self.viewer = Viewer()

    def tearDown(self):
        del self.viewer
        del self.app

    def testInit(self):
        print "testInit"
        return
        ## to force execution of setUp

#    def testChapterChangedSignal(self):
#        print "testChapterChangedSignal"
#        return
#        val = []
#        testFunc = (lambda n: val.append(n))
#        self.viewer.chapterChanged.connect(testFunc)
#        self.viewer.chapterChanged.emit(0)
#        self.assertEqual([0], val)





if __name__ == '__main__':
    unittest.main()
