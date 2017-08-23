from PyQt5 import QtWidgets, QtCore
from MPLWidget import MPLWidget, MyNavigationToolbar
from SideBar import SideBar


class PlotWindow(QtWidgets.QMainWindow):

    sigNewPlot = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, plotter_factory, parent=None):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.WindowMaximizeButtonHint)

        # create plot line model and view
        self.plot_line_model = plotter_factory.model()

        # create sidebar
        sidebar = SideBar(plotter_factory, self)

        # create Matplotlib widget
        mpl_widget = MPLWidget(self.plot_line_model, self)

        # add toolbar
        self.toolbar = MyNavigationToolbar(mpl_widget.canvas, self, coordinates=False)
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
        splitter.addWidget(mpl_widget)

        # connect stale legend signals to regenerate_legend slot
        self.toolbar.sigStaleLegend.connect(mpl_widget.regenerate_legend)
        self.plot_line_model.rowsInserted.connect(mpl_widget.plot)
        self.plot_line_model.rowsRemoved.connect(mpl_widget.plot)
        self.plot_line_model.rowsRemoved.connect(mpl_widget.plot)

        # connect toolbar signals
        self.toolbar.sigNewLine.connect(sidebar.new_line)
        self.toolbar.sigConfigurePlot.connect(mpl_widget.configure_plot)
        self.toolbar.sigStatusText.connect(self.statusBar().showMessage)
        self.toolbar.sigNewPlot.connect(lambda: self.sigNewPlot.emit(self.pos()))
        self.toolbar.sigDeleteLine.connect(sidebar.delete_current)

        sidebar.sigItemSelected.connect(self.toolbar.set_item_selected)

