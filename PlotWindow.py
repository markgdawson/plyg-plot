from PyQt5 import QtWidgets, QtCore

from MPLWidget import MPLWidget, MyNavigationToolbar
from SideBar import SideBar


class PlotWindow(QtWidgets.QMainWindow):
    sigNewPlot = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, plot_line_model, available_views, parent=None):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.WindowMaximizeButtonHint)

        # no interpreter instance yet
        self.interpreter = None
        # create plot line model and view
        self.plot_line_model = plot_line_model

        # create sidebar
        sidebar = SideBar(plot_line_model, available_views, self)

        # create Matplotlib widget
        self.mpl_widget = MPLWidget(self.plot_line_model, self)

        # plot line model needs a function to generate plotters
        self.plot_line_model.set_plotter_generator(self.mpl_widget.new_plotter)

        # add toolbar
        self.toolbar = MyNavigationToolbar(self.mpl_widget.canvas, self, coordinates=False)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")
        self.addToolBar(self.toolbar)
        self.toolbar.setStyleSheet("border-bottom: 1px solid #777;")

        # add splitter
        splitter = QtWidgets.QSplitter()
        self.setCentralWidget(splitter)
        splitter.setStyleSheet("QSplitter::handle:horizontal {"
                               "    border-right: 1px solid #777;"
                               "    width: 1px;"
                               "}")
        splitter.addWidget(sidebar)
        splitter.addWidget(self.mpl_widget)

        # connect stale legend signals to update slot
        self.toolbar.sigStaleLegend.connect(self.mpl_widget.redraw)

        # connect toolbar signals
        self.toolbar.sigNewLine.connect(sidebar.new_line)
        self.toolbar.sigConfigurePlot.connect(self.mpl_widget.configure_plot)
        self.toolbar.sigStatusText.connect(self.statusBar().showMessage)
        self.toolbar.sigNewPlot.connect(lambda: self.sigNewPlot.emit(self.pos()))
        self.toolbar.sigDeleteLine.connect(sidebar.delete_current)
        self.toolbar.sigPythonInterpreter.connect(self.start_python_interpreter)

        sidebar.sigItemSelected.connect(self.toolbar.set_item_selected)

    def start_python_interpreter(self):
        if self.interpreter is None:
            from EmbeddedPythonInterpreter import EmbeddedPythonInterpreter
            import sys
            from IPython.core import release

            banner = ''.join([
                "Python %s\n" % sys.version.split("\n")[0],
                "IPython {version} -- An enhanced Interactive Python. Type '?' for help.\n\n".format(
                    version=release.version),
                "* The figure axis is available as plt (e.g. plt.plot([0,1],[0,2]) )\n",
                "* The update() function should be called to reflect changes in the plot window\n",
            ])

            self.interpreter = EmbeddedPythonInterpreter(banner=banner)

            # make variables available to interpreter
            self.interpreter.push_variable('plt', self.mpl_widget.ax)
            self.interpreter.push_variable('update', self.mpl_widget.redraw)

        self.interpreter.show()
