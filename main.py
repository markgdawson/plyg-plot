import sys
from PyQt5 import QtWidgets
from PlotWindow import PlotWindow
from PlotType_Geo import GeoLineFactory

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = PlotWindow(GeoLineFactory())
    main.show()

    sys.exit(app.exec_())