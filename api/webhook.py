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
    body = request.get_data(as_text=True)
    print("接收到的內容：", body)  # 這行會在 Vercel log 中出現
    events = json.loads(body).get('events', [])

    if len(events) == 0:
        return 'OK'

    for event in events:
        if event['type'] == 'message':
            user_message = event['message']['text']
            reply_token = event['replyToken']

            response = process_message(user_message)
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
