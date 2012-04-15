from superficie.animations.animation import Animation
from superficie.util import Vec3, vsum
from arrow import Arrow

class CurveVectorField(Arrow):
    """
    Holds the data needed to draw an arrow along a vector field
    Suppose you have functions f, f': R -> R^3
    If you want to use an arrow for representing f', this arrow should start in f(t)
    and end in f(t) + f'(t).

    Now, suppose you have already pre-calculated all the points
        { p_i = f(t_i) }

    then the tip of the arrow for each point t_i is at
        p_i + f'(t_i)

    Thus, the vector field referred in the name is:
        V: p -> p + f'(t)

    The arguments of the constructor are:
    function: f'
    base_arrow_points: { p_i }
    domain_points: { t_i }
    """
    def __init__(self, function, domain_points, base_arrow_points):
        super(CurveVectorField, self).__init__(Vec3(0,0,0), Vec3(0,0,0))
        self.function = function
        self.domain_points = None
        self.base_arrow_points = None
        self.end_points = None
        self.animation = None
        self.last_i = 0
        self.updatePoints(domain_points, base_arrow_points)
        self.setDiffuseColor((1, 0, 0))
        self.animation = Animation(self.animateArrow, (8000, 0, len(self.base_arrow_points) - 1))

    def animateArrow(self, i):
        print i
        self.setPoints(self.base_arrow_points[i], self.end_points[i])
        self.last_i = i

    def updatePoints(self, domain_points, base_arrow_points):
        self.domain_points = domain_points
        self.base_arrow_points = base_arrow_points
        self.end_points = vsum(self.base_arrow_points, map(self.function, self.domain_points))
        self.animateArrow(self.last_i)


