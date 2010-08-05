# -*- coding: utf-8 -*-
__author__ = "jpablo"
__date__ = "$18/05/2009 12:47:43 AM$"

from PyQt4 import QtCore
from pivy.coin import *
from superficie.util import nodeDict


def fluid(method):
    def func(self, *args, **kwargs):
        method(self,*args, **kwargs)
        return self
    return func

class GraphicObject(SoSwitch):
    '''
    The base clase of all container graphics classes
    '''
    def __init__(self, visible=False, parent=None, viewer=None):
        SoSwitch.__init__(self)
        self.qobject = QtCore.QObject()
        self.parent = parent
        self.children = nodeDict()
        ## this permits get at children by position
        self.childrenList = []
        self.setVisible(visible)
        ## ============================
        self.separator = SoSeparator()
#        SoSwitch.addChild(self,self.separator)
        super(SoSwitch, self).addChild(self.separator)
        ## ============================
        self.translation = SoTranslation()
        self.translation.translation = (0, 0, 0)
        self.separator.addChild(self.translation)
        self.animation = None
        ## ============================
        self.material = SoMaterial()
        self.transType = SoTransparencyType()
        self.separator.addChild(self.material)
        self.separator.addChild(self.transType)
        ## ============================
        self.drawStyle = SoDrawStyle()
        self.separator.addChild(self.drawStyle)
        ## ============================
        if parent:
            parent.addChild(self)

    def __getitem__(self, key):
        return self.childrenList[key]

    def addChild(self, node):
        root = getattr(node, "root", node)
        self.separator.addChild(root)
        self.children[root] = node
        self.childrenList.append(node)
        return node

    def getChildren(self):
        return self.children.values()

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
    def setVisible(self, visible):
        if visible:
            self.whichChild = SO_SWITCH_ALL
        else:
            self.whichChild = SO_SWITCH_NONE

    def getVisible(self):
        if self.whichChild.getValue() == SO_SWITCH_ALL:
            return True
        elif self.whichChild.getValue() == SO_SWITCH_NONE:
            return False

    visible = property(fget=getVisible, fset=setVisible)

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
    
    @fluid
    def setColor(self, val):
        self.setDiffuseColor(val)
        self.setEmissiveColor(val)
        self.setAmbientColor(val)
        self.setSpecularColor(val)
    
    color = property(fset=setColor)

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
        
    diffuseColor = property(fset=setDiffuseColor)

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
        self.transType.value = trans
        
    def toText(self):
        wa = SoWriteAction()
        return wa.apply(self)



if __name__ == "__main__":
    print "Hello";
