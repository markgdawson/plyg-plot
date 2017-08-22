from PyQt5 import QtWidgets, QtCore, QtGui
from QPushButtonMinSize import QPushButtonMinSize
from TorqueFile import TorqueFile
from GeoFile import Geom
import os, time


# maintains a list of simulations, and maintains parent.simulation as the current simulation object
class SimulationComboBox(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SimulationComboBox, self).__init__(parent)

        if self.parent() is not None:
            self.parent().set_simulation(None)

        # setup default or provided model
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # create label
        self.layout().addWidget(QtWidgets.QLabel("Geometry:", self))
        # create combo box
        widget = QtWidgets.QWidget(self)
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)

        self.combo_box = QtWidgets.QComboBox(self)
        self.model = SimulationModelInstance
        self.combo_box.setModel(self.model)
        widget.layout().addWidget(self.combo_box)

        self.combo_box.currentIndexChanged.connect(self.current_index_changed)

        # create new line button
        button = QPushButtonMinSize("Load...", self)
        button.clicked.connect(self.load_simulation)
        widget.layout().addWidget(button)

        self.layout().addWidget(widget)

    def current_index_changed(self, index):
        if self.parent() is not None:
            self.parent().set_simulation(self.current_simulation())

    def current_simulation(self):
        index = self.combo_box.currentIndex()
        item = self.combo_box.model().item(index)
        return item.data(QtCore.Qt.UserRole)

    def load_simulation(self):
        filename, file_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'caption', 'C:/', 'Geo Files (*.geo)')
        if len(filename) > 0:
            text, accepted = QtWidgets.QInputDialog.getText(self, 'Get Label',
                                                            'Simulation Label:', QtWidgets.QLineEdit.Normal, filename)
            if accepted:
                item = QtGui.QStandardItem()
                item.setText(text)
                view = self.parent()
                simulation = Simulation(self, filename, view)
                item.setData(simulation, QtCore.Qt.UserRole)
                self.model.insertRow(0, item)


class SimulationModel(QtGui.QStandardItemModel):
    pass


class Simulation(QtCore.QObject):

    def __init__(self, parent, geo_file, view):
        super(Simulation, self).__init__(parent)

        self._geom = None

        thread = GeomFileLoader(self, geo_file)
        thread.sigFileLoadFinished.connect(self.__geom_loaded)
        thread.sigProgressDoneTasks.connect(view.progress_bar_tasks_done)
        thread.sigProgressIncTasks.connect(view.progress_bar_inc_tasks)
        thread.sigProgressMessage.connect(view.progress_message)
        thread.start()

        torque_file = os.path.join(os.path.dirname(geo_file), 'TORQUE.csv')
        if os.path.isfile(torque_file):
            self._torque = TorqueFile(torque_file)
        else:
            self._torque = None

    def torque(self):
        return self._torque

    def geom(self):
        return self._geom

    def __geom_loaded(self, geom):
        self._geom = geom


class GeomFileLoader(QtCore.QThread):

    sigFileLoadFinished = QtCore.pyqtSignal(Geom)
    sigProgressDoneTasks = QtCore.pyqtSignal(int)
    sigProgressIncTasks = QtCore.pyqtSignal(int)
    sigProgressMessage = QtCore.pyqtSignal(str)

    def __init__(self, parent, geo_file):
        QtCore.QThread.__init__(self, parent)
        self.geo_file = geo_file

        self.progress_step = 0
        self.progress_count = 0
        self.progress_total = 0

    def run(self):
        geom = Geom(self.geo_file)
        geom.geo.read(progress_init_func=self.tasks_init, progress_inc_func=self.tasks_done, message_func=self.message)
        self.sigFileLoadFinished.emit(geom)

    def message(self, msg):
        self.sigProgressMessage.emit(msg)

    def tasks_init(self, total):
        self.progress_total = total
        self.progress_step = int(total/100)

        self.sigProgressIncTasks.emit(total)

    def tasks_done(self):
        self.progress_count += 1
        if self.progress_count == self.progress_step:
            self.sigProgressDoneTasks.emit(self.progress_count)
            self.progress_count = 0

SimulationModelInstance = SimulationModel()
