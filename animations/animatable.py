from animations.Animation import Animation

__author__ = 'jpablo'

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