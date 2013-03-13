import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.uic
from superficie.Animation0 import AnimeType, Timer
from superficie.util import identity, filePath, conecta, partial

__author__ = 'jpablo'

class Slider2(QtGui.QWidget):
    def __init__(self, iter=('w', 0, 1, 101), tini=0,  func=identity,  preF = None,  postF = None,  tipoAnim = AnimeType.unavez, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(filePath("Gui","paramTemplate.ui"), self)
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