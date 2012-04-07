# -*- coding: utf-8 -*-
__author__="jpablo"
__date__ ="$8/12/2009 01:10:52 AM$"

from PyQt4 import QtGui
from superficie.Book import Chapter, Page
import sys
import unittest


class TestChapter(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.chapter = Chapter("test")

    def tearDown(self):
        del self.chapter
        del self.app

    def testAddPage(self):
        self.chapter.addPage(Page())
        self.chapter.addPage(Page())

        self.assertEqual(2, len(self.chapter.pagesSwitch))
        self.assertEqual(2, len(self.chapter.pages))
        self.assertEqual(2, self.chapter.widget.pageStack.count())
        self.assertEqual(1, self.chapter.widget.pageStack.currentIndex())

    def testWhichPage(self):
        self.chapter.addPage(Page())
        self.chapter.addPage(Page())

        self.assertEqual(1,self.chapter.whichPage)

        self.chapter.whichPage = 0
        self.assertEqual(0,self.chapter.whichPage)

    def testChangePage(self):
        self.chapter.createPage()
        self.chapter.createPage()

        self.chapter.nextPage()
        self.assertEqual(0,self.chapter.whichPage)
        self.chapter.prevPage()
        self.assertEqual(1,self.chapter.whichPage)

    def testCurrentPage(self):
        self.assertEqual(None,self.chapter.page)

        page1 = self.chapter.createPage()
        page2 = self.chapter.createPage()
        self.assertEqual(page2,self.chapter.page)

        self.chapter.prevPage()
        self.assertEqual(page1,self.chapter.page)

        ## it's circular
        self.chapter.prevPage()
        self.assertEqual(page2,self.chapter.page)

if __name__ == '__main__':
    unittest.main()
