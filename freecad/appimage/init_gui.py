import sys
import time
import os
from PySide2 import QtWidgets, QtGui, QtCore

import FreeCAD
import FreeCADGui

DIR = os.path.dirname(__file__)
FreeCADGui.addIconPath(os.path.join(DIR, "icons"))

class AppImagePreferencePage:
    def __init__(self):
        ui_file = os.path.join(DIR, "ui", "preferences.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_file)
        self.form.check_updates_button.clicked.connect(self.start_updater)
        self.revision = int(FreeCAD.Version()[2].split(" ")[0])

        self.progress_dialog = None

        # Dialog boxes
        self.box = QtWidgets.QMessageBox()
        self.box.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        # importing the plugin and creating an instance
        self.loader = QtCore.QPluginLoader()
        self.loader.setFileName("libQAppImageUpdate")
        self.loaded = self.loader.load()
        if self.loaded:
            self.updater = self.loader.instance()
            self.updater.quit.connect(self.quit_freecad)
            self.updater.finished.connect(self.handle_update_info)
            self.updater.progress.connect(self.handle_update_check_progress)
            self.updater.error.connect(self.handle_update_check_error)

    def start_gui_updater(self):
        if not self.loaded:
            return

        # Get Icon for FreeCAD.
        icon = QtCore.QByteArray()
        buf = QtCore.QBuffer(icon)
        buf.open(QtCore.QIODevice.WriteOnly);
        pixmap = QtGui.QPixmap(":/icons/freecad.svg")
        pixmap.save(buf, "PNG")

        self.updater.setApplicationName("FreeCAD")
        self.updater.setIcon(icon)
        self.updater.start(self.updater.getConstant("Action::UpdateWithGUI"))

    def handle_update_check_error(self, code, action):
        if action != self.updater.getConstant("Action::CheckForUpdate"):
            return

        if self.progress_dialog is not None:
            self.progress_dialog.hide()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None

        self.box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        self.box.setWindowTitle("Update Error")
        self.box.setText("FreeCAD cannot update because, " + self.updater.errorCodeToDescriptionString(code))
        self.box.exec()

    def handle_update_check_progress(self, percentage , br, bt, speed, speed_units, action):
        if action != self.updater.getConstant("Action::CheckForUpdate"):
            return

        if self.progress_dialog is not None:
            self.progress_dialog.setValue(percentage)


    def handle_update_info(self, info, action):
        if action != self.updater.getConstant("Action::CheckForUpdate"):
            return

        remote_target_filename = info["RemoteTargetFileName"]
        v = remote_target_filename.split("-")
        revision = 0
        for i in v:
            try:
                revision = int(i)
                break
            except:
                revision = 0

        if self.progress_dialog is not None:
            self.progress_dialog.hide()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None

        if revision == 0:
            # Fallback to traditional delta update.
            self.start_gui_updater()
            return

        if revision > self.revision:
            # Trigger update.
            self.start_gui_updater()
        else:
            # No update needed.
            # Show a simple dialog box.
            self.box.setIcon(QtWidgets.QMessageBox.Icon.Information)
            self.box.setWindowTitle("No Update Needed")
            self.box.setText("You are already using the latest version of FreeCAD.")
            self.box.exec()

    def quit_freecad(self):
        FreeCADGui.getMainWindow().close()

    def start_updater(self):
        if not self.loaded:
            return

        self.updater.cancel()
        self.updater.clear()
        if self.progress_dialog is not None:
            self.progress_dialog.hide()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None

        # Check the FreeCAD revision no. in filename with the
        # remote target file to know if we really
        # need a update since SHA1 hashes differ
        # every week.
        self.updater.setApplicationName("FreeCAD")
        self.updater.start(self.updater.getConstant("Action::CheckForUpdate"))

        # QProgressDialog while checking for update.
        self.progress_dialog = QtWidgets.QProgressDialog("Checking for Update", None, 0, 100)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

    def saveSettings(self):
        pass

FreeCADGui.addPreferencePage(AppImagePreferencePage,'AppImage')

preference_tabel = FreeCAD.ParamGet('User parameter:BaseApp/Preferences/AppImage')
