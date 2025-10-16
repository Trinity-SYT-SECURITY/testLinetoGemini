import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # 或 gemini-pro

    def generate_response(self, query, knowledge):
        prompt = f"""
        你是智慧報修助理，請根據以下知識與使用者提問內容，回覆適當的建議。
        
        知識內容：
        {knowledge}
        
        使用者問題：
        {query}
        """
        response = self.model.generate_content(prompt)
        return response.text

    def generate_response_with_image(self, image_bytes):
        prompt = "這是用戶上傳的報修圖片，請協助判斷問題及建議處理方式。"

        response = self.model.generate_content(
            [prompt, image_bytes],
            generation_config={"temperature": 0.4}
        )
        return response.text
