from PyQt4 import QtGui, QtCore
import random


class PlotLine:

    def __init__(self, model):
        self._xdata = range(10)
        self._ydata = [random.random() for i in self._xdata ]
        self._label = ""
        self._mpl_line = None
        self.model = model
        self.stditem = QtGui.QStandardItem()
        self.stditem.setData(self, QtCore.Qt.UserRole)

        self.set_label(self.model.default_label())

        self.model.insertRow(0, self.stditem)
        self.model.lines_created += 1


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
        self._ydata = [random.random() for i in self._xdata ]
        self.data_changed()

    def unplot(self):
        line = self.mpl_line()
        if line is not None:
            line.remove()

    def data_changed(self):
        self.model.emit(self.model.dataChanged,self.model.createIndex(0,0),self.model.createIndex(0,self.model.rowCount()))


class PlotLineModel(QtGui.QStandardItemModel):

    def __init__(self, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self.lines_created = 0

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
    def __init__(self, plot_line, parent=None):
        super(PlotLineView, self).__init__(parent)
        self.layout = QtGui.QVBoxLayout()
        self.plot_line = None

        # add regenerate button
        button = QtGui.QPushButton()
        button.setText("Regenerate")
        self.layout.addWidget(button)

        self.connect(button, button.clicked, self.regenerate)

        self.setLayout(self.layout)
        self.setEnabled(False)

    def set_plot_line(self, plot_line):
        self.plot_line = plot_line
        self.setEnabled(self.plot_line is not None)

    def regenerate(self):
        if self.plot_line is not None:
            self.plot_line.regenerate()



