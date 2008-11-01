# -*- coding: utf-8 -*-

from pivy.coin import SoOneShot, SoSFFloat
from PyQt4 import QtCore
from superficie.util import conecta, GenIntervalo



class AnimeType:
    unavez, vaiven, continuo = range(3)

class Timer(QtCore.QTimer):
    "evalua automaticamente una funcion en los puntos del intervalo dado"
    def __init__(self, iter,  func,  tipo = 't',  preF = None,  postF = None,  tipoAnim = AnimeType.unavez,  parent=None):
        ## iter = (min,max,n)
        ## tipo = 't' | 'n'
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
        except StopIteration, dir:
            self.stop()
            self.emit(QtCore.SIGNAL("finished()"))

    def reset(self):
        self.intervalo = GenIntervalo(self.iter,self. func, self.tipo)
    
    def restart(self, msec):
        self.reset()
        self.start(msec)



class OneShot(QtCore.QObject):
    def __init__(self, duration):
        QtCore.QObject.__init__(self)
        self.oneshot = SoOneShot()
        self.oneshot.duration = duration
        self.oneshot.flags = SoOneShot.HOLD_FINAL
        ## necesitamos un SoField para poder extraer el
        ## valor con getValue()
        ## ¿se puede obtener directamente el valor de un SoEngineOutput?
        self.value = SoSFFloat()
        self.value.connectFrom(self.oneshot.ramp)
        self.sensor = SoFieldSensor(self.callback, self.value)
        self.sensor.attach(self.value)
    def callback(self, ffloat, sensor):
        t = ffloat.getValue()
        QtCore.QObject.emit(self, QtCore.SIGNAL("ramp(float)"), t)
        if t == 1.0:
            self.emit(QtCore.SIGNAL("finished(bool)"), True)
    def start(self):
        self.oneshot.trigger.touch()


