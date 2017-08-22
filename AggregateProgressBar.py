from PyQt5 import QtWidgets

class AggregateProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        super(AggregateProgressBar, self).__init__(parent)

        self.setValue(0)
        self.setMinimum(0)
        self.setMaximum(0)

        self.todo = 0
        self.done = 0

    def inc_tasks(self, num_tasks):
        self.todo += num_tasks

    def tasks_done(self, num_tasks):
        self.done += num_tasks
        self.setValue(self.done)
        self.setMaximum(self.todo)
