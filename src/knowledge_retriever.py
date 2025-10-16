class KnowledgeRetriever:
    def __init__(self):
        # 定義你的產品知識
        self.knowledge_base = {
            "產品介紹": {
                "keywords": ["什麼", "功能", "介紹"],
                "content": "我們的產品可以..."
            },
            "價格方案": {
                "keywords": ["價格", "費用", "多少錢"],
                "content": "基本版免費，進階版每月..."
            },
            # 加入更多知識...
        }
    
    def retrieve(self, query):
        """根據用戶問題找出相關知識"""
        results = []
        for category, info in self.knowledge_base.items():
            # 檢查關鍵字是否匹配
            if any(kw in query for kw in info["keywords"]):
                results.append(info["content"])
        return results