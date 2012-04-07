from pivy.coin import SoCoordinate3, SoQuadMesh, SoNormalBinding, SoShapeHints, SoScale, SoSeparator
from superficie.Animation import Animation
from BaseObject import GraphicObject
from nodes.line import Line

__author__ = 'jpablo'

class Bundle3(GraphicObject):
    def __init__(self, curve, cp, factor=1):
        """curve is something derived from Line"""
        super(Bundle3,self).__init__()
        self.curve = curve
        self.cp = cp
        self.factor = factor
        self.line = Line(())
        ## ============================
        self.coords = SoCoordinate3()
        self.mesh = SoQuadMesh()
        self.mesh.verticesPerColumn = len(curve)
        self.mesh.verticesPerRow = 2
        nb = SoNormalBinding()
#        nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        sHints = SoShapeHints()
        sHints.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE

        self.generateArrows()
        ## ============================
        self.scale = SoScale()
        ## ============================
        sep = SoSeparator()
        sep.addChild(nb)
        sep.addChild(sHints)
        sep.addChild(self.scale)
        sep.addChild(self.coords)
        sep.addChild(self.mesh)
#        self.addChild(self.line)
        self.addChild(sep)

        self.animation = Animation(lambda num: float(num) / len(curve) * self.material.transparency.getValue(), (4000, 1, len(curve)))

    def __len__(self):
        """the same lengh as the base curve"""
        return len(self.curve)

    def setFactor(self, factor):
        """
        Set multiplicative factor for arrow length
        @param factor:
        """
        self.factor = factor
        self.generateArrows()

    def generateArrows(self):
        """
        create the arrows
        """
        points = self.curve.getCoordinates()
        #pointsp = [self.curve[i]+self.cp(t)*self.factor for i,t in enumerate(intervalPartition(self.curve.iter))]
        pointsp = [self.curve[i] + self.cp(t) * self.factor for i, t in enumerate(self.curve.domainPoints)]
        pointsRow = zip(map(tuple, points), map(tuple, pointsp))

        pointsRowFlatten = []
        vertexIndexes = []
        for p, pp in pointsRow:
            ## TODO: triangular!!
            pointsRowFlatten.append(p)
            pointsRowFlatten.append(pp)
            vertexIndexes.append(2)
        ## ============================
        self.line.points = pointsRowFlatten
        self.line.numVerticesPerSegment = vertexIndexes
        self.coords.point.setValues(0, len(pointsRowFlatten), pointsRowFlatten)


    def setNumVisibleArrows(self, num):
        """set the number of arrow to show"""
        self.mesh.verticesPerColumn = num