__author__ = 'jpablo'

class Bundle(BaseObject):
    def __init__(self, c, cp, partition, col, factor=1, name="", visible=False, parent=None):
        BaseObject.__init__(self, visible, parent)
        tmin, tmax, n = partition
        puntos = [c(t) for t in intervalPartition([tmin, tmax, n])]
        puntosp = [c(t) + cp(t) * factor for t in intervalPartition([tmin, tmax, n])]
        for p, pp in zip(puntos, puntosp):
            self.addChild(Arrow(p, pp, extremos=True, escalaVertice=3, visible=True))

        self.animation = Animation(lambda num: self[num - 1].show(), (4000, 1, n))

    def setMaterial(self, mat):
        for c in self.getChildren():
            c.material.ambientColor = mat.ambientColor
            c.material.diffuseColor = mat.diffuseColor
            c.material.specularColor = mat.specularColor
            c.material.shininess = mat.shininess

    def setHeadMaterial(self, mat):
        for c in self.getChildren():
            c.head_material.ambientColor = mat.ambientColor
            c.head_material.diffuseColor = mat.diffuseColor
            c.head_material.specularColor = mat.specularColor
            c.head_material.shininess = mat.shininess

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)

    def setLengthFactor(self, factor):
        for c in self.getChildren():
            if hasattr(c, "setLengthFactor"):
                c.setLengthFactor(factor)

    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()

