from flask import Flask, request, abort
import json
import requests
import os

app = Flask(__name__)

# 你的 LINE 憑證
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

@app.route("/api/webhook", methods=['POST'])
def webhook():
    # 接收 LINE 的訊息
    body = request.get_data(as_text=True)
    events = json.loads(body).get('events', [])
    
    for event in events:
        if event['type'] == 'message':
            # 取得用戶訊息
            user_message = event['message']['text']
            reply_token = event['replyToken']
            
            # 處理訊息（呼叫 L1 + L2）
            response = process_message(user_message)
            
            # 回覆用戶
            reply_to_line(reply_token, response)
    
    return 'OK'

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