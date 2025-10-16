
# 智慧報修 LINE AI 客服系統

## 專案簡介

本系統是一個結合 LINE Official Account、Google Gemini AI 多模態模型與 Vercel 雲端平台的智慧客服機器人。支援文字與圖片訊息的智能分析與回覆，適合用於報修服務、客戶諮詢等場景，提升客服效率並降低人力成本。

## 核心功能

- 支援 LINE 傳送文字與圖片訊息
- 利用 L1 知識檢索快速找到相關資訊
- 利用 Gemini 2.5 Flash 多模態模型結合圖片與文字分析
- 上下文對話管理，提供更連貫的對話體驗
- 對話與圖片資料儲存，方便後續查詢與分析
- 自動發送客服通知，快速回應用戶需求
- 快速選單設計，提升用戶互動體驗
- 低成本部署，24/7 全天候服務

## 系統架構

```mermaid
flowchart TD
  User["用戶 - Line"] -->|文字/圖片訊息| LINEWebhook["Webhook 接收端"]
  LINEWebhook -->|文字| L1Retriever["L1: 知識檢索"]
  LINEWebhook -->|圖片| ImageStorage["圖片暫存服務"]
  ImageStorage --> GeminiAI["Gemini AI 多模態模型"]
  L1Retriever --> GeminiAI
  GeminiAI --> ContextMgr["上下文管理"]
  ContextMgr --> ResponseGen["生成回應"]
  ResponseGen --> LINEWebhook
  LINEWebhook -->|回覆訊息| User
  ResponseGen --> DB[(資料庫)]
  LINEWebhook -->|推播通知| Admin["客服人員"]

````

## 專案架構

```
my-line-bot/
├── src/
│   ├── knowledge_retriever.py   # L1 知識檢索
│   ├── gemini_responder.py      # L2 多模態 Gemini AI 回應
│   ├── context_manager.py       # 對話上下文管理
│   └── database.py              # 資料庫操作
├── api/
│   └── webhook.py               # LINE Webhook 入口
├── static/
│   └── images/                  # 暫存用戶上傳圖片
├── requirements.txt
├── vercel.json
└── README.md
```

## 快速開始

1. 申請並設定以下帳號與金鑰：

   * LINE Developers：取得 Channel Secret、Access Token
   * Google AI Studio：取得 Gemini API Key
   * Vercel：部署平台

2. 設定環境變數

   ```
   LINE_CHANNEL_SECRET=your_channel_secret
   LINE_CHANNEL_ACCESS_TOKEN=your_access_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. 安裝套件

   ```bash
   pip install -r requirements.txt
   ```

4. 本地測試

   ```bash
   flask run
   ```

5. 部署到 Vercel

   ```bash
   vercel --prod
   ```

## 未來優化方向

* 增加多語言支援
* 整合客服後台系統
* 加強模型微調提升準確度
* 結合語音訊息辨識
* 加入自動報表功能

