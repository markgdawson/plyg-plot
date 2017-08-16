from PyQt4 import QtGui, QtCore


class SimulationComboBox(QtGui.QWidget):

    def __init__(self, simulation_model, parent=None):
        super(SimulationComboBox, self).__init__(parent)

        self.simulation = None

        # setup default or provided model
        self.setLayout(QtGui.QHBoxLayout())

        # create combo box
        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.setModel(simulation_model)
        self.layout().addWidget(self.combo_box)

        # create new line button
        button = QtGui.QPushButton("Load...", self)
        self.connect(button, button.clicked, self.load_simulation)

        self.layout().addWidget(button)
