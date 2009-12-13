import superficie
from superficie.Viewer import Viewer
from PyQt4 import QtGui
from superficie.Book import Book
import sys
import unittest


class TestBook(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.book = Book()

    def tearDown(self):
        del self.book
        del self.app

    def testAddChapter(self):
        self.book.createChapter()
        self.book.createChapter()

        self.assertEqual(2, len(self.book.chapters))
        self.assertEqual(2, len(self.book.chaptersObjects))

    def testProperties(self):
        self.assertEqual(None, self.book.page)

        chap1 = self.book.createChapter()
        chap2 = self.book.createChapter()

        ## self.book.chapter is the switch child of the separator "root"
        self.assertEqual(chap2.pagesSwitch, self.book.chapterSwitch)
        self.assertEqual(chap2, self.book.chapter)
        self.assertEqual(1, self.book.whichChapter)
        self.book.whichChapter = 0
        self.assertEqual(0, self.book.whichChapter)

#    def testChapterChangedSignal(self):
#        val = []
#        testFunc = (lambda n: val.append(n))
#        self.book.chapterChanged.connect(testFunc)
#        self.book.chapterChanged.emit(0)
#        self.assertEqual([0], val)


if __name__ == '__main__':
    unittest.main()
