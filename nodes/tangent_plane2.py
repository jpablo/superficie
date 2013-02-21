from superficie.base import BaseObject
from superficie.util import Vec3
from superficie.nodes.base_plane import BasePlane
from superficie.nodes.line import Line
from superficie.nodes.sphere import Sphere

class TangentPlane2(BaseObject):
    def __init__(self, param, par1, par2, (x0, y0), color):
        """The tangent plane of a surface in space.

        The plane has its origin at the point param(x0,y0)

        @param param: function f: R^2 -> R^3
        @param par1: partial derivative of f wrt the 1st variable
        @param par2: partial derivative of f wrt the 2nd variable
        @param color: diffuse/emissive color of the plane
        """
        super(TangentPlane2, self).__init__()
        self.par1 = par1
        self.par2 = par2
        self.param = param
        self.localOrigin = (x0, y0)
        self.r0 = (-1, 1, 30)

        self.baseplane = BasePlane()
        self.baseplane.setTransparency(.4).setDiffuseColor(color).setEmissiveColor(color)
        self.separator.addChild(self.baseplane.root)
        self.localOriginSphere = Sphere(param(*self.localOrigin), radius=.03, color=(1, 0, 0))
        self.separator.addChild(self.localOriginSphere.root)

        self.localXAxis = Line([], color=(1, 0, 0))
        self.localYAxis = Line([], color=(1, 0, 0))
        self.separator.addChild(self.localXAxis.root)
        self.separator.addChild(self.localYAxis.root)
        ## ============================
        self.setLocalOrigin(self.localOrigin)

    def setLocalOrigin(self, pt):
        self.localOrigin = pt
        ve = self.par1(*pt)
        ve.normalize()
        ue = self.par2(*pt)
        ue.normalize()
        orig = Vec3(self.param(*pt))
        self.planeParam = lambda h, t: tuple(orig + h * ve + t * ue)
        self.baseplane.setRange(self.r0, plane=self.planeParam)
        self.localOriginSphere.setOrigin(orig)
        self.localXAxis.setPoints([self.planeParam(*pt) for pt in [(self.r0[0], 0), (self.r0[1], 0)]])
        self.localYAxis.setPoints([self.planeParam(*pt) for pt in [(0, self.r0[0]), (0, self.r0[1])]])

    def setU(self, val):
        self.setLocalOrigin((val, self.localOrigin[1]))

    def setV(self, val):
        self.setLocalOrigin((self.localOrigin[0], val))

    def setRange(self, r0):
        self.r0 = r0
        self.baseplane.setRange(self.r0)
        self.setLocalOrigin(self.localOrigin)