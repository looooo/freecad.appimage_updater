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

        # importing the plugin and creating an instance
        self.loader = QtCore.QPluginLoader()
        self.loader.setFileName("libQAppImageUpdate")
        self.loaded = self.loader.load()
        if self.loaded:
            self.updater = self.loader.instance()
            self.updater.quit.connect(self.quit_freecad)

    def quit_freecad(self):
        FreeCADGui.getMainWindow().close()

    def start_updater(self):
        if not self.loaded:
            return

        self.updater.cancel()
        self.updater.clear()
        

        # Get Icon for FreeCAD.
        icon = QtCore.QByteArray()
        buf = QtCore.QBuffer(icon)
        buf.open(QtCore.QIODevice.WriteOnly);
        pixmap = QtGui.QPixmap(":/icons/freecad.svg")
        pixmap.save(buf, "PNG")

        self.updater.setApplicationName("FreeCAD")
        self.updater.setIcon(icon)
        self.updater.start(self.updater.getConstant("Action::UpdateWithGUI"))

    def saveSettings(self):
        pass

FreeCADGui.addPreferencePage(AppImagePreferencePage,'AppImage')

preference_tabel = FreeCAD.ParamGet('User parameter:BaseApp/Preferences/AppImage')
