# -*- coding: utf-8 -*-
#from pivy.coin import SoDrawStyle, SoMaterial, SoSeparator, SoTransform, SoCylinder
import os.path
from pivy.coin import *
from PyQt4 import QtGui,QtCore, uic
from util import norma, resta, cross3, dot,  conecta,  conectaParcial,  searchByName,  searchByNodeType, envuelve
from math import acos, log, sqrt, pow


def esfera(p, radius=.05, mat = None):
    sep = SoSeparator()
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

def tubo(p1, p2, escala = 0.01, escalaVertice = 2.0, mat = None, extremos = False):
    sep = SoSeparator()
    if extremos:
        sep.addChild(esfera(p1, escala*escalaVertice))
        sep.addChild(esfera(p2, escala*escalaVertice))
    tr1 = SoTransform()
    tr2 = SoTransform()
    if mat == None:
        mat = SoMaterial()
        mat.ambientColor.setValue(.0, .0, .0)
        mat.diffuseColor.setValue(.4, .4, .4)
        mat.specularColor.setValue(.8, .8, .8)
        mat.shininess = .1
    cil = envuelve(SoCylinder())
    cil.setName("segmento")
    sep.addChild(tr2)
    sep.addChild(tr1)
    sep.addChild(mat)
    sep.addChild(cil)
    vec = resta(p2, p1)
    t = norma(vec)
    tr1.translation = (0, t/2.0, 0)
    cil[0].radius = escala
    cil[0].height = t
    tr2.translation = p1
    ejeRot = cross3((0, t, 0), vec)
    ang = acos(dot((0, t, 0), vec)/t**2)
    if norma(ejeRot) < .0001:
        ## son paralelos, así que el prod. cruz da el vector nulo.
        ## como el vector base es de la forma (0,t,0), entonces
        ## (1,0,0) es ortogonal a el, y puede proceder la rotación
        ejeRot = (1, 0, 0)
    tr2.rotation.setValue(SbVec3f(ejeRot), ang)
    return sep


def parteIndices(lst):
    if lst == []:
        return []
    else:
        ind = lst.index(-1)
        return [lst[:ind]] + parteIndices(lst[ind+1:])
## parteIndices([1,2,1,2,-1,1,4,-1,3,4,5,6,-1])  ==>  [[1, 2, 1, 2], [1, 4], [3, 4, 5, 6]]

def aristas(poligono):
    pares = []
    for i in range(len(poligono[:-1])):
        pares.append((poligono[i], poligono[i+1]))
    pares.append((poligono[-1], poligono[0]))
    return pares
## aristas([1,0,3]) ==> [(1,0), (0,3), (3,1)]


def reduceEsqueleto(ptos, indices):
    reducidoInd = []
    for poligono in indices:
        pares = aristas(poligono)
        for p in pares:
            if p not in reducidoInd and tuple(reversed(p)) not in reducidoInd:
                reducidoInd.append(p)
    return [(ptos[i1], ptos[i2]) for i1, i2 in reducidoInd]
    

class Poliedro1(object):
    def __init__(self,root,nombre="", caras=True, aristas=True, vertices=True, transparencia=False, datos=(), colores=[], coloresInd=[]):
        self.root = root
        ## at this point root.ref() == 0
        ## so we need to increment it
        root.ref()
        self.name = nombre
        ## ============================
        ## caras
        carasNode = searchByName(root,  "caras")
        carasNode.setName("")
        ## ponemos un SoSwitch entre el node raiz
        ## y el node de las caras, para poder
        ## mostra/ocultar las caras
        self.caras = envuelve(carasNode, caras)
        self.caras.setName("caras")
        root.removeChild(carasNode)
        root.addChild(self.caras)
        ## ============================
#        negros = [(0, 0, 0) for i in range(len(colores))]
        mb = SoMaterialBinding()
        mat = searchByNodeType(carasNode, SoMaterial)
        if mat == None:
            mat = SoMaterial()
            carasNode.insertChild(mat, 0)
        if colores != []:
#            mat.ambientColor.setValues(0, len(negros), negros)
            mat.diffuseColor.setValues(0, len(colores), colores)
