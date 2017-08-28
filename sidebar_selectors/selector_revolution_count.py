from PyQt5 import QtGui, QtCore, QtWidgets

from sidebar_selectors.base_class_selector import SidebarSelectorBase
from sidebar_selectors.selector_time_units import UnitsComboBox


class RevCountSelector(SidebarSelectorBase):
    sigNumRevsChanged = QtCore.pyqtSignal(float, int)

    def __init__(self, num_revs_window, parent=None, label='Select Revolution Count'):
        super(RevCountSelector, self).__init__(parent, label=label,
                                               layout=SidebarSelectorBase.GRID_LAYOUT)

        self.validator = QtGui.QDoubleValidator(0.0, 10.0, 0, parent)

        self.units = None
        units = UnitsComboBox(self)
        units.sigUnitsChanged.connect(self.units_changed)
        units.selection_changed()

        ctl = QtWidgets.QLineEdit(self)
        ctl.setText("%.1f" % num_revs_window)
        ctl.setValidator(self.validator)
        ctl.textChanged.connect(self.text_changed)

        self.layout().addWidget(ctl, 1, 0, 1, 1)
        self.layout().addWidget(units, 1, 1, 1, 1)

    def units_changed(self, units):
        self.units = units

    def text_changed(self, text):
        form_widget = self.sender()
        state = self.validator.validate(form_widget.text(), 0)[0]

        try:
            val = float(text)
        except Exception as err:
            state = QtGui.QValidator.Invalid

        if state == QtGui.QValidator.Acceptable:
            color = '#ffffff'  # white
            self.sigNumRevsChanged.emit(val, self.units)
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        form_widget.setStyleSheet('QLineEdit { background-color: %s }' % color)


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    widget = RevCountSelector(1.0)
    widget.show()
    sys.exit(app.exec_())
