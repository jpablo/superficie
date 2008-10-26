#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pivy.coin import *
from pivy.gui.soqt import SoQt,  SoQtExaminerViewer
from util import lee,  Segmento,  main,  proyeccionVecs,  param3, OneShot, conectaParcial
from Parametro import Motor
from Poliedro import tubo
from random import uniform
from math import cos, sin, pi
import logging

log = logging.getLogger("PuntoReflejado")
log.setLevel(logging.DEBUG)

## cp is a 4 element array where:
## cp[0] is the starting point, or P0 in the above diagram
## cp[1] is the first control point, or P1 in the above diagram
## cp[2] is the second control point, or P2 in the above diagram
## cp[3] is the end point, or P3 in the above diagram
## t is the parameter value, 0 <= t <= 1

def pointOnCubicBezier( cp, t ):
    #float   ax, bx, cx;
    #float   ay, by, cy;
    #float   tSquared, tCubed;
    result = Point3D()
    
    ##  calculate the polynomial coefficients 
    
    cx = 3.0 * (cp[1].x - cp[0].x)
    bx = 3.0 * (cp[2].x - cp[1].x) - cx
    ax = cp[3].x - cp[0].x - cx - bx
    
    cy = 3.0 * (cp[1].y - cp[0].y)
    by = 3.0 * (cp[2].y - cp[1].y) - cy
    ay = cp[3].y - cp[0].y - cy - by

    cz = 3.0 * (cp[1].z - cp[0].z)
    bz = 3.0 * (cp[2].z - cp[1].z) - cz
    az = cp[3].z - cp[0].z - cz - bz
    
    ## calculate the curve point at parameter value t 
    
    tSquared = t * t
    tCubed = tSquared * t
    
    result.x = (ax * tCubed) + (bx * tSquared) + (cx * t) + cp[0].x
    result.y = (ay * tCubed) + (by * tSquared) + (cy * t) + cp[0].y
    result.z = (az * tCubed) + (bz * tSquared) + (cz * t) + cp[0].z
    norma = result.norma()
    retUnit = Point3D(result.x/norma,result.y/norma,result.z/norma)
    return retUnit;


## ComputeBezier fills an array of Point2D structs with the curve   
## points generated from the control points cp. Caller must 
## allocate sufficient memory for the result, which is 
## <sizeof(Point2D) numberOfPoints>

def ComputeBezier( cp, numberOfPoints, curve ):
    dt = 1.0 / ( numberOfPoints - 1 );
 
    for i in range(numberOfPoints):
        curve[i] = PointOnCubicBezier( cp, i*dt );

def ptoAzar():
    delta = 0.5
    nx = uniform(-1,1) * delta
    ny = uniform(-1,1) * delta
    nz = uniform(-1,1) * delta
    return Point3D(nx,ny,nz)
    


