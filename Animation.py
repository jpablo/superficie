# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from superficie.util import connect

#Animation(setNumVertices,(2000,0,npuntos))

class Animation(QtCore.QTimeLine):
    def __init__(self,func,rango):
        duration, nmin, nmax = rango
        self.functions = [func]
        ## TODO: buscar un sinonimo en ingles de "range"
        QtCore.QTimeLine.__init__(self,duration)
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


class Animatable(object):
    '''
    Minimal stuff needed to animate an object
    '''
    def __init__(self,func,rango):
        self.func = func
        self.animation = Animation(self.func, rango)

    def getAnimation(self):
        return self.animation
    
    def resetObjectForAnimation(self):
        pass    



class AnimationGroup(object):
    '''
    Runs several animations in parallel
    '''
    # TODO: this could be the basis for an "animatable" interface like object
    def __init__(self,objects,rango):
        self.objects = objects
        self.animation = Animation(self.eachFrame, rango)

    def getAnimation(self):
        return self.animation
    
    def eachFrame(self,n):
        for ob in self.objects:
            ob.animation.function(n)

    def resetObjectForAnimation(self):
        for ob in self.objects:
            ob.resetObjectForAnimation()

        
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
