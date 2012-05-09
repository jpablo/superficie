from pivy.coin import SoShapeHints, SoCoordinate3, SoQuadMesh, SoNormalBinding, SoMaterial, SoSeparator
from superficie.base.base_object import BaseObject

__author__ = 'jpablo'

class Plane(BaseObject):
    """
    """
    def __init__(self, pos, visible=True, parent=None):
        BaseObject.__init__(self)#, visible, parent)
        self.setVisible(visible)
        self.altura = -1
        vertices = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
        for p in vertices:
            p.insert(pos, self.altura)
        sh = SoShapeHints()
        sh.vertexOrdering = SoShapeHints.COUNTERCLOCKWISE
        sh.faceType = SoShapeHints.UNKNOWN_FACE_TYPE
        sh.shapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
        coords = SoCoordinate3()
        coords.point.setValues(0, len(vertices), vertices)
        mesh = SoQuadMesh()
        mesh.verticesPerColumn = 2
        mesh.verticesPerRow = 2
        nb = SoNormalBinding()
#            nb.value = SoNormalBinding.PER_VERTEX_INDEXED
        mat = SoMaterial()
        mat.transparency = 0.5
        #self.setTransparencyType(8)
        #self.separator.setTransparencyType(8)
        ## ============================
        root = SoSeparator()
        root.addChild(sh)
        root.addChild(mat)
        root.addChild(nb)
        root.addChild(coords)
        root.addChild(mesh)
        #self.addChild(root)
        self.separator.addChild(root)
