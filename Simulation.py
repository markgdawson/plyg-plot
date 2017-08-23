from PyQt5 import QtCore
from TorqueFile import TorqueFile
from GeometryFiles import Geom
import os


class Simulation(QtCore.QObject):
    sigUpdateProgress = QtCore.pyqtSignal()
    sigLoaded = QtCore.pyqtSignal()
    sigUpdateLabel = QtCore.pyqtSignal(str)

    def __init__(self, parent, geo_file):
        super(Simulation, self).__init__(parent)

        self._geom = None
        self.geo_file_name = geo_file
        self.loaded = False

        self.__sig_emitDataChanged = None

        ThreadLoader(self, self).start()

        # progress update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.sigUpdateProgress.emit)
        self.timer.start(500)
        self.sigLoaded.connect(lambda: [self.timer.stop(), self.sigUpdateProgress.emit()])

        torque_file = os.path.join(os.path.dirname(geo_file), 'TORQUE.csv')
        if os.path.isfile(torque_file):
            self._torque = TorqueFile(torque_file)
        else:
            self._torque = None

    def connect_signals_to_item(self, item):
        self.__sig_emitDataChanged = item.emitDataChanged
        self.sigUpdateProgress.connect(self.__sig_emitDataChanged)

    def disconnect_signals_from_item(self):
        if self.__sig_emitDataChanged is not None:
            self.sigUpdateProgress.disconnect(self.__sig_emitDataChanged)

    def torque(self):
        return self._torque

    def geom(self):
        return self._geom

    def load(self):
        self._geom = Geom(self.geo_file_name)
        self._geom.load()
        self.loaded = True
        self.sigLoaded.emit()
        self._geom.geo.cache()

    def progress(self):
        if self._geom is not None and self._geom.geo is not None:
            return self._geom.geo.progress, self._geom.geo.progress_total
        else:
            return None, None

    def set_label(self, label):
        self._label = label
        self.sigUpdateLabel.emit(label)

    def label(self):
        return self._label


# creates the simulation Geom object (including loading the file) in a seperate thread
class ThreadLoader(QtCore.QThread):

    def __init__(self, parent, load_obj):
        QtCore.QThread.__init__(self, parent)
        self.load_obj = load_obj

    def run(self):
        self.load_obj.load()

