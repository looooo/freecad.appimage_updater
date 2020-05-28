import os

import FreeCAD
import FreeCADGui

from . update import AppImageUpdaterDialog

ui_file = os.path.join(os.path.dirname(__file__), "ui", "preferences.ui")
FreeCADGui.addPreferencePage(ui_file,'AppImage')
preference_tabel = FreeCAD.ParamGet('User parameter:BaseApp/Preferences/AppImage')
appimage_auto_update = preference_tabel.GetBool("appimage_auto_update", False)
if appimage_auto_update:
    FreeCAD.appimage_updater = AppImageUpdaterDialog()
