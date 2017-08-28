from main_window.plot_line_bases import PlotLineView
from sidebar_selectors import interface_build


class PlotLineGeoView(PlotLineView):
    def __init__(self, parent, plotter, label):
        super(PlotLineGeoView, self).__init__(parent, plotter, label)

        self.simulation = None

        # build interface components
        patch_select = interface_build.face_patch_selector(self, patches_connect=self.plot)

        sim_select = interface_build.simulation_selector(self, simulation_connect=(self.set_simulation,
                                                                                   patch_select.set_simulation))

        self.layout().addWidget(sim_select)
        self.layout().addWidget(patch_select)

    def set_simulation(self, simulation):
        self.simulation = simulation

    def plot(self, patches):
        if self.simulation is not None:
            geom = self.simulation.geom()
            if geom is not None:
                x, y = geom.get_patch_faces(patches)
                self.plotter.plot(x, y)


if __name__ == "__main__":
    import sys
    from main_window.main_plot_window import PlotWindow
    from main_window.plot_line_bases import PlotLineModel, PlotLineView
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    pw = PlotWindow(PlotLineModel, ('Plot Line Geo', PlotLineGeoView))
    pw.show()
    pw.toolbar.sigNewLine.emit()
    sys.exit(app.exec_())
