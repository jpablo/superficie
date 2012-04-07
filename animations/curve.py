from animations.Animation import Animation

__author__ = 'jpablo'

class AnimationCurve(Animation):
    def __init__(self,func,curve,duration):
        self.curve = curve
        self.func = func
        Animation.__init__(self,self.eachFrame,(duration,0,len(curve)-1))

    def eachFrame(self,i):
        self.func(i,self.curve[i])