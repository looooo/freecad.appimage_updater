import sys
import os
import time
from PySide2 import QtWidgets, QtGui, QtCore, QtNetwork


class AppImageUpdaterDialog(QtWidgets.QDialog):
    is_shown = False
    def __init__(self, parent=None):
        super(AppImageUpdaterDialog, self).__init__(parent=parent)
        self.setWindowTitle("AppImage-Update")
        self.setLayout(QtWidgets.QVBoxLayout())

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.update_button = QtWidgets.QPushButton("Check for update")
        self.button_widget = QtWidgets.QWidget()
        self.button_widget.setLayout(QtWidgets.QHBoxLayout())
        self.button_widget.layout().addWidget(self.cancel_button)
        self.button_widget.layout().addWidget(self.update_button)
        self.update_button.clicked.connect(self.update)
        self.cancel_button.clicked.connect(self.reject)
        self.update_button.setEnabled(False)

        self.progress_bar = QtWidgets.QProgressBar()

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

        self.proxy = QtNetwork.QNetworkProxy()
        self.proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy)
        self.proxy.setHostName("127.1") # 127.0.0.1 can be written as 127.1
        self.proxy.setPort(9050)
        self.updater.setProxy(self.proxy)

        # check for updates
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
        self.log.moveCursor(QtGui.QTextCursor.End)

    def update_foo(self, available, update_info):
        if available:
            self.update_button.setEnabled(True)
            self.update_button.setText("Update")
            if self.isHidden():
                self.show()
        else:
            self.log.moveCursor(QtWidgets.QTextCursor.End)
            self.log.insertPlainText("\n")
            self.log.insertPlainText("\n")
            self.log.insertPlainText("The latest available AppImage is already installed.")
            self.log.moveCursor(QtGui.QTextCursor.End)

    def finished_foo(self, new, old):
        self.new_file_name = new["AbsolutePath"]
        self.update_button.setText("Restart")
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

