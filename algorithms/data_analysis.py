import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt

class DataAnalysis:
    def __init__(self, results_folder):
        self.results_folder = results_folder

    def ensure_directory(self):
        """إنشاء مجلد اليوم إذا لم يكن موجودًا"""
        today_folder = self.get_today_folder()
        if not os.path.exists(today_folder):
            os.makedirs(today_folder)
            print(f"[INFO] Created directory: {today_folder}")
        return today_folder

    def get_today_folder(self):
        """إرجاع المسار إلى مجلد اليوم بتنسيق YYYY-MM-DD"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        return os.path.join(self.results_folder, today)

    def analyze_and_save(self, csv_file):
        """تحليل البيانات وتصدير النتائج كصورة PNG"""
        try:
            # التحقق من وجود الملف
            if not os.path.exists(csv_file):
                print(f"[ERROR] File {csv_file} not found.")
                return

            df = pd.read_csv(csv_file)

            # التحقق من وجود الأعمدة المطلوبة
            if 'Time (s)' not in df.columns or 'Temperature (°C)' not in df.columns:
                print("[ERROR] CSV file does not contain required columns: 'Time (s)', 'Temperature (°C)'")
                return

            if df.empty:
                print("[ERROR] CSV file is empty.")
                return

            plt.figure(figsize=(2.28, 4), dpi=300)  # مقاس 58 ملم (2.28 انش)

            # رسم العنوان
            plt.text(0.5, 1.05, "Choco-Master", fontsize=14, ha='center', transform=plt.gca().transAxes)

            # رسم الشارت
            plt.plot(df['Time (s)'], df['Temperature (°C)'], label='Temperature', color='blue')
            plt.xlabel('Time (s)')
            plt.ylabel('Temperature (°C)')
            plt.title('Temperature Analysis')
            plt.legend()
            plt.grid()

            # حساب مؤشر التمبراندكس
            temper_index = round(df['Temperature (°C)'].mean(), 2)
            plt.text(0.5, -0.15, f"Temper Index: {temper_index}", fontsize=12, ha='center', transform=plt.gca().transAxes)

            # حفظ الصورة بصيغة PNG
            save_path = os.path.join(self.ensure_directory(), f"result_{datetime.datetime.now().strftime('%H-%M-%S')}.png")
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
            print(f"[SUCCESS] Analysis saved as PNG at: {save_path}")

        except Exception as e:
            print(f"[ERROR] An error occurred during analysis: {e}")

# مثال على الاستخدام
if __name__ == "__main__":
    csv_path = "C:\\Users\\32465\\Documents\\arkak project\\choco-master\\results\\2025-01-27\\exported_data.csv"
    analysis = DataAnalysis("C:\\Users\\32465\\Documents\\arkak project\\choco-master\\results")
    analysis.analyze_and_save(csv_path)
