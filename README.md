superficie
==========

Superficie is a python library for creating 3D graphics.

It is build upon Pivy (OpenInventor), and Qt4

It support several classes of objects:

* Simple objects: lines, planes, polygons, arrow, etc
* 3d charts: plot3d, parametric plots, etc.
* animations

The objects can be organized hierarchically via a book-like object, which has containers resembling chapters and pages.


## Quick start

```python
import sys
from PyQt4 import QtGui
from superficie.plots import Plot3D
from superficie.viewer import MinimalViewer


app = QtGui.QApplication(sys.argv)

viewer = MinimalViewer()
plot = Plot3D(lambda x, y: .5 * x ** 3 - .5 * 3 * x * y ** 2 + 2.5, (-1, 1), (-1, 1))
viewer.addChild(plot)
viewer.resize(400, 400)
viewer.show()
viewer.viewAll()

sys.exit(app.exec_())
```


![Plot3D](http://jpablo.github.com/superficie/images/plot3d.jpeg)