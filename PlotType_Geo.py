from PyQt5 import QtWidgets
from SimulationSelection import SimulationSelectionWidget
from PlotLineModel import PlotLine, PlotLineView, PlotLineModel


class PlotLineGeo(PlotLine):
    linestyle = '-'

    def __init__(self, model=None):
        super(PlotLineGeo, self).__init__(model)

    def update(self):
        sim = self.simulation()
        if sim is not None:
            geom = self.simulation().geom()
            if geom is not None:
                self._xdata, self._ydata = geom.get_patch_faces(range(12, 14))


class PlotLineGeoView(PlotLineView):
    def __init__(self, parent=None):
        super(PlotLineGeoView, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout()

        # sets the self.simulation object
        button = SimulationSelectionWidget()
        button.sigSimulationSelected.connect(self.set_simulation)
        self.layout.addWidget(button)

        # add regenerate button
        button = QtWidgets.QPushButton()
        button.setText("Update")
        self.layout.addWidget(button)

        button.clicked.connect(self.update)

        self.setLayout(self.layout)

    def update(self, **kwargs):
        plot_line = self.plot_line()
        sim = plot_line.simulation()
        try:
            if sim is None:
                raise ValueError("No Simulation Selected")
            elif not sim.loaded:
                raise ValueError("Simulation Not Loaded. Wait for simulation to load.")
            self.regenerate()
        except ValueError as err:
            QtWidgets.QMessageBox.information(self, "Error", str(err), QtWidgets.QMessageBox.Ok)


class GeoLineFactory:
    plot_line_class = PlotLineGeo
    plot_view_class = PlotLineGeoView
    plot_model_class = PlotLineModel

    def __init__(self):
        self._model = None

    def view(self, parent):
        return self.plot_view_class(parent)

    def plotter(self):
        return self.plot_line_class(self.model())

    def model(self):
        if self._model is None:
            self._model = self.plot_model_class(self.plot_line_class)

        return self._model
