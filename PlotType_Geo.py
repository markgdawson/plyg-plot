from PyQt5 import QtWidgets
from SimulationSelection import SimulationSelectionWidget
from PlotLineModel import PlotLineView


class PlotLineGeoView(PlotLineView):
    def __init__(self, parent=None):
        super(PlotLineGeoView, self).__init__(parent)

        # sets the self.simulation object
        self.simulation = None
        self.sim_select = SimulationSelectionWidget()
        self.sim_select.sigSimulationLoaded.connect(self.simulation_loaded)
        self.layout().addWidget(self.sim_select)

        # add regenerate button
        button = QtWidgets.QPushButton()
        button.setText("Update")
        self.layout().addWidget(button)

        button.clicked.connect(self.generate)

    def simulation_loaded(self):
        self.simulation = self.sim_select.simulation

        # build face patches
        face_patches = self.simulation.geom().get_face_patches()
        self.fpatch_checkboxes = QtWidgets.QButtonGroup()
        self.fpatch_checkboxes.setExclusive(False)
        for face_patch in face_patches:
            checkbox = QtWidgets.QCheckBox(self)
            checkbox.setText("%d" % face_patch)
            self.fpatch_checkboxes.addButton(checkbox,face_patch)
            self.layout().addWidget(checkbox)
        self.fpatch_checkboxes.buttonClicked.connect(self.patches_changed)

    def patches_changed(self):
        f = self.fpatch_checkboxes
        self.fpatches = [ f.id(b) for b in f.buttons() if b.isChecked()]
        self.plot_line().set_patches(self.fpatches)

    def generate(self):
        if self.simulation is None:
            QtWidgets.QMessageBox.information(self, "Error", "Simulation not loaded or not selected.",
                                              QtWidgets.QMessageBox.Ok)
        else:
            self.regenerate()

    def generate(self):
        sim = self.simulation()
        if sim is not None:
            geom = self.simulation().geom()
            if geom is not None:
                self._xdata, self._ydata = geom.get_patch_faces(range(12, 14))




