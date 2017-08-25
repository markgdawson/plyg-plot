import collections
from PyQt5 import QtWidgets, QtCore


class ValueCheckboxSelector(QtWidgets.QWidget):
    sigSelectionChanged = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(ValueCheckboxSelector, self).__init__(parent)

        # set layout and remove margins
        self.setLayout(QtWidgets.QGridLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.buttonClicked[int].connect(self.values_changed)
        self.button_group.setExclusive(False)
        self.selected_values = []

        self.row = 0
        self.column = 0
        self.columns = 3

        self.label = None
        self.warnings = dict({})

    def set_label(self, label):
        self.label = label

    def set_num_columns(self, columns):
        self.columns = columns

    def reset(self):
        for button in self.button_group.buttons():
            button

        self.row = 0
        self.column = 0

        if self.label is not None:
            label = QtWidgets.QLabel(self.label)
            self.layout().addWidget(label, self.row, self.column, 1, self.columns)
            self.row += 1


    def set_values(self, indexes):
        self.reset()
        for index in indexes:
            if isinstance(index, collections.Iterable):
                index = index[0]
                text = index[1]
            else:
                index = index
                text = "%s" % index
            self.add_checkbox(text, index)

        self.sigSelectionChanged.emit(self.selected_values)

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

    def values_changed(self, id):
        button = self.button_group.button(id)
        if button.isChecked() and id in self.warnings.keys():
            reply = QtWidgets.QMessageBox.warning(self, "Warning", self.warnings[id],
                                                   QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
            if not reply == QtWidgets.QMessageBox.Yes:
                button.setChecked(False)
                return
        self.selected_values = [self.button_group.id(b) for b in self.button_group.buttons() if b.isChecked()]
        self.sigSelectionChanged.emit(self.selected_values)


class FacePatchSelector(ValueCheckboxSelector):

    def set_simulation(self, simulation):
        # populate face_patch_selector
        geom = simulation.geom()
        face_patches = geom.get_face_patches()
        num_face_patches = geom.get_count_face_patches()
        self.set_values(face_patches, num_face_patches)

    def set_torque(self, torque):
        # populate face_patch_selector
        face_patches = torque.patches
        self.set_values(face_patches)

    def set_values(self, indexes, counts=None, limit=10000):
        super(FacePatchSelector, self).set_values(indexes)

        if counts is not None:
            # add warnings for large plots
            for index, count in counts.items():
                if count > limit:
                    warning = "You about to attempt to plot %d faces! \n\n" \
                              "this may take a long time " \
                              "and/or may cause the program to crash or become unusable.\n\n" \
                              "Do you wish to proceed?" % count
                    self.add_warning(warning, index)
