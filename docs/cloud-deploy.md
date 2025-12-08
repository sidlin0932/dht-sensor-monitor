# ☁️ 雲端部署指南

## 概述

本指南說明如何將 DHT 監測系統部署到 Render 雲端，實現雙重備援架構。

## 架構

```
[Arduino] → [筆電本機] ─────┬──────▶ [本地 SQLite + Dashboard]
                           │
                           └──HTTP──▶ [Render 雲端]
                                           │
                                      [PostgreSQL]
                                           │
                                      [雲端 Dashboard]
                                           │
                                      [Discord 通知]
```

## 部署步驟

### 1. 準備 Git Repository

確保專案已上傳到 GitHub：

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/dht-monitor.git
git push -u origin main
```

### 2. 在 Render 建立服務

1. 前往 [Render Dashboard](https://dashboard.render.com/)
2. 點擊 **New +** → **Web Service**
3. 連接您的 GitHub Repository
4. 設定如下：
   - **Name**: `dht-monitor`
   - **Region**: `Singapore`（離台灣最近）
   - **Branch**: `main`
   - **Build Command**: `pip install -r cloud/requirements.txt`
   - **Start Command**: `cd cloud && gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. 建立 PostgreSQL 資料庫

1. 在 Render Dashboard，點擊 **New +** → **PostgreSQL**
2. 設定：
   - **Name**: `dht-monitor-db`
   - **Region**: `Singapore`
   - **Plan**: Free
3. 建立後複製 **Internal Database URL**

### 4. 設定環境變數

在 Web Service 的 **Environment** 頁面，新增以下變數：

| 變數名稱 | 值 |
|---------|---|
| `DATABASE_URL` | 貼上剛才複製的 Database URL |
| `API_KEY` | 自訂一個安全的密碼（至少 32 字元） |
| `DISCORD_WEBHOOK_URL` | 您的 Discord Webhook URL |
| `TEMP_WARNING_HIGH` | 35 |
| `TEMP_WARNING_LOW` | 10 |
| `HUMIDITY_WARNING_HIGH` | 80 |
| `HUMIDITY_WARNING_LOW` | 20 |

### 5. 設定本機同步

在本機的 `python/.env` 檔案中：

```
CLOUD_SYNC_ENABLED=true
CLOUD_API_URL=https://your-app-name.onrender.com
CLOUD_API_KEY=your-api-key-here
```

### 6. 測試

1. 啟動本機程式：`python main.py` 或 `python simulator.py`
2. 開啟雲端儀表板：`https://your-app-name.onrender.com`
3. 確認數據正在同步

## 注意事項

### Render Free Tier 限制

- 服務閒置 15 分鐘後會休眠
- 首次請求會有 ~30 秒延遲（冷啟動）
- 每月有執行時數限制

### 建議

- 本機儀表板作為主要監控
- 雲端儀表板用於遠端存取
- 兩邊數據獨立儲存，互為備份

## 檔案結構

```
cloud/
├── app.py              # 雲端 API 伺服器
└── requirements.txt    # 雲端依賴

render.yaml             # Render 部署設定（選用）
```

## API 端點

| 端點 | 方法 | 說明 |
|-----|------|------|
| `/api/push` | POST | 接收本機推送的數據 |
| `/api/current` | GET | 取得目前數據 |
| `/api/history` | GET | 取得歷史數據 |
| `/api/stats` | GET | 取得統計數據 |
| `/api/status` | GET | 取得系統狀態 |
| `/api/health` | GET | 健康檢查 |

### 推送數據範例

```bash
curl -X POST https://your-app.onrender.com/api/push \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"temperature": 25.5, "humidity": 60.2}'
```
