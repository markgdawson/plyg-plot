from PyQt5 import QtWidgets, QtCore, QtGui
from PlotLineModel import PlotLineModel, PlotLineView
from LineComboBox import LineComboBox
from MPLWidget import MPLWidget, MyNavigationToolbar


class PlotWindow(QtWidgets.QDialog):
    def __init__(self, plotter_factory, parent=None):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.WindowMaximizeButtonHint)
        splitter = QtWidgets.QSplitter()
        splitter.setStyleSheet("QSplitter::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eee, stop:1 #ccc); border: 1px solid #777; width: 13px; margin-top: 2px; margin-bottom: 2px; border-radius: 4px; }")

        # create sidebar
        self.widget = QtWidgets.QWidget(self)
        widget_layout = QtWidgets.QVBoxLayout()
        self.widget.setLayout(widget_layout)
        splitter.addWidget(self.widget)

        # create plot line model
        plot_line_model = plotter_factory.model()
        self.plot_line_view = plotter_factory.view(self)

        # create Matplotlib widget
        self.mplWidget = MPLWidget(plot_line_model, self)
        splitter.addWidget(self.mplWidget)

        # add Navigation toolbar
        self.toolbar = MyNavigationToolbar(self.mplWidget.canvas, self, coordinates=False)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")
        widget_layout.addWidget(self.toolbar)

        # add line editor
        line_combo_box = LineComboBox(self, plot_line_model)
        widget_layout.addWidget(line_combo_box)

        # add plot line view
        widget_layout.addWidget(self.plot_line_view)

        # add stretch
        widget_layout.addStretch()

        # add status text
        self.text = QtWidgets.QLabel()
        widget_layout.addWidget(self.text)

        # set layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(splitter)

        # connect stale legend signals to regenerate_legend slot
        self.toolbar.sigStaleLegend.connect(self.mplWidget.regenerate_legend)
        plot_line_model.rowsInserted.connect(self.mplWidget.plot)
        plot_line_model.rowsRemoved.connect(self.mplWidget.plot)
        plot_line_model.rowsRemoved.connect(self.mplWidget.plot)
        line_combo_box.sigCurrentItemChanged.connect(self.plot_line_view.set_plot_line)

    def status_message(self, msg):
        self.text.setText(msg)

    def show(self):
        super(PlotWindow, self).show()
        # fix widget width to Navigation toolbar width
        width = self.toolbar.width() + 20
        self.widget.setMinimumWidth(width)

    def configure_plot(self):
        self.mplWidget.configure_plot()


