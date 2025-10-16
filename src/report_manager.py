import pandas as pd
import os
from datetime import datetime

class ReportManager:
    def __init__(self, save_path="/tmp/reports"):
        self.save_path = save_path
        os.makedirs(self.save_path, exist_ok=True)
        self.records = []

    def add_record(self, user_id, user_message, ai_reply, pdf_filename=None, image_bytes=None):
        image_filename = None
        if image_bytes:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{user_id}_{timestamp}.jpg"
            path = os.path.join(self.save_path, image_filename)
            with open(path, "wb") as f:
                f.write(image_bytes)

        record = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "UserID": user_id,
            "UserMessage": user_message,
            "PDF_File": pdf_filename if pdf_filename else "",
            "Image_File": image_filename if image_bytes else "",
            "AI_Reply": ai_reply
        }
        self.records.append(record)

    def export_excel(self):
        filename = f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path = os.path.join(self.save_path, filename)
        df = pd.DataFrame(self.records)
        df.to_excel(path, index=False)
        return path
