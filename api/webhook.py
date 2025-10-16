from flask import Flask, request
import json
import requests
import os
from datetime import datetime
import pandas as pd

from src.knowledge_retriever import KnowledgeRetriever
from src.gemini_responder import GeminiResponder

app = Flask(__name__)

# LINE 設定
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 初始化模組
retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=os.getenv('GEMINI_API_KEY'))

# Serverless 可寫目錄
TMP_DIR = "/tmp/reports"
os.makedirs(TMP_DIR, exist_ok=True)

# 報修資料管理
report_records = []

def add_report_record(user_id, user_message, ai_reply, image_filename=None):
    record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "UserID": user_id,
        "UserMessage": user_message,
        "ImageSaved": image_filename if image_filename else "",
        "AI_Reply": ai_reply
    }
    report_records.append(record)
    # 同步更新 Excel
    excel_path = os.path.join(TMP_DIR, "report.xlsx")
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    df.to_excel(excel_path, index=False)
    return excel_path

# LINE 回覆
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

# 取得 LINE 圖片
def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗，狀態碼：{res.status_code}")
        return None
    return res.content

# 處理文字訊息
def process_text_message(user_message, user_id):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge)
    ai_reply = responder.generate_response(user_message, combined_knowledge)

    if "不太確定" in ai_reply or "無明確" in combined_knowledge:
        ai_reply += "\n\n（如果方便，您可以更具體描述一下問題，我會再幫您確認。）"

    add_report_record(user_id, user_message, ai_reply)
    return ai_reply

# 處理圖片訊息
def process_image_message(image_bytes, user_message, user_id):
    ai_reply = responder.generate_response_with_image(image_bytes)

    # 儲存圖片
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_filename = f"{user_id}_{timestamp}.jpg"
    image_path = os.path.join(TMP_DIR, image_filename)
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    add_report_record(user_id, user_message, ai_reply, image_filename)
    return ai_reply

# 處理圖片+文字分析
def process_image_with_text(image_bytes, user_message, user_id):
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge) if knowledge else ""
    prompt = f"""
使用者上傳了一張報修圖片，並描述問題如下：
「{user_message}」

請結合圖片與描述內容，分析可能問題與建議。
"""
    response = responder.model.generate_content([prompt, image_bytes])
    ai_reply = response.text
    add_report_record(user_id, user_message, ai_reply)
    return ai_reply

# Webhook 主程式
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
                    response = process_text_message(user_message, user_id)
                    reply_to_line(reply_token, response)

                elif msg_type == 'image':
                    message_id = event['message']['id']
                    image_bytes = get_line_image(message_id)
                    if image_bytes:
                        # 可改成 process_image_with_text 進行文字+圖片分析
                        response = process_image_message(image_bytes, "", user_id)
                        reply_to_line(reply_token, response)
                    else:
                        reply_to_line(reply_token, "圖片下載失敗")

                else:
                    reply_to_line(reply_token, "抱歉，目前只支援文字與圖片訊息。")

        return 'OK'
    except Exception as e:
        print("Webhook 錯誤:", e)
        return 'Error', 500