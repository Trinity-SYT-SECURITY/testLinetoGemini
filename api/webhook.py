from flask import Flask, request
import json
import requests
import os
from datetime import datetime
from src.knowledge_retriever import KnowledgeRetriever
from src.gemini_responder import GeminiResponder
from src.report_manager import ReportManager

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=os.getenv('GEMINI_API_KEY'))
report_manager = ReportManager()

# 確保 /tmp/reports 目錄存在
os.makedirs("/tmp/reports", exist_ok=True)

# 取得 LINE 圖片
def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗，狀態碼：{res.status_code}")
        return None
    return res.content

# 回覆 LINE
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

# 處理文字訊息
def process_text_message(user_message, user_id):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge)
    ai_reply = responder.generate_response(user_message, combined_knowledge)

    if "不太確定" in ai_reply or "無明確" in combined_knowledge:
        ai_reply += "\n\n（請更具體描述，我會再幫您分析。）"

    report_manager.add_record(user_id, user_message, ai_reply)
    return ai_reply

# 處理圖片+文字
def process_image_with_text(image_bytes, user_message, user_id):
    ai_reply = responder.generate_response_with_image(image_bytes, user_message)
    report_manager.add_record(user_id, user_message, ai_reply, image_bytes=image_bytes)
    return ai_reply

# Webhook
@app.route("/api/webhook", methods=['POST'])
def webhook():
    try:
        body = request.get_data(as_text=True)
        events = json.loads(body).get('events', [])

        for event in events:
            if event['type'] != 'message':
                continue

            msg_type = event['message']['type']
            reply_token = event['replyToken']
            user_id = event['source']['userId']

            if msg_type == 'text':
                user_message = event['message']['text']
                response = process_text_message(user_message, user_id)
                reply_to_line(reply_token, response)

            elif msg_type == 'image':
                message_id = event['message']['id']
                image_bytes = get_line_image(message_id)
                if image_bytes:
                    # ✅ 修正：呼叫 process_image_with_text 讓 Gemini 分析圖片內容
                    user_message = "用戶上傳圖片需要分析問題"
                    response = process_image_with_text(image_bytes, user_message, user_id)
                    reply_to_line(reply_token, response)
                else:
                    reply_to_line(reply_token, "圖片下載失敗")

            else:
                reply_to_line(reply_token, "抱歉，目前只支援文字與圖片訊息。")

        return 'OK'
    except Exception as e:
        print("Webhook 錯誤:", e)
        return 'Error', 500

# 可加首頁檢查
@app.route("/", methods=['GET'])
def index():
    return "LINE Bot Webhook Running!"
