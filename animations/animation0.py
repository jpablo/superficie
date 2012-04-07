# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from superficie.util import conecta, GenIntervalo

## This is probably obsoleted by QTimeLine

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



