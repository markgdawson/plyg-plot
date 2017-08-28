from computation.torque import NoPatchesError
from main_window.plot_line_bases import PlotLineView
from sidebar_selectors import interface_build
import qt_error_handling


class PlotLineSlidingWindowView(PlotLineView):
    def __init__(self, parent, plotter, label):
        super(PlotLineSlidingWindowView, self).__init__(parent, plotter, label)
        self.torque = None
        self.patches = []
        self.num_revs_window = 1

        # build interface components
        patch_select = interface_build.face_patch_selector(self, patches_connect=self.patches_changed)

        sim_select = interface_build.simulation_selector(self, torque_connect=(patch_select.set_torque,
                                                                               self.set_torque))

        num_revs = interface_build.revolution_count_selector(self, self.num_revs_window,
                                                             revs_change_connect=self.set_num_revs)

        # layout
        self.layout().addWidget(sim_select)
        self.layout().addWidget(patch_select)
        self.layout().addWidget(num_revs)

    def set_num_revs(self, num_revs):
        self.num_revs_window = float(num_revs)
        self.plot()

    def patches_changed(self, patches):
        self.patches = patches
        self.plot()

    def set_torque(self, torque):
        self.torque = torque

    def plot(self):
        if self.torque is not None and self.patches is not None:
            try:
                try:
                    x, y = self.compute_value(self.torque)
                    self.plotter.plot(x, y)
                except NoPatchesError:
                    self.plotter.plot([], [])
            except Exception as error:
                qt_error_handling.python_exception_dialog(error, parent)

    def compute_value(self, torque):
        return [], []


class PlotLineCpSlidingWindowView(PlotLineSlidingWindowView):
    def compute_value(self, torque):
        y, x = torque.cp_mean_over_sliding_window(n_revs_window=self.num_revs_window, patches=self.patches)
        return x, y

    def help(self):
        return 'Mean cp, considering selected patches, averaged over a sliding window in time.'


class PlotLineTorqueSlidingWindowView(PlotLineSlidingWindowView):
    def compute_value(self, torque):
        y, x = torque.total_torque_mean_over_sliding_window(n_revs_window=self.num_revs_window, patches=self.patches)
        return x, y

    def help(self):
        return 'Sum of torques over selected patches, averaged over a sliding window in time.'


if __name__ == "__main__":
    import sys
    from main_window.main_plot_window import PlotWindow
    from main_window.plot_line_bases import PlotLineModel, PlotLineView
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    available_views = ('Plot Line Sliding Window', PlotLineCpSlidingWindowView)
    pw = PlotWindow(PlotLineModel(), available_views)
    pw.show()
    pw.toolbar.sigNewLine.emit()
    sys.exit(app.exec_())
