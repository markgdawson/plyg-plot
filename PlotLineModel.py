from PyQt4 import QtGui, QtCore
import random


class PlotLine:

    def __init__(self):
        super(PlotLine, self).__init__()
        self._xdata = range(10)
        self._ydata = [random.random() for i in self._xdata ]
        self._label = ""
        self._mpl_line = None

    def set_label(self, label):
        self._label = label

        line = self.mpl_line()
        if line is not None:
            line.set_label(label)

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


class PlotLineModel(QtGui.QStandardItemModel):

    def __init__(self, parent=None):
        super(PlotLineModel, self).__init__(parent)
        self._lines = []

    def add_line(self, line):
        item = QtGui.QStandardItem()
        item.setText(line.label())
        self._lines.insert(0, line)
        self.insertRow(0, item)

    def set_label(self, index, string):
        if self.item(index) is not None:
            self.line(index).set_label(string)
            self.item(index).setText(string)

    def lines(self):
        return self._lines

    def line(self,index):
        return self._lines[index]


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

        # add delete button
        button = QtGui.QPushButton()
        button.setText("Delete")
        self.layout.addWidget(button)
        self.setLayout(self.layout)
        self.setEnabled(False)

    def set_plot_line(self, plot_line):
        self.line_edit.setText(plot_line.label())
        self.setEnabled(True)

    def regenerate(self):
        if self.plot_line is not None:
            self.plot_line.regenerate()



