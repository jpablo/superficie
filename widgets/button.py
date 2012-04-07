from PyQt4 import QtGui
from superficie.util import connect

class Button(QtGui.QPushButton):
    def __init__(self,text,func,parent=None):
        QtGui.QPushButton.__init__(self,text)
        self.func = func
        connect(self,"clicked(bool)", lambda x: func())
        if parent:
            parent.addWidget(self)