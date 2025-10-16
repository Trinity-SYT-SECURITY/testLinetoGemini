from flask import Flask, request
import json, os
from datetime import datetime
import requests
from src.gemini_responder import GeminiResponder
from src.knowledge_retriever import KnowledgeRetriever
from src.report_manager import ReportManager
from src.pdf_processor import PDFProcessor

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 初始化模組
retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=os.getenv('GEMINI_API_KEY'))
pdf_processor = PDFProcessor()
report_manager = ReportManager()

# Serverless 可寫目錄
TMP_DIR = "/tmp/reports"
os.makedirs(TMP_DIR, exist_ok=True)

# ---------------- LINE 功能 ----------------
def reply_to_line(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {'replyToken': reply_token, 'messages': [{'type': 'text', 'text': text}]}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"LINE 回覆失敗: {resp.status_code} {resp.text}")

def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗，狀態碼：{res.status_code}")
        return None
    return res.content

# ---------------- 處理訊息 ----------------
def process_text_message(user_message, user_id):
    # 先取得 PDF chunks
    pdf_chunks = pdf_processor.retrieve_relevant_chunks(user_id)

    # 動態檢索
    knowledge_chunks = retriever.retrieve(user_message, pdf_chunks)

    ai_reply = responder.generate_response(user_message, knowledge_chunks)

    # 過濾亂問
    if len(user_message.strip()) == 0 or len(user_message) > 300:
        ai_reply = "抱歉，我不太理解這個問題，能換個方式問嗎？"

    return ai_reply


def process_image_message(image_bytes, user_message, user_id):
    ai_reply = responder.generate_response_with_image(image_bytes, user_message)
    report_manager.add_record(user_id, user_message, ai_reply, image_bytes=image_bytes)
    return ai_reply

# ---------------- Webhook ----------------
@app.route("/api/webhook", methods=['POST'])
def webhook():
    try:
        body = request.get_data(as_text=True)
        events = json.loads(body).get('events', [])

        for event in events:
            if event['type'] != 'message':
                continue

            reply_token = event['replyToken']
            user_id = event['source']['userId']
            msg_type = event['message']['type']

            if msg_type == 'text':
                user_message = event['message']['text']
                response = process_text_message(user_message, user_id)
                reply_to_line(reply_token, response)

            elif msg_type == 'image':
                message_id = event['message']['id']
                image_bytes = get_line_image(message_id)
                if image_bytes:
                    response = process_image_message(image_bytes, "", user_id)
                    reply_to_line(reply_token, response)
                else:
                    reply_to_line(reply_token, "圖片下載失敗")

            elif msg_type == 'file':
                file_name = event['message'].get('fileName', 'document.pdf')
                file_bytes = get_line_image(event['message']['id'])
                if file_bytes and file_name.lower().endswith(".pdf"):
                    pdf_processor.save_pdf(user_id, file_name, file_bytes)
                    reply_to_line(reply_token, f"PDF 已上傳並解析完成：{file_name}")
                else:
                    reply_to_line(reply_token, "請上傳 PDF 文件。")

            else:
                reply_to_line(reply_token, "抱歉，目前只支援文字、圖片與 PDF。")

        return 'OK'
    except Exception as e:
        print("Webhook 錯誤:", e)
        return 'Error', 500