#            mat.specularColor.setValues(0, len(negros), negros)
            mat.emissiveColor = (1, 1, 1)
            mb.value = SoMaterialBinding.PER_FACE_INDEXED
        else:
            mat.diffuseColor.setValue(.8, 0, 0)
            mat.ambientColor.setValue(.2, .2, .2)
        carasNode.insertChild(mb, 0)
        self.faceSet = searchByNodeType(carasNode, SoIndexedFaceSet)
        if coloresInd != []:
            self.faceSet.materialIndex.setValues(0,len(coloresInd), coloresInd)
        self.material = mat
        self.transparency = mat.transparency
        self.transparency.setValue(0.08)
        ## ============================
        aristasNode = searchByName(root, "aristas")
        ## si las caras ya son triángulos, el archivo no contiene información extra
        if aristasNode != None:
            ## esto al menos tiene que haber
            self.coord3 = searchByNodeType(aristasNode, SoCoordinate3)
            self.lineSet = searchByNodeType(aristasNode, SoIndexedLineSet, interest=SoSearchAction.ALL)
            ## si las aristas no definen sus propias coordenadas
            ## usamos las de las caras
            if self.coord3 == None:
                self.coord3 = searchByNodeType(caras, SoCoordinate3)
            aristasNode.setName("")
        else:
            self.coord3 = searchByNodeType(carasNode, SoCoordinate3)
            self.lineSet = searchByNodeType(carasNode, SoIndexedFaceSet, interest=SoSearchAction.ALL)
            ## OJO:
            ## self.lineSet es una lista de SoIndexedFaceSet
        ## ============================
        self.creaAristas(aristas, vertices)
        ## ============================
        self.setupGui(transparencia)
        self.setupInfoPanel(datos)

    def getGui(self):
        return self.paramW
    
    def layout(self):
        return self.getGui().layout()
    
    def getName(self):
        return self.name
    
    def creaAristas(self, aristas, vertices):
        ## ============================
        ## bbox
        vpReg = SbViewportRegion()
        vpReg.setWindowSize(300, 200)
        bboxAction = SoGetBoundingBoxAction(vpReg)
        estado = self.caras.whichChild.getValue()
        self.caras.whichChild = 0
        bboxAction.apply(self.caras)
        self.caras.whichChild = estado
        vol = bboxAction.getXfBoundingBox().getVolume()
        ## ============================
        ## aristas
        sepA = SoSeparator()
        self.verticesP = [p.getValue() for p in self.coord3.point]
        indices = []
        for ls in self.lineSet:
            indices += list(ls.coordIndex)
        ind = parteIndices(indices)
        self.aristasP = reduceEsqueleto(self.verticesP, ind)
        self.escala = log(vol+1, 2) * .01 / pow(vol, 1.0/6.0)
        for p1, p2 in self.aristasP:
            sepA.addChild(tubo(p1, p2, self.escala, 0))
        ## esto nos permite mostrar/ocultar
        ## las aristas
        self.aristas = envuelve(sepA, aristas)
        self.aristas.setName("aristas")
        self.root.addChild(self.aristas)
        ## ============================
        ## vertices
        sepV = SoSeparator()
        for p in self.verticesP:
            sepV.addChild(esfera(p, 2*self.escala))
        self.vertices = envuelve(sepV, vertices)
        self.vertices.setName("vertices")
        self.root.addChild(self.vertices)
    
    def getAristasRadio(self):
        tubos = self.aristas[0].getChildren()
        ## nos quedamos con el primer valor
        ## (deberían ser iguales todos)
        return searchByName(tubos[0],"segmento")[0].radius.getValue()
        
    def setAristasRadio(self, val):
        tubos = self.aristas[0].getChildren()
        for t in tubos:
            searchByName(t,"segmento")[0].radius.setValue(val)
    
    def setVertexRadius(self, val):
        for es in self.vertices[0]:
            es[2].radius.setValue(val)
    
    def showEsqueleto(self, mostrar=True):
        if mostrar:
            self.esqueleto.whichChild = 0
        else:
            self.esqueleto.whichChild = -1
    
    def setupInfoPanel(self, datos):
        if len (datos) > 0:
            self.panel = uic.loadUi("modulos/datos-poliedros.ui")
            self.layout().addWidget(self.panel)
            self.layout().addStretch()
            ## ============================
            if len(datos) >= 3:
                self.panel.caras.setText(str(datos[0]))
                self.panel.aristas.setText(str(datos[1]))
                self.panel.vertices.setText(str(datos[2]))
            if len(datos) >= 4:
                    fname = datos[3]
                    name, ext = os.path.splitext(fname)
                    if ext == ".svg":
                        self.panel.svg.load(fname)
                    elif ext == ".png":
                        self.panel.layout().removeWidget(self.panel.svg)
                        ## ============================
                        label = QtGui.QLabel()
                        label.setPixmap(QtGui.QPixmap(fname))
                        layout = QtGui.QHBoxLayout()
                        layout.addStretch()
                        layout.addWidget(label)
                        layout.addStretch()
                        self.panel.layout().insertLayout(2, layout)
        
        
    def setupGui(self, transparencia):
        "agrega el widget para los parámetros + el título"
        self.paramW = QtGui.QWidget()
        self.paramWlayout  =  QtGui.QVBoxLayout()
        self.paramWlayout.setMargin(0)
        self.paramWlayout.setSpacing(20)
        self.paramW.setLayout(self.paramWlayout)
        ## ============================
        if self.name != "":
            label = QtGui.QLabel("<h2>%s</h2>" % self.name)
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.layout().addWidget(label)
        ## ============================
        if transparencia:
            label = QtGui.QLabel("<h3>transparencia:</h3>")
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.paramWlayout.addWidget(label)
            ## ============================
            sl = QtGui.QSlider(QtCore.Qt.Horizontal,  self.paramW)
            maxSL = 50
            sl.setMinimum(0)
            sl.setMaximum(maxSL)
            sl.setValue(maxSL * self.transparency[0])
            conectaParcial(sl, "valueChanged(int)", 
                lambda n: self.transparency.setValue(n/float(maxSL)))
            ## ============================
            self.layout().addWidget(sl)


