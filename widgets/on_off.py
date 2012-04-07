import PyQt4.QtGui
from superficie.util import wrap, connectPartial
from widgets.gui import setWhichChildCB

__author__ = 'jpablo'

def onOff(ob, text="", show=True):
    switch = wrap(ob, show)
    box = QtGui.QCheckBox(text)
    box.setChecked(show)
    connectPartial(box,"stateChanged(int)", setWhichChildCB, switch)
    return box, switch