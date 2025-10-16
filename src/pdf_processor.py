import fitz  # PyMuPDF
import os

class PDFProcessor:
    """
    輕量版 PDF 文字擷取器。
    將 PDF 拆成小段落 (chunks)，避免超過 Gemini context。
    """
    def __init__(self, save_dir="/tmp/pdf_uploads"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.chunk_size = 1500  # 每段字元上限，避免超過 context window

    def extract_text_chunks(self, pdf_path):
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        # 切割成 chunks
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i+self.chunk_size])

        return chunks

    def save_pdf(self, file_bytes, filename):
        pdf_path = os.path.join(self.save_dir, filename)
        with open(pdf_path, "wb") as f:
            f.write(file_bytes)
        return pdf_path

    def retrieve_relevant_chunks(self, user_id):
        """
        之後可根據 user_id 找對應 PDF。
        現在簡化處理為直接回傳最新上傳的 PDF chunks。
        """
        pdf_files = [f for f in os.listdir(self.save_dir) if f.endswith(".pdf")]
        if not pdf_files:
            return []
        latest_pdf = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(self.save_dir, f)))
        pdf_path = os.path.join(self.save_dir, latest_pdf)
        return self.extract_text_chunks(pdf_path)
