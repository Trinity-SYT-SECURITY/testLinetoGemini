import os
import csv
from datetime import datetime

class ReportManager:
    def __init__(self, save_path="/tmp/reports"):
        self.save_path = save_path
        os.makedirs(self.save_path, exist_ok=True)
        self.records = []
        self.csv_file = os.path.join(self.save_path, "report.csv")
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Timestamp","UserID","UserMessage","ImageSaved","AI_Reply"])
                writer.writeheader()

    def add_record(self, user_id, user_message, ai_reply, image_filename=None):
        record = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "UserID": user_id,
            "UserMessage": user_message,
            "ImageSaved": image_filename if image_filename else "",
            "AI_Reply": ai_reply
        }
        self.records.append(record)
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            writer.writerow(record)
        return self.csv_file
