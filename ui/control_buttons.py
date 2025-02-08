from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from ui.settings_ui import SettingsUI
from ui.print_ui import PrintUI

class ControlButtons(QWidget):
    # إشارات لزر Start/Stop والإعدادات للتفاعل مع الواجهة الرئيسية
    start_clicked = pyqtSignal(bool)  # إشارة عند الضغط على زر Start/Stop
    stop_clicked = pyqtSignal()       # إشارة عند الضغط على Stop
    settings_clicked = pyqtSignal()   # إشارة عند الضغط على زر Settings

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.setFixedHeight(50)
        self.start_button.setStyleSheet(
            "font-size: 20px; padding: 15px; border-radius: 8px; background-color: #00FF00; color: black;"
        )
        self.start_button.clicked.connect(self.toggle_start_stop)
        layout.addWidget(self.start_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet(
            "font-size: 20px; padding: 15px; background-color: #333; color: white; border: 2px solid #f1c232;"
        )
        self.settings_button.clicked.connect(self.settings_clicked.emit)  # إرسال الإشارة عند الضغط
        layout.addWidget(self.settings_button)

        self.history_button = QPushButton("History")
        self.history_button.setStyleSheet(
            "font-size: 20px; padding: 15px; background-color: #333; color: white; border: 2px solid #cc0000;"
        )
        self.history_button.clicked.connect(self.open_history)
        layout.addWidget(self.history_button)

        self.setLayout(layout)
        self.running = False  # حالة الزر (تشغيل أو إيقاف)

    def toggle_start_stop(self):
        if not self.running:
            self.start_button.setText("Stop")
            self.start_button.setStyleSheet("background-color: #FF0000; color: white;")
            self.start_clicked.emit(True)  # إرسال إشارة لبدء المخطط البياني
        else:
            self.start_button.setText("Start")
            self.start_button.setStyleSheet("background-color: #00FF00; color: black;")
            self.stop_clicked.emit()  # إرسال إشارة لإيقاف التحديث
        self.running = not self.running

    def open_history(self):
        self.history_window = PrintUI(self)
        self.history_window.show()
