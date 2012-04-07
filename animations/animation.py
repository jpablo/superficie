# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from superficie.util import connect
from superficie.util import tuplize

#Animation(setNumVertices,(2000,0,npuntos))
from one_shot import OneShot

class Animation(OneShot):
    def __init__(self,func,(duration, nmin, nmax), times = 1):
        self.functions = [func]
        super(Animation,self).__init__(duration / 1000.0, times)
#        self.setCurveShape(self.LinearCurve)
        self.setFrameRange(nmin, nmax)
        connect(self, "frameChanged(int)", self.functions[-1])
#        connect(self, "ramp(float)", self.functions[-1])
        ## ======================================
        ## This is used for the static method "chain"
        ## it is the pause between animations
        self.pauseTimer = QtCore.QTimer()
        self.pauseTimer.setSingleShot(True)
        self.__anim_queue = []

    @staticmethod
    def chain(animations, pause=100):
        '''
        Runs all animations one after another
        @param animations:
        @param pause:
        '''
        for i in range(len(animations)-1):
            animations[i].pauseTimer.setInterval(pause)
            connect(animations[i],"finished()",animations[i].pauseTimer.start)
            connect(animations[i].pauseTimer,"timeout()",animations[i+1].start)

    def addFunction(self,func):
        self.functions.append(func)
        connect(self, "frameChanged(int)", self.functions[-1])

    def afterThis(self, other):
        '''
        @param other: Animation
        '''
        self.__anim_queue.append(other)
        Animation.chain([self,other])
        return other

    def onFinished(self):
        '''
        Executes func when this animation is finished
        @param func:
        '''
        return self

    def onStart(self, func):
        "Executes func at the same time that this animation"
        for f in tuplize(func):
            connect(self, "started()", f)
        return self

    def wait(self, miliseconds):
        return self.afterThis(Animation(lambda x:None, (miliseconds,0,1)))

    def execute(self, func):
        return self.afterThis(Animation(lambda x:func(),(1,0,1)))

    def resetObjectForAnimation(self):
        self.stop()
        for fn in self.functions:
            fn(self.startFrame)

    def setDuration(self,msecs):
        self.oneshot.duration = msecs / 1000.0


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
