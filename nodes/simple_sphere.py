from pivy.coin import SoSeparator, SoMaterial, SoSphere, SoTranslation


def SimpleSphere(p, radius=.05, mat=None):
    sep = SoSeparator()
    sep.setName("Sphere")
    tr = SoTranslation()
    tr.setName("Translation")
    sp = SoSphere()
    sp.radius = radius
    tr.translation = p
    if mat is None:
        mat = SoMaterial()
        mat.ambientColor.setValue(.33, .22, .27)
        mat.diffuseColor.setValue(.78, .57, .11)
        mat.specularColor.setValue(.99, .94, .81)
        mat.shininess = .28
    sep.addChild(tr)
    sep.addChild(mat)
    sep.addChild(sp)
    return sep