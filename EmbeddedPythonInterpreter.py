from IPython.core import usage
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.qt import QtGui
from qtconsole.rich_jupyter_widget import RichJupyterWidget


class EmbeddedPythonInterpreter(RichJupyterWidget):
    def __init__(self, parent=None, banner=None):
        # Create an in-process kernel
        if banner is not None:
            usage.default_banner = banner

        super(EmbeddedPythonInterpreter, self).__init__(parent)

        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel(show_banner=False)
        kernel = self.kernel_manager.kernel
        kernel.gui = 'qt4'

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

    def push_variable(self, name, variable):
        kernel = self.kernel_manager.kernel
        kernel.shell.push({name: variable})


if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = EmbeddedPythonInterpreter()
    w.push_variable('myvariable', 'variable_value')
    w.show()
    app.exec_()
