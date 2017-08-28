import collections

import matplotlib.pyplot as plt
import qtawesome as qta
from PyQt5 import QtWidgets, QtCore
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
            ('Configuration', 'Configure plot', 'subplots', 'configure_plot'),
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
    def __init__(self, line_model, parent=None):
        super(MPLWidget, self).__init__(parent)

        self.line_model = line_model

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Create canvas on which self.figure is plotted
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        self.layout().addWidget(self.canvas)

        self.text = QtWidgets.QLabel(self.canvas)
        # give text a length, to avoid needing to handle resize signals
        self.text.setText("                                                             ")
        self.text.setMargin(10)

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

    # this plot will automatically be labelled and managed internally
    def plot(self, x, y):
        self._master = self.auxplot(x, y, handle=self._master, label=True)
        self.redraw()

    # auxiliary/additional plotted lines, which must be handled by caller
    def auxplot(self, x, y, handle=None, label=False):
        if handle is None:
            handle, = self.ax.plot(x, y)
        else:
            handle.set_data(x, y)

        self._process_properties(label, handle)

        self.ax.relim()
        self.ax.autoscale_view()

        self.ax.figure.tight_layout()

        return handle

    def _process_properties(self, label, handle):

        if label:
            label = self._label
            self._labelled[handle] = True
        else:
            label = None
            if handle in self._labelled.keys() and self._labelled[handle]:
                self._labelled[handle] = False

        handle.set_label(label)

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
        self._remove_handle(handle)

        handle = self.ax.add_artist(artist)
        handle.set_label(label)

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
                line.set_label(label)

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
