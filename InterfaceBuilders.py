import collections

from RevCountSelector import RevCountSelector
from RevolutionRangeSelector import RevolutionRangeSelector
from SimulationSelection import SimulationSelectionWidget
from ValueCheckboxSelector import FacePatchSelector


def revolution_range_selector(self, default_start, default_end, range_connect=None):
    revs = RevolutionRangeSelector(self)
    revs.init(default_start, default_end)
    self.layout().addWidget(revs)

    connect_signals(revs.sigRangeChanged, range_connect)

    return revs


LastSimulationSelected = None


def simulation_selector(parent, torque_connect=None, simulation_connect=None):
    sim_select = SimulationSelectionWidget(parent)

    connect_signals(sim_select.sigTorqueLoaded, torque_connect)
    connect_signals(sim_select.sigSimulationLoaded, simulation_connect)

    if LastSimulationSelected is not None:
        sim_select.set_simulation(LastSimulationSelected)

    sim_select.sigSimulationSelected.connect(set_last_selected_simulation)

    return sim_select


def set_last_selected_simulation(simulation):
    global LastSimulationSelected
    LastSimulationSelected = simulation


def face_patch_selector(parent, label="Select Face Patches:", columns=4, patches_connect=None):
    patch_select = FacePatchSelector(parent)
    patch_select.set_label(label)
    patch_select.set_num_columns(columns)

    connect_signals(patch_select.sigSelectionChanged, patches_connect)

    return patch_select


def revolution_count_selector(parent, num_revs_window, revs_change_connect=None):
    revs = RevCountSelector(num_revs_window, parent)

    connect_signals(revs.sigNumRevsChanged, revs_change_connect)

    return revs


def connect_signals(signal, slots):
    if slots is not None:
        if not isinstance(slots, collections.Iterable):
            slots = (slots,)
        for slot in slots:
            signal.connect(slot)
