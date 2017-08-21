from PyQt4 import QtGui, QtCore
import random


class PlotLine:

    def __init__(self, model=None):
        self._xdata = []
        self._ydata = []
        self._label = ""
        self._mpl_line = None
        self.model = model
        self.stditem = QtGui.QStandardItem()
        self.stditem.setData(self, QtCore.Qt.UserRole)
        self._simulation = None

        if self.model is not None:
            self.set_label(self.model.default_label())

            self.model.insertRow(0, self.stditem)
            self.model.lines_created += 1

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

    def data_changed(self):
        if self.model is not None:
            self.model.emit(self.model.dataChanged,self.model.createIndex(0,0),self.model.createIndex(0,self.model.rowCount()))


class PlotLineModel(QtGui.QStandardItemModel):

    def __init__(self, plot_line_class, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0
        self.PlotLineClass = plot_line_class

    def default_label(self):
        return "Line %d" % ( self.lines_created + 1 )

    def delete_line(self, index):
        plot_line = self.line(index)
        if plot_line is not None:
            plot_line.unplot()
        self.removeRow(index)

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


class PlotLineView(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PlotLineView, self).__init__(parent)
        self._plot_line = None
        self._simulation = None
        self.setEnabled(False)

    def set_plot_line(self, plot_line):
        self._plot_line = plot_line
        self.setEnabled(self._plot_line is not None)

    def plot_line(self):
        return self._plot_line

    def regenerate(self):
        if self._plot_line is not None:
            self._plot_line.regenerate()

    def set_simulation(self, simulation):
        self._simulation = simulation

    def simulation(self):
        return self._simulation
