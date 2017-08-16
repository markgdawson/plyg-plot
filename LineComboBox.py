from PyQt4 import QtGui, QtCore
from PlotLineModel import PlotLine, PlotLineModel
import random


class LineComboBox(QtGui.QWidget):

    sigCurrentItemChanged = QtCore.pyqtSignal(PlotLine)

    def __init__(self, parent=None, model=None):
        super(LineComboBox, self).__init__(parent)

        # setup default or provided model
        if model is None:
            model = PlotLineModel()

        self.setLayout(QtGui.QVBoxLayout())

        # create select-and-add widget
        select_and_add_widget = QtGui.QWidget(self)
        select_and_add_widget.setLayout(QtGui.QHBoxLayout())
        select_and_add_widget.layout().setMargin(0)

        # create combo box
        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.setModel(model)

        # create new line button
        new_line_button = QtGui.QPushButton(self)
        button_text = "Add"
        new_line_button.setText(button_text)
        width = new_line_button.fontMetrics().boundingRect(button_text).width() + 20
        new_line_button.setMaximumWidth(width)

        # add new line button and combo box to vertical layout
        select_and_add_widget.layout().addWidget(self.combo_box)
        select_and_add_widget.layout().addWidget(new_line_button)
        self.layout().addWidget(select_and_add_widget)

        # create label-and-delete widget
        self.label_and_delete_widget = QtGui.QWidget(self)
        self.label_and_delete_widget.setLayout(QtGui.QHBoxLayout())
        self.label_and_delete_widget.layout().setMargin(0)

        # add label QLineEdit
        self.label_line_edit = QtGui.QLineEdit()
        self.label_and_delete_widget.layout().addWidget(self.label_line_edit)

        # add delete line button
        del_line_button = QtGui.QPushButton(self)
        width = del_line_button.fontMetrics().boundingRect(button_text).width() + 20
        del_line_button.setMaximumWidth(width)
        button_text = "Del"
        del_line_button.setText(button_text)

        # add label-and-delete widget
        self.label_and_delete_widget.setEnabled(False)
        self.label_and_delete_widget.layout().addWidget(del_line_button)

        self.layout().addWidget(self.label_and_delete_widget)

        self.connect(new_line_button, new_line_button.clicked, self.add_line)
        self.connect(model, model.rowsInserted, self.rowsInserted)
        self.connect(self.label_line_edit, self.label_line_edit.textChanged, self.label_line_edit_text_changed)
        self.connect(del_line_button, del_line_button.clicked, self.delete_current)

        self.connect(self.combo_box, self.combo_box.currentIndexChanged, self.update_current_item)
        self.connect(self.combo_box, self.combo_box.model().rowsRemoved, self.update_current_item)

    def rowsInserted(self, index):
        self.combo_box.setCurrentIndex(0)

    def add_line(self):
        line = PlotLine(self.combo_box.model())

    def update_current_item(self, index):
        plot_line = self.combo_box.model().line(index)
        if plot_line is None:
            self.label_line_edit.setText("")
        else:
            self.label_line_edit.setText(plot_line.label())

        self.label_and_delete_widget.setEnabled(index != -1)
        self.emit(self.sigCurrentItemChanged, plot_line)


    def delete_current(self):
        model = self.combo_box.model()
        model.delete_line(self.combo_box.currentIndex())

    def label_line_edit_text_changed(self, string):
        index = self.combo_box.currentIndex()
        self.combo_box.model().set_label(index, string)
