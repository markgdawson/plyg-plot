from PyQt4 import QtGui, QtCore
from QPushButtonMinSize import QPushButtonMinSize
from TorqueFile import TorqueFile
from GeoFile import Geom
import os


# maintains a list of simulations, and maintains parent.simulation as the current simulation object
class SimulationComboBox(QtGui.QWidget):

    def __init__(self, parent=None):
        super(SimulationComboBox, self).__init__(parent)

        if self.parent() is not None:
            self.parent().set_simulation(None)

        # setup default or provided model
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)

        # create label
        self.layout().addWidget(QtGui.QLabel("Geometry:", self))
        # create combo box
        widget = QtGui.QWidget(self)
        widget.setLayout(QtGui.QHBoxLayout())
        widget.layout().setMargin(0)

        self.combo_box = QtGui.QComboBox(self)
        self.model = SimulationModelInstance
        self.combo_box.setModel(self.model)
        widget.layout().addWidget(self.combo_box)

        self.connect(self.combo_box, self.combo_box.currentIndexChanged, self.current_index_changed)

        # create new line button
        button = QPushButtonMinSize("Load...", self)
        self.connect(button, button.clicked, self.load_simulation)
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
        filename = QtGui.QFileDialog.getOpenFileName(self, 'caption', 'C:/', 'Geo Files (*.geo)')
        if(len(filename) > 0):
            text, accepted = QtGui.QInputDialog.getText(self, 'Get Label','Simulation Label:',QtGui.QLineEdit.Normal,filename)
            if(accepted):
                item = QtGui.QStandardItem()
                item.setText(text)
                item.setData(Simulation(filename),QtCore.Qt.UserRole)
                self.model.insertRow(0,item)


class SimulationModel(QtGui.QStandardItemModel):
    pass


class Simulation:
    def __init__(self, geo_file):
        self.geo_file = geo_file
        self.torque_file = os.path.join(os.path.dirname(geo_file),'TORQUE.csv')
        self._geom = None
        self._torque = None

    def torque(self):
        if self._torque is None:
            self._torque = TorqueFile(self.torque_file)
        return self._torque

    def geom(self):
        if self._geom is None:
            self._geom = Geom(self.geo_file)

        return self._geom

SimulationModelInstance = SimulationModel()
