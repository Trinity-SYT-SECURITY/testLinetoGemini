import pdfplumber, os
from datetime import datetime

class PDFProcessor:
    def __init__(self):
        self.pdf_dir = "/tmp/pdfs"
        os.makedirs(self.pdf_dir, exist_ok=True)
        self.pdf_chunks = {}  # user_id -> list of chunks

    def save_pdf(self, user_id, file_name, file_bytes):
        path = os.path.join(self.pdf_dir, f"{user_id}_{file_name}")
        with open(path, "wb") as f:
            f.write(file_bytes)
        # 解析 PDF
        self.pdf_chunks[user_id] = self._extract_chunks(path)

    def _extract_chunks(self, path, chunk_size=500):
        chunks = []
        try:
            with pdfplumber.open(path) as pdf:
                text_all = ""
                for page in pdf.pages:
                    text_all += page.extract_text() + "\n"
            # 切 chunk
            text_all = text_all.replace("\n", " ")
            for i in range(0, len(text_all), chunk_size):
                chunks.append(text_all[i:i+chunk_size])
        except Exception as e:
            print("PDF 解析錯誤:", e)
        return chunks

    def retrieve_relevant_chunks(self, query, user_id=None):
        if user_id and user_id in self.pdf_chunks:
            return self.pdf_chunks[user_id]
        return []
