from PyQt5 import QtWidgets, QtCore, QtGui
from TorqueFile import TorqueFile
from GeometryFiles import Geom
import os
import ui_SimulationSelectionDialog


# maintains a list of simulations, and maintains parent.simulation as the current simulation object
class SimulationSelectionDialog(QtWidgets.QDialog, ui_SimulationSelectionDialog.Ui_SimulationSelectionDialog)
    def __init__(self, parent=None):
        super(SimulationSelectionDialog, self).__init__(parent)

        self.setupUi(self)

        self.model = SimulationModelInstance
        self.tableView.setModel(self.model)
        delegate = SimulationTableDelegate()
        self.tableView.setItemDelegate(delegate)
        self.tableView.selectionModel().selectionChanged.connect(self.selection_changed)

        self.__nothing_selected_text = self.status.text()

        self.model.dataChanged.connect(self.tableView.resizeColumnsToContents)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.loadButton.clicked.connect(self.load_simulation)
        self.deleteButton.clicked.connect(self.delete_selected)

    def load_simulation(self):
        filename, file_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'caption', 'C:/', 'Geo Files (*.geo)')
        if len(filename) > 0:
            simulation = Simulation(self.model, filename)

            self.model.add_simulation(simulation)
            index = self.model.index(0, 0, QtCore.QModelIndex())
            self.tableView.edit(index)

    def delete_selected(self):
        indexes = self.tableView.selectedIndexes()
        rows = [i.row() for i in indexes]

        for row in reversed(sorted(set(rows))):
            self.model.beginRemoveRows(QtCore.QModelIndex(), row, row)
            index = self.model.createIndex(row, 0)
            self.model.simulation(index).disconnect_signals_from_item()
            self.model.removeRow(row)
            self.model.endRemoveRows()

    def selection_changed(self, index):
        rows = sorted(set(i.row() for i in index.indexes()))
        if len(rows) > 0:
            labels = []
            for row in rows:
                labels.append(self.model.item(row).text())
            text = "Selected: " + ",".join(labels)
            selected = True
        else:
            text = self.__nothing_selected_text
            selected = False

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(selected)
        self.status.setText(text)


class SimulationTableDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        if index.column() == 1:
            sim = index.data(role=QtCore.Qt.UserRole)

            progress, progress_total = sim.progress()

            if progress < progress_total:
                progress_bar_option = QtWidgets.QStyleOptionProgressBar()

                progress_bar_option.rect = option.rect
                progress_bar_option.minimum = 0
                progress_bar_option.maximum = progress_total
                progress_bar_option.progress = progress
                progress_bar_option.text = "%d %%" % progress
                progress_bar_option.textVisible = True
                progress_bar_option.textAlignment = QtCore.Qt.AlignLeft

                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, progress_bar_option, painter)
            else:
                super(SimulationTableDelegate, self).paint(painter, option, index)

        else:
            super(SimulationTableDelegate, self).paint(painter, option, index)


class SimulationModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(SimulationModel, self).__init__(parent)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return QtCore.QVariant("Label")
                elif section == 1:
                    return QtCore.QVariant("Loaded")
                elif section == 2:
                    return QtCore.QVariant("Filename")
            else:
                return QtCore.QVariant(int(section+1))
        else:
            return QtCore.QVariant()

    def flags(self, index):
        flags = super(SimulationModel, self).flags(index)

        if index.column() != 0:
            # ony first column is editable
            return flags ^ QtCore.Qt.ItemIsEditable

        return flags

    def add_simulation(self, simulation):
        self.insertRow(0)

        # simulation item + simulation object in userData (column 1)
        item = QtGui.QStandardItem()
        item.setText("Simulation %d" % (self.rowCount()))
        self.setItem(0, 0, item)

        item = QtGui.QStandardItem()
        item.setText("Yes")
        item.setData(simulation, QtCore.Qt.UserRole)
        self.setItem(0, 1, item)

        # update progress bar twice a second
        simulation.connect_signals_to_item(item)

        # filename item (column 2)
        item = QtGui.QStandardItem()
        item.setText(simulation.geo_file_name)
        self.setItem(0, 2, item)

    def simulation(self, index):
        row = index.row()
        item = self.item(row, 1)
        return item.data(role=QtCore.Qt.UserRole)


class Simulation(QtCore.QObject):
    sigUpdateProgress = QtCore.pyqtSignal()
    sigLoaded = QtCore.pyqtSignal()

    def __init__(self, parent, geo_file):
        super(Simulation, self).__init__(parent)

        self._geom = None
        self.geo_file_name = geo_file

        self.__sig_emitDataChanged = None

        ThreadLoader(self, self).start()

        # progress update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.sigUpdateProgress.emit)
        self.timer.start(500)
        self.sigLoaded.connect(lambda: [self.timer.stop(), self.sigUpdateProgress.emit()])

        torque_file = os.path.join(os.path.dirname(geo_file), 'TORQUE.csv')
        if os.path.isfile(torque_file):
            self._torque = TorqueFile(torque_file)
        else:
            self._torque = None

    def connect_signals_to_item(self, item):
        self.__sig_emitDataChanged = item.emitDataChanged
        self.sigUpdateProgress.connect(self.__sig_emitDataChanged)

    def disconnect_signals_from_item(self):
        if self.__sig_emitDataChanged is not None:
            self.sigUpdateProgress.disconnect(self.__sig_emitDataChanged)

    def torque(self):
        return self._torque

    def geom(self):
        return self._geom

    def load(self):
        self._geom = Geom(self.geo_file_name)
        self._geom.load()
        self.sigLoaded.emit()
        self._geom.geo.cache()

    def progress(self):
        if self._geom is not None and self._geom.geo is not None:
            return self._geom.geo.progress, self._geom.geo.progress_total
        else:
            return None, None


# creates the simulation Geom object (including loading the file) in a seperate thread
class ThreadLoader(QtCore.QThread):

    def __init__(self, parent, load_obj):
        QtCore.QThread.__init__(self, parent)
        self.load_obj = load_obj

    def run(self):
        self.load_obj.load()

SimulationModelInstance = SimulationModel()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    diag = SimulationSelectionDialog()
    diag.show()
    sys.exit(app.exec_())

