import sys
from PyQt5 import QtWidgets, QtCore
from PlotWindow import PlotWindow
from PlotType_Geo import PlotLineGeoView
from PlotLineModel import PlotLineModel


def new_plot(last_win_pos=None):
    factory = WindowFactory()
    accepted = factory.exec()

    if accepted:
        plot = factory.plot

        # setup window position
        if last_win_pos is not None:
            position = last_win_pos + QtCore.QPoint(40, 40)
            available = QtWidgets.QApplication.desktop().availableGeometry(plot)
            frame = plot.frameGeometry()

            if position.x() + frame.width() > available.right():
                position.setX(available.left())
            if position.y() + frame.height() > available.bottom() - 40:
                position.setY(available.top())

            # set window position if specified
            plot.move(position)

        plot.show()

    return accepted


class WindowFactory(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(WindowFactory, self).__init__(parent)

        self.plot = None

        factories = [
            ('Geometry', PlotLineGeoView)
        ]

        self.setLayout(QtWidgets.QVBoxLayout())

        # add combo box
        self.layout().addWidget(QtWidgets.QLabel("Plot Type:"))
        self.line_list = QtWidgets.QComboBox(self)
        self.layout().addWidget(self.line_list)

        for name, view in factories:
            self.line_list.addItem(name, userData=view)

        # create and connect buttons
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)

        self.setMinimumWidth(250)

    def accept(self):
        View = self.line_list.currentData(role=QtCore.Qt.UserRole)
        self.plot = PlotWindow(PlotLineModel(View))

        # connect new plot signal to factory plot function
        self.plot.sigNewPlot.connect(new_plot)
        
        super(WindowFactory, self).accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    ok = new_plot()

    if ok:
        # only start event loop if the dialog box was not closed
        sys.exit(app.exec_())
