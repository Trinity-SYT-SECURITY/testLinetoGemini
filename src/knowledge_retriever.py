class KnowledgeRetriever:
    """
    動態知識檢索，主要從 PDF 或教材 chunk 取得資訊。
    如果找不到，fallback 到通用知識。
    """
    def __init__(self):
        # 可以放一些常識或 FAQ
        self.fallback_knowledge = [
            "這是一個學習助手，可以回答學科問題，提供學習建議。",
            "如果問題涉及計算、概念、定義等，我會儘量給出繁體中文解釋。"
        ]

    def retrieve(self, query, pdf_chunks=None):
        """
        query: 使用者問題
        pdf_chunks: list of str, 從 PDF 拆出來的 chunk
        """
        results = []

        # 先檢查 PDF 內容
        if pdf_chunks:
            for chunk in pdf_chunks:
                if any(word in chunk for word in query.split()):
                    results.append(chunk)

        # 如果沒有匹配任何 chunk，回傳 fallback 知識
        if not results:
            results = self.fallback_knowledge.copy()

        return results
