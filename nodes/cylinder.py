from math import pi
from pivy.coin import SoSeparator, SoCylinder, SoShapeHints, SoMaterial, SoRotationXYZ, SoTransparencyType

__author__ = 'jpablo'

def Cylinder(col, length, radius = 0.98):
    sep = SoSeparator()

    cyl = SoCylinder()
    cyl.radius.setValue(radius)
    cyl.height.setValue(length)
    cyl.parts = SoCylinder.SIDES

    light = SoShapeHints()
    mat = SoMaterial()
    mat.emissiveColor = col
    mat.diffuseColor = col
    mat.transparency.setValue(0.5)

    rot = SoRotationXYZ()
    rot.axis = SoRotationXYZ.X
    rot.angle = pi / 2

    trans = SoTransparencyType()
#    trans.value = SoTransparencyType.DELAYED_BLEND
    trans.value = SoTransparencyType.SORTED_OBJECT_BLEND
#    trans.value = SoTransparencyType.SORTED_OBJECT_SORTED_TRIANGLE_BLEND

    sep.addChild(light)
    sep.addChild(rot)
    sep.addChild(trans)
    sep.addChild(mat)
    sep.addChild(cyl)

    return sep