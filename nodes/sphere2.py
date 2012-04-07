__author__ = 'jpablo'

def Sphere2(p, radius=.05, mat=None):
    sep = SoSeparator()
    sep.setName("Sphere")
    tr = SoTranslation()
    sp = SoSphere()
    sp.radius = radius
    tr.translation = p
    if mat == None:
        mat = SoMaterial()
        mat.ambientColor.setValue(.33, .22, .27)
        mat.diffuseColor.setValue(.78, .57, .11)
        mat.specularColor.setValue(.99, .94, .81)
        mat.shininess = .28
    sep.addChild(tr)
    sep.addChild(mat)
    sep.addChild(sp)
    return sep