import sys
from pivy.coin import *
from pivy.gui.soqt import *
from PyQt4 import QtCore, QtGui, uic
from superficie.util import conectaParcial, wrap, conecta, identity, partial, pjoin, segment
from superficie.animation import AnimeType, Timer

modulosPath = "superficie"

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
    def __init__(self, range=('w', 0, 1, 101, 0), func=identity, time=1000, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(pjoin(modulosPath,"Gui","paramTemplate.ui"), self)
        self.name = range[0]
        self.func = func
        ## ============================
        self.range = range[1:]
        self.vmin, self.vmax, self.npoints, self.vini = self.range
        ## valueChanged(qreal) always is in the range 0 <= x <= 1
        ## whereas func not necesarily
        self.funcTrans = partial(segment, self.vmin, self.vmax)
        self.timeline = QtCore.QTimeLine(time)
        self.timeline.setFrameRange(0, self.npoints-1)
        curTime = float(self.vini) /(self.vmax - self.vmin) * time
        self.timeline.setCurrentTime(curTime)
        ## ============================
        conecta(self.timeline, QtCore.SIGNAL("valueChanged(qreal)"), lambda t: self.func(self.funcTrans(t)))
        conecta(self.timeline, QtCore.SIGNAL("valueChanged(qreal)"), lambda t: self.updateLabel(self.funcTrans(t)))
        conecta(self.timeline, QtCore.SIGNAL("frameChanged(int)"), self.slider.setValue)
        ## ============================
        self.setupUi()
        
    def setupUi(self,):
        self.nombre.setTitle(self.name + ": %.3f" % self.vini)
        self.slider.setMaximum(self.npoints-1)
        self.slider.setValue(self.timeline.currentFrame())
        conecta(self.slider, QtCore.SIGNAL("valueChanged(int)"), self.updateFromSlider)
        self._d = []
        for f, i in zip([self.atras, self.pausa, self.adelante], [-1, 0, 1]):
            self._d.append(partial(self.estadoAnimacion,i))
            conecta(f, QtCore.SIGNAL("clicked()"), self._d[-1])
            
    def estadoAnimacion(self,dir):
        tl = self.timeline
        if dir == 0:
            if tl.state() == tl.Running:
                tl.setPaused(True)
        elif dir == 1 and tl.currentValue() < 1.0:
            tl.setDirection(tl.Forward)
            tl.resume()
        elif dir == -1 and tl.currentValue() > 0.0:
            tl.setDirection(tl.Backward)
            tl.resume()

    def updateFromSlider(self,n):
        if self.timeline.state() == self.timeline.Running:
            return
        prop = float(n) / (self.npoints-1)
        curTime = prop * self.timeline.duration()
        ## ============================
        self.timeline.blockSignals(True)
        self.timeline.setCurrentTime(curTime)
        self.func(self.funcTrans(prop))
        self.updateLabel(self.funcTrans(prop))
        self.timeline.blockSignals(False)
        ## probably this triggers the signals

    def updateLabel(self, t):
        self.nombre.setTitle(self.name + ": %.3f" % t)

        
        
class Slider2(QtGui.QWidget):
    def __init__(self, iter=('w', 0, 1, 101), tini=0,  func=identity,  preF = None,  postF = None,  tipoAnim = AnimeType.unavez, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(pjoin(modulosPath,"Gui","paramTemplate.ui"), self)
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

