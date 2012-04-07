from pivy.coin import SoCoordinate3
from BaseObject import GraphicObject

__author__ = 'jpablo'

class Polygon(GraphicObject):
    def __init__(self, coords, name=""):
        super(Polygon, self).__init__()

        ## is a 2d point
        dim = len(coords[0])
        if  dim == 2:
            self.coords = [p + (0,) for p in coords]
        elif dim == 3:
            self.coords = coords
        ## just project to the first 3 coordinates
        elif dim > 3:
            self.coords = [(p[0], p[1], p[2]) for p in coords]
        ## ===============================
        coor = SoCoordinate3()
        coor.point.setValues(0, len(self.coords), self.coords)

        self.addChild(coor)


