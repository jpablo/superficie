# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore, uic
#from functools import partial
from util import partial
from util import Segmento, GenIntervalo,   conecta,  main,  identity

modulosPath = "modulos/"

class Animacion:
    unavez, vaiven, continuo = range(3)

class Motor(QtCore.QTimer):
    "evalua automaticamente una funcion en los puntos del intervalo dado"
    def __init__(self, iter,  func,  tipo = 't',  preF = None,  postF = None,  tipoAnim = Animacion.unavez,  parent=None):
        ## iter = (min,max,n)
        QtCore.QTimer.__init__(self, parent)
        if preF: preF()
        self.func = func
        self.iter = iter
        self.tipo = tipo
        self.reset()
        conecta(self, QtCore.SIGNAL("timeout()"), self.actualiza)
        if postF:
            conecta(self, QtCore.SIGNAL("finished()"), postF)

    def actualiza(self):
        try:
            self.intervalo.next()
        except StopIteration,  dir:
#            print "StopIteration",  dir
            self.stop()
            self.emit(QtCore.SIGNAL("finished()"))

    def reset(self):
        self.intervalo = GenIntervalo(self.iter,self. func, self.tipo)




class Parametro2(QtGui.QWidget):
    def __init__(self, iter=('w', 0, 1, 101), tini=0,  func=identity,  preF = None,  postF = None,  tipoAnim = Animacion.unavez, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi(modulosPath+ "paramTemplate.ui", self)
        self.name = iter[0]
        self.motor = Motor( iter[1:], self.updateFromMotor, tipo = 'n',  preF=preF,  postF=postF, tipoAnim=tipoAnim, parent=parent)
        ## ============================
        ## copiamos algunas variables de Motor (PyQt4 no soporta herencia multiple de bases de Qt4)
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

if __name__ == "__main__":
    modulosPath = "./"
    from pivy.gui.soqt import SoQt
    def px(x): print x
    app = main()
    p = Parametro2( ("x", -1, 1,11), tini=-1,  func=px)
    p.show()
    SoQt.mainLoop()
