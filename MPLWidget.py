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

    def __init__(self, figure_canvas, parent=None, coordinates=False):
        delete_text = 'Delete Line'
        new_line_text = 'New Line'
        new_plot_text = 'New Plot'

        self.toolitems = (
            (new_plot_text, 'Create new plot', 'fa.file-o', 'new_plot'),
            (None, None, None, None),
            (new_line_text, 'Add new plottable line', 'fa.plus', 'new_line'),
            (delete_text, 'Add current plottable line', 'fa.minus', 'delete_line'),
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
            ('Edit Paramters', 'Edit Plot Visuals', 'qt4_editor_options', 'do_edit_parameters'),
            ('Configuration', 'Configure plot', 'subplots', 'configure_plot')
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
    def update_legend(self):
        if self.ax.legend_ is not None:
            self.ax.legend_.remove()
            self.ax.legend()
        else:
            self.ax.legend(loc="best")

        if self.ax.legend_ is not None:
            self.ax.legend_.draggable(True)

        self.redraw()

    def redraw(self):
        self.canvas.draw()

    def new_plotter(self):
        return MPLPlotter(self)


class MPLPlotter():
    def __init__(self, mpl_widget):
        self.ax = mpl_widget.ax
        self.mpl_widget = mpl_widget
        self.mpl_lines = dict({})

    def plot(self, x, y, label=None, linestyle='-', index=-1):
        if index in self.mpl_lines.keys():
            line = self.mpl_lines[index]
            line.set_data(x, y)
        else:
            l, = self.ax.plot(x, y, linestyle, label=label)
            self.mpl_lines[index] = l

        self.ax.relim()
        self.ax.autoscale_view()

        self.ax.figure.tight_layout()

        # refresh canvas
        self.mpl_widget.redraw()

    def unplot(self):
        for line in self.mpl_lines:
            line.remove()

        self.mpl_widget.redraw()

    def set_label(self, label, index=-1):
        if index not in self.mpl_lines.keys():
            self.plot([], [], label=label, linestyle='-')
        self.mpl_lines[index].set_label(label)
        self.mpl_widget.update_legend()

