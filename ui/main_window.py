import json
from PySide6 import QtCore, QtGui, QtWidgets
from pynput import keyboard, mouse

from core.adb_manager import AdbManager
from core.macro_engine import MacroEngine
from core.code_manager import CodeManager
from models.action import ActionType, AdbAction
from pathlib import Path

APP_THEME = """
/* ═══════════════════════════════════════════════════
   PREMIUM BLUE STUDIO (DIMMED)
   Soft Gray & Blue (#3399FF) - Modern, Less Glare
   ═══════════════════════════════════════════════════ */

/* --- Global & Base --- */
QMainWindow {
    background-color: #E2E8F0;
}
QWidget {
    font-family: 'Segoe UI Variable', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}
QStatusBar {
    background-color: #CBD5E1;
    color: #475569;
    border-top: 1px solid #94A3B8;
    font-size: 12px;
    padding: 2px 8px;
}
QStatusBar::item { border: none; }

/* ===================================================
   LEFT PANEL (Cool Gray)
   =================================================== */
QTabWidget#left_panel::pane {
    background-color: #E2E8F0;
    border: none;
    border-radius: 12px;
}
QTabWidget#left_panel > QTabBar::tab {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
}
QTabWidget#left_panel > QTabBar::tab:selected {
    color: #3399FF;
    border-bottom: 2px solid #3399FF;
}
QTabWidget#left_panel > QTabBar::tab:hover:!selected {
    color: #334155;
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
}
QWidget#left_panel_content, QWidget#code_panel_content {
    background-color: #E2E8F0;
    color: #334155;
}
QWidget#left_panel_content QLabel, QWidget#code_panel_content QLabel {
    color: #334155;
}

/* Left Panel ListWidgets */
QTabWidget#left_panel QListWidget {
    background-color: #CBD5E1;
    border: 1px solid #94A3B8;
    border-radius: 10px;
    padding: 4px;
    color: #334155;
}
QTabWidget#left_panel QListWidget::item {
    background-color: #E2E8F0;
    border: 1px solid #94A3B8;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 2px 0px;
}
QTabWidget#left_panel QListWidget::item:selected {
    background-color: #DBEAFE;
    border: 1px solid #3399FF;
    color: #1E3A8A;
}
QTabWidget#left_panel QListWidget::item:hover:!selected {
    background-color: #F1F5F9;
    border: 1px solid #64748B;
}

/* ===================================================
   CENTER & RIGHT PANELS (Soft Dim Workspace)
   =================================================== */
QFrame#mid_panel, QFrame#right_panel {
    background-color: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
}
QFrame#mid_panel QLabel, QFrame#right_panel QLabel {
    color: #475569;
}
QFrame#mid_panel QLabel[class="title"], QFrame#right_panel QLabel[class="title"] {
    color: #1E293B;
    font-size: 16px;
    font-weight: 700;
}

/* Workspace ListWidget (Macro Steps) */
QFrame#mid_panel QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QFrame#mid_panel QListWidget::item {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 3px 0px;
    color: #334155;
}
QFrame#mid_panel QListWidget::item:selected {
    background-color: #DBEAFE;
    border: 1px solid #3399FF;
    border-left: 4px solid #3399FF;
    color: #1E3A8A;
    font-weight: 600;
}
QFrame#mid_panel QListWidget::item:hover:!selected {
    background-color: #FFFFFF;
    border: 1px solid #94A3B8;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.03);
}

/* Input Fields (Global) */
QLineEdit, 
QComboBox, 
QSpinBox, 
QDoubleSpinBox {
    background-color: #F8FAFC;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
}
QLineEdit:focus, 
QComboBox:focus, 
QSpinBox:focus {
    border: 1px solid #3399FF;
    background-color: #FFFFFF;
}

/* Fix QComboBox Dropdown List */
QComboBox QAbstractItemView {
    background-color: #F8FAFC;
    color: #334155;
    border: 1px solid #CBD5E1;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    outline: none;
}

/* Form Layout Labels */
QFormLayout QLabel {
    color: #64748B;
    font-weight: 500;
}

/* ===================================================
   BUTTONS
   =================================================== */
QPushButton {
    background-color: #F8FAFC;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #FFFFFF;
    border: 1px solid #94A3B8;
}
QPushButton:pressed {
    background-color: #E2E8F0;
}

/* Sidebar Buttons */
QTabWidget#left_panel QPushButton {
    background-color: #F1F5F9;
    color: #334155;
    border: 1px solid #CBD5E1;
}
QTabWidget#left_panel QPushButton:hover {
    background-color: #F8FAFC;
    border: 1px solid #94A3B8;
}

/* Action Buttons (The colorful row) */
QPushButton[action="tap"] { background-color: #2DD4BF; color: white; border: none; }
QPushButton[action="tap"]:hover { background-color: #14B8A6; }
QPushButton[action="swipe"] { background-color: #FBBF24; color: white; border: none; }
QPushButton[action="swipe"]:hover { background-color: #F59E0B; }
QPushButton[action="text"] { background-color: #94A3B8; color: white; border: none; }
QPushButton[action="text"]:hover { background-color: #64748B; }
QPushButton[action="key"] { background-color: #E2E8F0; color: #4F46E5; border: 1px solid #CBD5E1; }
QPushButton[action="key"]:hover { background-color: #F8FAFC; border: 1px solid #A5B4FC; }
QPushButton[action="delay"] { background-color: #64748B; color: white; border: none; }
QPushButton[action="delay"]:hover { background-color: #475569; }
QPushButton[action="code"] { background-color: #A855F7; color: white; border: none; }
QPushButton[action="code"]:hover { background-color: #9333EA; }

/* Semantic Buttons (Primary = Blue #3399FF) */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60A5FA, stop:1 #3399FF);
    color: white;
    border: none;
    font-weight: 600;
}
QPushButton[class="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #93C5FD, stop:1 #3B82F6);
}
QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F87171, stop:1 #EF4444);
    color: white;
    border: none;
    font-weight: 600;
}
QPushButton[class="danger"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FCA5A5, stop:1 #DC2626);
}

/* ===================================================
   SCROLLBARS
   =================================================== */
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background-color: #CBD5E1;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #94A3B8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

QTabWidget#left_panel QScrollBar::handle:vertical { background-color: #CBD5E1; }
QTabWidget#left_panel QScrollBar::handle:vertical:hover { background-color: #94A3B8; }
"""


