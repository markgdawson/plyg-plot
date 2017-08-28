from PyQt5 import QtWidgets, QtCore

from computation.torque import TorqueFile


class UnitsComboBox(QtWidgets.QComboBox):
    sigUnitsChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(UnitsComboBox, self).__init__(parent)

        contents = (('revolutions', TorqueFile.UNITS_REVOLUTIONS),)

        for text, data in contents:
            self.addItem(text, userData=data)

        self.currentIndexChanged.connect(self.selection_changed)

    def selection_changed(self):
        data = self.currentData(role=QtCore.Qt.UserRole)
        self.sigUnitsChanged.emit(data)
