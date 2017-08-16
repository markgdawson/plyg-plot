import sys
from PyQt4 import QtGui, QtCore
from PlotWindow import PlotWindow
from PlotLineModel import PlotLineView, PlotLine

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotWindow()
    main.show()
    main = QtGui.QMainWindow()
    #plot_line = PlotLine()
    #plot_line.set_label("my label")
    #main.setCentralWidget(PlotLineView(plot_line))
    #main.show()

    sys.exit(app.exec_())