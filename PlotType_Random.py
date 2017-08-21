from PyQt4 import QtGui
from PlotLineModel import PlotLine, PlotLineView, PlotLineModel
import random


class PlotLineRandom(PlotLine):
    def __init__(self, model=None):
        super(PlotLineRandom, self).__init__(model)

    def update(self):
        self._xdata = range(10)
        self._ydata = [random.random() for i in self._xdata ]


class PlotLineRandomView(PlotLineView):
    def __init__(self, parent=None):
        super(PlotLineRandomView, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout()

        # add regenerate button
        button = QtGui.QPushButton()
        button.setText("Update")
        self.layout.addWidget(button)

        self.connect(button, button.clicked, self.regenerate)

        self.setLayout(self.layout)

    def regenerate(self):
        super(PlotLineRandomView, self).regenerate()


class RandomLineFactory:
    plot_line_class = PlotLineRandom
    plot_view_class = PlotLineRandomView
    plot_model_class = PlotLineModel

    def __init__(self):
        self._model = None

    def view(self, parent):
        return self.plot_view_class(parent)

    def plotter(self):
        return self.plot_line_class(self.model())

    def model(self):
        if self._model is None:
            self._model = self.plot_model_class(self.plot_line_class)

        return self._model