class MainWindow(QtWidgets.QMainWindow):
    # Tin hieu phat ra tu thread keyboard listener de update UI
    coordinate_captured = QtCore.Signal(int, int, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔ Auto LDPlayer — Macro Studio")
        self.resize(1050, 680)
        self.setStyleSheet(APP_THEME)

        self.adb_manager = AdbManager()
        self.code_manager = CodeManager(Path("codes.json"))
        self.macro_engine = MacroEngine(self.adb_manager, self.code_manager)

        self.actions = []  # Danh sach buoc macro
        self.current_action = None

        # Controller pynput de lay toa do chuot
        self.mouse_controller = mouse.Controller()
        
        # Thiet lap listener bat toa do
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f9>': self._on_capture_hotkey_start,
            '<f10>': self._on_capture_hotkey_end
        })
        self.hotkey_listener.start()

        # Connect signal
        self.coordinate_captured.connect(self.on_coordinate_captured)

        self._init_ui()
        self.refresh_devices()

    def _on_capture_hotkey_start(self):
        x, y = self.mouse_controller.position
        self.coordinate_captured.emit(int(x), int(y), True)

    def _on_capture_hotkey_end(self):
        x, y = self.mouse_controller.position
        self.coordinate_captured.emit(int(x), int(y), False)

    def on_coordinate_captured(self, x, y, is_start):
        from core.window_capture import get_mapped_coordinate
        
        # Lay selected device neu co
        selected_serial = None
        selected = self.device_list.selectedItems()
        if selected:
            selected_serial = selected[0].data(QtCore.Qt.UserRole)
            
        # Thuc hien map toa do thong minh
        adb_x, adb_y = get_mapped_coordinate(x, y, self.adb_manager, selected_serial)
        
        if is_start:
            self.statusBar().showMessage(f"Đã bắt tọa độ Bắt đầu: {adb_x}, {adb_y} (Gốc màn hình: {x}, {y})", 3000)
            if self.current_action and self.current_action.action_type in [ActionType.TAP, ActionType.SWIPE]:
                self.input_x.setValue(adb_x)
                self.input_y.setValue(adb_y)
                self.save_action_details()
        else:
            self.statusBar().showMessage(f"Đã bắt tọa độ Kết thúc: {adb_x}, {adb_y} (Gốc màn hình: {x}, {y})", 3000)
            if self.current_action and self.current_action.action_type == ActionType.SWIPE:
                self.input_end_x.setValue(adb_x)
                self.input_end_y.setValue(adb_y)
                self.save_action_details()

    def start_swipe_recording(self):
        self.statusBar().showMessage("📸 Đang ghi hình Vuốt... Hãy nhấn giữ chuột, kéo trên LDPlayer rồi thả ra.", 5000)
        
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                if pressed:
                    self.coordinate_captured.emit(int(x), int(y), True)
                else:
                    self.coordinate_captured.emit(int(x), int(y), False)
                    return False  # Stop the listener
                    
        listener = mouse.Listener(on_click=on_click)
        listener.start()


    def _init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # ---- LEFT TABS ----
        self.left_tabs = QtWidgets.QTabWidget()
        self.left_tabs.setObjectName("left_panel")
        self.left_tabs.setFixedWidth(300)
        
        # TAB 1: QUAN LY THIET BI
        left_panel = QtWidgets.QWidget()
        left_panel.setObjectName("left_panel_content")
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        
        lbl_devices = QtWidgets.QLabel("📱 Thiết bị LDPlayer")
        lbl_devices.setProperty("class", "title")
        
        self.device_list = QtWidgets.QListWidget()
        self.device_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        btn_refresh = QtWidgets.QPushButton("🔄 Làm mới")
        btn_refresh.setToolTip("Quét lại danh sách giả lập đang chạy")
        btn_refresh.clicked.connect(self.refresh_devices)

        btn_run = QtWidgets.QPushButton("▶ Chạy Macro")
        btn_run.setProperty("class", "primary")
        btn_run.setToolTip("Bắt đầu chạy kịch bản trên các giả lập đã chọn")
        btn_run.clicked.connect(self.run_macro)

        btn_stop = QtWidgets.QPushButton("⏹ Dừng Tất Cả")
        btn_stop.setProperty("class", "danger")
        btn_stop.setToolTip("Dừng ngay toàn bộ kịch bản đang chạy")
        btn_stop.clicked.connect(self.stop_macro)

        left_layout.addWidget(lbl_devices)
        left_layout.addWidget(self.device_list)
        left_layout.addWidget(btn_refresh)
        left_layout.addWidget(btn_run)
        left_layout.addWidget(btn_stop)
        
        # TAB 2: QUAN LY CODE
        code_panel = QtWidgets.QWidget()
        code_panel.setObjectName("code_panel_content")
        code_layout = QtWidgets.QVBoxLayout(code_panel)
        
        lbl_code = QtWidgets.QLabel("🎁 Quản lý Code")
        lbl_code.setProperty("class", "title")
        
        range_layout = QtWidgets.QHBoxLayout()
        range_layout.addWidget(QtWidgets.QLabel("Phạm vi:"))
        
        self.input_code_start = QtWidgets.QLineEdit()
        self.input_code_start.setValidator(QtGui.QIntValidator(1, 999999))
        self.input_code_start.setPlaceholderText("Tất cả")
        self.input_code_start.setFixedWidth(70)
        
        self.input_code_end = QtWidgets.QLineEdit()
        self.input_code_end.setValidator(QtGui.QIntValidator(1, 999999))
        self.input_code_end.setPlaceholderText("Tất cả")
        self.input_code_end.setFixedWidth(70)
        
        range_layout.addWidget(QtWidgets.QLabel("Từ:"))
        range_layout.addWidget(self.input_code_start)
        range_layout.addWidget(QtWidgets.QLabel("Đến:"))
        range_layout.addWidget(self.input_code_end)
        btn_code_layout = QtWidgets.QHBoxLayout()

        self.btn_fetch_code = QtWidgets.QPushButton("🌐 Tải từ Web")
        self.btn_fetch_code.setProperty("class", "primary")
        self.btn_fetch_code.setToolTip("Lấy danh sách code từ API")
        self.btn_fetch_code.clicked.connect(self.code_manager.fetch_from_api)

        self.btn_import_code = QtWidgets.QPushButton("📝 Nhập từ văn bản")
        self.btn_import_code.setProperty("class", "primary")
        self.btn_import_code.setToolTip("Nhập code từ văn bản copy/paste")
        self.btn_import_code.clicked.connect(self.show_import_text_dialog)

        btn_code_layout.addWidget(self.btn_fetch_code)
        btn_code_layout.addWidget(self.btn_import_code)
        
        self.code_list = QtWidgets.QListWidget()
        self.code_list.itemClicked.connect(self.on_code_item_clicked)
        
        code_layout.addWidget(lbl_code)
        code_layout.addLayout(range_layout)
        code_layout.addLayout(btn_code_layout)
        code_layout.addWidget(self.code_list)
        
        self.left_tabs.addTab(left_panel, "📱 Giả lập")
        self.left_tabs.addTab(code_panel, "🎁 Code")
        
        # Kết nối signal của code_manager
        self.code_manager.codes_loaded.connect(self.on_codes_loaded)
        self.code_manager.error_occurred.connect(lambda e: self.statusBar().showMessage(e, 5000))
        self.code_manager.load_from_json()

        # ---- PANEL GIUA: DANH SACH MACRO ----
        mid_panel = QtWidgets.QFrame()
        mid_panel.setObjectName("mid_panel")
        mid_layout = QtWidgets.QVBoxLayout(mid_panel)

        lbl_macro = QtWidgets.QLabel("📜 Kịch bản Macro")
        lbl_macro.setProperty("class", "title")

        # Save / Load Buttons
        file_btn_layout = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton("💾 Lưu Kịch Bản")
        btn_save.setToolTip("Lưu kịch bản hiện tại ra file JSON")
        btn_save.clicked.connect(self.save_to_json)
        btn_load = QtWidgets.QPushButton("📂 Mở Kịch Bản")
        btn_load.setToolTip("Tải kịch bản đã lưu từ file JSON")
        btn_load.clicked.connect(self.load_from_json)
        file_btn_layout.addWidget(btn_save)
        file_btn_layout.addWidget(btn_load)

        self.macro_list = QtWidgets.QListWidget()
        self.macro_list.itemClicked.connect(self.on_action_selected)
        self.macro_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.macro_list.model().rowsMoved.connect(self.on_macro_reordered)

        # Buttons them action
        btn_layout = QtWidgets.QHBoxLayout()
        btn_add_tap = QtWidgets.QPushButton("👆 Chạm")
        btn_add_tap.setProperty("action", "tap")
        btn_add_tap.setToolTip("Thêm bước: Chạm vào 1 điểm trên màn hình")
        btn_add_tap.clicked.connect(lambda: self.add_action(ActionType.TAP))
        
        btn_add_swipe = QtWidgets.QPushButton("👉 Vuốt")
        btn_add_swipe.setProperty("action", "swipe")
        btn_add_swipe.setToolTip("Thêm bước: Vuốt từ điểm A đến điểm B")
        btn_add_swipe.clicked.connect(lambda: self.add_action(ActionType.SWIPE))
        
        btn_add_text = QtWidgets.QPushButton("✏ Nhập chữ")
        btn_add_text.setProperty("action", "text")
        btn_add_text.setToolTip("Thêm bước: Gõ một đoạn văn bản")
        btn_add_text.clicked.connect(lambda: self.add_action(ActionType.TEXT))
        
        btn_add_key = QtWidgets.QPushButton("⌨ Phím")
        btn_add_key.setProperty("action", "key")
        btn_add_key.setToolTip("Thêm bước: Bấm phím cứng (Enter, Back...)")
        btn_add_key.clicked.connect(lambda: self.add_action(ActionType.KEYEVENT))
        
        btn_add_delay = QtWidgets.QPushButton("⏱ Chờ")
        btn_add_delay.setProperty("action", "delay")
        btn_add_delay.setToolTip("Thêm bước: Dừng lại chờ một khoảng thời gian")
        btn_add_delay.clicked.connect(lambda: self.add_action(ActionType.DELAY))
        
        btn_add_code = QtWidgets.QPushButton("🎁 Code")
        btn_add_code.setProperty("action", "code")
        btn_add_code.setToolTip("Thêm bước: Nhập code từ danh sách quản lý")
        btn_add_code.clicked.connect(lambda: self.add_action(ActionType.INPUT_CODE))

        btn_layout.addWidget(btn_add_tap)
        btn_layout.addWidget(btn_add_swipe)
        btn_layout.addWidget(btn_add_text)
        btn_layout.addWidget(btn_add_key)
        btn_layout.addWidget(btn_add_delay)
        btn_layout.addWidget(btn_add_code)

        btn_delete = QtWidgets.QPushButton("🗑 Xóa bước")
        btn_delete.setToolTip("Xóa bước đang được chọn trong danh sách")
        btn_delete.clicked.connect(self.delete_selected_action)

        self.input_loop = QtWidgets.QSpinBox()
        self.input_loop.setRange(0, 100000)
        self.input_loop.setValue(1)
        
        loop_layout = QtWidgets.QFormLayout()
        loop_layout.addRow("Số lần lặp (0=Vô hạn):", self.input_loop)

        mid_layout.addWidget(lbl_macro)
        mid_layout.addLayout(file_btn_layout)
        mid_layout.addWidget(self.macro_list)
        mid_layout.addLayout(btn_layout)
        mid_layout.addWidget(btn_delete)
        mid_layout.addLayout(loop_layout)

        main_layout.addWidget(self.left_tabs)
        main_layout.addWidget(mid_panel, stretch=1)

        # ---- PANEL PHAI: CHI TIET ACTION ----
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("right_panel")
        self.right_layout = QtWidgets.QFormLayout(right_panel)
        self.right_layout.setVerticalSpacing(16)
        
        lbl_details = QtWidgets.QLabel("⚙ Chi tiết Bước")
        lbl_details.setProperty("class", "title")
        self.right_layout.addRow(lbl_details)
        
        lbl_hint = QtWidgets.QLabel("💡 Bấm F9 = lấy tọa độ bắt đầu\n      F10 = lấy tọa độ kết thúc")
        lbl_hint.setStyleSheet("color: #53D8C7; font-size: 12px; font-style: italic;")
        self.right_layout.addRow(lbl_hint)

        # Cac widget cho chi tiet
        self.input_x = QtWidgets.QSpinBox()
        self.input_x.setRange(-9999, 9999)
        self.input_y = QtWidgets.QSpinBox()
        self.input_y.setRange(-9999, 9999)
        
        self.input_end_x = QtWidgets.QSpinBox()
        self.input_end_x.setRange(-9999, 9999)
        self.input_end_y = QtWidgets.QSpinBox()
        self.input_end_y.setRange(-9999, 9999)
        
        self.input_duration = QtWidgets.QSpinBox()
        self.input_duration.setRange(0, 10000)
        self.input_duration.setValue(500)

        self.input_text = QtWidgets.QLineEdit()
        self.input_keycode = QtWidgets.QSpinBox()
        self.input_keycode.setRange(0, 300)
        self.input_delay = QtWidgets.QDoubleSpinBox()
        self.input_delay.setRange(0, 100000)
        
        self.input_key = QtWidgets.QComboBox()
        self.input_key.addItems([
            "Enter (66)",
            "Back (4)",
            "Home (3)",
            "Tab (61)",
            "Esc (111)",
            "Backspace (67)"
        ])
        
        self.input_delay = QtWidgets.QSpinBox()
        self.input_delay.setRange(0, 60000)
        self.input_delay.setValue(1000)

        self.btn_record_swipe = QtWidgets.QPushButton("📸 Ghi hình Vuốt")
        self.btn_record_swipe.setProperty("class", "primary")
        self.btn_record_swipe.clicked.connect(self.start_swipe_recording)

        # Add rows (se an hien tuy loai action)
        self.row_x = self.right_layout.addRow("Tọa độ X:", self.input_x)
        self.row_y = self.right_layout.addRow("Tọa độ Y:", self.input_y)
        self.row_end_x = self.right_layout.addRow("Tọa độ tới X:", self.input_end_x)
        self.row_end_y = self.right_layout.addRow("Tọa độ tới Y:", self.input_end_y)
        self.row_duration = self.right_layout.addRow("TG Vuốt (ms):", self.input_duration)
        self.row_record_swipe = self.right_layout.addRow("", self.btn_record_swipe)
        
        self.row_text = self.right_layout.addRow("Văn bản:", self.input_text)
        self.row_key = self.right_layout.addRow("Phím cứng:", self.input_key)
        self.row_delay = self.right_layout.addRow("TG Chờ (ms):", self.input_delay)

        self.btn_save_action = QtWidgets.QPushButton("Lưu thay đổi")
        self.btn_save_action.setProperty("class", "primary")
        self.btn_save_action.clicked.connect(self.save_action_details)
        self.right_layout.addRow(self.btn_save_action)

        right_panel.setFixedWidth(320)

        main_layout.addWidget(right_panel)

        self.hide_all_editors()
        self.statusBar().showMessage("⚔ Sẵn sàng chiến đấu! (F9 = Bắt tọa độ)")

    def hide_all_editors(self):
        for i in range(2, self.right_layout.rowCount() - 1): # Start from 2 to keep Title and Hint
            if self.right_layout.itemAt(i, QtWidgets.QFormLayout.LabelRole):
                self.right_layout.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().hide()
            if self.right_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole):
                self.right_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().hide()

    def show_editor_row(self, row_widget):
        for i in range(2, self.right_layout.rowCount() - 1):
            field = self.right_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole)
            if field and field.widget() == row_widget:
                label = self.right_layout.itemAt(i, QtWidgets.QFormLayout.LabelRole)
                if label:
                    label.widget().show()
                row_widget.show()
                break

    def refresh_devices(self):
        self.device_list.clear()
        devices = self.adb_manager.get_devices()
        if not devices:
            # Thu quet manual port 5555 toi 5565
            self.adb_manager.scan_local_emulators()
            devices = self.adb_manager.get_devices()

        # Lọc bỏ các thiết bị trùng lặp (ví dụ: emulator-5564 và 127.0.0.1:5565 là một)
        valid_devices = []
        tcp_ports = set()
        
        for d in devices:
            if d.serial.startswith('127.0.0.1:'):
                try:
                    tcp_ports.add(int(d.serial.split(':')[1]))
                except ValueError:
                    pass

        for d in devices:
            if d.serial.startswith('emulator-'):
                try:
                    emu_port = int(d.serial.split('-')[1])
                    if (emu_port + 1) in tcp_ports:
                        continue  # Bỏ qua vì đã có địa chỉ 127.0.0.1 tương ứng
                except ValueError:
                    pass
            valid_devices.append(d)

        for d in valid_devices:
            item = QtWidgets.QListWidgetItem(f"📱 {d.serial}")
            item.setData(QtCore.Qt.UserRole, d.serial)
            self.device_list.addItem(item)
            
        if valid_devices:
            self.statusBar().showMessage(f"Đã tìm thấy {len(valid_devices)} thiết bị giả lập.")
        else:
            self.statusBar().showMessage("Không tìm thấy giả lập nào.")

    def update_macro_list_ui(self):
        self.macro_list.clear()
        for idx, action in enumerate(self.actions):
            text = f"{idx+1}. {action.action_type.value}"
            if action.action_type == ActionType.TAP:
                text += f" ({action.x}, {action.y})"
            elif action.action_type == ActionType.SWIPE:
                text += f" ({action.x},{action.y} -> {action.end_x},{action.end_y})"
            elif action.action_type == ActionType.TEXT:
                text += f" '{action.text}'"
            elif action.action_type == ActionType.KEYEVENT:
                text += f" (Mã phím: {action.keycode})"
            elif action.action_type == ActionType.INPUT_CODE:
                text += " [Lấy từ Code Manager]"
            elif action.action_type == ActionType.DELAY:
                text += f" {action.delay_ms}ms"
            
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, action.id)
            self.macro_list.addItem(item)

    def on_macro_reordered(self, parent, start, end, destination, row):
        new_actions = []
        for i in range(self.macro_list.count()):
            item = self.macro_list.item(i)
            action_id = item.data(QtCore.Qt.UserRole)
            for action in self.actions:
                if action.id == action_id:
                    new_actions.append(action)
                    break
        self.actions = new_actions
        self.macro_list.blockSignals(True)
        self.update_macro_list_ui()
        self.macro_list.blockSignals(False)

    def add_action(self, atype):
        action = AdbAction(action_type=atype)
        self.actions.append(action)
        self.update_macro_list_ui()
        self.macro_list.setCurrentRow(len(self.actions) - 1)
        self.on_action_selected(self.macro_list.item(len(self.actions) - 1))

    def on_action_selected(self, item):
        if not item: return
        action_id = item.data(QtCore.Qt.UserRole)
        self.current_action = next((a for a in self.actions if a.id == action_id), None)
        if not self.current_action: return

        self.hide_all_editors()
        a = self.current_action

        if a.action_type == ActionType.TAP:
            self.input_x.setValue(a.x)
            self.input_y.setValue(a.y)
            self.show_editor_row(self.input_x)
            self.show_editor_row(self.input_y)
        
        elif a.action_type == ActionType.SWIPE:
            self.input_x.setValue(a.x)
            self.input_y.setValue(a.y)
            self.input_end_x.setValue(a.end_x)
            self.input_end_y.setValue(a.end_y)
            self.input_duration.setValue(a.duration_ms)
            self.show_editor_row(self.input_x)
            self.show_editor_row(self.input_y)
            self.show_editor_row(self.input_end_x)
            self.show_editor_row(self.input_end_y)
            self.show_editor_row(self.input_duration)
            self.show_editor_row(self.btn_record_swipe)
            
        elif a.action_type == ActionType.TEXT:
            self.input_text.setText(a.text)
            self.show_editor_row(self.input_text)
            
        elif a.action_type == ActionType.KEYEVENT:
            index = 0
            # Tim index trong combo box dua vao keycode
            for i in range(self.input_key.count()):
                if str(a.keycode) in self.input_key.itemText(i):
                    index = i
                    break
            self.input_key.setCurrentIndex(index)
            self.show_editor_row(self.input_key)
            
        elif a.action_type == ActionType.DELAY:
            self.input_delay.setValue(a.delay_ms)
            self.show_editor_row(self.input_delay)

    def save_action_details(self):
        if not self.current_action: return
        a = self.current_action
        if a.action_type == ActionType.TAP:
            a.x = self.input_x.value()
            a.y = self.input_y.value()
        elif a.action_type == ActionType.SWIPE:
            a.x = self.input_x.value()
            a.y = self.input_y.value()
            a.end_x = self.input_end_x.value()
            a.end_y = self.input_end_y.value()
            a.duration_ms = self.input_duration.value()
        elif a.action_type == ActionType.TEXT:
            a.text = self.input_text.text()
        elif a.action_type == ActionType.KEYEVENT:
            # Trich xuat so tu "Enter (66)"
            text = self.input_key.currentText()
            import re
            match = re.search(r'\((\d+)\)', text)
            if match:
                a.keycode = int(match.group(1))
        elif a.action_type == ActionType.INPUT_CODE:
            pass # No extra parameters
        elif a.action_type == ActionType.DELAY:
            a.delay_ms = self.input_delay.value()
            
        self.update_macro_list_ui()

    def delete_selected_action(self):
        row = self.macro_list.currentRow()
        if row >= 0:
            del self.actions[row]
            self.current_action = None
            self.hide_all_editors()
            self.update_macro_list_ui()

    # --- TINH NANG SAVE / LOAD ---
    def save_to_json(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Lưu Kịch Bản", "", "JSON Files (*.json)")
        if filename:
            try:
                data = {
                    "loop_count": self.input_loop.value(),
                    "actions": [a.to_dict() for a in self.actions]
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                QtWidgets.QMessageBox.information(self, "Thành công", "Đã lưu kịch bản thành công!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

    def load_from_json(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Mở Kịch Bản", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Ho tro format cu (list object) hoac format moi (dict)
                if isinstance(data, list):
                    self.actions = [AdbAction.from_dict(d) for d in data]
                    self.input_loop.setValue(1)
                else:
                    self.actions = [AdbAction.from_dict(d) for d in data.get("actions", [])]
                    self.input_loop.setValue(data.get("loop_count", 1))
                    
                self.update_macro_list_ui()
                self.hide_all_editors()
                self.current_action = None
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể đọc file: {e}")

    def run_macro(self):
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất 1 thiết bị LDPlayer từ danh sách!")
            return
        if not self.actions:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Kịch bản trống!")
            return

        has_input_code = any(a.action_type == ActionType.INPUT_CODE for a in self.actions)
        if has_input_code:
            start_text = self.input_code_start.text().strip()
            end_text = self.input_code_end.text().strip()
            if not start_text or not end_text:
                range_text = ""
            else:
                range_text = f"{start_text}-{end_text}"
            total_queue = self.code_manager.setup_queue(range_text)
            if total_queue == 0:
                QtWidgets.QMessageBox.warning(self, "Lỗi", "Không có Code nào trong hàng đợi (Hãy kiểm tra lại phạm vi hoặc tải code)!")
                return
        else:
            # Reset queue if no INPUT_CODE just in case
            self.code_manager.reset_queue()

        loop_count = self.input_loop.value()
        for item in selected_items:
            device_id = item.data(QtCore.Qt.UserRole)
            self.macro_engine.start_macro(device_id, self.actions, loop_count, self.on_macro_status)
            
        self.statusBar().showMessage(f"Đang chạy macro trên {len(selected_items)} thiết bị...")

    def stop_macro(self):
        self.macro_engine.stop_all()
        self.statusBar().showMessage("Đã phát lệnh dừng toàn bộ.")

    def on_macro_status(self, device_id, status):
        # Ham callback duoc goi tu thread, ta can luu y khi cap nhat UI 
        # nhung chi in ra console cho don gian.
        print(f"[Thiết bị: {device_id}] Trạng thái: {status}")

    def closeEvent(self, event):
        self.stop_macro()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        super().closeEvent(event)

    def on_codes_loaded(self, codes):
        self.code_list.clear()
        for c in codes:
            self.code_list.addItem(c.preview(50))
        self.statusBar().showMessage(f"Đã tải {len(codes)} code thành công.")

    def on_code_item_clicked(self, item):
        row = self.code_list.row(item)
        if 0 <= row < len(self.code_manager.codes):
            code_str = self.code_manager.codes[row].context
            QtWidgets.QApplication.clipboard().setText(code_str)
            self.statusBar().showMessage(f"📋 Đã copy code: {code_str}", 3000)

    def show_import_text_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Nhập code từ văn bản")
        dialog.setMinimumSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        lbl_info = QtWidgets.QLabel("Dán đoạn văn bản chứa code vào đây:\n(Hỗ trợ định dạng có số thứ tự ở đầu, ví dụ: '1. code', '1 code', '1/ code', ...)")
        layout.addWidget(lbl_info)
        
        text_edit = QtWidgets.QPlainTextEdit()
        layout.addWidget(text_edit)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            text = text_edit.toPlainText()
            if text.strip():
                self.code_manager.import_from_text(text)
