import matplotlib.patches as mplpatches
import numpy as np

import InterfaceBuilders
import errors
from PlotLineModel import PlotLineView


class AngularTorquePlotter:
    def __init__(self, plotter):
        self.torque = None

        self.nSteps = 200
        self.nRadialLines = 20
        self.plot_zero = 3.5
        self.plot_depth = 0.5 / 100
        self.plot_max = 1
        self.patches = []
        self.iRevStart = 1.0
        self.iRevEnd = 2.0

        self.plotter = plotter

        self.radial_handles = []
        self.circle_handle = None

        self.bin_theta = []
        self.bin_index = []

    def set_torque_file(self, torque_file):
        self.torque = torque_file
        self.plot()

    def set_range(self, rev_start, rev_end):
        self.iRevStart = rev_start
        self.iRevEnd = rev_end
        self.plot()

    def set_patches(self, patches):
        self.patches = patches
        try:
            self.plot()
        except ValueError as err:
            errors.warning(self, err)

    def theta_bins(self):
        if len(self.bin_index) != 0:
            return

        # theta value, indexed by time step and patch number
        theta_step = np.arctan2(self.torque.X[:, :, 0], self.torque.X[:, :, 1])
        theta_positive = theta_step + np.pi

        # zero-indexed bin number for positive theta
        bin_size = 2 * np.pi / self.nSteps
        self.bin_index = np.floor(theta_positive / bin_size)
        self.bin_theta = (np.arange(0, self.nSteps, 1, dtype=int) + 0.5) * bin_size - np.pi

    def plot_circle(self):
        # add circle to plot
        if self.circle_handle is None:
            circle = mplpatches.Circle((0, 0), self.plot_zero, color=None, ec='gray', fill=False, linewidth=0.5,
                                       linestyle='--')
            self.circle_handle = self.plotter.add_artist(circle, self.circle_handle)

    def plot(self):
        # return if values are None
        if self.torque is None or len(self.patches) == 0:
            return

        self.theta_bins()
        mean_torque = self.mean_torque(self.iRevStart, self.iRevEnd)

        # make plots circular
        bins = np.append(self.bin_theta, self.bin_theta[0])
        mean_torque = np.append(mean_torque, mean_torque[0])

        if np.any(np.isnan(mean_torque)):
            raise ValueError("NaN found in input TORQUE.csv file")

        # scale mean torque by plot depth
        mean_torque = mean_torque * self.plot_depth
        min_torque = np.min(mean_torque)
        zero_offset = self.plot_zero + min_torque
        mean_torque = mean_torque - min_torque + zero_offset

        self.plot_circle()

        y = mean_torque * np.cos(bins)
        x = mean_torque * np.sin(bins)

        self.plot_radial_lines(bins, mean_torque)

        self.plotter.plot(x, y)

    def plot_radial_lines(self, bins, mean_torque):
        if len(self.radial_handles) > 0:
            return

        self.plotter.clear(self.radial_handles)
        self.radial_handles = []

        # plot lines
        def plot_radial_line(theta_plt, r_min, r_max):
            x_rad = np.empty([2, 2])
            x_rad[0, 0] = r_min * np.sin(theta_plt)
            x_rad[1, 0] = r_min * np.cos(theta_plt)

            x_rad[0, 1] = r_max * np.sin(theta_plt)
            x_rad[1, 1] = r_max * np.cos(theta_plt)

            h = self.plotter.auxplot(x_rad[0, :], x_rad[1, :])
            self.radial_handles.append(h)

        if self.nSteps > 0:
            line_indexes = [int(i) for i in np.round(np.linspace(0, self.nSteps, self.nRadialLines + 1))]
            for i in line_indexes:
                plot_radial_line(bins[i], self.plot_zero, mean_torque[i])

        self.plotter.set_properties(self.radial_handles, color='gray', linestyle=':', linewidth=1)

    def mean_torque(self, start_rev, end_rev):

        if len(self.patches) == 0:
            return

        # start and end range
        start_ts = round(self.torque.params.StepsPerRev * start_rev)
        end_ts = round(self.torque.params.StepsPerRev * end_rev)

        torque = self.torque.torque

        bi_tmp = self.bin_index[start_ts:end_ts, self.patches]
        t_tmp = torque[start_ts:end_ts, self.patches]

        # check number of contributions
        num_contributions = [np.sum(np.where(bi_tmp == i, [1], [0])) for i in range(0, self.nSteps)]

        if np.min(num_contributions) == 0:
            raise ValueError("Some bins have zero values. Raise time range or reduce number of bins")

        # compute mean torque in each bin (extending to be circular)
        tot_torque = np.array([np.sum(np.where(bi_tmp == i, t_tmp, [0])) for i in range(0, self.nSteps)])

        return tot_torque / num_contributions


class PlotLineAngularTorqueView(PlotLineView):
    def __init__(self, parent, plotter, label):
        super(PlotLineAngularTorqueView, self).__init__(parent, plotter, label)

        # plotting parameter defaults
        self.torque_plotter = AngularTorquePlotter(self.plotter)

        # build interface components
        patch_select = InterfaceBuilders.face_patch_selector(self, patches_connect=self.torque_plotter.set_patches)

        revs = InterfaceBuilders.revolution_range_selector(self, self.torque_plotter.iRevStart,
                                                           self.torque_plotter.iRevEnd,
                                                           range_connect=self.torque_plotter.set_range)

        sim_select = InterfaceBuilders.simulation_selector(self, torque_connect=(patch_select.set_torque,
                                                                                 self.torque_plotter.set_torque_file,
                                                                                 revs.set_max_from_torque_revs))

        self.layout().addWidget(sim_select)
        self.layout().addWidget(patch_select)
        self.layout().addWidget(revs)

        # self.torque_plotter.plot()
        #
        # self.plotter.ax.set_xticks([])
        # self.plotter.ax.set_yticks([])
        # self.plotter.set_spine_visible(False)
        #
        # self.plotter.ax.set_xlim([-10, 10])
        # self.plotter.ax.set_ylim([-10, 10])


if __name__ == "__main__":
    import sys
    from PlotWindow import PlotWindow
    from PlotLineModel import PlotLineModel, PlotLineView
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    model = PlotLineModel()
    available_views = ('Plot Line Angular Torque', PlotLineAngularTorqueView)
    pw = PlotWindow(PlotLineModel, available_views)
    pw.show()
    pw.inject_simulation_into_current_line()
    sys.exit(app.exec_())
