import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, query, knowledge):
        prompt = f"""
你是一位智慧學習助手，幫助學生考前複習。  

⚠️ 嚴格規範：
1. 僅根據知識內容回答，不要編造答案。
2. 若知識不足，要告訴學生「這部分我不太確定，可以參考課本或請教老師」。
3. 回答要自然、簡潔、友善。

=== 知識內容 ===
{knowledge}

=== 使用者問題 ===
{query}

請以繁體中文回覆。
"""
        response = self.model.generate_content(
            prompt,
            generation_config={"temperature": 0.3, "top_p": 0.9}
        )
        return response.text.strip()

    def generate_response_with_image(self, image_bytes, user_message="用戶上傳圖片需要分析"):
        prompt = f"""
使用者上傳了一張圖片（可能是筆記或題目），並描述問題如下：
「{user_message}」

請分析圖片內容並回答問題，僅提供可能答案或建議。
"""
        response = self.model.generate_content([prompt, image_bytes])
        return response.text.strip()
