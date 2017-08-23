from PyQt5 import QtWidgets, QtCore, QtGui
import ui_SimulationSelectionDialog
from Simulation import Simulation


class SimulationSelectionWidget(QtWidgets.QPushButton):
    sigSimulationSelected = QtCore.pyqtSignal(Simulation)

    def __init__(self, parent=None):
        super(SimulationSelectionWidget, self).__init__(parent)

        self.default_text = "Select Simulation..."
        self.setText("Select Simulation...")
        self.setDefault(True)
        self.clicked.connect(self.__select_simulation)
        self.simulation = None

        self.dialog = None

    def __select_simulation(self):
        self.dialog = SimulationSelectionDialog(self)
        self.dialog.setModal(True)
        self.dialog.setWindowModality(QtCore.Qt.WindowModal)
        accepted = self.dialog.exec()
        if accepted:
            self.simulation = self.dialog.simulation()
            self.sigSimulationSelected.emit(self.simulation)
            self.update_label
            self.simulation.sigUpdateLabel.connect(self.update_label)
            self.simulation.sigUpdateProgress.connect(self.update_label)

    def update_label(self):
        if self.simulation is None:
            self.setText(self.default_text)
        else:
            progress, progress_total = self.simulation.progress()
            if progress_total - progress == 0:
                text = self.simulation.label()
            else:
                percent = round((progress/progress_total)*100)
                text = "%s (%d %%)" % (self.simulation.label(), percent)
            self.setText(text)


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

    def rows_from_indexes(self, indexes):
        return sorted(set(i.row() for i in indexes))

    def simulation(self):
        indexes = self.tableView.selectedIndexes()
        if len(indexes) > 0:
            return self.model.simulation(indexes[0])
        else:
            return None

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

        # ensure that item text and simulation label remain up to date
        self.itemChanged.connect(self.update_simulation_label)

    def update_simulation_label(self, item):
        if item.index().column()==0:
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
    diag = SimulationSelectionDialog()
    diag.show()
    sys.exit(app.exec_())

