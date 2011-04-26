# -*- coding: utf-8 -*-
from pivy.coin import SoWriteAction, SoSwitch, SoSeparator, SoTranslation, SoMaterial, SoTransparencyType, SoDrawStyle, SoSFPlane, SbPlane, SoClipPlane, SO_SWITCH_ALL, SO_SWITCH_NONE

__author__ = "jpablo"
__date__ = "$18/05/2009 12:47:43 AM$"


def fluid(method):
    def func(self, *args, **kwargs):
        method(self,*args, **kwargs)
        return self
    return func

class BaseObject(object):
    'Common functionality for all graphic objects'

    def __init__(self, name=''):
        self.animation  = None
        self.switch     = SoSwitch()
        self.root       = SoSeparator()
        self.drawStyle  = SoDrawStyle()
        self.translation = SoTranslation()

        self.switch.setName(name)
        self.translation.translation = (0, 0, 0)

        self.switch.addChild(self.root)
        self.root.addChild(self.drawStyle)
        self.root.addChild(self.translation)

    @fluid
    def show(self):
        self.setVisible(True)

    @fluid
    def hide(self):
        self.setVisible(False)

    @fluid
    def setBoundingBox(self, xrange=None, yrange=None, zrange=None):
        '''
        @param xrange: 2-tuple
        @param yrange: 2-tuple
        @param zrange: 2-tuple
        '''
        def createPlane(normalref, point):
            sfplane = SoSFPlane()
            sfplane.setValue(SbPlane(normalref, point))
            return sfplane

        if yrange is not None:
            self.clipPlaneXZ1 = SoClipPlane()
            self.clipPlaneXZ2 = SoClipPlane()
            self.clipPlaneXZ1.plane = createPlane(SbVec3f(0, 1, 0), SbVec3f(0, yrange[0], 0))
            self.clipPlaneXZ2.plane = createPlane(SbVec3f(0, -1, 0), SbVec3f(0, yrange[1], 0))
            self.root.insertChild(self.clipPlaneXZ1, 0)
            self.root.insertChild(self.clipPlaneXZ2, 1)
        if xrange is not None:
            self.clipPlaneYZ1 = SoClipPlane()
            self.clipPlaneYZ2 = SoClipPlane()
            self.clipPlaneYZ1.plane = createPlane(SbVec3f(1, 0, 0), SbVec3f(xrange[0], 0, 0))
            self.clipPlaneYZ2.plane = createPlane(SbVec3f(-1, 0, 0), SbVec3f(xrange[1], 0, 0))
            self.root.insertChild(self.clipPlaneYZ1, 2)
            self.root.insertChild(self.clipPlaneYZ2, 3)
        if zrange is not None:
            self.clipPlaneXY1 = SoClipPlane()
            self.clipPlaneXY2 = SoClipPlane()
            self.clipPlaneXY1.plane = createPlane(SbVec3f(0, 0, 1), SbVec3f(0, 0, zrange[0]))
            self.clipPlaneXY2.plane = createPlane(SbVec3f(0, 0, -1), SbVec3f(0, 0, zrange[1]))
            self.root.insertChild(self.clipPlaneXY1, 4)
            self.root.insertChild(self.clipPlaneXY2, 5)

    @fluid
    def setDrawStyle(self, style):
        self.drawStyle.style = style

    @fluid
    def setVisible(self, visible):
        if visible:
            self.switch.whichChild = SO_SWITCH_ALL
        else:
            self.switch.whichChild = SO_SWITCH_NONE

    def getVisible(self):
        if self.switch.whichChild.getValue() == SO_SWITCH_ALL:
            return True
        elif self.switch.whichChild.getValue() == SO_SWITCH_NONE:
            return False

    visible = property(fget=getVisible, fset=setVisible)

    @fluid
    def setOrigin(self, pos):
        ''
        self.translation.translation = pos

    def getOrigin(self):
        return self.translation.translation.getValue()

    origin = property(fget=getOrigin, fset=setOrigin)

    def getAnimation(self):
        return self.animation

    def resetObjectForAnimation(self):
        pass



    def toText(self):
        'obtains the openinventor format representation'
        wa = SoWriteAction()
        return wa.apply(self.switch)




class MaterialMixin(object):
    'Material related functions'

    def __init__(self):
        self.material   = SoMaterial()
        self.transparencyType = SoTransparencyType()

        ## self.root is assumed here!
        self.root.addChild(self.material)
        self.root.addChild(self.transparencyType)


    @fluid
    def setTransparency(self, val):
        self.material.transparency.setValue(val)

    def getTransparency(self):
        return self.material.transparency.getValues()

    transparency = property(fset=setTransparency, fget=getTransparency)

    @fluid
    def setEmissiveColor(self, val):
        self.material.emissiveColor.setValue(val)

    emissiveColor = property(fset=setEmissiveColor)

    @fluid
    def setDiffuseColor(self, val):
        self.material.diffuseColor.setValue(val)

    def getDiffuseColor(self):
        return self.material.diffuseColor
    
    diffuseColor = property(getDiffuseColor,setDiffuseColor)

    @fluid
    def setAmbientColor(self, val):
        self.material.ambientColor.setValue(val)

    @fluid
    def setSpecularColor(self, val):
        self.material.specularColor.setValue(val)

    @fluid
    def setShininess(self, val):
        self.material.shininess = val

    @fluid
    def setTransparencyType(self, trans):
        self.transparencyType.value = trans

    @fluid
    def setColor(self, val):
        'set diffuse, emissive, ambient and specular properties at once'
        self.setDiffuseColor(val)
        self.setEmissiveColor(val)
        self.setAmbientColor(val)
        self.setSpecularColor(val)

    color = property(fset=setColor)


class GraphicObject(BaseObject, MaterialMixin):
    'The base object + material managment'

    def __init__(self, name=''):
        super(GraphicObject, self).__init__(name)
        MaterialMixin.__init__(self)


if __name__ == "__main__":
    ob = GraphicObject("objeto")
    ob.show()
    print ob.toText()
