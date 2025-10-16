from flask import Flask, request
import json
import requests
import os
from src.report_manager import ReportManager
from src.knowledge_retriever import KnowledgeRetriever
from src.gemini_responder import GeminiResponder

app = Flask(__name__)

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=os.getenv('GEMINI_API_KEY'))




report_manager = ReportManager()

# 修改 process_text_message 與 process_image_message，新增收集功能
def process_text_message(user_message, user_id):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge)
    ai_reply = responder.generate_response(user_message, combined_knowledge)

    # 新增報修記錄
    report_manager.add_record(user_id, user_message, ai_reply)
    return ai_reply


def process_image_message(image_bytes, user_message, user_id):
    ai_reply = responder.generate_response_with_image(image_bytes)
    # 儲存圖片
    image_filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image_path = os.path.join("reports", image_filename)
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    # 新增報修記錄
    report_manager.add_record(user_id, user_message, ai_reply, image_filename)
    return ai_reply


def process_text_message(user_message):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge)
    ai_reply = responder.generate_response(user_message, combined_knowledge)

    if "不太確定" in ai_reply or "無明確" in combined_knowledge:
        ai_reply += "\n\n（如果方便，您可以更具體描述一下問題，我會再幫您確認。）"

    return ai_reply


def process_image_message(image_bytes):
    return responder.generate_response_with_image(image_bytes)


def process_image_with_text(image_bytes, user_message):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge) if knowledge else ""
    prompt = f"""
使用者上傳了一張報修圖片，並描述問題如下：
「{user_message}」

請結合圖片與描述內容，分析可能問題與建議。
"""
    response = responder.model.generate_content([prompt, image_bytes])
    return response.text


@app.route("/api/webhook", methods=['POST'])
def webhook():
    try:
        body = request.get_data(as_text=True)
        events = json.loads(body).get('events', [])

        if len(events) == 0:
            return 'OK'

        for event in events:
            if event['type'] == 'message':
                msg_type = event['message']['type']
                reply_token = event['replyToken']
                user_id = event['source']['userId']

                if msg_type == 'text':
                    user_message = event['message']['text']
                    response = process_text_message(user_message)
                    reply_to_line(reply_token, response)

                elif msg_type == 'image':
                    message_id = event['message']['id']
                    image_bytes = get_line_image(message_id)
                    # 這邊先用簡單圖片回應，也可以改用文字結合圖片：
                    response = process_image_message(image_bytes)
                    reply_to_line(reply_token, response)

                else:
                    reply_to_line(reply_token, "抱歉，目前只支援文字與圖片訊息。")

        return 'OK'
    except Exception as e:
        print("Webhook 錯誤:", e)
        return 'Error', 500


def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗，狀態碼：{res.status_code}")
        return None
    return res.content


def reply_to_line(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"回覆訊息失敗: {resp.status_code} {resp.text}")
