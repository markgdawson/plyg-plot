from PyQt5 import QtWidgets


class QPushButtonMinSize(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super(QPushButtonMinSize, self).__init__(parent)
        self.setText(text)
        width = self.fontMetrics().boundingRect(text).width() + 30
        self.setMaximumWidth(width)
