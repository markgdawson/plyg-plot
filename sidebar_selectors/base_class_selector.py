from PyQt5 import QtWidgets


class SidebarSelectorBase(QtWidgets.QFrame):
    GRID_LAYOUT = 1
    VBOX_LAYOUT = 2

    def __init__(self, parent, label, layout=VBOX_LAYOUT, columns=2):
        super(SidebarSelectorBase, self).__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)

        # add label
        self.selector_label = QtWidgets.QLabel(self)
        self.selector_label.setText(label)

        if layout == self.VBOX_LAYOUT:
            layout = QtWidgets.QVBoxLayout()
            self.setLayout(layout)
            layout.addWidget(self.selector_label)
        elif layout == self.GRID_LAYOUT:
            layout = QtWidgets.QGridLayout()
            self.setLayout(layout)
            layout.addWidget(self.selector_label, 0, 0, 1, columns)
        else:
            raise ValueError("unrecognised layout type")

        margin = 10
        self.layout().setContentsMargins(margin, margin, margin, margin)

