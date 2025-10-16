import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, query, knowledge_chunks):
        knowledge_text = "\n".join(knowledge_chunks) if knowledge_chunks else ""
        prompt = f"""
你是一位學生臨時抱佛腳助手，請幫助學生回答問題。

⚠️ 嚴格規範：
1. 僅根據提供知識回答，不能編造答案。
2. 若知識不足，請回答「這部分我不太確定，建議查閱課本或詢問老師」。
3. 回答簡短、自然、繁體中文。

=== 相關知識 ===
{knowledge_text}

=== 學生問題 ===
{query}
"""
        response = self.model.generate_content(prompt, generation_config={"temperature":0.4, "top_p":0.9})
        return response.text.strip()

    def generate_response_with_image(self, image_bytes, extra_text=""):
        prompt = f"""
學生上傳了一張學習相關圖片，請協助分析並回答可能問題。
額外說明：{extra_text}
"""
        response = self.model.generate_content([prompt, image_bytes], generation_config={"temperature":0.4, "top_p":0.9})
        return response.text.strip()
