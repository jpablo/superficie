from PyQt4 import QtGui
from superficie.util import connect


class CheckBox(QtGui.QCheckBox):
    def __init__(self, funcOn, funcOff, text="", state=False):
        QtGui.QCheckBox.__init__(self,text)
        self.setChecked(state)
        def checkBoxCB(n):
            if n == 2:
                funcOn()
            elif n == 0:
                funcOff()
        connect(self, "stateChanged(int)", checkBoxCB)