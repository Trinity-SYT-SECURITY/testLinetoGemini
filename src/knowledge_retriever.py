import re

class KnowledgeRetriever:
    def __init__(self):
        self.knowledge_base = {
            "產品": {
                "keywords": ["產品", "功能", "介紹", "說明", "用途"],
                "content": "本系統支援智慧報修、自動派工、AI 圖片判斷問題等功能。"
            },
            "價格": {
                "keywords": ["價格", "費用", "多少錢", "收費", "價錢"],
                "content": "基本版免費使用，專業版每月 NT$499。"
            },
            "維修": {
                "keywords": ["維修", "報修", "壞了", "修理", "問題"],
                "content": "請上傳故障圖片，我們會自動判斷問題並派工。"
            }
        }

    def retrieve(self, query):
        results = []
        matched = False
        for topic, info in self.knowledge_base.items():
            if any(kw in query for kw in info["keywords"]):
                results.append(info["content"])
                matched = True
        if not matched:
            results.append("無明確知識匹配。")
        return results