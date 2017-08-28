import errors
from main_window.plot_line_bases import PlotLineView
from sidebar_selectors import interface_build


class PlotLineMeanValuesView(PlotLineView):
    def __init__(self, parent, plotter, label):
        super(PlotLineMeanValuesView, self).__init__(parent, plotter, label)

        self.torque = None
        self.patches = []
        self.start_range = 1.0
        self.end_range = 2.0

        # build interface components
        face_patch = interface_build.face_patch_selector(self, patches_connect=self.set_patches)

        revs = interface_build.revolution_range_selector(self, self.start_range, self.end_range,
                                                         range_connect=self.set_range)

        sim_select = interface_build.simulation_selector(self, torque_connect=(self.set_torque_file,
                                                                               face_patch.set_torque,
                                                                               revs.set_max_from_torque_revs))

        # add face patch selector
        self.layout().addWidget(sim_select)
        self.layout().addWidget(face_patch)
        self.layout().addWidget(revs)

    def set_torque_file(self, torque_file):
        self.torque = torque_file
        self.do_plot()

    def set_range(self, start, end):
        self.start_range = start
        self.end_range = end
        self.do_plot()

    def set_patches(self, patches):
        self.patches = patches
        self.do_plot()

    def do_plot(self):
        if self.torque is not None and len(self.patches) > 0:
            if self.start_range is not None and self.end_range is not None:
                try:
                    mean, time_steps = self.compute()
                    self.plotter.plot(time_steps, [mean, mean])
                except Exception as err:
                    self.plotter.plot([], [])
                    errors.warning(self, err)


class PlotLineMeanTorqueOverRevs(PlotLineMeanValuesView):
    def compute(self):
        return self.torque.mean_torque_over_revs(self.start_range, self.end_range, patches=self.patches)


class PlotLineMeanCpOverRevs(PlotLineMeanValuesView):
    def compute(self):
        return self.torque.mean_cp_over_revs(self.start_range, self.end_range, patches=self.patches)


if __name__ == "__main__":
    import sys
    from main_window.mpl_widget import MPLPlotter, MPLWidget
    from main_window.plot_line_bases import PlotLineModel
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    line_model = PlotLineModel()
    mpl_widget = MPLWidget(line_model)
    plotter = MPLPlotter(mpl_widget)

    pw = PlotLineMeanValuesView(None, plotter, 'Test Label' )
    pw.show()
    #pw = PlotWindow(PlotLineModel(), ('Plot Line Mean Torque', PlotLineMeanTorqueOverRevs))
    #pw.show()
    sys.exit(app.exec_())
