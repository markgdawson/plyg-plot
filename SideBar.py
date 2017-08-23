from PyQt5 import QtWidgets, QtCore


class SideBar(QtWidgets.QWidget):

    sigItemSelected = QtCore.pyqtSignal(object)

    def __init__(self, plotter_factory, model, parent=None):
        super(SideBar, self).__init__(parent)

        # create model and plot_line_view
        self.model = plotter_factory.model()

        # create combo box
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.setModel(self.model)

        # create label editor
        self.label_editor = QtWidgets.QLineEdit(self)
        self.label_editor.setText("")
        self.label_editor.setEnabled(False)
        self.label_editor.textChanged.connect(self.update_label)

        self.stack = QtWidgets.QStackedWidget(self)
        plotter_factory.set_view_parent(self.stack)

        # layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.combo_box)
        self.layout().addWidget(self.label_editor)
        self.layout().addWidget(self.stack)
        self.setMinimumWidth(250)

        # add stretch
        self.layout().addStretch()

        # connect signals
        self.combo_box.currentIndexChanged.connect(self.current_index_changed)
        self.model.rowsInserted.connect(self.rows_inserted)

    def rows_inserted(self, index):
        self.combo_box.setCurrentIndex(0)

    def update_label(self ):
        string = self.label_editor.text()
        index = self.combo_box.currentIndex()
        self.model.set_label(index, string)

    def delete_current(self):
        self.model.delete_line(self.combo_box.currentIndex())

    def current_index_changed(self, index):
        text = self.combo_box.currentText()
        self.label_editor.setText(text)
        self.label_editor.setEnabled(index != -1)

        # set current view widget
        self.swap_view_widgets()

        # notify others (e.g. toolbar) that there is an item selected
        self.sigItemSelected.emit(index != -1)

    def current_plot_line(self):
        return self.model.line(self.combo_box.currentIndex())

    def swap_view_widgets(self):
        self.stack.setCurrentWidget(self.current_plot_line().view())

    def new_line(self):
        self.model.new_line()
