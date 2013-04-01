from pivy.coin import SoComplexity
from Animation import Animation
from util import intervalPartition


class VectorField3D(GraphicObject):
    def __init__(self, curve, cp, col, factor=1, name="", visible = False, parent = None):
        """curve is something derived from Line"""
        GraphicObject.__init__(self,visible,parent)
        comp = SoComplexity()
        comp.value.setValue(.1)
        self.separator.addChild(comp)
        ## ============================
        points = curve.getPoints()
        pointsp = [curve[i]+cp(t)*factor for i,t in enumerate(intervalPartition(curve.iter))]
        for p,pp in zip(points,pointsp):
            self.addChild(Arrow(p,pp,visible=True,escala=.005,extremos=True))

        self.animation = Animation(lambda num: self[num-1].show(),(4000,1,len(points)))

    def setMaterial(self,mat):
        for c in self.getChildren():
            c.material.ambientColor  = mat.ambientColor
            c.material.diffuseColor  = mat.diffuseColor
            c.material.specularColor = mat.specularColor
            c.material.shininess     = mat.shininess

    def setHeadMaterial(self,mat):
        for c in self.getChildren():
            c.matHead.ambientColor  = mat.ambientColor
            c.matHead.diffuseColor  = mat.diffuseColor
            c.matHead.specularColor = mat.specularColor
            c.matHead.shininess     = mat.shininess

    def resetObjectForAnimation(self):
        self.hideAllArrows()

    def setRadius(self, r):
        for c in self.getChildren():
            c.setRadius(r)

    def setLengthFactor(self, factor):
        for c in filter(lambda c: isinstance(c,Arrow), self.getChildren()):
            c.setLengthFactor(factor)

    def hideAllArrows(self):
        for arrow in self.getChildren():
            arrow.hide()

    def setNumVisibleArrows(self, num):
        """set the number of arrow to show"""
        print "setNumVisibleArrows:", num