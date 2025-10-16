import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, query, knowledge):
        prompt = f"""
你是一位智慧報修客服助理，請根據下列「知識內容」與「使用者問題」回答。

⚠️ 嚴格規範：
1. 回答時只能根據知識內容與常識作答。
2. 若知識內容不足，請誠實回覆「這部分我不太確定，但可以幫您轉交人工客服了解。」。
3. 不要自行編造資訊、價格或政策。
4. 回答要自然、簡潔、友善。

=== 知識內容 ===
{knowledge}

=== 使用者問題 ===
{query}

請以繁體中文回覆。
"""
        response = self.model.generate_content(
            prompt,
            generation_config={"temperature": 0.4, "top_p": 0.9}
        )
        return response.text.strip()
