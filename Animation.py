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
        self.pauseTimer = QtCore.QTimer()
        self.pauseTimer.setSingleShot(True)

    @staticmethod
    def chain(animations, pause=100):
        for i in range(len(animations)-1):
            animations[i].pauseTimer.setInterval(pause)
            connect(animations[i],"finished()",animations[i].pauseTimer.start)
            connect(animations[i].pauseTimer,"timeout()",animations[i+1].start)
