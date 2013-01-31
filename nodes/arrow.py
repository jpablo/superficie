
from math import acos, sqrt
from pivy.coin import SoSeparator, SoTransform, SoCylinder, SoCone, SoMaterial
from superficie.base import MaterialNode
from superficie.util import Vec3, segment
from superficie.utils import fluid


def adjustArg(arg):
    if arg > 1.0:
        return 1.0
    elif arg < -1.0:
        return -1.0
    return arg


def calc_transformations(p1, p2, factor):
    scaledP2 = segment(p1, p2, factor)
    vec = scaledP2 - p1
    length = vec.length() if vec.length() != 0 else .00001
    ## why a vector on the y axis? because by default the axis of the cylinder is the y axis
    ## so we need to calculate the rotation from the y axis to de desired position
    y_axis = Vec3(0, length, 0)
    rot_axis = y_axis.cross(vec)
    ## v.y == |v| |y| cos(t) ; where t: angle between v and y
    ## in this case, |y_axis| == |vec| == length
    #if length < 0.0001:
    #    cos_angle = 0.0
    #else:
    cos_angle = y_axis.dot(vec) / length ** 2
    angle = acos(adjustArg(cos_angle))
    if rot_axis.length() < .0001:
        rot_axis = Vec3(1, 0, 0)
    return angle, rot_axis, length


class Arrow(MaterialNode):
    """An arrow
    Example: Arrow((1,1,1),(0,0,1))
    """
    def __init__(self, p1, p2, radius = 0.04):
        """p1,p2: Vec3"""
        super(Arrow,self).__init__()
        self.p1 = Vec3(p1)
        self.p2initial = self.p2 = Vec3(p2)
        self.full_body_height = 1
        self.lengthFactor = 1
        self.widthFactor = 1
        ## ============================
        self.tr1 = SoTransform()
        self.tr2 = SoTransform()
        self.tr1.setName('tr1')
        self.tr2.setName('tr2')

#        self.material.ambientColor = (.0, .0, .0)
#        self.material.diffuseColor = (.4, .4, .4)
#        self.material.specularColor = (.8, .8, .8)
#        self.material.shininess = .1
        self.material.ambientColor = (0,0,1)
        self.material.diffuseColor = (0,0,1)
#        self.setAmbientColor((0,0,1))
#        self.setDiffuseColor((0,0,1))
        self.body = SoCylinder()
        self.body.setName("body")

#        self.hmaterial = SoMaterial()
#        self.material.ambientColor = (0, 0, 1)
#        self.material.diffuseColor = (0,0,1)

        ## ==========================
#        self.separator.addChild(self.hmaterial)
        self.separator.addChild(self.tr2)
        self.separator.addChild(self.tr1)
        self.separator.addChild(self.body)
        self.separator.addChild(self.build_head())
        ## ============================
        self.calcTransformation()
        self.setRadius(radius)

    def build_head(self):
        head_separator = SoSeparator()
        head_separator.setName('head')
        self.head = SoCone()
        self.head_transformation = SoTransform()
        self.head_material = SoMaterial()
        self.head_material.ambientColor = (.33, .22, .27)
        self.head_material.diffuseColor = (.78, .57, .11)
        self.head_material.specularColor = (.99, .94, .81)
        self.head_material.shininess = .28
        head_separator.addChild(self.head_material)
        head_separator.addChild(self.head_transformation)
        head_separator.addChild(self.head)
        return head_separator

    @fluid
    def setPoints(self, p1, p2):
        """"""
        self.p1 = Vec3(p1)
        self.p2initial = self.p2 = Vec3(p2)
        self.calcTransformation()
        self.adjust_body_height()

    @property
    def body_height(self):
        return self.body.height.getValue()

    @property
    def head_height(self):
        return self.head.height.getValue()

    def adjust_body_height(self):
        """
        Adjust the body height taking into account the head height
        """
        self.set_body_height(self.full_body_height - self.head_height)
        self.head_transformation.translation = (0, self.body_height/2 + self.head_height/2, 0)

    def calcTransformation(self):
        angle, rot_axis, length = calc_transformations(self.p1, self.p2initial, self.lengthFactor)
        self.full_body_height = length
        self.set_body_height(length)
        self.tr2.translation = self.p1
        self.tr2.rotation.setValue(rot_axis, angle)

    def set_body_height(self,length):
        self.body.height = length
        self.tr1.translation = (0, length / 2.0, 0)

    @fluid
    def setP2(self, pt):
        self.p2 = Vec3(pt)
        self.calcTransformation()
        self.adjust_body_height()

    @fluid
    def setLengthFactor(self, factor):
        self.lengthFactor = factor
        self.calcTransformation()
        self.adjust_body_height()

    @fluid
    def setWidthFactor(self, factor):
        self.widthFactor = factor
        self.setRadius( self.body.radius.getValue() * factor)

    @fluid
    def setRadius(self, r):
        self.body.radius = r
        self.head.bottomRadius = r * 1.5
        self.head.height = 3*sqrt(3)*r
        self.adjust_body_height()
