import PyQt4.QtGui
from superficie.util import connect

__author__ = 'jpablo'

class SpinBox(QtGui.QSpinBox):
    def __init__(self, text,iter,func,parent=None):
        QtGui.QSpinBox.__init__(self)
        (vmin, vmax, vini) = iter
        self.setMinimum(vmin)
        self.setMaximum(vmax)
        self.setValue(vini)
        self.func = func
        connect(self,"valueChanged(int)", lambda x: func(x))

        layout  =  QtGui.QHBoxLayout()
        lab = QtGui.QLabel(text)
        layout.addWidget(lab)
        layout.addWidget(self)

        if parent:
            parent.addLayout(layout)