from sidebar_selectors.selector_value_checkbox import ValueCheckboxSelector


class FacePatchSelector(ValueCheckboxSelector):
    def __init__(self, parent=None, label='Select Face Patches'):
        super(FacePatchSelector, self).__init__(label=label, parent=parent)

    def set_simulation(self, simulation):
        # populate face_patch_selector
        geom = simulation.geom()
        face_patches = geom.get_face_patches()
        num_face_patches = geom.get_count_face_patches()
        self.set_values(face_patches, num_face_patches)

    def set_torque(self, torque):
        # populate face_patch_selector
        if torque is not None:
            self.set_values(torque.patches)

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

if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    widget = FacePatchSelector()
    widget.set_values((1,2,3,4,5,6))
    widget.show()
    sys.exit(app.exec_())
