import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # 改用多模態新版

    def generate_response(self, query, knowledge):
        prompt = f"""
你是智慧報修助理，根據以下知識與使用者問題給出簡潔建議。

知識：
{knowledge}

問題：
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
