from pivy.coin import SoCoordinate3
from .material_node import MaterialNode


class GeometryNode(MaterialNode):
    """The base object + material managment"""

    def __init__(self):
        super(GeometryNode, self).__init__()
        self.coordinates = SoCoordinate3()
        self.separator.addChild(self.coordinates)