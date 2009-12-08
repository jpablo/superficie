# -*- coding: utf-8 -*-
__author__="jpablo"
__date__ ="$8/12/2009 01:10:52 AM$"

import superficie
from PyQt4 import QtGui
from superficie.base import Chapter, Page
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

        self.assertEqual(2, len(self.chapter.pages))
        self.assertEqual(2, len(self.chapter.pagesObjects))
        self.assertEqual(2, self.chapter.widget.pageStack.count())
        self.assertEqual(1, self.chapter.widget.pageStack.currentIndex())

    def testWhichPage(self):
        print "testWhichPage"
        self.chapter.addPage(Page())
        self.chapter.addPage(Page())

        self.assertEqual(1,self.chapter.whichPage)

        self.chapter.whichPage = 0
        self.assertEqual(0,self.chapter.whichPage)

    def testChangePage(self):
        self.chapter.addPage(Page())
        self.chapter.addPage(Page())

        self.chapter.nextPage()
        self.assertEqual(0,self.chapter.whichPage)
        self.chapter.prevPage()
        self.assertEqual(1,self.chapter.whichPage)

if __name__ == '__main__':
    unittest.main()
