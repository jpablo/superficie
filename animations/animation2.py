import PyQt4.QtCore
from superficie.util import connect
from animations.Animation import Animation

__author__ = 'jpablo'

class Animation2(QtCore.QTimeLine):
    def __init__(self,func,(duration, nmin, nmax)):
        self.functions = [func]
        ## TODO: buscar un sinonimo en ingles de "range"
        #QtCore.QTimeLine.__init__(self,duration)
        super(Animation,self).__init__(duration)
        self.setCurveShape(self.LinearCurve)
        self.setFrameRange(nmin, nmax)
        connect(self, "frameChanged(int)", self.functions[-1])
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
        connect(self, "stateChanged(QTimeLine::State)", lambda state: func() if state == 2 else None)
        return self

    def wait(self, miliseconds):
        return self.afterThis(Animation(lambda x:None, (miliseconds,0,1)))

    def execute(self, func):
        return self.afterThis(Animation(lambda x:func(),(1,0,1)))

    def resetObjectForAnimation(self):
        self.stop()
        for fn in self.functions:
            fn(self.startFrame())