from pivy.coin import SoMaterial, SoTransparencyType
from ..utils import fluid
from .base_object import BaseObject


class MaterialNode(BaseObject):
    """Material capable node"""

    def __init__(self):
        super(MaterialNode,self).__init__()

        self.material = SoMaterial()
        self.transparencyType = SoTransparencyType()

        self.separator.addChild(self.material)
        self.separator.addChild(self.transparencyType)

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

    ambientColor = property(fset=setAmbientColor)

    @fluid
    def setSpecularColor(self, val):
        self.material.specularColor.setValue(val)

    specularColor = property(fset=setSpecularColor)

    @fluid
    def setShininess(self, val):
        self.material.shininess = val

    @fluid
    def setTransparencyType(self, trans):
        self.transparencyType.value = trans

    @fluid
    def setColor(self, val):
        """set diffuse, emissive, ambient and specular properties at once"""
        self.setDiffuseColor(val)
        self.setEmissiveColor(val)
        self.setAmbientColor(val)
        self.setSpecularColor(val)

    color = property(getDiffuseColor,setColor)