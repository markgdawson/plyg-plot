from PyQt5 import QtWidgets
import qt_error_handling
from main_window.plot_line_bases import PlotLineView
from sidebar_selectors import interface_build


class PlotLineTransientValuesView(PlotLineView):
    def __init__(self, parent, plotter, label):
        super(PlotLineTransientValuesView, self).__init__(parent, plotter, label)

        self.torque = None
        self.patches = []

        # build interface components
        face_patch = interface_build.face_patch_selector(self, patches_connect=self.set_patches)

        sim_select = interface_build.simulation_selector(self, torque_connect=(self.set_torque_file,
                                                                               face_patch.set_torque))
        # add face patch selector
        self.layout().addWidget(sim_select)
        self.layout().addWidget(face_patch)

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
            try:
                time_steps, mean = self.compute()
                self.plotter.plot(time_steps, mean)
            except Exception as err:
                self.plotter.plot([], [])
                qt_error_handling.python_exception_dialog(err, self)


class PlotLineTransientTotalTorque(PlotLineTransientValuesView):
    def compute(self):
        total_torque_per_time_step = self.torque.total_torque_per_time_step(patches=self.patches)
        return self.torque.time_steps, total_torque_per_time_step

    def help(self):
        return 'Sum of torque over all specified patches for each time step.'


class PlotLineTransientMeanTorque(PlotLineTransientValuesView):
    def compute(self):
        total_torque_per_time_step = self.torque.total_torque_per_time_step(patches=self.patches)
        mean_torque_per_time_step = total_torque_per_time_step / len(self.patches)
        return self.torque.time_steps, mean_torque_per_time_step

    def help(self):
        return 'Mean torque over specified patches for each time step.'


class PlotLineTransientCp(PlotLineTransientValuesView):
    def compute(self):
        cp_per_time_step, time_steps = self.torque.cp_per_time_step(patches=self.patches)
        return time_steps, cp_per_time_step

    def help(self):
        return 'Instantaneous CP over specified patches for each time step.'

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
