from PyQt5 import QtWidgets, QtCore, QtGui
from PlotLineModel import PlotLine, PlotLineModel


class LineComboBox(QtWidgets.QWidget):

    sigCurrentItemChanged = QtCore.pyqtSignal(PlotLine)

    def __init__(self, parent=None, model=None):
        super(LineComboBox, self).__init__(parent)

        # setup default or provided model
        if model is None:
            model = PlotLineModel()

        self.setLayout(QtWidgets.QVBoxLayout())

        # create combo box
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.setModel(model)
        self.layout().addWidget(self.combo_box)

        # create new line button
        button = QtWidgets.QPushButton("Add Line", self)
        button.clicked.connect(self.add_line)

        # buttons widget
        buttons = QtWidgets.QWidget(self)
        buttons.setLayout(QtWidgets.QHBoxLayout())
        buttons.layout().addWidget(button)
        buttons.layout().setContentsMargins(0, 0, 0, 0)

        # create delete line button
        button = QtWidgets.QPushButton("Delete", self)
        buttons.layout().addWidget(button)
        button.setEnabled(False)
        button.clicked.connect(self.delete_current)
        self.del_button = button

        # create rename line button
        button = QtWidgets.QPushButton("Rename", self)
        buttons.layout().addWidget(button)
        button.setEnabled(False)
        button.clicked.connect(self.rename_current)
        self.rename_button = button

        # add button to layout
        self.layout().addWidget(buttons)

        model.rowsInserted.connect(self.rowsInserted)

        self.combo_box.currentIndexChanged.connect(self.update_current_item)
        self.model().rowsRemoved.connect(self.update_current_item)

    def rowsInserted(self, index):
        self.combo_box.setCurrentIndex(0)

    def add_line(self):
        line = self.model().PlotLineClass(self.model())

    def model(self):
        return self.combo_box.model()

    def update_current_item(self, index):
        plot_line = self.current_item()
        self.rename_button.setEnabled(index != -1)
        self.del_button.setEnabled(index != -1)
        self.sigCurrentItemChanged.emit(plot_line)

    def current_item(self):
        return self.model().line(self.combo_box.currentIndex())

    def rename(self, plot_item):
        text, accepted = QtWidgets.QInputDialog.getText(self, 'Label', 'Choose New Label', QtWidgets.QLineEdit.Normal, plot_item.label())
        if accepted:
            plot_item.set_label(text)

    def rename_current(self):
        plot_item = self.current_item()
        self.rename(plot_item)

    def delete_current(self):
        model = self.model()
        model.delete_line(self.combo_box.currentIndex())

    def label_line_edit_text_changed(self, string):
        index = self.combo_box.currentIndex()
        self.model().set_label(index, string)
