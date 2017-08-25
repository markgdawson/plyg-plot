from PyQt5 import QtWidgets, QtCore


class SideBar(QtWidgets.QWidget):

    sigItemSelected = QtCore.pyqtSignal(object)

    def __init__(self, plot_line_model, available_views, parent=None):
        super(SideBar, self).__init__(parent)

        # create model and plot_line_view
        self.model = plot_line_model
        self.available_views = available_views

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
        diag = LineSelect(self.available_views, self)
        accepted = diag.exec()
        if accepted and diag.view is not None:
            item = self.model.new_line(diag.view, diag.name)
            self.line_list.setCurrentIndex(item.index())
            self.line_list.edit(item.index())


class LineSelect(QtWidgets.QDialog):
    def __init__(self, options, parent=None):
        super(LineSelect, self).__init__(parent)

        self.view = None

        self.setLayout(QtWidgets.QVBoxLayout())

        # add combo box
        self.layout().addWidget(QtWidgets.QLabel("Line Type:"))
        self.line_list = QtWidgets.QComboBox(self)
        self.layout().addWidget(self.line_list)

        for name, view in options:
            self.line_list.addItem(name, userData=view)

        # create and connect buttons
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)

        self.setMinimumWidth(250)

    def accept(self):
        self.view = self.line_list.currentData(role=QtCore.Qt.UserRole)
        self.name = self.line_list.currentData(role=QtCore.Qt.DisplayRole)

        super(LineSelect, self).accept()


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
