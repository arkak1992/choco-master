import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal

SETTINGS_FILE = "settings.json"

class SettingsUI(QWidget):
    settings_applied = pyqtSignal(dict)  # إشارة لإرسال القيم المختارة

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 1024, 600)
        self.setStyleSheet("background-color: #0F2027; color: white; font-family: Arial;")

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Settings")
        self.title_label.setStyleSheet("font-size: 50px; font-weight: bold; color: #00FFFF;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Grid layout for settings options
        settings_layout = QGridLayout()

        # Start Temperature
        self.temp_label = QLabel("Start Temperature")
        self.temp_combo = QComboBox()
        self.temp_combo.addItems([str(i) + " °C" for i in range(24, 37)])
        settings_layout.addWidget(self.temp_label, 0, 0)
        settings_layout.addWidget(self.temp_combo, 0, 1)

        # Process Duration
        self.time_label = QLabel("Process Duration")
        self.time_combo = QComboBox()
        self.time_combo.addItems([str(i) + " min" for i in range(3, 21)])
        settings_layout.addWidget(self.time_label, 1, 0)
        settings_layout.addWidget(self.time_combo, 1, 1)

        layout.addLayout(settings_layout)

        # Apply Button
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.setStyleSheet("font-size: 24px; padding: 15px;")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        # Load saved settings
        self.load_settings()

        # حفظ تلقائي عند التغيير في القيم
        self.temp_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.time_combo.currentIndexChanged.connect(self.auto_save_settings)

        self.setLayout(layout)

    def get_settings(self):
        """إرجاع القيم المختارة من الإعدادات"""
        return {
            "start_temperature": int(self.temp_combo.currentText().split()[0]),
            "duration": int(self.time_combo.currentText().split()[0])
        }

    def apply_settings(self):
        """حفظ القيم المختارة وإرسالها إلى الواجهة الرئيسية"""
        settings = self.get_settings()
        self.settings_applied.emit(settings)
        self.save_settings(settings)
        print(f"✅ Settings applied: {settings}")
        self.close()

    def auto_save_settings(self):
        """حفظ الإعدادات تلقائيًا عند التغيير"""
        settings = self.get_settings()
        self.save_settings(settings)
        print(f"💾 Auto-saved settings: {settings}")

    def save_settings(self, settings):
        """حفظ القيم إلى ملف JSON"""
        try:
            with open(SETTINGS_FILE, 'w') as file:
                json.dump(settings, file)
        except Exception as e:
            print(f"⚠ Error saving settings: {e}")

    def load_settings(self):
        """تحميل القيم من ملف JSON عند بدء التشغيل"""
        try:
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.temp_combo.setCurrentText(f"{settings['start_temperature']} °C")
                self.time_combo.setCurrentText(f"{settings['duration']} min")
                print(f"🔄 Loaded settings: {settings}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠ No valid settings found, using defaults.")
            default_settings = {"start_temperature": 30, "duration": 5}
            self.save_settings(default_settings)  # حفظ القيم الافتراضية

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = QWidget()
    window = SettingsUI(main_win)
    window.show()
    sys.exit(app.exec())
