from PyQt5 import QtWidgets, QtCore


class SideBar(QtWidgets.QWidget):

    sigItemSelected = QtCore.pyqtSignal(object)

    def __init__(self, plot_line_model, parent=None):
        super(SideBar, self).__init__(parent)

        # create model and plot_line_view
        self.model = plot_line_model

        # create combo box
        self.line_list = QtWidgets.QListView(self)
        self.line_list.setModel(self.model)
        self.selectionModel = self.line_list.selectionModel()

        self.stack = QtWidgets.QStackedWidget(self)
        plot_line_model.set_view_parent(self.stack)

        # create blank selection widget
        self.blank = QtWidgets.QLabel(self.stack)
        self.blank.setText("No line selected.")
        self.stack.addWidget(self.blank)
        self.stack.setCurrentWidget(self.blank)

        # layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.line_list)
        self.layout().addWidget(self.stack)
        self.setMinimumWidth(250)

        # add stretch
        self.layout().addStretch()

        # connect signals
        self.selectionModel.selectionChanged.connect(self.current_index_changed)

    def delete_current(self):
        self.model.delete_line(self.line_list.currentIndex())

    def current_index_changed(self, index):
        # set current view widget
        self.swap_view_widgets()

        # notify others (e.g. toolbar) that there is an item selected
        self.sigItemSelected.emit(index != -1)

    def current_plot_line(self):
        index = self.line_list.currentIndex()
        return self.model.line(index)

    def swap_view_widgets(self):
        if self.current_plot_line() is None:
            widget = self.blank
        else:
            widget = self.current_plot_line()

        self.stack.setCurrentWidget(widget)

    def new_line(self):
        item = self.model.new_line()
        self.line_list.setCurrentIndex(item.index())
        self.line_list.edit(item.index())

if __name__ == "__main__":
    import sys
    from PlotLineModel import PlotLineModel
    from PlotType_Geo import PlotLineGeoView

    app = QtWidgets.QApplication(sys.argv)
    model = PlotLineModel(PlotLineGeoView)
    sb = SideBar(model)
    sb.new_line()
    sb.new_line()
    sb.show()
    sys.exit(app.exec_())
