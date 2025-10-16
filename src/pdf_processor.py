import PyPDF2

class PDFProcessor:
    def __init__(self):
        self.documents = {}

    def load_pdf(self, user_id, file_path, chunk_size=1000):
        """解析 PDF 並拆成 chunk"""
        text_chunks = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # 拆成 chunk
                    for i in range(0, len(text), chunk_size):
                        text_chunks.append(text[i:i+chunk_size])
        self.documents[user_id] = text_chunks
        return len(text_chunks)

    def retrieve_chunks(self, user_id, query, max_chunks=3):
        """簡單檢索包含 query 關鍵詞的 chunk"""
        chunks = self.documents.get(user_id, [])
        results = [c for c in chunks if query in c]
        return results[:max_chunks] if results else chunks[:max_chunks]
