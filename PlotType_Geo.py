from PyQt5 import QtWidgets
from SimulationSelection import SimulationSelectionWidget
from PlotLineModel import PlotLineView
from ValueCheckboxSelector import FacePatchSelector


class PlotLineGeoView(PlotLineView):
    def init(self):
        # add simulation selector
        self.sim_select = SimulationSelectionWidget()
        self.sim_select.sigSimulationLoaded.connect(self.face_patch_selector.set_simulation)
        self.layout().addWidget(self.sim_select)

        # add face patch selector
        self.face_patch_selector = FacePatchSelector(self)
        self.face_patch_selector.set_label("Select Face Patches:")
        self.face_patch_selector.set_num_columns(4)
        self.face_patch_selector.sigSelectionChanged.connect(self.plot)
        self.layout().addWidget(self.face_patch_selector)

    def plot(self, patches):
        simulation = self.sim_select.simulation
        if simulation is not None:
            geom = simulation.geom()
            if geom is not None:
                x, y = geom.get_patch_faces(patches)
                self.plotter.plot(x, y)

if __name__ == "__main__":
    import sys
    from PlotWindow import PlotWindow
    from PlotLineModel import PlotLineModel, PlotLineView
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    pw = PlotWindow(PlotLineModel(PlotLineGeoView))
    pw.show()
    pw.toolbar.sigNewLine.emit()
    sys.exit(app.exec_())
