import sys
import os
import time
from PySide import QtGui, QtCore


class AppImageUpdaterDialog(QtGui.QDialog):
    is_shown = False
    def __init__(self, parent=None):
        super(AppImageUpdaterDialog, self).__init__(parent=parent)
        self.setWindowTitle("AppImage-Update")
        self.setLayout(QtGui.QVBoxLayout())

        self.log = QtGui.QTextEdit()
        self.log.setReadOnly(True)

        self.update_button = QtGui.QPushButton("check for update")
        self.button_widget = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel)
        self.button_widget.setLayout(QtGui.QHBoxLayout())
        self.button_widget.layout().addWidget(self.update_button)
        self.update_button.clicked.connect(self.update)
        self.button_widget.rejected.connect(self.reject)
        self.update_button.setEnabled(False)

        self.progress_bar = QtGui.QProgressBar()

        self.layout().addWidget(self.log)
        self.layout().addWidget(self.progress_bar)
        self.layout().addWidget(self.button_widget)

        # importing the plugin and creating an instance
        self.loader = QtCore.QPluginLoader()
        self.loader.setFileName("libAppImageUpdaterBridge")
        self.loaded = self.loader.load()
        self.updater = self.loader.instance()
        self.logging_foo("loading the plugin: {}".format(str(self.loaded)), None)

        # connecting signals
        self.updater.updateAvailable.connect(self.update_foo)
        self.updater.logger.connect(self.logging_foo)
        self.updater.progress.connect(self.progress_foo)
        self.updater.finished.connect(self.finished_foo)
        self.updater.updateAvailable.connect(self.show)

        # set the appimage and check for updates
        self.updater.setAppImage(os.environ['APPIMAGE'])
        self.updater.checkForUpdate()

    def sizeHint(self, *args):
        return QtCore.QSize(1000, 500)

    def update(self):
        self.logging_foo("start with update process")
        self.update_button.setEnabled(False)
        self.updater.start()

    def progress_foo(self, *args):
        self.progress_bar.setValue(args[0])

    def logging_foo(self, msg, appimage=None):
        self.log.moveCursor(QtGui.QTextCursor.End)
        self.log.insertPlainText(msg)
        self.log.insertPlainText("\n")

    def update_foo(self, available, update_info):
        if available:
            self.update_button.setEnabled(True)
            self.update_button.setText("update")
        else:
            self.log.moveCursor(QtGui.QTextCursor.End)
            self.log.insertPlainText("\n")
            self.log.insertPlainText("\n")

    def finished_foo(self, new, old):
        self.new_file_name = new["AbsolutePath"]
        self.update_button.setText("restart")
        self.update_button.clicked.disconnect()
        self.update_button.setEnabled(True)
        self.update_button.clicked.connect(self.restart)

    def reject(self, *args):
        self.updater.cancel()
        self.updater.clear()
        super(AppImageUpdaterDialog, self).reject(*args)

    def restart(self):
        import FreeCADGui as Gui
        closing = Gui.getMainWindow().close()
        if closing:
            os.system(self.new_file_name);

