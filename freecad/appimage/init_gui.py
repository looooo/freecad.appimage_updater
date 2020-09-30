import os

import FreeCAD
import FreeCADGui

from . update import AppImageUpdaterDialog

DIR = os.path.dirname(__file__)
FreeCADGui.addIconPath(os.path.join(DIR, "icons"))

class AppImagePreferencePage:
    def __init__(self):
        ui_file = os.path.join(DIR, "ui", "preferences.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_file)
        self.form.check_updates_button.clicked.connect(self.show_updater)
        self.form.always_check_updates.setChecked(preference_tabel.GetBool("appimage_auto_update", False))

    def show_updater(*args):
        FreeCAD.appimage_updater = AppImageUpdaterDialog()
        FreeCAD.appimage_updater.exec()

    def saveSettings(self):
        preference_tabel.SetBool("appimage_auto_update", bool(self.form.always_check_updates.isChecked()))

FreeCADGui.addPreferencePage(AppImagePreferencePage,'AppImage')

preference_tabel = FreeCAD.ParamGet('User parameter:BaseApp/Preferences/AppImage')
appimage_auto_update = preference_tabel.GetBool("appimage_auto_update", False)

if appimage_auto_update:
    FreeCAD.appimage_updater = AppImageUpdaterDialog()