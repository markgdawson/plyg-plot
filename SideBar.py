from PyQt5 import QtWidgets, QtCore


class SideBar(QtWidgets.QWidget):

    sigItemSelected = QtCore.pyqtSignal(object)

    def __init__(self, plotter_factory, parent=None):
        super(SideBar, self).__init__(parent)

        # create model and plot_line_view
        self.model = plotter_factory.model()

        # create combo box
        self.combo_box = QtWidgets.QListView(self)
        self.combo_box.setModel(self.model)
        self.selectionModel = self.combo_box.selectionModel()

        # create label
        self.label = QtWidgets.QLabel()
        self.label.setMinimumWidth(200)

        self.stack = QtWidgets.QStackedWidget(self)
        plotter_factory.set_view_parent(self.stack)

        # create blank selection widget
        self.blank = QtWidgets.QLabel(self.stack)
        self.blank.setText("No line selected.")
        self.stack.addWidget(self.blank)
        self.stack.setCurrentWidget(self.blank)

        # layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.combo_box)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.stack)
        self.setMinimumWidth(250)

        # add stretch
        self.layout().addStretch()

        # connect signals
        self.selectionModel.selectionChanged.connect(self.current_index_changed)
        self.model.sigLegendChanged.connect(self.update_label)

    def delete_current(self):
        self.model.delete_line(self.combo_box.currentIndex())

    def update_label(self):
        text = self.combo_box.currentIndex().data()
        self.label.setText("%s:" % text)

    def current_index_changed(self, index):
        self.update_label()

        # set current view widget
        self.swap_view_widgets()

        # notify others (e.g. toolbar) that there is an item selected
        self.sigItemSelected.emit(index != -1)

    def current_plot_line(self):
        return self.model.line(self.combo_box.currentIndex())

    def swap_view_widgets(self):
        if self.current_plot_line() is None:
            widget = self.blank
        else:
            widget = self.current_plot_line().view()

        self.stack.setCurrentWidget(widget)

    def new_line(self):
        item = self.model.new_line()
        self.combo_box.setCurrentIndex(item.index())
        self.combo_box.edit(item.index())

if __name__ == "__main__":
    import sys
    import PlotType_Geo
    from PyQt5 import QtGui

    class PltrFact:
        _model = QtGui.QStandardItemModel()

        def model(self):
            return self._model

        def set_view_parent(self,view):
            None

    app = QtWidgets.QApplication(sys.argv)
    factory = PlotType_Geo.GeoLineFactory()
    sb = SideBar(factory)
    sb.new_line()
    sb.new_line()
    sb.show()
    sys.exit(app.exec_())
