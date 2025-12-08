# ☁️ 雲端部署教學 (Cloud Deployment Guide)

本指南將教你如何將此專案部署到 Render 雲端平台，並使用 UptimeRobot 保持服務運行。

---

## 📋 目錄

1. [Render 部署設定](#render-部署設定)
2. [環境變數設定](#環境變數設定)
3. [Start Command 設定](#start-command-設定)
4. [UptimeRobot 監控設定](#uptimerobot-監控設定)
5. [常見問題](#常見問題)

---

## 🚀 Render 部署設定

### 步驟 1：建立 Render 帳號

1. 前往 [Render.com](https://render.com/)
2. 使用 GitHub 帳號註冊/登入（推薦）

### 步驟 2：建立新的 Web Service

1. 點擊右上角的 **"New +"** 按鈕
2. 選擇 **"Web Service"**
3. 連接你的 GitHub repository：`sidlin0932/dht-sensor-monitor`
4. 選擇 `main` 分支（穩定版本）

### 步驟 3：基本設定

填寫以下資訊：

| 欄位 | 設定值 |
|:---|:---|
| **Name** | `dht-sensor-monitor`（或你喜歡的名稱） |
| **Region** | Singapore（新加坡，離台灣最近） |
| **Branch** | `main` |
| **Root Directory** | `python` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | 見下方 👇 |

---

## 🎯 Start Command 設定

### 方案 A：僅 Web 伺服器（推薦用於雲端）⭐

如果你只想在雲端運行 Web Dashboard（接收本地推送的數據）：

```bash
python render_start.py --web-only
```

> 💡 **注意**：這個方案適合「本地收集數據 + 雲端顯示」的架構。你需要：
> - 本地電腦運行 `main.py`（連接 Arduino）
> - 本地的 `cloud_sync.py` 會自動推送數據到 Render 的資料庫 API

### 方案 B：完整系統（使用模擬數據）

如果你想在雲端運行完整系統（包含模擬感測器）：

```bash
python render_start.py
```

> 💡 這會啟動完整的監測系統，並自動產生模擬的溫濕度數據用於測試（因為雲端沒有 Arduino）。

### 方案 C：使用 Gunicorn（正式環境推薦）

對於正式部署，建議使用 Gunicorn 作為 WSGI 伺服器：

**先更新 `requirements.txt`，加入：**
```
gunicorn==21.2.0
```

**Start Command：**
```bash
gunicorn --bind 0.0.0.0:$PORT web_server:app
```

> ⚠️ 注意：Render 會自動設定環境變數 `$PORT`，不要寫死 port 號。

---

## 🔐 環境變數設定

在 Render 的 **Environment** 區塊，新增以下環境變數：

### 必要變數

| Key | Value | 說明 |
|:---|:---|:---|
| `PYTHON_VERSION` | `3.11.0` | Python 版本 |
| `WEB_HOST` | `0.0.0.0` | 允許外部連線 |
| `WEB_PORT` | `$PORT` | Render 自動分配（或填 `5000`） |

### Discord 相關（選填）

| Key | Value | 說明 |
|:---|:---|:---|
| `DISCORD_BOT_TOKEN` | `你的 Bot Token` | Discord Bot（若不需要可不填） |
| `DISCORD_WEBHOOK_URL` | `你的 Webhook URL` | Discord 通知 |

### 模擬模式（選填）

| Key | Value | 說明 |
|:---|:---|:---|
| `SIMULATE_MODE` | `true` | 啟用模擬感測器 |
| `SERIAL_PORT` | `SIMULATE` | 告訴系統使用模擬模式 |

> 💡 **提示**：在 Render 上，環境變數的設定會自動覆蓋 `.env` 檔案。

---

## 📊 部署流程總覽

完成上述設定後：

1. 點擊 **"Create Web Service"**
2. Render 會自動：
   - Clone 你的 GitHub repository
   - 執行 `pip install -r requirements.txt`
   - 執行你設定的 Start Command
3. 等待 3-5 分鐘，部署完成！

你會得到一個網址，例如：
```
https://dht-sensor-monitor.onrender.com
```

---

## 🤖 UptimeRobot 監控設定

> **為什麼需要 UptimeRobot？**  
> Render 的免費方案會在 15 分鐘無活動後自動休眠。UptimeRobot 會定期發送請求，保持服務運行。

### 步驟 1：建立 UptimeRobot 帳號

1. 前往 [UptimeRobot.com](https://uptimerobot.com/)
2. 免費註冊一個帳號

### 步驟 2：新增監控

1. 登入後，點擊 **"+ Add New Monitor"**
2. 填寫以下資訊：

| 欄位 | 設定值 |
|:---|:---|
| **Monitor Type** | `HTTP(s)` |
| **Friendly Name** | `DHT Monitor` |
| **URL** | `https://你的render網址.onrender.com/api/status` |
| **Monitoring Interval** | `5 minutes`（免費方案最小值） |

3. 點擊 **"Create Monitor"**

### 步驟 3：設定通知（選填）

如果你想在服務掛掉時收到通知：

1. 進入 **"Alert Contacts"**
2. 新增你的 Email 或整合其他服務（Slack、Discord 等）
3. 回到 Monitor 設定，選擇要通知的聯絡人

---

## ✅ 驗證部署

部署完成後，測試以下 API 端點：

```bash
# 系統狀態
https://你的網址.onrender.com/api/status

# 目前數據
https://你的網址.onrender.com/api/current

# 歷史數據
https://你的網址.onrender.com/api/history?hours=24
```

打開瀏覽器訪問主網址，應該能看到儀表板！

---

## 🏗️ 混合架構建議

### 架構說明

```
┌─────────────────┐         ┌─────────────────┐
│  本地電腦 (PC)   │         │  Render 雲端     │
│                 │         │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │
│  │ Arduino   │──┼────USB──┼─X│  無法連接  │  │
│  │ DHT22     │  │         │  └───────────┘  │
│  └───────────┘  │         │                 │
│        │        │         │                 │
│  ┌─────▼──────┐ │  HTTPS  │  ┌───────────┐  │
│  │ main.py    │─┼────────►│  │ Web API   │  │
│  │ (收集數據)  │ │  Push   │  │ (接收數據) │  │
│  └────────────┘ │  Data   │  └─────┬─────┘  │
│                 │         │        │        │
│  ┌────────────┐ │         │  ┌─────▼──────┐ │
│  │ 本地資料庫  │ │         │  │ 雲端資料庫  │ │
│  │ (備份)     │ │         │  │ (主要)     │ │
│  └────────────┘ │         │  └───────────┘  │
│                 │         │        │        │
│                 │         │  ┌─────▼──────┐ │
│                 │         │  │ Dashboard  │─┼──► 全球訪問
│                 │         │  │ (網頁)     │ │
└─────────────────┘         └──┴────────────┴─┘
                                      ▲
                            ┌─────────┴─────────┐
                            │  UptimeRobot      │
                            │  (每 5 分鐘 ping) │
                            └───────────────────┘
```

### 本地與雲端的分工

| 位置 | 運行內容 | 優勢 |
|:---|:---|:---|
| **本地電腦** | `main.py`（連接 Arduino） | 真實數據、本地備份 |
| **Render 雲端** | `web_server.py`（儀表板） | 隨時隨地訪問 |
| **UptimeRobot** | 定期 Ping Render | 保持服務活躍 |

---

## ❓ 常見問題

### Q1: Render 上的服務一直崩潰？

**A**: 檢查 Logs，常見原因：
- 環境變數沒設定（如 `SERIAL_PORT=SIMULATE`）
- `requirements.txt` 缺少套件
- Start Command 寫錯

### Q2: 本地如何推送數據到 Render？

**A**: 使用 `cloud_sync.py`：
1. 在本地 `.env` 新增：
   ```ini
   CLOUD_API_URL=https://你的render網址.onrender.com
   ```
2. `main.py` 會自動調用 `cloud_sync.py` 推送數據

### Q3: UptimeRobot 顯示 "Down"？

**A**: 可能原因：
- Render 服務正在部署中（等幾分鐘）
- URL 設定錯誤（確認是 `/api/status`）
- Render 免費額度用完（每月 750 小時）

### Q4: 如何查看 Render 的即時 Logs？

**A**: 
1. 進入你的 Render Dashboard
2. 點擊你的 Web Service
3. 選擇 **"Logs"** 標籤頁

### Q5: Render 免費方案的限制？

**A**:
- ✅ 750 小時/月（約 31 天）
- ✅ 自動休眠（15 分鐘無活動）
- ✅ 啟動時間較慢（約 30 秒）
- ❌ 無法持續運行超過 750 小時
- 💡 使用 UptimeRobot 可避免休眠

---

## 🎉 完成！

現在你已經成功：
- ✅ 將專案部署到 Render
- ✅ 設定正確的 Start Command
- ✅ 配置環境變數
- ✅ 使用 UptimeRobot 保持服務運行

你的溫濕度監控系統現在可以在全球任何地方訪問了！🌍
