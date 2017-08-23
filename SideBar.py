from PyQt5 import QtWidgets, QtCore


class SideBar(QtWidgets.QWidget):

    sigItemSelected = QtCore.pyqtSignal(object)

    def __init__(self, plotter_factory, model, parent=None):
        super(SideBar, self).__init__(parent)

        # create model and plot_line_view
        self.model = plotter_factory.model()
        plot_line_view = plotter_factory.view(self)

        # create combo box
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.setModel(self.model)

        # create label editor
        self.label_editor = QtWidgets.QLineEdit(self)
        self.label_editor.setText("")
        self.label_editor.setEnabled(False)
        self.label_editor.textChanged.connect(self.update_label)

        self.stack = QtWidgets.QStackedWidget(self)

        # layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.combo_box)
        self.layout().addWidget(self.label_editor)
        self.layout().addWidget(plot_line_view)
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

        self.sigItemSelected.emit(index != -1)

    def current_item(self):
        return self.model.line(self.combo_box.currentIndex())

    def new_line(self):
        self.model.new_line()
