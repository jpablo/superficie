from superficie.base import BaseObject

class TangentPlane(BaseObject):
    """Represents the tangent plane around a given point """

    def __init__(self, param, par1, par2, pt, color):
        BaseObject.__init__(self)
        ve = par1(pt[0])
        ve.normalize()
        ue = par2(pt[1])
        ue.normalize()

        def planePar(h, t):
            return tuple(Vec3(param(*pt)) + h * ve + t * ue)

        baseplane = BasePlane()
        baseplane.setRange((-.5, .5, 30), plane=planePar)
        baseplane.setTransparency(0)
        baseplane.setDiffuseColor(color)
        baseplane.setEmissiveColor(color)
        self.addChild(baseplane)
