from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import qtawesome as qta

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
        reply = QtWidgets.QMessageBox.question(self, "Delete Confirmation", "Delete current line?")
        if reply == QtWidgets.QMessageBox.Yes:
            self.sigDeleteLine.emit()

    def new_plot(self):
        self.sigNewPlot.emit()

    def current_item_changed(self, plot_item):
        self.delete_action.setEnabled(plot_item is not None)


class MPLWidget(QtWidgets.QWidget):
    def __init__(self, line_model, parent=None):
        super(MPLWidget, self).__init__(parent)

        self.line_model = line_model

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Create canvas on which self.figure is plotted
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout().addWidget(self.canvas)

        self.text = QtWidgets.QLabel(self.canvas)
        # give text a length, to avoid needing to handle resize signals
        self.text.setText("                                                             ")
        self.text.setMargin(10)

        line_model.dataChanged.connect(self.regenerate_legend)
        line_model.dataChanged.connect(self.plot)

    def regenerate_legend(self):
        # always re-generate legend
        all_axes = self.figure.get_axes()
        for ax in all_axes:
            if ax.legend_ is not None:
                ax.legend_.remove()
            ax.legend(loc="best")
            if ax.legend_ is not None:
                ax.legend_.draggable(True)
        self.canvas.draw()

    def plot(self):
        # generate axes unless exist
        all_axes = self.figure.get_axes()
        if len(all_axes) == 0:
            ax = self.figure.add_subplot(111)
        else:
            ax = all_axes[0]

        for line in self.line_model.lines():
            if line.mpl_line() is None:
                l, = ax.plot(line.xdata(), line.ydata(), line.linestyle, label=line.label())
                line.set_mpl_line(l)
            else:
                line.mpl_line().set_data(line.xdata(), line.ydata())

        ax.relim()
        ax.autoscale_view()

        self.figure.tight_layout()
        self.regenerate_legend()

        # refresh canvas
        self.canvas.draw()

    def configure_plot(self):
        QtWidgets.QMessageBox.information(self, "No Configuration Options", "No configuration options available for this plot type", QtWidgets.QMessageBox.Ok)