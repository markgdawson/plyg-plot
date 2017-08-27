from PyQt5 import QtWidgets, QtGui, QtCore


class RevCountSelector(QtWidgets.QWidget):
    sigNumRevsChanged = QtCore.pyqtSignal(float)

    def __init__(self, num_revs_window, parent):
        super(RevCountSelector, self).__init__(parent)

        self.validator = QtGui.QDoubleValidator(0.0, 10.0, 0, parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        label = QtWidgets.QLabel(self)
        label.setText("length of sliding window (revolutions):")

        ctl = QtWidgets.QLineEdit(self)
        ctl.setText("%.1f" % num_revs_window)
        ctl.setValidator(self.validator)
        ctl.textChanged.connect(self.text_changed)

        self.layout().addWidget(label)
        self.layout().addWidget(ctl)

    def text_changed(self, text):
        form_widget = self.sender()
        state = self.validator.validate(form_widget.text(), 0)[0]

        try:
            val = float(text)
        except Exception as err:
            state = QtGui.QValidator.Invalid

        if state == QtGui.QValidator.Acceptable:
            color = '#ffffff'  # white
            self.sigNumRevsChanged.emit(val)
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        form_widget.setStyleSheet('QLineEdit { background-color: %s }' % color)
