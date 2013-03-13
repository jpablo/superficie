from superficie.widgets.checkbox import CheckBox


class VisibleCheckBox(CheckBox):
    def __init__(self, text,ob, state=True, parent = None):
        CheckBox.__init__(self,ob.show,ob.hide,text,state)
        if parent:
            parent.addWidget(self)
