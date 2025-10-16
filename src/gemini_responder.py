import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_response(self, query, knowledge):
        # 建立 AI 的指令
        prompt = f"""
        你是客服助理，請根據以下資訊回答用戶問題。
        
        相關知識：
        {knowledge}
        
        用戶問題：{query}
        
        請用友善、簡潔的方式回答。
        """
        
        response = self.model.generate_content(prompt)
        return response.text