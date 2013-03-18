# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic


def big(txt):
    return "<font size=+3 face=Serif>%s</font>" % txt


class Eq(object):
    def __init__(self, expr):
        self.expr = expr

    def update(self, val):
        print val

    def eval(self, layout):
        self.formato(layout, self)

    def __neg__(self):
        return Eq(('-',  self))

    def __add__(self, other):
        return Eq(('+',  self,  other))

    def __radd__(self, other):
        return Eq(('+',  other,  self))

    def __sub__(self, other):
        return Eq(('-',  self,  other))

    def __rsub__(self, other):
        return Eq(('-',  other,  self))

    def __mul__(self, other):
        return Eq(('*',  self,  other))

    def __rmul__(self, other):
        return Eq(('*',  other,   self))

    def __div__(self, other):
        return Eq(('/',  self,  other))

    def __rdiv__(self, other):
        return Eq(('/',  other, self))

    def __pow__(self, other):
        return Eq(('^',  self,  other))

    def __xor__(self, other):
        return Eq(('^',  self,  other))

    def __eq__(self, other):
        return Eq(('=',  self,  other))

    def  __call__(self, *others):
        return Eq(['func', self] +  list(others) )

## ============================
    @staticmethod
    def frac(layout, a, b):
            vboxlayout = QtGui.QVBoxLayout()
            vboxlayout.setMargin(0)
            vboxlayout.setSpacing(0)

            num = QtGui.QHBoxLayout()
            num.setMargin(0)
            num.setSpacing(0)
            Eq.formato(num, a)
            vboxlayout.addLayout(num)

            line = QtGui.QFrame()
            line.setFrameShape(QtGui.QFrame.HLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            vboxlayout.addWidget(line)

            denom = QtGui.QHBoxLayout()
            denom.setMargin(0)
            denom.setSpacing(0)
            Eq.formato(denom, b)
            vboxlayout.addLayout(denom)

            layout.addLayout(vboxlayout)

    @staticmethod
    def pow(layout, x, n):
        Eq.formato(layout, x)
        layout.addWidget(QtGui.QLabel(big("<sup>%s</sup>" % n)))

    @staticmethod
    def plus(layout, *expr):
        op = expr[0]
        for a in expr[1:-1]:
            Eq.formato(layout, a)
            layout.addWidget(QtGui.QLabel(big(" "+op+"")))
        else:
            Eq.formato(layout, expr[-1])

    @staticmethod
    def mult(layout,  a,  b):
        Eq.formato(layout, a)
        layout.addWidget(QtGui.QLabel(" "))
        Eq.formato(layout, b)

    @staticmethod
    def func(layout, args):
        fn = args[0].expr
        layout.addWidget(QtGui.QLabel(big(fn + '(')))
        for a in args[1:]:
            Eq.formato(layout, a)
        layout.addWidget(QtGui.QLabel(big(')')))

    @staticmethod
    def var(layout, expr):
        if len(unicode(expr)) == 1 and unicode(expr).isalpha():
            expr = '<em>%s</em>' % expr
        label = QtGui.QLabel(big(expr))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

    @staticmethod
    def operacion(layout, ob):
        expr = ob.expr[1]
#        if len(unicode(expr)) == 1 and unicode(expr).isalpha():
        ## en general el valor inicial es 0
#        num = eval(ob.expr[1].replace(ob.expr[2], "0"))
        if not hasattr(ob,  "labels"):
            ob.labels = []
        exprRoja = '<em style="color:red">%s</em>' % ob.expr[1]
        label = QtGui.QLabel(big(exprRoja))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        ob.labels.append(label)

    @staticmethod
    def param(layout, ob):
        name = ob.expr[1]
        ## puede haber varias etiquetas asociadas al mismo parámetro
        if not hasattr(ob,  "labels"):
            ob.labels = []
        ## en general el valor inicial es 0
        ## hacer esto mas general!
        ob.labels.append(QtGui.QLabel(big('<em style="color:red">%s</em>' % name)))
        layout.addWidget(ob.labels[-1])

    def setParamValue(self, val):
        valstr = "%.2f" % val
        if valstr == "1.00":
            valstr = "1"
        elif valstr == "0.00":
            valstr = "0"
        if self.expr[0] == "par":
            for label in self.labels:
                label.setText(big('<span style="color:red">%s</span>' % valstr))
        elif self.expr[0] == "operacion":
            ## self.expr == ("operacion", expr, val)
            num = eval(self.expr[1].replace(self.expr[2], valstr))
            for label in self.labels:
                label.setText(big('<span style="color:red">%s</span>' % num))

    @staticmethod
    def formato(layout, ob):
        ## ob puede ser de tipo  Eq, o número, o cadena
        if hasattr(ob, "expr"):
            expr = ob.expr
        else:
            expr = ob
        t = type(expr)
        if t == tuple or t == list:
            head = expr[0]
        if t  == str or t == unicode or t == int or t == float:
            Eq.var(layout, expr)
        elif head == "func":
            Eq.func(layout, expr[1:])
        elif head == "+" or head == "-" or head == "=":
            Eq.plus(layout, *expr)
        elif head == "^":
            Eq.pow(layout, expr[1], expr[2])
        elif head == "/":
            Eq.frac(layout, expr[1],  expr[2])
        elif head == "*":
            Eq.mult(layout, expr[1],  expr[2])
        elif head == "par":
            Eq.param(layout, ob)
        elif head == "operacion":
            Eq.operacion(layout, ob)

def defVars(*args):
    ## no funciona
    for a in args:
        exec("%s = Eq('%s')" % (a, a))

def createVars(*args):
    return map(Eq,  *args)

def createVarParam(name):
    return Eq(('par', name))

def createOpParam(expr, var):
    return Eq(('operacion', expr, var))
