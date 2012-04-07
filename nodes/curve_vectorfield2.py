__author__ = 'jpablo'

class CurveVectorField2(BaseObject):
    '''
    Holds data needed to draw an arrow along a vector field
    '''
    def __init__(self, function, domain_points, base_arrow_points, visible=True, parent=None):
        BaseObject.__init__(self, visible, parent)
        self.function = function
        self.domain_points = None
        self.base_arrow_points = None
        self.end_points = None
        self.arrow = None
        self.animation = None
        self.last_i = 0
        self.arrow = Arrow(Vec3(0,0,0), Vec3(0,0,0), escala=0.1, escalaVertice=2, extremos=True, visible=True)
        self.updatePoints(domain_points, base_arrow_points)
        self.arrow.setDiffuseColor((1, 0, 0))
        self.arrow.cono.height = .5
        self.arrow.base.setDiffuseColor((1, 1, 0))
        self.addChild(self.arrow)
        self.animation = Animation(self.animate_field, (8000, 0, len(self.base_arrow_points) - 1))


    def animate_field(self, i):
        self.arrow.setPoints(self.base_arrow_points[i], self.base_arrow_points[i] + self.end_points[i])
        self.last_i = i


    @fluid
    def setLengthFactor(self, factor):
        self.arrow.setLengthFactor(factor)

    @fluid
    def setWidthFactor(self, factor):
        self.arrow.setWidthFactor(factor)

    def updatePoints(self, domain_points, base_arrow_points):
        self.domain_points = domain_points
        self.base_arrow_points = base_arrow_points
        self.end_points = map(self.function, self.domain_points)
        self.animate_field(self.last_i)



