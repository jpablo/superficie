from exceptions import StopIteration
import PyQt4.QtCore
from superficie.util import connect
from util import GenIntervalo


class Timer(QtCore.QTimer):
    "evalua automaticamente una funcion en los puntos del intervalo dado"
    def __init__(self,func,rango):
        QtCore.QTimer.__init__(self, None)
        self.func = func
        self.rango = rango
        self.reset()
        connect(self, "timeout()", self.update)

    def update(self):
        try:
            self.intervalo.next()
        except StopIteration, dir:
            self.stop()
            self.emit(QtCore.SIGNAL("finished()"))

    def reset(self):
        self.intervalo = GenIntervalo(self.rango,self. func)

    def restart(self, msec):
        self.reset()
        self.start(msec)