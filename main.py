import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random

class MyNavigationToolbar(NavigationToolbar):
    def __init__(self, figure_canvas, parent= None, coordinates=False):
        self.toolitems = (
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            (None, None, None, None),
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),                        
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            (None, None, None, None),
            ('Edit Paramters', 'Edit Plot Visuals', 'qt4_editor_options', 'do_edit_parameters'),
            ('Configuration', 'Configure plot', 'subplots', 'configure_plot')
          )
            
        super(MyNavigationToolbar,self).__init__(figure_canvas, parent=parent, coordinates=coordinates)
 
    def do_edit_parameters(self):
        self.edit_parameters()
        self.regenerate_legend()
        
    def configure_plot(self):
        self.parent.configure_plot()
    
    def set_message(self,msg):
        self.parent.statusmessage(msg)
                

class MPLWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MPLWidget, self).__init__(parent)
        
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.plot()
        self.canvas.mpl_connect("resize_event", self.do_resize)   
        
        self.layout().addWidget(self.canvas) 
        
        self.text = QtGui.QLabel(self.canvas)
        self.text.setText("                                                             ")
        self.text.setMargin(10)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = MyNavigationToolbar(self.canvas, self, coordinates=False)
        self.toolbar.setMinimumWidth(300)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")
    
    def regenerate_legend(self):
        # always re-generate legend
        all_axes = self.figure.get_axes()
        for ax in all_axes:
            if ax.legend_ is not None:
                ax.legend_.remove()
            ax.legend(loc="best")
            if ax.legend_ is not None:
                ax.legend_.draggable(True)
        self.canvas.draw()

    def plot(self):
        # random data
        data = [random.random() for i in range(10)]
        
        ax = self.figure.add_subplot(111)
        # colorize figure and axes to make transparency obvious
        ax.plot(data, '.-')
        self.figure.tight_layout()

        self.regenerate_legend()

        # refresh canvas
        self.canvas.draw()

    def statusmessage(self,msg):
        self.text.setText(msg)
    
    def do_resize(self, event):
        # on resize reposition the navigation toolbar to (0,0) of the axes.
        axes = self.figure.axes
        figw, figh = self.figure.get_size_inches()
        
        x,y = axes[0].transAxes.transform((0,0))
        ynew = figh*self.figure.dpi-y -self.toolbar.frameGeometry().height()
        self.text.move(x,ynew)
        
        x,y = axes[0].transAxes.transform((0,1.0))
        ynew = figh*self.figure.dpi-y
        xnew = x + 10
        ynew = ynew + 10
        self.toolbar.move(xnew,ynew)

    def configure_plot(self):
        QtGui.QMessageBox.information(self,"No Configuration Options","Error: No configuration options available for this plot type",QtGui.QMessageBox.Ok);
        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    widget = MPLWidget()
    main = QtGui.QMainWindow()
    main.setCentralWidget(widget)
    main.show()

    sys.exit(app.exec_())