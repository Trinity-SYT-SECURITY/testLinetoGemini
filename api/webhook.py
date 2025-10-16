from flask import Flask, request
import json
import requests
import os

from src.knowledge_retriever import KnowledgeRetriever
from src.gemini_responder import GeminiResponder

app = Flask(__name__)

# LINE 憑證
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 初始化知識檢索器與 AI 回應者
retriever = KnowledgeRetriever()
responder = GeminiResponder(api_key=os.getenv('GEMINI_API_KEY'))

def process_image_message(image_bytes):
    return responder.generate_response_with_image(image_bytes)
    
def process_image_with_text(image_bytes, user_message):
    knowledge = retriever.retrieve(user_message)
    prompt = f"""
使用者上傳了一張報修圖片，並描述問題如下：
「{user_message}」

請結合圖片與描述內容，分析可能問題與建議。
"""

    response = responder.model.generate_content([prompt, image_bytes])
    return response.text


@app.route("/api/webhook", methods=['POST'])
def webhook():
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
                response = process_image_message(image_bytes)
                reply_to_line(reply_token, response)

    return 'OK'

def get_line_image(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    res = requests.get(url, headers=headers)
    return res.content  # 回傳圖片的 binary

def reply_to_line(reply_token, text):
    """透過 LINE API 回覆訊息"""
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }

    requests.post(url, headers=headers, json=data)

def process_message(user_message):
    """整合 L1（知識）+ L2（AI）處理訊息"""
    knowledge = retriever.retrieve(user_message)
    combined_knowledge = "\n".join(knowledge)
    ai_reply = responder.generate_response(user_message, combined_knowledge)
    return ai_reply




