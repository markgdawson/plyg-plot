import collections

import matplotlib.pyplot as plt
import qtawesome as qta
from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class MyNavigationToolbar(NavigationToolbar):
    sigStaleLegend = QtCore.pyqtSignal()
    sigNewLine = QtCore.pyqtSignal()
    sigDeleteLine = QtCore.pyqtSignal()
    sigConfigurePlot = QtCore.pyqtSignal()
    sigStatusText = QtCore.pyqtSignal(str)
    sigNewPlot = QtCore.pyqtSignal()
    sigPythonInterpreter = QtCore.pyqtSignal()

    def __init__(self, figure_canvas, parent=None, coordinates=False):
        delete_text = 'Delete Line'
        new_line_text = 'New Line'
        new_plot_text = 'New Plot'

        self.toolitems = (
            (new_plot_text, 'Create new plot', 'fa.file-o', 'new_plot'),
            (None, None, None, None),
            (new_line_text, 'Add new plot line', 'fa.plus', 'new_line'),
            (delete_text, 'Delete current plot line', 'fa.minus', 'delete_line'),
            (None, None, None, None),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            (None, None, None, None),
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            (None, None, None, None),
            ('Edit Parameters', 'Edit Plot Visuals', 'qt4_editor_options', 'do_edit_parameters'),
            #('Configuration', 'Configure plot', 'subplots', 'configure_plot'),
            (None, None, None, None),
            ('Python Interpreter', 'Start a python interpreter', 'fa.terminal', 'do_start_interpreter')
        )

        super(MyNavigationToolbar, self).__init__(figure_canvas, parent=parent, coordinates=coordinates)

        # get created Qt actions
        self.new_plot_action = [a for a in self.actions() if a.text() == new_plot_text][0]
        self.delete_action = [a for a in self.actions() if a.text() == delete_text][0]
        self.new_line_action = [a for a in self.actions() if a.text() == new_line_text][0]

        # set delete action to no enabled
        self.delete_action.setEnabled(False)

    def _icon(self, icn):
        if icn[0:3] == 'fa.':
            return qta.icon(icn[:-4])
        else:
            return super(MyNavigationToolbar, self)._icon(icn)

    def do_edit_parameters(self):
        self.edit_parameters()
        self.sigStaleLegend.emit()

    def do_start_interpreter(self):
        self.sigPythonInterpreter.emit()

    def configure_plot(self):
        self.sigConfigurePlot.emit()

    def set_message(self, msg):
        self.sigStatusText.emit(msg)

    def new_line(self):
        self.sigNewLine.emit()

    def delete_line(self):
        reply = QtWidgets.QMessageBox.question(self, "Delete Confirmation", "Delete current line?",
                                               QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            self.sigDeleteLine.emit()

    def new_plot(self):
        self.sigNewPlot.emit()

    def set_item_selected(self, is_selected):
        self.delete_action.setEnabled(is_selected)


class MPLWidget(QtWidgets.QWidget):
    AxisEqual = 1
    GeometryPlot = 2
    TimePlot = 3

    UNITS_TIME_STEPS = 1
    UNITS_SECONDS = 2
    UNITS_REVOLUTIONS = 3
    UNITS_NONE = 0

    unit_choices = [('Time', UNITS_SECONDS),
                    ('Time Steps', UNITS_TIME_STEPS),
                    ('Revolutions', UNITS_REVOLUTIONS)]

    sigUnitsChanged = QtCore.pyqtSignal(int)

    def __init__(self, line_model, options=(), parent=None):
        super(MPLWidget, self).__init__(parent)

        self.axis_equal = False

        if self.AxisEqual in options:
            self.axis_equal = True

        self.line_model = line_model

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Create canvas on which self.figure is plotted
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        if self.GeometryPlot in options:
            self.ax.set_position([0.0, 0.0, 1.0, 1.0])
            self.units = self.UNITS_NONE

            for spine in self.ax.spines.values():
                spine.set_visible(False)

            self.ax.set_xticks([])
            self.ax.set_yticks([])

        if self.TimePlot in options:
            self.ax.set_ylabel('Magnitude')
            self.set_time_units(self.UNITS_SECONDS)
            self.unit_selector = QtWidgets.QComboBox(self)
            for name, unit in self.unit_choices:
                self.unit_selector.addItem(name, userData=unit)
            self.unit_selector.currentIndexChanged.connect(self.select_units)

        self.layout().addWidget(self.canvas)

        self.text = QtWidgets.QLabel(self.canvas)
        # give text a length, to avoid needing to handle resize signals
        self.text.setText("                                                             ")
        self.text.setMargin(10)

    def select_units(self):
        self.set_time_units(self.unit_selector.currentData())

    def set_time_units(self, units):
        self.units = units
        if units == self.UNITS_TIME_STEPS:
            self.ax.set_xlabel('Number of Time Steps')
        elif units == self.UNITS_SECONDS:
            self.ax.set_xlabel('Time (seconds)')
        elif units == self.UNITS_REVOLUTIONS:
            self.ax.set_xlabel('Time (revolutions)')
        self.sigUnitsChanged.emit(self.units)
        self.canvas.draw()

    def configure_plot(self):
        QtWidgets.QMessageBox.information(self, "No Configuration Options",
                                          "No configuration options available for this plot type",
                                          QtWidgets.QMessageBox.Ok)

    def redraw(self):
        if self.ax.legend_ is not None:
            self.ax.legend_.remove()
            self.ax.legend()
        else:
            self.ax.legend(loc="best")

        if self.ax.legend_ is not None:
            self.ax.legend_.draggable(True)

        self.canvas.draw()

    def new_plotter(self):
        return MPLPlotter(self)


class MPLPlotter:
    def __init__(self, mpl_widget):
        self.ax = mpl_widget.ax
        self.mpl_widget = mpl_widget
        self.mpl_lines = dict({})
        self.artists = dict({})
        self.visible = True
        self._label = None
        self._labelled = {}
        self._plotted = {}
        self._master = None

        # handle changes of units
        self.convert = dict({MPLWidget.UNITS_NONE: 1})
        self.mpl_widget.sigUnitsChanged.connect(self.units_changed)
        self.units = self.mpl_widget.units

    def units_changed(self, units):
        self.units = units
        for handle in self._plotted:
            x, y = handle.mydata
            label = handle.mylabelflag
            self.auxplot(x, y, handle, label)

    def set_convert(self, time_step_length, steps_per_rev):
        self.convert[MPLWidget.UNITS_SECONDS] = time_step_length
        self.convert[MPLWidget.UNITS_REVOLUTIONS] = 1 / steps_per_rev
        self.convert[MPLWidget.UNITS_TIME_STEPS] = 1

    # this plot will automatically be labelled and managed internally
    def plot(self, x, y):
        self._master = self.auxplot(x, y, handle=self._master, label=True)
        self.redraw()

    # auxiliary/additional plotted lines, which must be handled by caller
    def auxplot(self, x, y, handle=None, label=False):
        x_plot = self.convert[self.units] * x
        if handle is None:
            handle, = self.ax.plot(x_plot, y)
        else:
            handle.set_data(x_plot, y)

        handle.mydata = (x, y)
        handle.mylabelflag = label

        self._process_properties(label, handle)

        if self.mpl_widget.axis_equal:
            self.ax.axis('equal')

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)

        return handle

    @staticmethod
    def _handle_set_label(label, handle):
        if label is None or not label:
            label = '_nolegend_'

        handle.set_label(label)

    def _process_properties(self, label, handle):
        if label:
            label = self._label
            self._labelled[handle] = True
        else:
            label = None
            if handle in self._labelled.keys() and self._labelled[handle]:
                self._labelled[handle] = False

        self._handle_set_label(label, handle)

        # set visibility
        handle.set_visible(self.visible)

        # store handles
        self._plotted[handle] = True

    def redraw(self):
        self.mpl_widget.redraw()

    def _remove_handle(self, handle):
        if handle is None:
            return

        if handle in self._plotted.keys():
            del self._plotted[handle]

        if handle in self._labelled.keys():
            del self._labelled[handle]

        try:
            handle.remove()
        except ValueError:
            pass

    def add_artist(self, artist, handle=None, label=False):
        if label is None:
            label = False
        self._remove_handle(handle)

        handle = self.ax.add_artist(artist)
        self._handle_set_label(label, handle)

        self._process_properties(label, handle)

        self._plotted[handle] = True

        return handle

    def set_properties(self, handles, **kwargs):
        handles = self._make_iterable(handles)
        for handle in handles:
            handle.update(kwargs)

    def clear(self, handles=None):
        handles = self._make_iterable(handles)
        for handle in handles:
            handle.remove()
            self._remove_handle(handle)

        self.redraw()

    def set_label(self, label):
        self._label = label
        for line in self._labelled.keys():
            if self._labelled[line]:
                self._handle_set_label(label, line)

        self.redraw()

    def set_visibility(self, visible, handles=None):
        self.visible = visible

        handles = self._make_iterable(handles)
        for handle in handles:
            handle.set_visible(self.visible)

        self.redraw()

    def _make_iterable(self, handles):
        if handles is None:
            return list(self._plotted.keys())
        if isinstance(handles, collections.Iterable):
            return handles
        else:
            return [handles]

    def set_spine_visible(self, visibility, spines=('left', 'right', 'top', 'bottom')):
        for spine in spines:
            self.ax.spines[spine].set_visible(visibility)
