from flask import Flask, request
import os, json
from datetime import datetime
from src.pdf_processor import PDFProcessor
from src.gemini_responder import GeminiResponder
from src.report_manager import ReportManager

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

pdf_processor = PDFProcessor()
responder = GeminiResponder(api_key=GEMINI_API_KEY)
report_manager = ReportManager()

TMP_DIR = "/tmp/uploads"
os.makedirs(TMP_DIR, exist_ok=True)

def reply_to_line(reply_token, text):
    import requests
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {"Content-Type":"application/json", "Authorization":f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    data = {"replyToken": reply_token, "messages":[{"type":"text","text":text}]}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"回覆訊息失敗 {resp.status_code}: {resp.text}")

def get_line_image(message_id):
    import requests
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization":f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"下載圖片失敗 {res.status_code}")
        return None
    return res.content

@app.route("/api/webhook", methods=['POST'])
def webhook():
    try:
        body = request.get_data(as_text=True)
        events = json.loads(body).get("events", [])

        if len(events)==0:
            return "OK"

        for event in events:
            if event["type"] != "message":
                continue
            reply_token = event["replyToken"]
            user_id = event["source"]["userId"]
            msg_type = event["message"]["type"]

            if msg_type == "text":
                user_message = event["message"]["text"]
                chunks = pdf_processor.retrieve_chunks(user_id, user_message)
                ai_reply = responder.generate_response(user_message, chunks)
                report_manager.add_record(user_id, user_message, ai_reply)
                reply_to_line(reply_token, ai_reply)

            elif msg_type == "image":
                message_id = event["message"]["id"]
                image_bytes = get_line_image(message_id)
                if image_bytes:
                    ai_reply = responder.generate_response_with_image(image_bytes)
                    report_manager.add_record(user_id, "[圖片]", ai_reply)
                    reply_to_line(reply_token, ai_reply)
                else:
                    reply_to_line(reply_token, "圖片下載失敗")

            else:
                reply_to_line(reply_token, "抱歉，只支援文字與圖片訊息。")
        return "OK"

    except Exception as e:
        print("Webhook 錯誤:", e)
        return "Error", 500

@app.route("/", methods=['GET'])
def index():
    return "學生臨時抱佛腳助手運行中！"

@app.route("/api/upload_pdf", methods=["POST"])
def upload_pdf():
    try:
        file = request.files.get("file")
        user_id = request.form.get("user_id", "anonymous")
        if not file or not file.filename.endswith(".pdf"):
            return "請上傳 PDF 文件", 400
        file_path = os.path.join(TMP_DIR, f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        file.save(file_path)
        num_chunks = pdf_processor.load_pdf(user_id, file_path)
        return f"PDF 上傳成功，拆成 {num_chunks} 個段落"
    except Exception as e:
        print("PDF 上傳錯誤:", e)
        return "Error", 500
