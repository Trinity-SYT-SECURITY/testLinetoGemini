class KnowledgeRetriever:
    def __init__(self):
        self.knowledge_base = {}  # user_id -> list of pdf chunks

    def add_pdf_chunks(self, user_id, chunks):
        if user_id not in self.knowledge_base:
            self.knowledge_base[user_id] = []
        self.knowledge_base[user_id].extend(chunks)

    def retrieve(self, user_id, query):
        # 簡單關鍵字匹配 + 模糊檢索
        results = []
        chunks = self.knowledge_base.get(user_id, [])
        for chunk in chunks:
            if any(word in chunk for word in query.split()):
                results.append(chunk)
        # 如果沒匹配到 PDF，回空
        return results if results else ["無匹配 PDF 內容"]
