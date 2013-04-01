

class Planes(BaseObject):
    def __init__(self, visible=False, parent=None):
        BaseObject.__init__(self, visible, parent)
        self.addChild(Plane(0))
        self.addChild(Plane(1))
        self.addChild(Plane(2))



