from PyQt5 import QtWidgets, QtCore, QtGui


class PlotLine:

    def __init__(self):
        self._xdata = []
        self._ydata = []
        self._label = ""
        self._mpl_line = None
        self._view = None
        self.stditem = QtGui.QStandardItem()
        self.stditem.setData(self, QtCore.Qt.UserRole)
        self._simulation = None

        # callbacks to notify model of changes
        self._label_notify = None
        self._data_notify = None

    def set_view(self, view):
        self._view = view

    def view(self):
        return self._view

    def set_simulation(self, simulation):
        self._simulation = simulation

    def simulation(self):
        return self._simulation

    def set_label(self, label):
        self._label = label

        line = self.mpl_line()
        if line is not None:
            line.set_label(label)

        self.stditem.setText(label)
        self.label_changed()

    def label(self):
        return self._label

    def set_mpl_line(self, mpl_line):
        self._mpl_line = mpl_line

    def mpl_line(self):
        return self._mpl_line

    def xdata(self):
        return self._xdata

    def ydata(self):
        return self._ydata

    def regenerate(self):
        self.update()
        self.data_changed()

    def unplot(self):
        line = self.mpl_line()
        if line is not None:
            line.remove()

    def set_callbacks(self, label_notify, data_notify):
        self._label_notify = label_notify
        self._data_notify = data_notify

    def label_changed(self):
        if self._label_notify is not None:
            self._label_notify()

    def data_changed(self):
        if self._data_notify is not None:
            self._data_notify(self)

    def is_plotted(self):
        return self._mpl_line is not None


class PlotLineModel(QtGui.QStandardItemModel):

    sigLegendChanged = QtCore.pyqtSignal()
    sigPlotDataChanged = QtCore.pyqtSignal(PlotLine)

    def __init__(self, plot_line_factory, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0
        self.PlotLineFactory = plot_line_factory

    def default_label(self):
        return "Line %d" % (self.lines_created + 1)

    def delete_line(self, index):
        plot_line = self.line(index)
        if plot_line is not None:
            plot_line.unplot()
        self.removeRow(index)
        self.sigLegendChanged.emit()

    def new_line(self):
        plot_line = self.PlotLineFactory.plot_line()
        plot_line.set_label(self.default_label())
        plot_line.set_callbacks(self.label_changed, self.data_changed)
        self.PlotLineFactory.view(plot_line)

        self.insertRow(0, plot_line.stditem)
        self.lines_created += 1
        self.sigLegendChanged.emit()

    def set_label(self, index, string):
        if self.item(index) is not None:
            self.line(index).set_label(string)

    def lines(self):
        l = []
        for row in range(self.rowCount()):
            item = self.item(row)
            plot_line = item.data(QtCore.Qt.UserRole)
            l.append(plot_line)
        return l

    def line(self, index):
        item = self.item(index)
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