class Point3D:
    def __init__(self,x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    def refleja(self,pto):
        xr = -pto.x + 2*self.x
        yr = -pto.y + 2*self.y
        zr = -pto.z + 2*self.z
        return Point3D(xr,yr,zr)
    def __str__(self):
        return `(self.x,self.y,self.z)`
    def __repr__(self):
        return str(self)
    def norma(self):
        return sqrt(pow(self.x,2)+pow(self.y,2)+pow(self.z,2))
    def toUnitario(self):
        norma = self.norma()
        return Point3D( self.x / norma, self.y / norma, self.z / norma)
    def toTuple(self):
        return (self.x,self.y,self.z)


class Simetria(SoSeparator):
    def __init__(self,  index=0):
        SoSeparator.__init__(self)
        self.normal = (0, 0, 1)
        ## =========================
        color = SoMaterial()
        color.diffuseColor.setValue(0, 1, 0)
        ## =========================
        ## el punto de simetría
        self.origen = creaPunto(radio=.03, color=(0,1,0))
        self.eje = tubo((0,0, -2), (0,0, 2), .005, .99, color)
        self.plano = lee("""
                  Separator {
                        Complexity { value 1.0 }
                        Material {
                            transparency 0.6
                        }
                        Cube { depth 3 width 3 height .001 }
                }
        """)
        self.plano[1].emissiveColor.setValue(0, 1, 0)
        self.plano.insertChild(self.anillo(60), 2)
        self.switch = SoSwitch()
        self.switch.addChild(self.origen)
        self.switch.addChild(self.eje)
        self.switch.addChild(self.plano)
        self.switch.whichChild = 0
        self.addChild(self.switch)
        self.setTipo(index)
    
    def anillo(self, n):
        r = .999
        ## hacemos una copia de los puntos
        ptos = [(r*cos(2*pi * t/n), 0.005, r*sin(2*pi * t/n)) for t in range(n+1) ]
        coords = SoCoordinate3()
        coords.point.setValues(0, len(ptos), ptos)
        index = SoIndexedLineSet()
        index.coordIndex.setValues(0, n+2, range(n+1) + [0])
        ## y ponemos otra copia del otro lado del plano y = 0.
        trans = SoTranslation()
        trans.translation = (0, -.01, 0)
        mat = SoMaterial()
        mat.diffuseColor = (.75, .75, .75)
        sep = SoSeparator()
        sep.addChild(mat)
        sep.addChild(coords)
        sep.addChild(index)
        sep.addChild(trans)
        sep.addChild(coords)
        sep.addChild(index)
        return sep
        
    def __call__(self, vec):
        return self.tipo(vec)
    
    def setTipo(self, index):
        if index == 0:
            self.tipo = self.puntual
            self.switch.whichChild = 0
        elif index == 1:
            self.tipo = self.axial
            self.switch.whichChild = 1
        elif index == 2:
            self.tipo = self.plana
            self.switch.whichChild = 2
        else:
            log.debug("simetria desconocida")
        
    def puntual(self, coords):
        x, y, z = coords
        return (-x, -y, -z)
        
    def axial(self, coords):
        m = proyeccionVecs(coords, self.normal)
        return param3(coords,m,2)
    
    def plana(self, coords):
        ## esto asume que estamos reflejando respecto
        ## al plano xz
        x, y, z = coords
        return (x, -y, z)



def creaPunto(radio, color=(.5, .5, .5), emissive = (0, 0, 0)):
    colorStr = " ".join(map(str,color))
    emissiveStr = " ".join(map(str,emissive))
    sep = lee("""
        Separator {
            Translation {}
            Material {
                diffuseColor  %(colorStr)s
                specularColor  .7 .7 .7
                emissiveColor  %(emissiveStr)s
                shininess 0.1
            }
            Sphere { radius %(radio)f }
      }
    """ % vars())
    sep.translation = sep[0].translation
    sep.esfera = sep[2]
    return sep

    

## TODO: esto deberia ser mas general:
## deberia poder animar una linea entre dos puntos
## arbitrarios, y no solamente entre un pto. y su reflejado
class PuntoReflejado(SoSeparator):
    def __init__(self, p1, tipoSimetria):
        SoSeparator.__init__(self)
        ## tipoSimetria es un objeto de tipo 'Simetria'
        self.enlace = None
        ## el tipo de simetria
        self.creaSimetrico = tipoSimetria
        ## compatibilidad
        self.root = self
        ## el punto original
        self.p1 = creaPunto(radio=.03, color=(1, .3, .3))
        self.addChild(self.p1)
        ## el reflejado
        self.p2 = creaPunto(radio=.03, color=(.2,.2, 1))
        ## la proyección
        self.p3 = creaPunto(radio=.02, color=(.2,1,.2))
        sep = SoSeparator()
        sep.addChild(self.p2)
        sep.addChild(self.p3)
        self.switch = SoSwitch()
        self.switch.addChild(sep)
        self.addChild(self.switch)
        ## =========================
        ## la linea
        sep = lee("""
            Separator {
                Coordinate3 { }
                Normal { vector 1 1 1 }
                Material {
                    diffuseColor  1 0 0
                    ambientColor  1 0 0
                    emissiveColor  1 0 0
                }
                LineSet {  }
          }
        """)
        self.addChild(sep)
        self.linea = sep[0]
        ## ============================    
        self.segmento = Segmento(self.getValue(), self.getValueReflex())
        ## ============================
        ## esto inicializa todas las coordenadas
        self.setValue(p1)
        ## ============================
        self.oneshot = OneShot(1.0)
        conectaParcial(self.oneshot, "ramp(float)", self.animaLinea)
        conectaParcial(self.oneshot, "finished(bool)", self.reflexOn)
    
    def start(self):
        self.oneshot.start()
        
    def update(self):
        "actualizamos el punto reflejado y la linea"
        self.setValue(self.getValue().getValue())
        
    def animaLinea(self, t):
        p1p2 = (self.segmento.p1(),self.segmento.eval(t))
        self.linea.point.setValues(0,len(p1p2), p1p2)
        
    def reflexOn(self, val):
        self.switch.whichChild = 0
    
    def setValue(self, coor):
        "modifica las coordenadas del punto, la linea y el reflejado"
        simCoords = self.creaSimetrico(coor)
        self.p1.translation.setValue(coor)
        self.p2.translation.setValue(simCoords)
        self.segmento = Segmento(coor,simCoords)
        self.p3.translation.setValue(self.segmento.eval(.5))
        self.animaLinea(1.0)
        
    def getValue(self):
        return self.p1.translation.getValue()

    def getValueReflex(self):
        return self.p2.translation.getValue()

        
if __name__ == "__main__":
    app = main(sys.argv)
    window = SoQtExaminerViewer()
    root = SoSeparator()
    sim = Simetria()
    ptos = []
    ptos.append( PuntoReflejado((1, 0, 0),  sim) )
    ptos.append( PuntoReflejado((0, 1, 0),  sim) )
    ptos.append( PuntoReflejado((0, 0, 1),  sim) )
    for p in ptos:
        root.addChild(p)
        p.start(40)
    o = creaPunto(.02,  (.5, .5, .5) )
    root.addChild(o)
    window.setSceneGraph(root)
    window.show()
    SoQt.mainLoop()
