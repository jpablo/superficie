'''
Created on 20/06/2010

@author: jpablo
'''
import csv
from PyQt4 import QtGui
from superficie.Plot3D import Mesh
from superficie.Viewer import Viewer
from superficie.util import _1
from superficie.VariousObjects import Points
from math import sin, cos, pi

def toTuple(lst):
    return eval(lst.replace("{","(").replace("}",")"))


def toEsf(vec):
    x,y,z = vec
    return (sin(x*pi)*cos(y*2*pi),sin(x*pi)*sin(y*2*pi),-cos(x*pi)*.99)

def proyEstereo(vec):
    x,y,z = vec
    return (2*x/(1-z),2*y/(1-z),-1)

def img_to_csv():
    lst = list(csv.reader(open("panorama.csv")))
    nx = float(len(lst))
    ny = float(len(lst[0]))
    print "x,y,r,g,b"
    for i,fila in enumerate(lst):
        for j,pto in enumerate(fila):
            r,g,b = _1(*toTuple(pto))
            print ",".join(map(str,(i/nx,1-j/ny,r,g,b))) 

if __name__ == "__main__":
    import sys
    #===========================================================================
    # 
    #===========================================================================
#    img_to_csv()
#    sys.exit()
    #===========================================================================
    # 
    #===========================================================================
    app = QtGui.QApplication(sys.argv)
    Mesh.autoAdd = True
    viewer = Viewer()
    lst = list(csv.reader(open("data.csv")))
    coords = []
    cols = []
    for row in lst[1:]:
        x,y,r,g,b = map(float,row)
        coords.append((x,y,0))
        cols.append((r,g,b))
    
            
    viewer.createChapter()
    viewer.chapter.createPage()
    
    pts = Points(coords,cols)
    viewer.page.addChild(pts)
    
    viewer.chapter.createPage()
    pts2 = Points(map(toEsf,coords),cols)
    viewer.page.addChild(pts2)
    
    def planoEstereo(vec):
        return proyEstereo(toEsf(vec))
    
#    viewer.chapter.createPage()
    pts3 = Points(map(planoEstereo,coords),cols)
    viewer.page.addChild(pts3)
    
    viewer.whichPage = 0
    viewer.resize(400, 400)
    viewer.show()
    viewer.chaptersStack.show()
    sys.exit(app.exec_())
#    