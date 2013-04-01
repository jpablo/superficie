from pivy.coin import SoSphere
from superficie.base import MaterialNode


class Sphere(MaterialNode):
    """A sphere"""

    def __init__(self, center, radius=.05, color=(1, 1, 1)):
        super(Sphere,self).__init__()
        self.sp = SoSphere()
        self.sp.radius = radius
#        ## ===================
        self.separator.addChild(self.sp)
        self.origin = center
        self.color = color

    def getRadius(self):
        return self.sp.radius.getValue()

    def setRadius(self, radius):
        self.sp.radius = radius

    radius = property(getRadius, setRadius)