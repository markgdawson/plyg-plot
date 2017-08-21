from PyQt4 import QtGui
from PlotLineModel import PlotLine, PlotLineView, PlotLineModel
from SimulationComboBox import SimulationComboBox


class PlotLineGeo(PlotLine):
    linestyle = '-'

    def __init__(self, model=None):
        super(PlotLineGeo, self).__init__(model)

    def update(self):
        geom = self.simulation().geom()
        if not geom.geo.loaded:
            print('Loading %s', self.simulation().geo_file)

        self._xdata, self._ydata = geom.getPatchFaces(range(12,14))


class PlotLineGeoView(PlotLineView):
    def __init__(self, parent=None):
        super(PlotLineGeoView, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout()

        # sets the self.simulation object
        sim_select = SimulationComboBox(self)
        self.layout.addWidget(sim_select)

        # add regenerate button
        button = QtGui.QPushButton()
        button.setText("Update")
        self.layout.addWidget(button)

        self.connect(button, button.clicked, self.update)

        self.setLayout(self.layout)

    def update(self):
        plot_line = self.plot_line()
        plot_line.set_simulation(self.simulation())
        self.regenerate()


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
