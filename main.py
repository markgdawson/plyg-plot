import sys
from PyQt4 import QtGui
from PlotWindow import PlotWindow
from PlotType_Random import RandomLineFactory

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotWindow(RandomLineFactory())
    main.show()

    sys.exit(app.exec_())