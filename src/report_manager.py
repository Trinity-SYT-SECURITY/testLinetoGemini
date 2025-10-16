import pandas as pd, os
from datetime import datetime

class ReportManager:
    def __init__(self):
        self.save_path = "/tmp/reports"
        os.makedirs(self.save_path, exist_ok=True)
        self.records = []

    def add_record(self, user_id, user_message, ai_reply, image_bytes=None):
        image_filename = ""
        if image_bytes:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{user_id}_{timestamp}.jpg"
            with open(os.path.join(self.save_path, image_filename), "wb") as f:
                f.write(image_bytes)

        self.records.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "UserID": user_id,
            "UserMessage": user_message,
            "ImageSaved": image_filename,
            "AI_Reply": ai_reply
        })

    def export_excel(self, filename=None):
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.save_path, filename)
        df = pd.DataFrame(self.records)
        df.to_excel(filepath, index=False)
        return filepath
