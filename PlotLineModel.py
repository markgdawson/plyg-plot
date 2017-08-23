from PyQt5 import QtWidgets, QtCore, QtGui


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
            self.model.dataChanged.emit(self.model.createIndex(0, 0), self.model.createIndex(0, self.model.rowCount()))


class PlotLineModel(QtGui.QStandardItemModel):
    def __init__(self, plot_line_class, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0
        self.PlotLineClass = plot_line_class

    def default_label(self):
        return "Line %d" % (self.lines_created + 1)

    def delete_line(self, index):
        plot_line = self.line(index)
        if plot_line is not None:
            plot_line.unplot()
        self.removeRow(index)

    def new_line(self):
        self.PlotLineClass(model=self)

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


class PlotLineView(QtWidgets.QWidget):
    def __init__(self, plot_window):
        super(PlotLineView, self).__init__(plot_window)
        self._plot_line = None
        self._simulation = None
        self.setVisible(False)

        self.plot_window = plot_window

    def set_plot_line(self, plot_line):
        self._plot_line = plot_line
        self.setVisible(self._plot_line is not None)

    def plot_line(self):
        return self._plot_line

    def regenerate(self):
        if self._plot_line is not None:
            self._plot_line.regenerate()

    def set_simulation(self, simulation):
        self._plot_line.set_simulation(simulation)

    def progress_bar_inc_tasks(self, num_tasks):
        self.plot_window.progress.inc_tasks(num_tasks)

    def progress_bar_tasks_done(self, num_tasks):
        self.plot_window.progress.tasks_done(num_tasks)

    def progress_message(self, msg):
        self.plot_window.statusBar().showMessage(msg)
