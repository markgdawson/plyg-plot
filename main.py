import sys
from PyQt4 import QtGui
from PlotWindow import PlotWindow
from PlotType_Geo import GeoLineFactory

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotWindow(GeoLineFactory())
    main.show()

    sys.exit(app.exec_())