
from pivy.coin import SoWriteAction, SoSwitch, SoSeparator, SoTranslation, SoDrawStyle, SoSFPlane, SbPlane, SoClipPlane, SO_SWITCH_ALL, SO_SWITCH_NONE, SbVec3f
from ..utils import fluid


class BaseObject(object):
    """Common functionality for all graphic objects.
    It's just a wrapper around a SoSeparator
    
    It has this OI structure:
    Switch {
      Separator {
        DrawStyle {}
        Translation { translation 0 0 0 }
      }
    }

    Has methods for hide/show itself, and for translation
    """

    def __init__(self):
        self.animation  = None
        self.root       = SoSwitch()
        self.separator  = SoSeparator()
        self.drawStyle  = SoDrawStyle()
        self.translation = SoTranslation()

        self.root.addChild(self.separator)
        self.separator.addChild(self.drawStyle)
        self.separator.addChild(self.translation)

        self.translation.translation = (0, 0, 0)

        self.show()

    @fluid
    def setVisible(self, visible):
        if visible:
            self.root.whichChild = SO_SWITCH_ALL
        else:
            self.root.whichChild = SO_SWITCH_NONE

    def getVisible(self):
        if self.root.whichChild.getValue() == SO_SWITCH_ALL:
            return True
        elif self.root.whichChild.getValue() == SO_SWITCH_NONE:
            return False

    visible = property(fget=getVisible, fset=setVisible)

    @fluid
    def show(self):
        self.setVisible(True)

    @fluid
    def hide(self):
        self.setVisible(False)


    @fluid
    def setName(self,name):
        self.root.setName(name)

    @fluid
    def setBoundingBox(self, xrange=None, yrange=None, zrange=None):
        """
        @param xrange: 2-tuple
        @param yrange: 2-tuple
        @param zrange: 2-tuple
        """
        def createPlane(normalref, point):
            sfplane = SoSFPlane()
            sfplane.setValue(SbPlane(normalref, point))
            return sfplane

        if yrange is not None:
            self.clipPlaneXZ1 = SoClipPlane()
            self.clipPlaneXZ2 = SoClipPlane()
            self.clipPlaneXZ1.plane = createPlane(SbVec3f(0, 1, 0), SbVec3f(0, yrange[0], 0))
            self.clipPlaneXZ2.plane = createPlane(SbVec3f(0, -1, 0), SbVec3f(0, yrange[1], 0))
            self.separator.insertChild(self.clipPlaneXZ1, 0)
            self.separator.insertChild(self.clipPlaneXZ2, 1)
        if xrange is not None:
            self.clipPlaneYZ1 = SoClipPlane()
            self.clipPlaneYZ2 = SoClipPlane()
            self.clipPlaneYZ1.plane = createPlane(SbVec3f(1, 0, 0), SbVec3f(xrange[0], 0, 0))
            self.clipPlaneYZ2.plane = createPlane(SbVec3f(-1, 0, 0), SbVec3f(xrange[1], 0, 0))
            self.separator.insertChild(self.clipPlaneYZ1, 2)
            self.separator.insertChild(self.clipPlaneYZ2, 3)
        if zrange is not None:
            self.clipPlaneXY1 = SoClipPlane()
            self.clipPlaneXY2 = SoClipPlane()
            self.clipPlaneXY1.plane = createPlane(SbVec3f(0, 0, 1), SbVec3f(0, 0, zrange[0]))
            self.clipPlaneXY2.plane = createPlane(SbVec3f(0, 0, -1), SbVec3f(0, 0, zrange[1]))
            self.separator.insertChild(self.clipPlaneXY1, 4)
            self.separator.insertChild(self.clipPlaneXY2, 5)

    @fluid
    def setDrawStyle(self, style):
        self.drawStyle.style = style

    @fluid
    def setOrigin(self, pos):
        """"""
        self.translation.translation = pos

    def getOrigin(self):
        return self.translation.translation.getValue()

    origin = property(fget=getOrigin, fset=setOrigin)

    def getAnimation(self):
        return self.animation

    def resetObjectForAnimation(self):
        pass


    def toText(self):
        """obtains the openinventor format representation"""
        wa = SoWriteAction()
        return wa.apply(self.root)

    @classmethod
    def Create(cls, oi_object):
        bo = cls()
        bo.separator.addChild(oi_object)
        return bo


