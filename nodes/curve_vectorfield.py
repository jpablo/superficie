from superficie.Animation import Animation
from util import Vec3, vsum

__author__ = 'jpablo'

class CurveVectorField(Arrow):
    """
    Holds data needed to draw an arrow along a vector field
    """
    def __init__(self, function, domain_points, base_arrow_points):
        super(CurveVectorField, self).__init__(Vec3(0,0,0), Vec3(0,0,0))
        self.function = function
        self.domain_points = None
        self.base_arrow_points = None
        # self.end_points are calculated by appliying function to domain_points
        self.end_points = None
        self.animation = None
        self.last_i = 0
        self.updatePoints(domain_points, base_arrow_points)
        self.setDiffuseColor((1, 0, 0))
        self.animation = Animation(self.animateArrow, (8000, 0, len(self.base_arrow_points) - 1))

    def animateArrow(self, i):
        self.setPoints(self.base_arrow_points[i], self.end_points[i])
        self.last_i = i

    def updatePoints(self, domain_points, base_arrow_points):
        self.domain_points = domain_points
        self.base_arrow_points = base_arrow_points
        self.end_points = vsum(self.base_arrow_points, map(self.function, self.domain_points))
        self.animateArrow(self.last_i)


