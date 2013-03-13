# -*- coding: utf-8 -*-
from math import *

from PyQt4 import QtGui
from pivy.coin import *

from superficie.nodes import Line, Curve3D
from superficie.book import Chapter, Page
from superficie.util import Vec3, _1, partial
from superficie.widgets import VisibleCheckBox, Slider, SpinBox
from superficie.plots import ParametricPlot3D
from superficie.animations import AnimationGroup


class PlanePage(Page):
    def __init__(self, name):
        Page.__init__(self, name)
        self.camera_position = (0, 0, 13)
        self.camera_point_at = [SbVec3f(0, 0, 0), SbVec3f(0, 1, 0)]
        self.showAxis(True)
        self.axis_z.setVisible(False)


class Tangent(PlanePage):
    """
    The <b>tangent</b> function is a bijection between an open segment and all the real numbers.
    """

    def __init__(self):
        PlanePage.__init__(self, 'Tangent')
        n_points = 100
        delta = .2

        # The curve fragments
        intervals = [
            (-pi, -pi / 2 - delta, n_points),
            (-pi / 2 + delta, pi / 2 - delta, n_points),
            (pi / 2 + delta, pi, n_points)
        ]
        # because intervals is a list of ranges, Curve3D will be a composite of curves
        curve = Curve3D(lambda t: Vec3(t, tan(t), 0), intervals, width=2).setBoundingBox((-5, 5), (-5, 5))

        # add the curve to this page
        self.addChild(curve)

        ## asymptotes
        self.addChild(Line([(-pi / 2, -5, 0), (-pi / 2, 5, 0)], color=(1, .5, .5)))
        self.addChild(Line([(pi / 2, -5, 0), (pi / 2, 5, 0)], color=(1, .5, .5)))

        # curve.attachField will create an arrow starting at the curve and ending in the vector given by derivative
        tangent_vector = curve.attachField("tangent", lambda t: Vec3(1, 1 / cos(t) ** 2, 0))
        # by default the arrow doesn't have a tail
        tangent_vector.add_tail(radius=0.08)
        # set up the default animations for this page (just the animation for the tangent_vector object in this case)
        self.setupAnimations([tangent_vector])


class PlaneCurves(Chapter):
    def __init__(self):
        Chapter.__init__(self, name="Plane Curve")
        self.addPage(Tangent())

if __name__ == "__main__":
    import sys
    from superficie.viewer.Viewer import Viewer
    app = QtGui.QApplication(sys.argv)
    visor = Viewer()
    visor.setColorLightOn(False)
    visor.setWhiteLightOn(True)
    visor.book.addChapter(PlaneCurves())
    visor.whichChapter = 0
    visor.chapter.whichPage = 0
    visor.resize(400, 400)
    visor.show()
    visor.chaptersStack.show()
    visor.notesStack.show()
    sys.exit(app.exec_())
