from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class MyNavigationToolbar(NavigationToolbar):
    sigStaleLegend = QtCore.pyqtSignal()

    def __init__(self, figure_canvas, parent= None, coordinates=False):
        self.toolitems = (
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

        super(MyNavigationToolbar,self).__init__(figure_canvas, parent=parent, coordinates=coordinates)

    def do_edit_parameters(self):
        self.edit_parameters()
        self.emit(self.sigStaleLegend)

    def configure_plot(self):
        self.parent.configure_plot()

    def set_message(self,msg):
        self.parent.status_message(msg)


class MPLWidget(QtGui.QWidget):
    def __init__(self, line_model, parent = None):
        super(MPLWidget, self).__init__(parent)

        self.line_model = line_model

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        # Create canvas on which self.figure is plotted
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot()

        self.layout().addWidget(self.canvas)

        self.text = QtGui.QLabel(self.canvas)
        self.text.setText("                                                             ")
        self.text.setMargin(10)

        self.connect(line_model, line_model.dataChanged, self.regenerate_legend)
        self.connect(line_model, line_model.dataChanged, self.plot)

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

        lines = self.line_model.lines()
        for line in lines:
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
        QtGui.QMessageBox.information(self,"No Configuration Options","Error: No configuration options available for this plot type",QtGui.QMessageBox.Ok);

