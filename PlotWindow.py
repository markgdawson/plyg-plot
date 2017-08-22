from PyQt5 import QtWidgets, QtCore
from LineComboBox import LineComboBox
from MPLWidget import MPLWidget, MyNavigationToolbar


class PlotWindow(QtWidgets.QMainWindow):

    sigNewPlot = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, plotter_factory, parent=None):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.WindowMaximizeButtonHint)

        # create plot line model and view
        self.plot_line_model = plotter_factory.model()
        self.plot_line_view = plotter_factory.view(self)

        # create sidebar
        self.sidebar = QtWidgets.QWidget(self)
        self.sidebar.setLayout(QtWidgets.QVBoxLayout())

        line_combo_box = LineComboBox(factory=plotter_factory, parent=self)
        self.sidebar.layout().addWidget(line_combo_box)

        self.sidebar.layout().addWidget(self.plot_line_view)
        self.sidebar.setMinimumWidth(250)

        # create Matplotlib widget
        self.mplWidget = MPLWidget(self.plot_line_model, self)

        # add toolbar
        self.toolbar = MyNavigationToolbar(self.mplWidget.canvas, self, coordinates=False)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")
        self.addToolBar(self.toolbar)
        self.toolbar.setStyleSheet("border-bottom: 1px solid #777;")

        # add stretch
        self.sidebar.layout().addStretch()

        # add splitter
        splitter = QtWidgets.QSplitter()
        self.setCentralWidget(splitter)
        splitter.setStyleSheet("QSplitter::handle:horizontal {"
                               "    border-right: 1px solid #777;"
                               "    width: 1px;"
                               "}")
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.mplWidget)

        # connect stale legend signals to regenerate_legend slot
        self.toolbar.sigStaleLegend.connect(self.mplWidget.regenerate_legend)
        self.plot_line_model.rowsInserted.connect(self.mplWidget.plot)
        self.plot_line_model.rowsRemoved.connect(self.mplWidget.plot)
        self.plot_line_model.rowsRemoved.connect(self.mplWidget.plot)
        line_combo_box.sigCurrentItemChanged.connect(self.plot_line_view.set_plot_line)

        # connect toolbar signals
        self.toolbar.sigNewLine.connect(self.plot_line_model.new_line)
        self.toolbar.sigDeleteLine.connect(line_combo_box.delete_current)
        self.toolbar.sigConfigurePlot.connect(self.mplWidget.configure_plot)
        self.toolbar.sigStatusText.connect(self.statusBar().showMessage)
        self.toolbar.sigNewPlot.connect(self.new_plot)

        line_combo_box.sigCurrentItemChanged.connect(self.toolbar.current_item_changed)

    def new_plot(self):
        self.sigNewPlot.emit(self.pos())
