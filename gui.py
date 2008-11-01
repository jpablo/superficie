import sys
from pivy.coin import *
from pivy.gui.soqt import *
from PyQt4 import QtCore, QtGui, uic
from superficie.util import conectaParcial, wrap, conecta, identity, partial
from superficie.animation import AnimeType, Timer

modulosPath = "superficie/"

def setWhichChildCB(switch, n):
    if n == 0:
        switch.whichChild = -1
    elif n == 2:
        switch.whichChild = 0


## I'm not sure about this one
## it's useful, but the interface...
def onOff(ob, text="", show=True):
    switch = wrap(ob, show)
    box = QtGui.QCheckBox(text)
    box.setChecked(show)
    conectaParcial(box,"stateChanged(int)", setWhichChildCB, switch)
    return box, switch


def CheckBox(parent, funcOn, funcOff, text="", state=False):
    box = QtGui.QCheckBox(text)
    box.setChecked(state)
    def checkBoxCB(n):
        if n == 2:
            funcOn()
        elif n == 0:
            funcOff()
    conecta(box,QtCore.SIGNAL("stateChanged(int)"), checkBoxCB)
    return box


class Slider(QtGui.QWidget):
    def __init__(self, iter=('w', 0, 1, 101), tini=0,  func=identity,  preF = None,  postF = None,  tipoAnim = AnimeType.unavez, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(modulosPath + "Gui/paramTemplate.ui", self)
        self.name = iter[0]
        self.motor = Timer( iter[1:], self.updateFromMotor, tipo = 'n',  preF=preF,  postF=postF, tipoAnim=tipoAnim, parent=parent)
        ## ============================
        ## copiamos algunas variables de Timer (PyQt4 no soporta herencia multiple de bases de Qt4)
        self.intervalo = self.motor.intervalo
        self.start = self.motor.start
        self.stop = self.motor.stop
        ## ============================
        self.direccion = 1
        self.tipoAnim = tipoAnim
        self.func = func
        self.intervalo.reset(t=tini)
        self.setupUi()
        
    def setValue(self, t):
        ## esta es la interfaz para poner el control en un valor arbitrario
        self.intervalo.reset(t=t)
        self.updateFromMotor(self.intervalo.n)

    def getValue(self):
        return self.intervalo.t

    def setupUi(self,):
        self.nombre.setTitle(self.name + ": %.3f" % self.intervalo.t)
        self.slider.setMaximum(self.intervalo.npoints-1)
        self.slider.setValue(self.intervalo.n)
        conecta(self.slider, QtCore.SIGNAL("valueChanged(int)"), self.updateFromSlider)
        self._d = []
        for f, i in zip([self.atras, self.pausa, self.adelante], [-1, 0, 1]):
            self._d.append(partial(self.estadoAnimacion,i))
            conecta(f, QtCore.SIGNAL("clicked()"), self._d[-1])
            
    def estadoAnimacion(self,dir):
        if dir == 0:
            self.stop()
        else:
            self.intervalo.direccion = dir
            self.start(50)

    def updateFromSlider(self,n):
        self.intervalo.reset(n=n)
        self.updateFunc(self.intervalo.t)

    def updateFromMotor(self,  n):
        if n == self.slider.value():
            self.updateFunc(self.intervalo.t)
        self.slider.setValue(n)

    def updateFunc(self, t):
        self.func(t)
        self.nombre.setTitle(self.name + ": %.3f" % t)
        self.emit(QtCore.SIGNAL("actualiza(float)"), t)
