from superficie.Viewer import Viewer
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


    def testChapterChangedSignal(self):
        val = []
        testFunc = (lambda n: val.append(n))
        self.viewer.chapterChanged.connect(testFunc)
        self.viewer.chapterChanged.emit(0)
        self.assertEqual([0], val)

    def testWhichChapter(self):
        self.viewer.createChapter()
        self.viewer.createChapter()
        self.viewer.whichChapter = 0
        self.assertEqual(0, self.viewer.whichChapter)
        self.assertEqual(2,len(self.viewer))


if __name__ == '__main__':
    unittest.main()
