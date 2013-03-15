from PyQt4 import QtGui, QtCore, uic
from superficie.util import identity, filePath, partial, segment, conecta
from superficie.animations import Animation, AnimationGroup


class Slider(QtGui.QWidget):
    def __init__(self, rangep=('w', 0, 1, 0, 10), func=identity, duration=1000, parent=None):
        # TODO: cambiar el orden: func, rangep...
        ## rangep = (name, vmin, vmax, vini, npoints)
        QtGui.QWidget.__init__(self)
        uic.loadUi(filePath("Gui","paramTemplate2.ui"), self)
        self.timeline = QtCore.QTimeLine(duration)
        self.name = rangep[0]
        self.npoints = rangep[-1]
        self.func = func
        ## ============================
        self.updateRange(rangep[1:-1])
        self.setupUi()
        if parent:
            parent.addWidget(self)


    def updateRange(self, rangep):
        ## rangep = (vmin, vmax, vini)
        self.timeline = QtCore.QTimeLine(self.timeline.duration())
        self.range = rangep + type(rangep)([self.npoints])
        self.vmin, self.vmax, self.vini, self.npoints = self.range
        self.funcTrans = partial(segment, self.vmin, self.vmax)
        self.timeline.setFrameRange(0, self.npoints-1)
        curTime = float(self.vini - self.vmin) /(self.vmax - self.vmin) * self.timeline.duration()
        self.timeline.setCurrentTime(curTime)
        ## ============================
        conecta(self.timeline, QtCore.SIGNAL("valueChanged(qreal)"), lambda t: self.func(self.funcTrans(t)))
        conecta(self.timeline, QtCore.SIGNAL("valueChanged(qreal)"), lambda t: self.updateLabel(self.funcTrans(t)))
        conecta(self.timeline, QtCore.SIGNAL("frameChanged(int)"), self.updateSlider)
        ## ============================
#        self.nombre.setTitle(self.name + ": %.3f" % self.vini)
        hasattr(self, 'nombre') and self.nombre.setText(self.name + ": %.3f" % self.vini)
        self.slider.setValue(self.timeline.currentFrame())

    def setupUi(self,):
        self.slider.setMaximum(self.npoints-1)
        conecta(self.slider, QtCore.SIGNAL("valueChanged(int)"), self.updateFromSlider)
        self._d = []
        for f, i in zip([self.atras, self.adelante], [-1, 1]):
            self._d.append(partial(self.estadoAnimacion,i))
            conecta(f, QtCore.SIGNAL("clicked()"), self._d[-1])

        def changeText(btn,text):
            btn.setText(text)
#        conecta(self.adelante, QtCore.SIGNAL("clicked()"), partial(changeText,self.adelante,"||"))
#        conecta(self.adelante, QtCore.SIGNAL("clicked()"), partial(changeText,self.atras,"<"))
#        conecta(self.atras, QtCore.SIGNAL("clicked()"), partial(changeText,self.atras,"||"))
#        conecta(self.atras, QtCore.SIGNAL("clicked()"), partial(changeText,self.adelante,"<"))

        conecta(self.timeline, QtCore.SIGNAL("finished()"), partial(changeText,self.adelante,">"))
        conecta(self.timeline, QtCore.SIGNAL("finished()"), partial(changeText,self.atras,"<"))


    def updateSlider(self, n):
        self.slider.blockSignals(True)
        self.slider.setValue(n)
        self.slider.blockSignals(False)

    def estadoAnimacion(self,dir):
        tl = self.timeline
        if dir == 0:
            if tl.state() == tl.Running:
                tl.setPaused(True)
        elif dir == 1 and tl.currentValue() < 1.0:
            tl.setDirection(tl.Forward)
            if tl.state()  != tl.Running:
                tl.resume()
                ## ======================
                self.adelante.setText("||")
                self.atras.setText("<")

        elif dir == -1 and tl.currentValue() > 0.0:
            tl.setDirection(tl.Backward)
            if tl.state()  != tl.Running:
                tl.resume()
                ## ======================
                self.atras.setText("||")
                self.adelante.setText(">")

    def updateFromSlider(self,n):
        prop = float(n) / (self.npoints-1)
        curTime = prop * self.timeline.duration()
        ## ============================
        self.timeline.blockSignals(True)
        self.timeline.setCurrentTime(curTime)
        self.func(self.funcTrans(prop))
        self.updateLabel(self.funcTrans(prop))
        self.timeline.blockSignals(False)

    def updateLabel(self, t):
#        self.nombre.setTitle(self.name + ": %.3f" % t)
        hasattr(self, 'nombre') and self.nombre.setText(self.name + ": %.3f" % t)
        self.emit(QtCore.SIGNAL("labelChanged(float)"), t)

    def getValue(self):
        return self.funcTrans(self.timeline.currentValue())

    def asAnimation(self):
        return Animation(self.slider.setValue,(2000,0,self.timeline.endFrame()))
