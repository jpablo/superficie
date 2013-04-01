from nodes.pointset import Points


class Point(Points):
    def __init__(self, coords, color=(1, 1, 1)):
        ## coords is a triple (x,y,z)
        Points.__init__(self, [coords], [color])

