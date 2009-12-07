import superficie.base
import superficie
from superficie.Viewer import Viewer
from PyQt4 import QtGui
import sys
import unittest


class TestBook(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.book = superficie.base.Book()

    def tearDown(self):
        del self.book
        del self.app

    def testAddChapter(self):
        self.book.createChapter()
        self.book.createChapter()

        self.assertEqual(2, len(self.book.chapters))
        self.assertEqual(2, len(self.book.chaptersObjects))

    def testProperties(self):
        chap1 = self.book.createChapter()
        chap2 = self.book.createChapter()

        ## self.book.chapter is the switch child of the separator "root"
        self.assertEqual(chap2.root[0], self.book.chapter)
        self.assertEqual(chap2, self.book.chapterObject)
        self.assertEqual(1, self.book.whichChapter)
        self.book.whichChapter = 0
        self.assertEqual(0, self.book.whichChapter)

        ## since there is no page yet
        self.assertEqual(-1, self.book.whichPage)
        ## this statement should do nothing
        self.book.whichPage = 0

    def testAddPage(self):
        chap1 = self.book.createChapter()
        chap1.addPage(superficie.base.Page())
#        self.assertEqual(0, self.book.whichPage)


if __name__ == '__main__':
    unittest.main()
