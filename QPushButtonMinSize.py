from PyQt4 import QtGui

class QPushButtonMinSize(QtGui.QPushButton):
    def __init__(self, text, parent=None):
        super(QPushButtonMinSize, self).__init__(parent)
        self.setText(text)
        width = self.fontMetrics().boundingRect(text).width() + 20
        self.setMaximumWidth(width)
