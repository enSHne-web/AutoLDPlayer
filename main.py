import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Ép Qt dùng Fusion style — tránh bị Windows theme ghi đè
    
    # Thiết lập icon cho ứng dụng
    icon_path = get_resource_path(os.path.join("assets", "app_icon.ico"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
