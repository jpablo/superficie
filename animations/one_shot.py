from PyQt4 import QtCore
from pivy.coin import SoOneShot, SoSFFloat, SoFieldSensor
from superficie.util import connect

__author__ = 'jpablo'

class OneShot(QtCore.QObject):
    def __init__(self, duration, times):
        QtCore.QObject.__init__(self)
        self.times = self.timesleft = times
        self.oneshot = SoOneShot()
        self.oneshot.duration = duration
        self.oneshot.flags = SoOneShot.HOLD_FINAL
        ## necesitamos un SoField para poder extraer el
        ## valor con getValue()
        ## can't this value be obtained directly from a SoEngineOutput?
        self.value = SoSFFloat()
        self.value.connectFrom(self.oneshot.ramp)
        self.sensor = SoFieldSensor(self.callback, self.value)
        self.sensor.attach(self.value)
        connect(self, "finished()", self.cycle)

    def callback(self, ffloat, sensor):
        t = ffloat.getValue()
#        QtCore.QObject.emit(self, QtCore.SIGNAL("ramp(float)"), t)
        ## 0 <= t <= 1
        ## nmin <= nmin + (nmax-nmin) * t <= nmax
        i = int(self.startFrame + self.spanFrame * t)
        QtCore.QObject.emit(self, QtCore.SIGNAL("frameChanged(int)"), i)
        if t == 0.0:
            self.emit(QtCore.SIGNAL("started()"))
        elif t == 1.0:
            self.emit(QtCore.SIGNAL("finished()"))

    def start(self):
        self.oneshot.trigger.touch()

    def stop(self):
        #self.oneshot.disable = True
        self.timesleft = self.times

    def setFrameRange(self, nmin, nmax):
        self.startFrame = nmin
        self.endFrame = nmax
        self.spanFrame = nmax - nmin

    def cycle(self):
        self.timesleft -= 1
        if self.timesleft > 0:
            self.start()