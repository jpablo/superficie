from BaseObject import BaseObject
from nodes.baseplane import BasePlane
from nodes.line import Line
from nodes.sphere import Sphere
from util import Vec3

__author__ = 'jpablo'

class TangentPlane2(BaseObject):
    def __init__(self, param, par1, par2, (xorig,yorig), color):
        super(TangentPlane2,self).__init__()
        self.par1 = par1
        self.par2 = par2
        self.param = param
        self.localOrigin = (xorig,yorig)
        self.r0 = (-1, 1, 30)

        self.baseplane = BasePlane()
        self.baseplane.setTransparency(.4).setDiffuseColor(color).setEmissiveColor(color)
        self.addChild(self.baseplane)
        self.localOriginSphere = Sphere(param(*self.localOrigin), radius=.03, color=(1,0,0))
        self.addChild(self.localOriginSphere)

        self.localXAxis = Line([], color=(1,0,0))
        self.localYAxis = Line([], color=(1,0,0))
        self.addChild(self.localXAxis)
        self.addChild(self.localYAxis)
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
        self.localXAxis.setPoints([self.planeParam(*pt) for pt in [(self.r0[0],0),(self.r0[1],0)]])
        self.localYAxis.setPoints([self.planeParam(*pt) for pt in [(0,self.r0[0]),(0,self.r0[1])]])

    def setU(self, val):
        self.setLocalOrigin((val, self.localOrigin[1]))

    def setV(self, val):
        self.setLocalOrigin((self.localOrigin[0], val))

    def setRange(self, r0):
        self.r0 = r0
        self.baseplane.setRange(self.r0)