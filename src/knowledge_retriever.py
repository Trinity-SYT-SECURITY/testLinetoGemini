class KnowledgeRetriever:
    def __init__(self):
        self.knowledge_base = {
            "產品介紹": {
                "keywords": ["什麼", "功能", "介紹"],
                "content": "我們的產品可以..."
            },
            "價格方案": {
                "keywords": ["價格", "費用", "多少錢"],
                "content": "基本版免費，進階版每月..."
            },
        }

    def retrieve(self, query):
        results = []
        for category, info in self.knowledge_base.items():
            if any(kw in query for kw in info["keywords"]):
                results.append(info["content"])
        if not results:
            results.append("抱歉，暫時沒有相關資訊。")
        return results
