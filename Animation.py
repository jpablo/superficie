# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from superficie.util import connect

#Animation(setNumVertices,(2000,0,npuntos))

class Animation(QtCore.QTimeLine):
    def __init__(self,func,rango):
        duration, nmin, nmax = rango
        ## TODO: buscar un sinonimo en ingles de "range"
        QtCore.QTimeLine.__init__(self,duration)
        self.setCurveShape(self.LinearCurve)
        self.setFrameRange(nmin, nmax)
        connect(self, "frameChanged(int)", func)
        ## ======================================
        ## This is used for the static method "chain"
        ## it is the pause between animations
        self.pauseTimer = QtCore.QTimer()
        self.pauseTimer.setSingleShot(True)

    @staticmethod
    def chain(animations, pause=100):
        for i in range(len(animations)-1):
            animations[i].pauseTimer.setInterval(pause)
            connect(animations[i],"finished()",animations[i].pauseTimer.start)
            connect(animations[i].pauseTimer,"timeout()",animations[i+1].start)


class AnimationCurve(Animation):
    def __init__(self,func,curve,duration):
        self.curve = curve
        self.func = func
        Animation.__init__(self,self.eachFrame,(duration,0,len(curve)-1))

    def eachFrame(self,i):
        self.func(i,self.curve[i])


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

if __name__ == "__main__":
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    tl = QtCore.QTimeLine(1000)
    tl.setFrameRange(1,1000)
    def fn(n): print n
    QtCore.QObject.connect(tl,QtCore.SIGNAL("frameChanged(int)"), fn)
    b = QtGui.QPushButton("correr")
    b.show()
    QtCore.QObject.connect(b,QtCore.SIGNAL("clicked(bool)"), tl.start)
    sys.exit(app.exec_())
