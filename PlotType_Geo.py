from PyQt5 import QtWidgets
from SimulationSelection import SimulationSelectionWidget
from PlotLineModel import PlotLineView
from ValueCheckboxSelector import FacePatchSelector


class PlotLineGeoView(PlotLineView):
    def __init__(self, parent=None):
        super(PlotLineGeoView, self).__init__(parent)

        # plotting parameter defaults
        self.simulation = None
        self.fpatches = []

        # INITIALISE USER INTERFACE

        # sets the self.simulation object
        self.sim_select = SimulationSelectionWidget()
        self.sim_select.sigSimulationLoaded.connect(self.simulation_loaded)
        self.layout().addWidget(self.sim_select)

        # add face patch selector
        self.face_patch_selector = FacePatchSelector(self)
        self.face_patch_selector.set_label("Select Face Patches:")
        self.face_patch_selector.set_num_columns(4)
        self.face_patch_selector.sigSelectionChanged.connect(self.patches_selected)
        self.layout().addWidget(self.face_patch_selector)

    def simulation_loaded(self):
        self.simulation = self.sim_select.simulation

        # populate face_patch_selector
        geom = self.simulation.geom()
        face_patches = geom.get_face_patches()
        num_face_patches = geom.get_count_face_patches()
        self.face_patch_selector.set_values(face_patches, num_face_patches)

        self.replot()

    def patches_selected(self, patches):
        self.fpatches = patches
        self.replot()

    def replot(self):
        if self.simulation is not None:
            geom = self.simulation.geom()
            if geom is not None:
                x,y = geom.get_patch_faces(self.fpatches)
                self.plotter.plot(x, y)

