from PyQt5 import QtWidgets, QtCore, QtGui


class RevolutionRangeSelector(QtWidgets.QWidget):
    sigRangeChanged = QtCore.pyqtSignal(float, float)

    def init(self, start, end, max=20.0):
        # set layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        # create form validator
        self.validator = QtGui.QDoubleValidator(0.0, max, 1)

        # set initial value
        self.start = start
        self.end = end
        self.prev = None

        # setup UI
        self.add_label("Select revolution range:", 0)

        self.start_le = self.add_row("from", start, 1)
        self.end_le = self.add_row("to", end, 2)

        self.label = self.add_label("", 3)

        self.emit_range_changed()

    def set_max_from_torque_revs(self, torque):
        self.validator = QtGui.QDoubleValidator(0.0, torque.num_revs(), 1)
        self.check_state()

    def add_label(self, text, row):
        label = QtWidgets.QLabel(self)
        label.setText(text)
        self.layout().addWidget(label, row, 0, 1, 2)
        return label

    def add_row(self, string, value, row):
        label = QtWidgets.QLabel(self)
        label.setText(string)
        self.layout().addWidget(label, row, 0)
        text = QtWidgets.QLineEdit(self)
        text.setText("%.1f" % value)
        text.setValidator(self.validator)
        self.layout().addWidget(text, row, 1)
        text.textChanged.connect(self.check_state)
        return text

    def check_state(self):
        condition = self.check_form_level_state(self.start_le) \
                    and self.check_form_level_state(self.end_le) \
                    and self.check_widget_level_state()

        if condition:
            if self.prev is None or self.start != self.prev[0] or self.end != self.prev[1]:
                self.emit_range_changed()
            self.prev = [self.start, self.end]

    def emit_range_changed(self):
        self.sigRangeChanged.emit(self.start, self.end)
        self.label.setText("Range: %.1f -> %.1f" % (self.start, self.end))

    def check_widget_level_state(self):
        try:
            self.start = float(self.start_le.text())
            self.end = float(self.end_le.text())
        except:
            return False

        if self.end <= self.start:
            color = '#f6989d'  # red
            for form_widget in [self.start_le, self.end_le]:
                form_widget.setStyleSheet('QLineEdit { background-color: %s }' % color)
            return False
        else:
            return True

    def check_form_level_state(self, form_widget):
        text = form_widget.text()
        state = self.validator.validate(form_widget.text(), 0)[0]

        try:
            float(text)
        except:
            state = QtGui.QValidator.Invalid

        ok = False
        if state == QtGui.QValidator.Acceptable:
            color = '#ffffff'  # white
            ok = True
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        form_widget.setStyleSheet('QLineEdit { background-color: %s }' % color)

        return ok


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    a = RevolutionRangeSelector()
    a.show()
    sys.exit(app.exec_())
