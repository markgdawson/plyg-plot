import collections
from PyQt5 import QtWidgets, QtCore
from sidebar_selectors.base_class_selector import SidebarSelectorBase


class ValueCheckboxSelector(SidebarSelectorBase):
    sigSelectionChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, label='Select Value', parent=None):
        self.columns = 3
        super(ValueCheckboxSelector, self).__init__(parent, label=label,
                                                    layout=SidebarSelectorBase.GRID_LAYOUT,
                                                    columns=self.columns)

        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.buttonClicked[int].connect(self.values_changed)
        self.button_group.setExclusive(False)
        self.selected_values = []

        self.warnings = dict({})

        self.all_checkbox = None

        self.reset()

    def set_num_columns(self, columns):
        self.columns = columns

    def reset(self):
        for button in self.button_group.buttons():
            self.layout().removeWidget(button)
        if self.all_checkbox is not None:
            self.layout().removeWidget(self.all_checkbox)

        self.row = 1
        self.column = 0

    def set_values(self, indexes):
        self.reset()
        for index in indexes:
            if isinstance(index, collections.Iterable):
                if isinstance(index, tuple):
                    index = index[0]
                    text = index[1]
                else:
                    raise ValueError("tuple of values expected")
            else:
                index = index
                text = "%s" % index
            self.add_checkbox(text, index)

        # add "all" checkbox
        if self.column >= self.columns:
            self.column = 0
            self.row += 1
        self.all_checkbox = QtWidgets.QCheckBox(self)
        self.all_checkbox.setText("All")
        self.layout().addWidget(self.all_checkbox, self.row, self.column)
        self.all_checkbox.toggled.connect(self.select_all)

        self.emit_selection_changed()

    def select_all(self, toggled):
        if toggled is True:
            self.button_group.buttonClicked[int].disconnect(self.values_changed)
            for button in self.button_group.buttons():
                if self.button_group.id(button) not in self.warnings.keys():
                    button.setChecked(toggled)
            self.button_group.buttonClicked[int].connect(self.values_changed)
            self.emit_selection_changed()

    def remove_all_checkbox_toggle(self):
        self.all_checkbox.setChecked(False)

    def add_checkbox(self, text, index):
        checkbox = QtWidgets.QCheckBox(self)
        checkbox.setText(text)
        self.button_group.addButton(checkbox, index)

        if self.column >= self.columns:
            self.column = 0
            self.row += 1

        self.layout().addWidget(checkbox, self.row, self.column)
        self.column += 1

    def add_warning(self, warning, index):
        self.warnings[index] = warning

    def values_changed(self, button_id):
        self.remove_all_checkbox_toggle()
        button = self.button_group.button(button_id)
        if button.isChecked() and button_id in self.warnings.keys():
            reply = QtWidgets.QMessageBox.warning(self, "Warning", self.warnings[button_id],
                                                  QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                  QtWidgets.QMessageBox.No)
            if not reply == QtWidgets.QMessageBox.Yes:
                button.setChecked(False)
                return
        self.emit_selection_changed()

    def emit_selection_changed(self):
        self.selected_values = [self.button_group.id(b) for b in self.button_group.buttons() if b.isChecked()]
        self.sigSelectionChanged.emit(tuple(self.selected_values))


