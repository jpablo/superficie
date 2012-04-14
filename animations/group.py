from animation import Animation

__author__ = 'jpablo'

class AnimationGroup(object):
    """
    Runs several animations in parallel
    """
    # TODO: this could be the basis for an "animatable" interface like object
    def __init__(self,objects,range):
        self.objects = objects
        self.animation = Animation(self.eachFrame, range)

    def getAnimation(self):
        return self.animation

    def eachFrame(self,n):
        for ob in self.objects:
            for fn in ob.animation.functions:
                fn(n)

    def resetObjectForAnimation(self):
        for ob in self.objects:
            ob.resetObjectForAnimation()