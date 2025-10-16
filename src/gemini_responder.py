import google.generativeai as genai

class GeminiResponder:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, query, knowledge_chunks):
        prompt_text = "你是一位智慧學習助理。\n"
        prompt_text += "使用者問題：\n" + query + "\n"
        prompt_text += "相關知識：\n" + "\n".join(knowledge_chunks) + "\n\n"
        prompt_text += ("請以人類能理解的語言回答問題，如果知識不足或問題無意義，回答："
                        "「抱歉，我不太理解這個問題，能換個方式問嗎？」")

        response = self.model.generate_content(
            prompt_text,
            generation_config={"temperature": 0.4, "top_p": 0.9}
        )
        return response.text.strip()

    def generate_response_with_image(self, image_bytes, user_message=""):
        prompt_text = "使用者上傳了一張圖片，請分析可能問題並給出建議。"
        if user_message:
            prompt_text += f"\n文字描述：{user_message}"

        response = self.model.generate_content(
            [prompt_text, image_bytes],
            generation_config={"temperature":0.4, "top_p":0.9}
        )
        return response.text.strip()
