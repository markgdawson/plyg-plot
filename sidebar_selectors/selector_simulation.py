import os

from PyQt5 import QtWidgets, QtCore, QtGui

from Simulation import Simulation, NoSimulationParamsFile
from computation.inform import InformFile
from computation.torque import TorqueFile
from sidebar_selectors.base_class_selector import SidebarSelectorBase
from sidebar_selectors.designer_files import ui_SimulationSelectionDialog


class SimulationSelectionSidebarWidget(SidebarSelectorBase):

    sigSimulationLoaded = QtCore.pyqtSignal(Simulation)
    sigSimulationSelected = QtCore.pyqtSignal(Simulation)
    sigTorqueLoaded = QtCore.pyqtSignal(TorqueFile)

    def __init__(self, parent=None):
        super(SimulationSelectionSidebarWidget, self).__init__(parent, 'Select Simulation')

        self.default_text = "Select Simulation..."
        self.button = QtWidgets.QPushButton(self)
        self.button.setText("< None >")
        self.button.setDefault(True)
        self.button.clicked.connect(self.select_simulation)
        self.layout().addWidget(self.button)

        self.simulation = None
        self.dialog = None

    def select_simulation(self):
        self.dialog = SimulationSelectionDialog(self)
        self.dialog.setModal(True)
        self.dialog.setWindowModality(QtCore.Qt.WindowModal)
        accepted = self.dialog.exec()
        if accepted:
            self.set_simulation(self.dialog.simulation())

    def set_simulation(self, simulation):
        self.simulation = simulation
        self.emit_simulation_selected()
        self.update_label()
        self.sigTorqueLoaded.emit(simulation.torque())
        if simulation.loaded:
            self.emit_simulation_loaded()
        else:
            simulation.sigUpdateLabel.connect(self.update_label)
            simulation.sigUpdateProgress.connect(self.update_label)
            simulation.sigLoaded.connect(self.emit_simulation_loaded)

    def emit_simulation_loaded(self):
        self.sigSimulationLoaded.emit(self.simulation)

    def emit_simulation_selected(self):
        self.sigSimulationSelected.emit(self.simulation)

    def update_label(self):
        if self.simulation is None:
            self.button.setText(self.default_text)
        else:
            progress, progress_total = self.simulation.progress()
            text = "Simulation: %s" % self.simulation.label()
            if progress_total - progress != 0:
                percent = round((progress / progress_total) * 100)
                text += " (%d %%)" % percent
            self.button.setText(text)


# maintains a list of simulations, and maintains parent.simulation as the current simulation object
class SimulationSelectionDialog(QtWidgets.QDialog, ui_SimulationSelectionDialog.Ui_SimulationSelectionDialog):
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

    def load_simulation(self, edit_on_load=False):
        filename, file_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Geo File', 'C:/',
                                                                      'Geo Files (*.geo)')
        if len(filename) == 0:
            return

        inform_file = os.path.join(os.path.dirname(filename), 'inform')

        if os.path.isfile(inform_file):
            params = InformFile(inform_file)
        else:
            msg = "Inform file not found automatically, please select inform file."
            QtWidgets.QMessageBox.information(self, "Warning", msg, QtWidgets.QMessageBox.Ok)

            inform_file, file_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Inform File', 'C:/',
                                                                             'Any File (*)')
            if len(inform_file) == 0:
                params = NoSimulationParamsFile()
            else:
                params = InformFile(inform_file)

        simulation = Simulation(self.model, filename, params=params)

        label = os.path.basename(os.path.dirname(filename))

        self.model.add_simulation(simulation, label=label)

        index = self.model.index(0, 0, QtCore.QModelIndex())
        if edit_on_load:
            self.tableView.edit(index)

        self.tableView.selectRow(0)

    def delete_selected(self):
        indexes = self.tableView.selectedIndexes()
        rows = [i.row() for i in indexes]

        for row in reversed(sorted(set(rows))):
            self.model.beginRemoveRows(QtCore.QModelIndex(), row, row)
            index = self.model.createIndex(row, 0)
            simulation = self.model.simulation(index)
            simulation.disconnect_signals_from_item()
            self.model.removeRow(row)
            self.model.endRemoveRows()

    def selection_changed(self, index):
        rows = self.rows_from_indexes(index.indexes())
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

    @staticmethod
    def rows_from_indexes(indexes):
        return sorted(set(i.row() for i in indexes))

    def simulation(self):
        indexes = self.tableView.selectedIndexes()
        if len(indexes) > 0:
            return self.model.simulation(indexes[0])
        else:
            return None


class SimulationTableDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        if index.column() == 1:
            sim = index.data(role=QtCore.Qt.UserRole)

            progress, progress_total = sim.progress()

            if progress < progress_total:
                progress_bar_option = QtWidgets.QStyleOptionProgressBar()

                progress_bar_option.rect = option.rect
                progress_bar_option.minimum = 0
                progress_bar_option.maximum = progress_total
                progress_bar_option.progress = progress

                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, progress_bar_option,
                                                           painter)
            else:
                super(SimulationTableDelegate, self).paint(painter, option, index)

        else:
            super(SimulationTableDelegate, self).paint(painter, option, index)


class SimulationModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(SimulationModel, self).__init__(parent)

        # ensure that item text and simulation label remain up to date
        self.itemChanged.connect(self.update_simulation_label)

    def update_simulation_label(self, item):
        if item.index().column() == 0:
            simulation = self.simulation(item.index())
            if simulation is not None:
                simulation.set_label(item.text())

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
                return QtCore.QVariant(int(section + 1))
        else:
            return QtCore.QVariant()

    def flags(self, index):
        flags = super(SimulationModel, self).flags(index)

        if index.column() != 0:
            # ony first column is editable
            return flags ^ QtCore.Qt.ItemIsEditable

        return flags

    def add_simulation(self, simulation, label=None):
        self.insertRow(0)
        if label is None:
            label = "Simulation %d" % self.rowCount()

        # simulation item + simulation object in userData (column 1)
        item = QtGui.QStandardItem()
        item.setText(label)
        self.setItem(0, 0, item)

        item = QtGui.QStandardItem()
        item.setText("Yes")
        item.setData(simulation, QtCore.Qt.UserRole)
        simulation.set_label(label)
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
        if item is None:
            return None
        else:
            return item.data(role=QtCore.Qt.UserRole)


SimulationModelInstance = SimulationModel()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SimulationSelectionSidebarWidget()
    widget.show()
    sys.exit(app.exec_())
