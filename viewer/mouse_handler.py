from PyQt4 import QtCore


def getPickedPoint(root, myPickAction, cursorPosition):
    myPickAction.setPoint(cursorPosition)
    myPickAction.setRadius(8.0)
    myPickAction.setPickAll(True)
    myPickAction.apply(root)
    return myPickAction.getPickedPointList()


class MouseHandler(object):

    def captureMouseClicked(self, slot1,  slot2=None):
        self.mouseEventCB.addEventCallback(SoMouseButtonEvent.getClassTypeId(),self.mousePressCB)
        conecta(self, QtCore.SIGNAL("mouse1Clicked"), slot1)
        if slot2 is not None:
            conecta(self, QtCore.SIGNAL("mouse2Clicked"), slot2)

    def mousePressCB(self, userData,  eventCB):
        event = eventCB.getEvent()
        view_port = eventCB.getAction().getViewportRegion()
        cursorPosition = event.getPosition(view_port)
        ## ============================
        pickAction = SoRayPickAction(view_port)
        myPickedPointList = getPickedPoint(self.getSRoot(), pickAction, cursorPosition)
        ## ============================
        if myPickedPointList.getLength() == 0:
            return FALSE
        if SoMouseButtonEvent.isButtonPressEvent(event, SoMouseButtonEvent.BUTTON1):
            self.emit(QtCore.SIGNAL("mouse1Clicked"), myPickedPointList)
            self.toggleEventMouseMoved(True)
            self.moving = True
            eventCB.setHandled()
        elif SoMouseButtonEvent.isButtonReleaseEvent(event, SoMouseButtonEvent.BUTTON1):
            self.moving = False
            self.movingOb = None
            self.toggleEventMouseMoved(False)
            eventCB.setHandled()
        elif SoMouseButtonEvent.isButtonPressEvent(event, SoMouseButtonEvent.BUTTON2):
            self.emit(QtCore.SIGNAL("mouse2Clicked"), myPickedPointList)
            eventCB.setHandled()

    def toggleEventMouseMoved(self, val):
        if val:
            self.mouseEventCB.addEventCallback(SoLocation2Event.getClassTypeId(), self.mouseMoveCB)
        else:
            self.mouseEventCB.removeEventCallback(SoLocation2Event.getClassTypeId(), self.mouseMoveCB)

    def mouseMoveCB(self, userData,  eventCB):
        if self.moving:
            event = eventCB.getEvent()
            view_port = eventCB.getAction().getViewportRegion()
            cursorPosition = event.getPosition()
            pickAction = SoRayPickAction(view_port)
            myPickedPointList = getPickedPoint(self.getSRoot(), pickAction, cursorPosition)
            if myPickedPointList.getLength() == 0:
                return FALSE
            self.emit(QtCore.SIGNAL("mouseMoved"), myPickedPointList)
            eventCB.setHandled()

    def captureMouseMoved(self, slot):
        conecta(self, QtCore.SIGNAL("mouseMoved"), slot)
