import os
import datetime
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

class GraphWidget(QWidget):
    process_completed = pyqtSignal()

    def __init__(self, arduino_reader, start_temperature=30, process_duration=3):
        super().__init__()

        layout = QVBoxLayout()
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("#1A1A1A")
        self.graph_widget.setTitle("Temperature vs Time", color="w", size="18pt")
        self.graph_widget.setLabel("left", "Temperature (\u00b0C)", color="white", size="14pt")
        self.graph_widget.setLabel("bottom", "Time (s)", color="white", size="14pt")

        layout.addWidget(self.graph_widget)
        self.setLayout(layout)

        self.start_temperature = start_temperature
        self.process_duration = process_duration * 60
        self.max_time = self.process_duration

        self.temperature_data = []
        self.time_data = []

        self.data_points = 0
        self.running = False
        self.process_started = False

        self.arduino_reader = arduino_reader
        self.curve = self.graph_widget.plot(pen=pg.mkPen(color="c", width=2))

        self.start_temp_line = pg.InfiniteLine(pos=self.start_temperature, angle=0,
                                               pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine))
        self.graph_widget.addItem(self.start_temp_line)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def start_graph(self):
        if not self.running:
            self.temperature_data.clear()
            self.time_data.clear()
            self.data_points = 0
            self.running = True
            self.process_started = True
            self.max_time = self.process_duration
            self.graph_widget.setXRange(0, self.max_time, padding=0)
            self.timer.start(4000)  # ✅ تحديث كل 4 ثوانٍ
            print(f"✅ Graph started (Duration: {self.process_duration} sec).", flush=True)

    def stop_graph(self):
        if not self.running:
            return

        self.running = False
        self.timer.stop()
        print("🛑 Stopping graph and saving results...", flush=True)
        self.save_results()
        print("✅ Graph stopped and results saved.", flush=True)

    def update_plot(self):
        if self.running:
            try:
                temperature = self.arduino_reader.get_latest_temperature()
                hidden_heat = self.arduino_reader.get_hidden_heat_signal()

                if temperature is None or not (15 <= temperature <= 36):
                    print(f"⚠ Ignoring invalid temperature: {temperature}", flush=True)
                    return

                self.data_points += 4  # ✅ تحديث كل 4 ثوانٍ
                current_time = self.data_points / 10
                self.time_data.append(current_time)
                self.temperature_data.append(temperature)

                if len(self.temperature_data) > 10:
                    smoothed_temp = savgol_filter(self.temperature_data, 11, 3).tolist()
                else:
                    smoothed_temp = self.temperature_data

                if hidden_heat is not None and 20 <= hidden_heat <= 26:
                    print(f"🔥 Hidden heat peak detected: {hidden_heat}\u00b0C", flush=True)
                    smoothed_temp[-1] = hidden_heat + 0.2  # ✅ إضافة قمة واضحة بدلًا من شد الخط

                self.curve.setData(self.time_data, smoothed_temp)
                min_temp = min(smoothed_temp) - 0.5
                max_temp = max(smoothed_temp) + 0.5
                self.graph_widget.setYRange(min_temp, max_temp, padding=0)

                if self.process_started and (self.data_points / 10 >= self.process_duration):
                    self.stop_graph()
                    self.process_completed.emit()

            except Exception as e:
                print(f"⚠ Error in update_plot: {e}", flush=True)

    def save_results(self):
        if not self.time_data or not self.temperature_data:
            print("⚠ No data to save. Skipping file creation.", flush=True)
            return

        today_folder = self.get_today_folder()
        os.makedirs(today_folder, exist_ok=True)

        image_path = os.path.join(today_folder, f"result_{datetime.datetime.now().strftime('%H-%M-%S')}.png")
        image_path = os.path.abspath(image_path)

        print(f"📁 Saving image at: {image_path}", flush=True)

        try:
            plt.figure(figsize=(6, 4), dpi=300)
            plt.plot(self.time_data, self.temperature_data, label="Temperature Curve", color="black", linewidth=1.5)
            plt.xlabel("Time (s)")
            plt.ylabel("Temperature (\u00b0C)")
            plt.title("Temperature Curve")
            plt.grid(True, linestyle="--", linewidth=0.5)
            plt.legend()

            plt.savefig(image_path, bbox_inches='tight')
            plt.close()

            print(f"📷 Image saved successfully at: {image_path}", flush=True)

        except Exception as e:
            print(f"❌ Error saving image: {e}", flush=True)

    def get_today_folder(self):
        base_path = r"C:/Users/32465/Documents/arkak project/choco-master/results"
        today = datetime.date.today().strftime("%Y-%m-%d")
        full_path = os.path.join(base_path, today)
        print(f"📂 Ensuring folder exists: {full_path}", flush=True)
        return full_path

    def update_start_temperature(self, new_temp):
        self.start_temperature = new_temp
        self.start_temp_line.setValue(new_temp)
        print(f"📌 Start temperature updated to: {new_temp}\u00b0C", flush=True)

    def update_process_duration(self, new_duration):
        self.process_duration = new_duration * 60
        self.max_time = self.process_duration
        self.graph_widget.setXRange(0, self.max_time, padding=0)
        print(f"📌 Process duration updated to: {new_duration} minutes", flush=True)
