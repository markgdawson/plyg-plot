from PyQt5 import QtWidgets
import traceback


def python_exception_dialog(err, parent):
    dialog = PythonExceptionDialog(err, parent)
    dialog.show()


class PythonExceptionDialog(QtWidgets.QDialog):
    def __init__(self, error, parent=None):
        super(PythonExceptionDialog, self).__init__(parent)

        label = QtWidgets.QLabel(self)
        label.setText("Error: %s" % str(error))

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(label)

        self.info_container = QtWidgets.QTextEdit(self)
        self.info_container_visible = False
        self.info_container.setVisible(self.info_container_visible)
        self.info_container.setMinimumHeight(300)
        self.info_container.setText(traceback.format_exc())
        self.layout().addWidget(self.info_container)

        buttons = QtWidgets.QWidget(self)
        buttons.setLayout(QtWidgets.QHBoxLayout())
        buttons.layout().addStretch()
        ok_button = QtWidgets.QPushButton(self)
        ok_button.setText("Ok")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        self.info_button = QtWidgets.QPushButton(self)
        self.info_button.setText("More Info")
        self.info_button.clicked.connect(self.info)
        buttons.layout().addWidget(self.info_button)
        buttons.layout().addWidget(ok_button)

        self.layout().addWidget(buttons)
        self.setMinimumWidth(300)

    def info(self):
        self.info_container_visible = not self.info_container_visible
        self.info_container.setVisible(self.info_container_visible)

        if self.info_container_visible:
            self.info_button.setText("Hide Info")
        else:
            self.info_button.setText("More Info")

if __name__ == '__main__':
    import sys
    try:
        raise Exception("Do Exception...!")
    except Exception as err:
        app = QtWidgets.QApplication(sys.argv)
        diag = PythonExceptionDialog(err)
        diag.show()
        sys.exit(app.exec_())
