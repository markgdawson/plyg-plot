from PyQt5 import QtWidgets
from SimulationSelection import SimulationSelectionWidget
from PlotLineModel import PlotLine, PlotLineView, PlotLineModel, PlotLineFactory


class PlotLineGeo(PlotLine):
    linestyle = '-'

    def generate(self):
        sim = self.simulation()
        if sim is not None:
            geom = self.simulation().geom()
            if geom is not None:
                self._xdata, self._ydata = geom.get_patch_faces(range(12, 14))


class PlotLineGeoView(PlotLineView):
    def __init__(self, plot_line, parent=None):
        super(PlotLineGeoView, self).__init__(plot_line, parent)

        self.layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(self)
        label.setText(plot_line.label())

        # sets the self.simulation object
        self.simulation = None
        self.sim_select = SimulationSelectionWidget()
        self.sim_select.sigSimulationLoaded.connect(self.simulation_loaded)
        self.layout.addWidget(self.sim_select)

        # add regenerate button
        button = QtWidgets.QPushButton()
        button.setText("Update")
        self.layout.addWidget(button)

        button.clicked.connect(self.generate)

        self.setLayout(self.layout)

    def simulation_loaded(self):
        self.simulation = self.sim_select.simulation
        face_patches = self.simulation.geom().get_face_patches()
        print(face_patches)

    def generate(self):
        if self.simulation is None:
            QtWidgets.QMessageBox.information(self, "Error", "Simulation not loaded or not selected.",
                                              QtWidgets.QMessageBox.Ok)
        else:
            self.regenerate()


class GeoLineFactory(PlotLineFactory):
    plot_line_class = PlotLineGeo
    plot_view_class = PlotLineGeoView
    plot_model_class = PlotLineModel
