from PyQt5 import QtWidgets


def warning(parent, error):
    QtWidgets.QMessageBox.warning(parent, "Warning", str(error), QtWidgets.QMessageBox.Ok)
