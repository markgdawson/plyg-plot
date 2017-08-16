from PyQt4 import QtGui, QtCore
from PlotLineModel import PlotLine, PlotLineModel


class LineComboBox(QtGui.QWidget):

    sigCurrentItemChanged = QtCore.pyqtSignal(PlotLine)

    def __init__(self, parent=None, model=None):
        super(LineComboBox, self).__init__(parent)

        # setup default or provided model
        if model is None:
            model = PlotLineModel()

        self.setLayout(QtGui.QVBoxLayout())

        # create combo box
        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.setModel(model)
        self.layout().addWidget(self.combo_box)

        # create new line button
        button = QtGui.QPushButton("Add Line", self)
        self.connect(button, button.clicked, self.add_line)

        # buttons widget
        buttons = QtGui.QWidget(self)
        buttons.setLayout(QtGui.QHBoxLayout())
        buttons.layout().addWidget(button)
        buttons.layout().setMargin(0)

        # create delete line button
        button = QtGui.QPushButton("Delete", self)
        buttons.layout().addWidget(button)
        button.setEnabled(False)
        self.connect(button, button.clicked, self.delete_current)
        self.del_button = button

        # create rename line button
        button = QtGui.QPushButton("Rename", self)
        buttons.layout().addWidget(button)
        button.setEnabled(False)
        self.connect(button, button.clicked, self.rename_current)
        self.rename_button = button

        # add button to layout
        self.layout().addWidget(buttons)

        self.connect(model, model.rowsInserted, self.rowsInserted)

        self.connect(self.combo_box, self.combo_box.currentIndexChanged, self.update_current_item)
        self.connect(self.combo_box, self.model().rowsRemoved, self.update_current_item)

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
        self.emit(self.sigCurrentItemChanged, plot_line)

    def current_item(self):
        return self.model().line(self.combo_box.currentIndex())

    def rename(self, plot_item):
        text, accepted = QtGui.QInputDialog.getText(self, 'Label', 'Choose New Label', QtGui.QLineEdit.Normal, plot_item.label())
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
