import functools

import matplotlib.pyplot as plt
import numpy as np


class IncompleteFile(EOFError):
    pass


class NoPatchesError(EOFError):
    pass


class TorqueFile:
    #
    # Sliding window quantities
    #

    def mean_torque_sliding_window(self, n_revs_window=1, patches=None):

        total_torque_per_time_step, time_steps = self.total_torque_per_time_step(patches=patches)

        num_steps = int(np.round(n_revs_window * self.params.StepsPerRev))

        # compute mean torque
        mean_torque_prev_rev = []
        for iTS in range(0, self.num_time_steps - num_steps):
            torque = np.mean(total_torque_per_time_step[iTS:iTS + num_steps])
            mean_torque_prev_rev.append(torque)

        mean_torque_prev_rev = np.array(mean_torque_prev_rev)
        time_steps_end_rev = np.array([iTS + num_steps for iTS in range(0, self.num_time_steps - num_steps)])

        return mean_torque_prev_rev, time_steps_end_rev

    def mean_cp_sliding_window(self, n_revs_window=1, plot=False, patches=None, units=None):

        torque, time_steps_end_rev = self.mean_torque_sliding_window(n_revs_window=n_revs_window, patches=patches)
        cp = self.cp(torque)

        if plot:
            self._plot_transient_over_range(cp, time_steps=time_steps_end_rev, units=units, y_label='Cp')

        return cp, time_steps_end_rev

    #
    # Quantities per time step
    #
    @functools.lru_cache(20)
    def total_torque_per_time_step(self, patches=None, plot=False, units=None):
        if patches is None or len(patches) == 0:
            raise NoPatchesError

        tot_torque = np.zeros(self.num_time_steps)

        time_steps = list(range(0, self.num_time_steps))

        for iTS in time_steps:
            for patch_index in patches:
                tot_torque[iTS] = tot_torque[iTS] + self.torque[iTS, patch_index]

        if plot:
            self._plot_transient_over_range(tot_torque, time_steps, units=units)

        return tot_torque, time_steps

    def cp_per_time_step(self, patches=None, plot=False, units=None):

        torque, time_steps = self.total_torque_per_time_step(patches=patches)

        cp = self.cp(torque)

        if plot:
            self._plot_transient_over_range(cp, time_steps, units=units, y_label='Cp')

        return cp, time_steps

    #
    # Mean values over ranges
    #
    def mean_torque_over_revs(self, start_rev, end_rev, patches=None, plot=False, units=None):
        total_torque_per_time_step = self.total_torque_per_time_step(patches=patches)

        start_ts = self.get_rev_time_step(start_rev)
        end_ts = self.get_rev_time_step(end_rev)

        time_steps = self.time_steps[start_ts:end_ts]
        total_torque_per_time_step = total_torque_per_time_step[start_ts:end_ts]

        mean_torque = np.mean(total_torque_per_time_step)

        if plot:
            self._plot_transient_over_range(total_torque_per_time_step, time_steps=time_steps, units=units)
            self._plot_scalar_over_range(mean_torque, start_ts, end_ts, units=units)

        return mean_torque, time_steps[[0, -1]]

    def mean_cp_over_revs(self, start_rev, end_rev, patches=None, units=None, plot=False):
        mean_torque, time_steps = self.mean_torque_over_revs(start_rev, end_rev, patches=patches)
        simulated_power = self.simulated_power(mean_torque)
        theoretical_power = self.theoretical_power()

        mean_cp = (simulated_power / theoretical_power) * 100

        if plot:
            self._plot_scalar_over_range(mean_cp, time_steps[0], time_steps[-1], units=units)

        return mean_cp, time_steps

    #
    # Convert between time units
    #

    UNITS_TIME = 0
    UNITS_REVOLUTIONS = 1
    UNITS_TIME_STEPS = 1

    def convert_units(self, time_steps, units=None):
        if units is None:
            units = self.UNITS_REVOLUTIONS

        if units == self.UNITS_TIME:
            time = [self.time[i] for i in time_steps - 1]
            x_label = 'time (s)'
        elif units == self.UNITS_REVOLUTIONS:
            time = np.true_divide(time_steps, self.params.StepsPerRev)
            x_label = 'time (revolutions)'
        elif units == self.UNITS_TIME_STEPS:
            time = time_steps
            x_label = 'time (number of time steps)'
        else:
            raise ValueError('%s not valid units value' % units)

        return time, x_label

    #
    #  File reading and setup
    #

    def __init__(self, file_name, params=None, label=None):
        self.fileName = file_name
        self.label = label
        self.params = params

        self.number_patches = None
        self.num_time_steps = None
        self.time_steps = None
        self.patches = None
        self.time = None
        self.omega = None
        self.torque = None
        self.F = None
        self.X = None
        self.area = None

        try:
            self.read_file()
            self._after_file_read_hook()
        except IncompleteFile as err:
            self._after_file_read_hook()
            raise err

    @staticmethod
    def read_header(file):
        tmp = file.readline().rstrip('\n')
        tmp = tmp.split(',')

        number_patches = int(tmp[1])
        number_time_steps = int(tmp[0])

        # discard header
        file.readline()

        return number_patches, number_time_steps

    def read_patch_numbers(self):
        with open(self.fileName) as file:
            self.number_patches, self.num_time_steps = self.read_header(file)
            self.patches = np.empty([self.number_patches], dtype=int)

            for iPatch in range(0, self.number_patches):
                tmp = file.readline().split(',')

                self.patches[iPatch] = int(tmp[2])

    def read_file(self):
        time_step = 0
        try:
            with open(self.fileName) as file:
                self.read_patch_numbers()

                max_patch_index = np.max(self.patches) + 1

                self.number_patches, self.num_time_steps = self.read_header(file)

                self.time = np.empty(self.num_time_steps, dtype=float)
                self.omega = np.empty(max_patch_index, dtype=float)

                self.torque = np.empty([self.num_time_steps, max_patch_index], dtype=float)

                self.F = np.empty([self.num_time_steps, max_patch_index, 3])

                self.X = np.empty([self.num_time_steps, max_patch_index, 3])

                self.area = np.empty([self.num_time_steps, max_patch_index])

                # read torque file
                lines = []
                for time_step in range(0, self.num_time_steps):
                    for iPatch in range(0, self.number_patches):
                        line = file.readline()
                        lines.append(line)
                        tmp = line.split(',')

                        if len(tmp[0]) == 0 or len(tmp) < 11:
                            raise IncompleteFile('Torque file incomplete: %s' % self.fileName)

                        self.time[time_step] = float(tmp[0])
                        self.omega[iPatch] = float(tmp[1])

                        patch_index = int(self.patches[iPatch])

                        if not patch_index == float(tmp[2]):
                            raise ValueError('invalid file')

                        self.torque[time_step, patch_index] = float(tmp[3])

                        self.F[time_step, patch_index, 0] = float(tmp[4])
                        self.F[time_step, patch_index, 1] = float(tmp[5])
                        self.F[time_step, patch_index, 2] = float(tmp[6])

                        self.X[time_step, patch_index, 0] = float(tmp[7])
                        self.X[time_step, patch_index, 1] = float(tmp[8])
                        self.X[time_step, patch_index, 2] = float(tmp[9])

                        self.area[time_step, patch_index] = float(tmp[10])

        except IncompleteFile as incomplete_file_exception:
            # remove last (possibly incomplete)
            time_step = time_step - 1
            self.truncate_torque_tile(time_step)
            raise incomplete_file_exception

    def _after_file_read_hook(self):
        self.time_steps = np.array([i + 1 for i in range(0, self.num_time_steps)])

    def truncate_torque_tile(self, num_time_steps):
        self.time = self.time[1:num_time_steps]

        self.torque = self.torque[1:num_time_steps, :]

        self.F = self.F[1:num_time_steps, :, :]

        self.X = self.X[1:num_time_steps, :, :]

        # adjust for zero indexing
        self.num_time_steps = num_time_steps - 1

    #
    # Accessors
    #

    def num_revs(self):
        return self.num_time_steps / self.params.StepsPerRev

    def max_time(self):
        return np.max(self.time)

    #
    # get start/end ranges
    #

    def get_rev_time_step(self, rev):
        if rev == 0:
            raise ValueError('input revolution value should be larger than 0')
        time_step = int((rev - 1) * self.params.StepsPerRev)

        if time_step > self.num_time_steps or time_step < 0:
            raise ValueError('revolution %d is outside of range' % rev)

        return time_step

    #
    # Drawing/Plotting Methods
    #

    def draw_torque_vector(self, time_step, patch_index, scale_factor=3000, linestyle='-', color=False):
        vector_start = self.X[time_step, patch_index, :2]
        force = self.F[time_step, patch_index, :2]
        force_unit = force / np.sqrt(np.sum(force ** 2))
        torque = self.torque[time_step, patch_index]
        torque_in_force_direction = force_unit * (np.abs(torque) / scale_factor)
        vector_end = vector_start + torque_in_force_direction

        plt.arrow(vector_start[0], vector_start[1], vector_end[0] - vector_start[0], vector_end[1] - vector_start[1],
                  head_width=0.1, head_length=0.2, fc=color, ec=color, linestyle=linestyle, linewidth=1)

        return torque, (vector_start, vector_end)

    def _plot_transient_over_range(self, transient, time_steps=None, units=None, color=None, y_label=None):

        if time_steps is None:
            time_steps = self.time_steps

        time, x_label = self.convert_units(time_steps, units=units)

        if color is None:
            l, = plt.plot(time, transient, label=self.label)
        else:
            l, = plt.plot(time, transient, label=self.label, color=color)

        plt.xlabel(x_label)

        if y_label is not None:
            plt.ylabel(y_label)

        return time, transient, l

    def _plot_scalar_over_range(self, scalar, time_step_start, time_step_end, units=None):
        time_steps = np.array([time_step_start, time_step_end], dtype=int)

        time, x_label = self.convert_units(time_steps, units=units)

        l, = plt.plot(time, [scalar, scalar])

        plt.xlabel(x_label)

        return l, time

    # Power and Torque per Time Step
    def simulated_power(self, torque):
        return torque * (self.params.TSR * self.params.Uinf / self.params.R)

    def theoretical_power(self):
        return 0.5 * self.params.density * (self.params.R * 2) * self.params.Uinf ** 3

    def cp(self, torque):
        return 100 * self.simulated_power(torque) / self.theoretical_power()

    def delta_t(self):
        return self.time[-1] - self.time[-2]


class ResumedTorqueFile(TorqueFile):
    def __init__(self, file_names, params=None, label=None):
        super(ResumedTorqueFile, self).__init__(file_names, params=None, label=None)
        self.fileName = file_names[1]
        self.label = label
        self.params = params
        self.read_file()

        time = self.time
        omega = self.omega
        torque = self.torque
        force = self.F
        x = self.X
        area = self.area

        self.fileName = file_names[0]

        self.read_file()

        self.time = np.append(self.time, time)
        self.omega = np.append(self.omega, omega)

        self.torque = np.append(self.torque, torque, axis=0)

        self.F = np.append(self.F, force, axis=0)

        self.X = np.append(self.X, x, axis=0)

        self.area = np.append(self.area, area, axis=0)

        self.patches = self.patches

        self.nTS = len(self.time)

        self._after_file_read_hook()
