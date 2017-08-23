from PyQt5 import QtWidgets, QtCore, QtGui


class PlotLine:

    def __init__(self):
        self._xdata = []
        self._ydata = []
        self._line_handle = None
        self._view = None
        self.stditem = QtGui.QStandardItem()
        self.stditem.setData(self, QtCore.Qt.UserRole)
        self._simulation = None

    def set_view(self, view):
        self._view = view

    def view(self):
        return self._view

    def set_simulation(self, simulation):
        self._simulation = simulation

    def simulation(self):
        return self._simulation

    def label(self):
        return self.stditem.text()

    def set_line_handle(self, line_handle):
        self._line_handle = line_handle

    def line_handle(self):
        return self._line_handle

    def xdata(self):
        return self._xdata

    def ydata(self):
        return self._ydata

    def regenerate(self):
        self.generate()
        model = self.stditem.model()
        model.sigPlotDataChanged.emit(self)

    def unplot(self):
        line = self.line_handle()
        if line is not None:
            line.remove()

    def set_callbacks(self, label_notify, data_notify):
        self._label_notify = label_notify
        self._data_notify = data_notify

    def generate(self):
        pass


class PlotLineModel(QtGui.QStandardItemModel):

    sigLegendChanged = QtCore.pyqtSignal()
    sigPlotDataChanged = QtCore.pyqtSignal(PlotLine)

    def __init__(self, plot_line_factory, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0
        self.PlotLineFactory = plot_line_factory
        self.itemChanged.connect(self.legend_changed)

    def legend_changed(self, item):
        # sync label to handle for changed item
        plot_line = item.data(QtCore.Qt.UserRole)
        handle = plot_line.line_handle()
        handle.set_label(plot_line.label())
        self.sigLegendChanged.emit()

    def delete_line(self, index):
        plot_line = self.line(index)
        if plot_line is not None:
            plot_line.unplot()
        self.removeRow(index.row())
        self.sigLegendChanged.emit()

    def new_line(self):
        plot_line = self.PlotLineFactory.plot_line()
        self.PlotLineFactory.view(plot_line)

        item = plot_line.stditem

        default_label = "Line %d" % (self.lines_created + 1)
        item.setText(default_label)

        self.insertRow(0, item)
        self.lines_created += 1
        self.sigLegendChanged.emit()
        return item

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

    def data_changed(self, plot_line):
        self.sigPlotDataChanged.emit(plot_line)

    def label_changed(self):
        self.sigLegendChanged.emit()


class PlotLineView(QtWidgets.QWidget):
    def __init__(self, plot_line, parent=None):
        super(PlotLineView, self).__init__(parent)
        self._plot_line = plot_line

    def plot_line(self):
        return self._plot_line

    def regenerate(self):
        if self._plot_line is not None:
            self._plot_line.regenerate()

class PlotLineFactory:
    plot_line_class = None
    plot_view_class = None
    plot_model_class = None

    def __init__(self):
        self._model = None
        self.view_parent = None

    def view(self, plot_line):
        view = self.plot_view_class(plot_line, self.view_parent)
        plot_line.set_view(view)
        self.view_parent.addWidget(view)

    def plot_line(self):
        return self.plot_line_class()

    def model(self):
        if self._model is None:
            self._model = self.plot_model_class(self)

        return self._model

    def set_view_parent(self, parent=None):
        self.view_parent = parent
