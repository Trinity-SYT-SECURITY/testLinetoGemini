from flask import Flask, request
import json
import requests
import os
from datetime import datetime
from src.pdf_processor import PDFProcessor
from src.knowledge_retriever import KnowledgeRetriever
from src.gemini_responder import GeminiResponder
from src.report_manager import ReportManager

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

pdf_processor = PDFProcessor()
retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=GEMINI_API_KEY)
report_manager = ReportManager()

# 確保目錄存在
os.makedirs("/tmp/reports", exist_ok=True)
os.makedirs("/tmp/pdf_uploads", exist_ok=True)

# LINE 圖片下載
def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗: {res.status_code}")
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

# 處理文字問題
def process_text_message(user_id, user_message):
    knowledge_chunks = retriever.retrieve(user_id, user_message)
    combined_knowledge = "\n".join(knowledge_chunks)
    ai_reply = responder.generate_response(user_message, combined_knowledge)
    report_manager.add_record(user_id, user_message, ai_reply)
    return ai_reply

# 處理 PDF 上傳
def process_pdf_upload(user_id, pdf_bytes):
    path = pdf_processor.save_pdf(user_id, pdf_bytes)
    chunks = pdf_processor.extract_text_chunks(user_id, path)
    retriever.add_pdf_chunks(user_id, chunks)
    return f"已上傳 PDF，總共 {len(chunks)} 個內容片段已加入知識庫。"

# 處理圖片
def process_image(user_id, image_bytes, user_message="用戶上傳圖片"):
    ai_reply = responder.generate_response_with_image(image_bytes, user_message)
    report_manager.add_record(user_id, user_message, ai_reply, image_bytes=image_bytes)
    return ai_reply

@app.route("/api/webhook", methods=['POST'])
def webhook():
    try:
        events = json.loads(request.get_data(as_text=True)).get("events", [])
        for event in events:
            if event['type'] != 'message':
                continue

            msg_type = event['message']['type']
            reply_token = event['replyToken']
            user_id = event['source']['userId']

            if msg_type == 'text':
                user_message = event['message']['text']
                # PDF 指令例: 上傳 PDF
                if user_message.startswith("/pdf "):
                    reply = "請用 LINE 上傳 PDF 文件"
                else:
                    reply = process_text_message(user_id, user_message)
                reply_to_line(reply_token, reply)

            elif msg_type == 'image':
                message_id = event['message']['id']
                image_bytes = get_line_image(message_id)
                if image_bytes:
                    reply = process_image(user_id, image_bytes)
                    reply_to_line(reply_token, reply)
                else:
                    reply_to_line(reply_token, "圖片下載失敗")

            elif msg_type == 'file':
                # PDF 上傳處理
                file_info = event['message']
                if file_info['fileName'].lower().endswith('.pdf'):
                    url = f"https://api-data.line.me/v2/bot/message/{file_info['id']}/content"
                    headers = {'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
                    res = requests.get(url, headers=headers)
                    if res.status_code == 200:
                        pdf_bytes = res.content
                        reply = process_pdf_upload(user_id, pdf_bytes)
                        reply_to_line(reply_token, reply)
                    else:
                        reply_to_line(reply_token, "PDF 下載失敗")
                else:
                    reply_to_line(reply_token, "只支援 PDF 文件")

        return "OK"
    except Exception as e:
        print("Webhook 錯誤:", e)
        return "Error", 500

@app.route("/", methods=['GET'])
def index():
    return "學生臨時抱佛腳助手運行中！"
