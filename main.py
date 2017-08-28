import sys

from PyQt5 import QtWidgets, QtCore

from main_window.main_plot_window import PlotWindow
from main_window.mpl_widget import MPLWidget
from main_window.plot_line_bases import PlotLineModel
from plot_types.angular_torque import PlotLineAngularTorqueView
from plot_types.mean_values import PlotLineMeanTorqueOverRevs, PlotLineMeanCpOverRevs
from plot_types.patches import PlotLineGeoView
from plot_types.sliding_window_plots import PlotLineCpSlidingWindowView, PlotLineTorqueSlidingWindowView
from plot_types.transient_values import PlotLineTransientCp, PlotLineTransientMeanTorque, \
    PlotLineTransientTotalTorque

WindowCount = dict({})


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

        geometry_factories = [('Patches', PlotLineGeoView),
                              ('Angular Torque', PlotLineAngularTorqueView)]

        time_factories = [('Sliding Window Mean Cp', PlotLineCpSlidingWindowView),
                          ('Transient Cp', PlotLineTransientCp),
                          ('Mean Cp Over Range', PlotLineMeanCpOverRevs),
                          ('Sliding Window Mean Torque', PlotLineTorqueSlidingWindowView),
                          ('Transient Total Torque', PlotLineTransientTotalTorque),
                          ('Transient Mean Torque', PlotLineTransientMeanTorque),
                          ('Mean Torque Over Range', PlotLineMeanTorqueOverRevs)]

        factories = [('Geometry', (geometry_factories, (MPLWidget.AxisEqual,MPLWidget.Geometry))),
                     ('Time', (time_factories, (MPLWidget.TimeSteps,)))]

        self.setLayout(QtWidgets.QVBoxLayout())

        # add combo box
        self.layout().addWidget(QtWidgets.QLabel("Plot Type:"))
        self.line_list = QtWidgets.QComboBox(self)
        self.layout().addWidget(self.line_list)

        for name, view_container in factories:
            self.line_list.addItem(name, userData=view_container)

        # create and connect buttons
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)

        self.setMinimumWidth(250)

    def title(self):
        selection_text = self.line_list.currentText()
        if selection_text not in WindowCount.keys():
            WindowCount[selection_text] = 0
        WindowCount[selection_text] += 1
        return "%s %d" % (selection_text, WindowCount[selection_text])

    def accept(self):
        view_container = self.line_list.currentData(role=QtCore.Qt.UserRole)
        available_views, mpl_options = view_container

        super(WindowFactory, self).accept()

        self.plot = PlotWindow(PlotLineModel(), available_views, title=self.title(), options=mpl_options)
        # connect new plot signal to factory plot function
        self.plot.sigNewPlot.connect(new_plot)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    ok = new_plot()

    if ok:
        # only start event loop if the dialog box was not closed
        sys.exit(app.exec_())
