import re

class KnowledgeRetriever:
    def __init__(self):
        self.knowledge_base = {
            "產品介紹": {
                "keywords": ["什麼", "功能", "介紹", "說明", "用途"],
                "content": "我們的產品支援 AI 報修、智慧分析與自動派工功能。"
            },
            "價格方案": {
                "keywords": ["價格", "費用", "多少錢", "收費", "價錢"],
                "content": "基本版免費使用，專業版每月 NT$499，企業方案可聯繫銷售人員。"
            },
        }

    def retrieve(self, query):
        results = []
        query = query.lower()

        for category, info in self.knowledge_base.items():
            for kw in info["keywords"]:
                if re.search(kw, query, re.IGNORECASE):
                    results.append(info["content"])
                    break

        if not results:
            results.append("抱歉，暫時沒有相關資訊。")
        return results