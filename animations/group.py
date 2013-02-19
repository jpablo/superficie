from animation import Animation


class AnimationGroup(object):
    """
    Runs several animations in parallel
    """
    # TODO: this could be the basis for an "animatable" interface like object
    def __init__(self, objects, config, times=1):
        self.objects = objects
        self.animation = Animation(self.eachFrame, config, times)

    def getAnimation(self):
        return self.animation

    def eachFrame(self, n):
        for ob in self.objects:
            for fn in ob.animation.functions:
                fn(n)

    def resetObjectForAnimation(self):
        for ob in self.objects:
            ob.resetObjectForAnimation()