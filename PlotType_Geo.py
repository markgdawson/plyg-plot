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
        self.sim_select = SimulationSelectionWidget()
        self.layout.addWidget(self.sim_select)

        # add regenerate button
        button = QtWidgets.QPushButton()
        button.setText("Update")
        self.layout.addWidget(button)

        button.clicked.connect(self.generate)

        self.setLayout(self.layout)

    def generate(self, **kwargs):
        sim = self.sim_select.simulation
        try:
            if sim is None:
                raise ValueError("No Simulation Selected")
            elif not sim.loaded:
                raise ValueError("Simulation Not Loaded. Wait for simulation to load.")
            self.regenerate()
        except ValueError as err:
            QtWidgets.QMessageBox.information(self, "Error", str(err), QtWidgets.QMessageBox.Ok)


class GeoLineFactory(PlotLineFactory):
    plot_line_class = PlotLineGeo
    plot_view_class = PlotLineGeoView
    plot_model_class = PlotLineModel