class Poliedro(object):
    def __init__(self,root,nombre="", procesar=True, esqueleto=True, transparencia=True):
        self.root = root
        ## at this point root.ref() == 0
        ## so we need to increment it
        root.ref()
        self.name = nombre
        if procesar:        
            caras = searchByName(root,  "caras")
            if caras == None:
                caras = root
            mat = searchByNodeType(caras, SoMaterial)
            if mat == None:
                mat = SoMaterial()
                caras.insertChild(mat, 0)
            self.transparency = mat.transparency
            self.transparency.setValue(0.08)
#            mat.shininess = .9
#            mat.specularColor = (.5, .5, .5)
            ## ============================
            aristas = searchByName(root,  "aristas")
            ## si las caras ya son triángulos, el archivo no contiene información extra
            if aristas != None:
                self.coord3 = searchByNodeType(aristas, SoCoordinate3)
                self.lineSet = searchByNodeType(aristas, SoIndexedLineSet)
            else:
                self.coord3 = searchByNodeType(caras, SoCoordinate3)
                self.lineSet = searchByNodeType(caras, SoIndexedFaceSet)
            ## ============================
            ## bbox
            vpReg = SbViewportRegion()
            vpReg.setWindowSize(300, 200)
            bboxAction = SoGetBoundingBoxAction(vpReg)
            bboxAction.apply(caras)
            vol = bboxAction.getXfBoundingBox().getVolume()
            ## ============================
            if esqueleto:
                self.creaEsqueleto(vol)
        ## ============================
        self.setupGui(procesar and transparencia)

    def getGui(self):
        return self.paramW
    
    def getName(self):
        return self.name
    
    def creaEsqueleto(self, vol):
        sep = SoSeparator()
        self.vertices = [p.getValue() for p in self.coord3.point]
        ind = parteIndices(list(self.lineSet.coordIndex))
        self.aristas = reduceEsqueleto(self.vertices, ind)
#            print "escala:",  log(vol+1, 2) * .01 / pow(vol, 1.0/6.0)
        for p1, p2 in self.aristas:
            esq = tubo(p1, p2, log(vol+1, 2) * .005 / pow(vol, 1.0/6.0))
#                esq = tubo(p1, p2, .01)
            sep.addChild(esq)
        ## esto nos permite mostrar/ocultar
        ## el esqueleto
        self.esqueleto = SoSwitch()
        self.esqueleto.setName("esqueleto")
        self.esqueleto.addChild(sep)
        self.esqueleto.whichChild = 0
        self.root.addChild(self.esqueleto)
    
    def showEsqueleto(self, mostrar=True):
        if mostrar:
            self.esqueleto.whichChild = 0
        else:
            self.esqueleto.whichChild = -1
            
    def setupGui(self, transparencia=True):
        "agrega el widget para los parámetros + el título"
        self.paramW = QtGui.QWidget()
#        self.paramW.setObjectName("MallaBaseGui")
        self.paramWlayout  =  QtGui.QVBoxLayout()
        self.paramWlayout.setMargin(0)
        self.paramWlayout.setSpacing(20)
        self.paramW.setLayout(self.paramWlayout)
        ## ============================
        if self.name != "":
            label = QtGui.QLabel("<h1>%s</h1>" % self.name)
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.paramWlayout.addWidget(label)
        ## ============================
        if transparencia:
            label = QtGui.QLabel("<h3>transparencia:</h3>")
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.paramWlayout.addWidget(label)
            ## ============================
            sl = QtGui.QSlider(QtCore.Qt.Horizontal,  self.paramW)
            maxSL = 50
            sl.setMinimum(0)
            sl.setMaximum(maxSL)
            sl.setValue(maxSL * self.transparency[0])
            conectaParcial(sl, "valueChanged(int)", 
                lambda n: self.transparency.setValue(n/float(maxSL)))
            ## ============================
            self.paramWlayout.addWidget(sl)
        self.paramWlayout.addStretch()


        
        
class Poliedro0(object):
    def __init__(self,root,nombre=""):
        self.root = root
        self.name = nombre
        self.setupGui()

    def getGui(self):
        return self.paramW
    
    def getName(self):
        return self.name
            
    def setupGui(self):
        "agrega el widget para los parámetros + el título"
        self.paramW = QtGui.QWidget()
        self.paramWlayout  =  QtGui.QVBoxLayout()
        self.paramWlayout.setMargin(0)
        self.paramWlayout.setSpacing(20)
        self.paramW.setLayout(self.paramWlayout)
        ## ============================
        if self.name != "":
            label = QtGui.QLabel("<h1>%s</h1>" % self.name)
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.paramWlayout.addWidget(label)
        ## ============================
        self.paramWlayout.addStretch()
        
