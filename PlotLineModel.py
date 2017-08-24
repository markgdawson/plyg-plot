from PyQt5 import QtWidgets, QtCore, QtGui


class PlotLineView(QtWidgets.QWidget):
    def __init__(self, parent):
        super(PlotLineView, self).__init__(parent)
        self.stditem = QtGui.QStandardItem()
        self.stditem.setData(self, role=QtCore.Qt.UserRole)
        self.plotter = None

        # add label and checkbox
        self.label_checkbox = QtWidgets.QCheckBox()
        self.label_checkbox.setChecked(True)
        self.label_checkbox.setMinimumWidth(200)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.label_checkbox)
        self.setLayout(layout)

    def set_plotter(self, plotter):
        self.plotter = plotter

    def label(self):
        return self.stditem.text()

    def set_label(self, label):
        self.stditem.setText(label)
        self.label_checkbox.setText(self.label())

    def sync_label(self):
        if self.plotter is not None:
            self.plotter.set_label(self.label())
        self.label_checkbox.setText(self.label())


class PlotLineModel(QtGui.QStandardItemModel):

    sigLegendChanged = QtCore.pyqtSignal()

    def __init__(self, plot_line_class, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0
        self.itemChanged.connect(self.on_stditem_changed)
        self.PlotLineClass = plot_line_class
        self.plotter_generator = None

    def delete_line(self, index):
        plot_line = self.line(index)
        if plot_line is not None:
            plot_line.unplot()
        self.removeRow(index.row())
        self.sigLegendChanged.emit()

    def new_line(self):
        plot_line = self.PlotLineClass(self._view_parent)

        # set label and plotter
        default_label = "Line %d" % (self.lines_created + 1)
        plot_line.set_plotter(self.plotter_generator())
        plot_line.set_label(default_label)

        # since plot_line is a view widget, it should be added to the view widget stack
        self._view_parent.addWidget(plot_line)

        # insert stditem into view
        self.insertRow(0, plot_line.stditem)

        self.lines_created += 1
        self.sigLegendChanged.emit()
        return plot_line.stditem

    def lines(self):
        l = []
        for row in range(self.rowCount()):
            item = self.item(row)
            plot_line = item.data(QtCore.Qt.UserRole)
            l.append(plot_line)
        return l

    def line(self, index):
        item = self.item(index.row())
        if item is None:
            return None
        else:
            return item.data(QtCore.Qt.UserRole)

    def on_stditem_changed(self, item):
        # sync label to handle for changed item
        plot_line = item.data(QtCore.Qt.UserRole)
        plot_line.sync_label()
        self.sigLegendChanged.emit()

    def set_view_parent(self, view_parent):
        self._view_parent = view_parent

    def set_plotter_generator(self, plotter_generator):
        self.plotter_generator = plotter_generator
