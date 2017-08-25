import matplotlib
import numpy as np
from RevolutionRangeSelector import RevolutionRangeSelector
from PlotLineModel import PlotLineView
from SimulationSelection import SimulationSelectionWidget
from ValueCheckboxSelector import FacePatchSelector


class AngularTorquePlotter:
    def __init__(self, plotter):
        self.torque = None

        self.nSteps = 200
        self.nRadialLines = 20
        self.plot_zero = 3.5
        self.plot_depth = 0.5
        self.plot_max = 1
        self.patches = []
        # Revolution before the revolution to plot (i.e. iRevStart = 4 plots average over revolution 5)
        self.iRevStart = 1.0
        self.iRevEnd = 2.0

        self.plotter = plotter

        self.handle = None
        self.temp_handles = []

    def set_torque_file(self, torque_file):
        self.torque = torque_file
        self.plot()

    def set_range(self, rev_start, rev_end):
        self.iRevStart = rev_start
        self.iRevEnd = rev_end
        self.plot()

    def set_patches(self, patches):
        self.patches = patches
        self.plot()

    def plot(self):
        self.plotter.clear(self.temp_handles)
        self.temp_handles = []

        # return if values are None
        if self.torque is None:
            return

        theta_bins = np.linspace(-np.pi, np.pi, self.nSteps)

        theta_dist = []

        a_torque = np.empty(self.nSteps)
        a_count = np.zeros(self.nSteps, dtype=int)
        a_theta = np.empty(self.nSteps)

        for i in range(len(self.patches)):
            patch_index = self.patches[i]
            torque = self.torque.torque
            x = self.torque.X[:, patch_index, 0]
            y = self.torque.X[:, patch_index, 1]

            theta = np.arctan2(x, y)

            start_ts = round(self.torque.params.StepsPerRev * self.iRevStart)
            end_ts = round(self.torque.params.StepsPerRev * self.iRevEnd)

            for iSource in range(start_ts, end_ts):
                if x[iSource] < -5:
                    raise ValueError('Not enough input values')

                index_target = np.argmin(np.abs(theta_bins - theta[iSource]))

                theta_dist.append(np.abs(theta_bins[index_target] - theta[iSource]))

                if not np.isnan(torque[iSource, patch_index]):
                    a_torque[index_target] += torque[iSource, patch_index]
                    a_count[index_target] += 1
                    a_theta[index_target] = theta[iSource]
                else:
                    raise ValueError('Warning: NaN encountered')

        if np.sum(a_count) == 0:
            return

        # only plot positive counts, and close loop
        indexes = a_count > 0
        indexes = [i for i, idx in enumerate(indexes) if idx]
        indexes.append(indexes[0])

        mean_torque = (a_torque[indexes] / a_count[indexes]) / 100
        mean_torque = mean_torque * self.plot_depth

        # noinspection PyTypeChecker
        min_torque = np.min(mean_torque)
        zero_offset = self.plot_zero + min_torque
        mean_torque = mean_torque - min_torque + zero_offset

        # add circle to plot
        circle = matplotlib.patches.Circle((0, 0), self.plot_zero, color=None, ec='gray', fill=False, linewidth=0.5, linestyle='--')
        h = self.plotter.add_artist(circle)
        self.temp_handles.append(h)

        theta_bins_mean = theta_bins[indexes]

        y = mean_torque * np.cos(theta_bins_mean)
        x = mean_torque * np.sin(theta_bins_mean)

        # plot lines
        def plot_radial_line(theta_plt, r_min, r_max):
            x_rad = np.empty([2, 2])
            x_rad[0, 0] = r_min * np.sin(theta_plt)
            x_rad[1, 0] = r_min * np.cos(theta_plt)

            x_rad[0, 1] = r_max * np.sin(theta_plt)
            x_rad[1, 1] = r_max * np.cos(theta_plt)

            h = self.plotter.auxplot(x_rad[0, :], x_rad[1, :])
            self.temp_handles.append(h)

        if self.nSteps > 0:
            line_indexes = [int(i) for i in np.round(np.linspace(0, self.nSteps, self.nRadialLines + 1))]
            for i in line_indexes:
                plot_radial_line(theta_bins_mean[i], self.plot_zero, mean_torque[i])

        self.plotter.set_properties(self.temp_handles, color='gray', linestyle=':', linewidth=1)

        self.plotter.plot(x, y)


class PlotLineAngularTorqueView(PlotLineView):
    def init(self):
        # plotting parameter defaults
        self.torque_plotter = AngularTorquePlotter(self.plotter)

        # add simulation selector
        sim_select = SimulationSelectionWidget()
        self.layout().addWidget(sim_select)

        # add face patch selector
        face_patch_selector = FacePatchSelector(self)
        face_patch_selector.set_label("Select Face Patches:")
        face_patch_selector.set_num_columns(4)
        self.layout().addWidget(face_patch_selector)

        # add revolution selector
        default_start = self.torque_plotter.iRevStart
        default_end = self.torque_plotter.iRevEnd

        revs = RevolutionRangeSelector(self)
        revs.init(default_start, default_end)
        self.layout().addWidget(revs)

        # setup connections
        sim_select.sigTorqueLoaded.connect(face_patch_selector.set_torque)
        sim_select.sigTorqueLoaded.connect(self.torque_plotter.set_torque_file)
        face_patch_selector.sigSelectionChanged.connect(self.torque_plotter.set_patches)
        revs.sigRangeChanged.connect(self.torque_plotter.set_range)
        sim_select.sigTorqueLoaded.connect(revs.set_max_from_torque_revs) # dynamically set range from torque file

    def replot(self):
        self.torque_plotter.plot()

        self.plotter.ax.set_xticks([])
        self.plotter.ax.set_yticks([])
        self.plotter.set_spine_visible(False)

        self.plotter.ax.set_xlim([-10, 10])
        self.plotter.ax.set_ylim([-10, 10])

if __name__ == "__main__":
    import sys
    from PlotWindow import PlotWindow
    from PlotLineModel import PlotLineModel, PlotLineView
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    pw = PlotWindow(PlotLineModel(PlotLineAngularTorqueView))
    pw.show()
    pw.inject_simulation_into_current_line()
    sys.exit(app.exec_())

