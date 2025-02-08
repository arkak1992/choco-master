import sys
import json
from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QVBoxLayout, QSizePolicy, QMessageBox
from ui.sensor_widget import SensorWidget
from ui.graph_widget import GraphWidget
from ui.control_buttons import ControlButtons
from ui.settings_ui import SettingsUI  # استيراد نافذة الإعدادات
from sensors.arduino_receiver import ArduinoReader  # استيراد قارئ البيانات
from PyQt6.QtGui import QPalette, QLinearGradient, QColor, QBrush

# تحميل إعدادات المستخدم من ملف JSON
def load_settings():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"start_temperature": 30, "duration": 5}  # القيم الافتراضية

# حفظ إعدادات المستخدم إلى ملف JSON
def save_settings(settings):
    with open("config.json", "w") as file:
        json.dump(settings, file)

class ChocoMasterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choco Master - User Interface")
        self.setGeometry(100, 100, 1024, 600)

        self.setup_background()

        # إنشاء كائن قارئ الأردوينو كمصدر بيانات مركزي
        self.arduino_reader = ArduinoReader(port='COM3', baudrate=115200)
        self.arduino_reader.start_reading()  # بدء استقبال البيانات عند تشغيل التطبيق

        # تحميل إعدادات المستخدم
        self.settings_data = load_settings()

        # التخطيط الرئيسي
        main_layout = QGridLayout()
        left_layout = QVBoxLayout()

        # تمرير كائن القارئ إلى مستشعر الحرارة
        self.sensor_widget = SensorWidget(self.arduino_reader)
        left_layout.addWidget(self.sensor_widget)

        # إضافة الأزرار وربطها بالأحداث
        self.buttons_widget = ControlButtons()
        self.buttons_widget.start_clicked.connect(self.start_graph)
        self.buttons_widget.stop_clicked.connect(self.stop_graph)
        self.buttons_widget.settings_clicked.connect(self.open_settings)  # فتح نافذة الإعدادات
        left_layout.addWidget(self.buttons_widget)

        main_layout.addLayout(left_layout, 0, 0)

        # تمرير كائن القارئ والإعدادات إلى الرسم البياني
        self.graph_widget = GraphWidget(
            self.arduino_reader,
            start_temperature=self.settings_data["start_temperature"],
            process_duration=self.settings_data["duration"]
        )
        self.graph_widget.process_completed.connect(self.handle_process_completion)
        main_layout.addWidget(self.graph_widget, 0, 1)

        # ضبط حجم العناصر لتكون قابلة للتغيير
        self.graph_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sensor_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.setLayout(main_layout)

    def setup_background(self):
        """إعداد خلفية النافذة بتدرج لوني جميل"""
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 1024, 600)
        gradient.setColorAt(0.0, QColor("#0F2027"))
        gradient.setColorAt(0.5, QColor("#203A43"))
        gradient.setColorAt(1.0, QColor("#2C5364"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

    def start_graph(self):
        """بدء الرسم البياني عند الضغط على زر Start"""
        if not self.graph_widget.running:
            # تحديث القيم قبل بدء الرسم
            self.graph_widget.update_start_temperature(self.settings_data["start_temperature"])
            self.graph_widget.update_process_duration(self.settings_data["duration"])
            self.graph_widget.start_graph()
            self.buttons_widget.start_button.setText("Stop")
            self.buttons_widget.start_button.setStyleSheet("background-color: red; color: white;")
            print(f"✅ Graph started with Start Temp: {self.settings_data['start_temperature']}°C, Duration: {self.settings_data['duration']} min.")
        else:
            print("⚠ Graph is already running!")

    def stop_graph(self):
        """إيقاف الرسم البياني عند الضغط على زر Stop"""
        self.graph_widget.stop_graph()
        self.buttons_widget.start_button.setText("Start")
        self.buttons_widget.start_button.setStyleSheet("background-color: green; color: white;")
        print("🛑 Graph stopped.")

    def handle_process_completion(self):
        """معالجة انتهاء العملية وتحديث الزر"""
        self.buttons_widget.start_button.setText("Start")
        self.buttons_widget.start_button.setStyleSheet("background-color: green; color: white;")
        print("✅ Process completed. Ready to start again.")

    def open_settings(self):
        """فتح نافذة الإعدادات عند الضغط على زر Settings"""
        if hasattr(self, 'settings_window') and self.settings_window is not None:
            self.settings_window.close()
        self.settings_window = SettingsUI(self)
        self.settings_window.settings_applied.connect(self.apply_settings)
        self.settings_window.show()

    def apply_settings(self, settings):
        """تطبيق القيم المختارة من نافذة الإعدادات"""
        self.settings_data.update(settings)
        save_settings(self.settings_data)

        # تحديث القيم في الرسم البياني أثناء تشغيله
        if self.graph_widget.running:
            print("🔄 Restarting graph with new settings...")
            self.stop_graph()
            self.start_graph()
        else:
            self.graph_widget.update_start_temperature(settings["start_temperature"])
            self.graph_widget.update_process_duration(settings["duration"])

        print(f"✅ Settings Applied: Start Temp = {self.settings_data['start_temperature']}°C, Duration = {self.settings_data['duration']} min")

    def closeEvent(self, event):
        """ضمان إيقاف العمليات عند إغلاق التطبيق"""
        reply = QMessageBox.question(self, "Exit Confirmation",
                                     "Are you sure you want to exit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.arduino_reader.stop_reading()  # إيقاف استقبال البيانات عند الإغلاق
            self.graph_widget.stop_graph()
            save_settings(self.settings_data)  # حفظ آخر الإعدادات قبل الإغلاق
            print("🛑 Application closed cleanly.")
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChocoMasterUI()
    window.show()
    sys.exit(app.exec())
