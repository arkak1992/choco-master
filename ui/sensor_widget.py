from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

class SensorWidget(QWidget):
    def __init__(self, arduino_reader):
        super().__init__()
        self.setStyleSheet("background-color: #333; border: 2px solid #00FFFF; border-radius: 10px; padding: 15px;")

        layout = QVBoxLayout()
        self.sensor_label = QLabel("Sensor Temperature")
        self.sensor_label.setStyleSheet("font-size: 24px; color: #00FFFF;")
        layout.addWidget(self.sensor_label)

        self.sensor_value = QLabel("Waiting...")
        self.sensor_value.setStyleSheet("font-size: 36px; font-weight: bold; color: #FF4500;")
        layout.addWidget(self.sensor_value)

        self.setLayout(layout)

        self.arduino_reader = arduino_reader

        # تحديث القيم 10 مرات في الثانية (كل 100ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_value)
        self.timer.start(100)  # تحديث كل 100 ميلي ثانية

    def update_sensor_value(self):
        """تحديث قيمة الحساس"""
        temperature = self.arduino_reader.get_latest_temperature()
        if temperature is not None:
            self.sensor_value.setText(f"{temperature:.2f} °C")
        else:
            self.sensor_value.setText("No Data")

    def closeEvent(self, event):
        """إيقاف المؤقت عند إغلاق النافذة"""
        self.timer.stop()
        event.accept()
