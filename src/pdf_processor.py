import pdfplumber
import os

class PDFProcessor:
    def __init__(self, save_path="/tmp/pdf_uploads", chunk_size=1000):
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)
        self.chunk_size = chunk_size  # 每個 chunk 字數上限
        self.chunks = {}  # user_id -> list of chunks

    def save_pdf(self, user_id, pdf_bytes, filename=None):
        if not filename:
            filename = f"{user_id}_lecture.pdf"
        path = os.path.join(self.save_path, filename)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
        return path

    def extract_text_chunks(self, user_id, pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # 分 chunk
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end

        self.chunks[user_id] = chunks
        return chunks

    def get_user_chunks(self, user_id):
        return self.chunks.get(user_id, [])
