# 🌡️ DHT 溫濕度監測系統

> 生物機電工程概論 期末專題

使用 Arduino + DHT11/22 感測器監測空氣溫濕度，透過筆電上的 Python 程式發送到 Discord，並提供美觀的網頁儀表板查看歷史數據。

![Dashboard Preview](docs/dashboard-preview.png)

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 🌡️ 即時監測 | 每分鐘讀取溫度與濕度 |
| 📤 Discord Webhook | 定時推送數據到 Discord 頻道 |
| 🤖 Discord Bot | 用指令查詢數據（`!now`、`!history`、`!chart` 等） |
| 💾 數據儲存 | SQLite 資料庫保存所有歷史數據 |
| 📊 網頁儀表板 | 美觀的即時儀表板 + 趨勢圖表 |
| ⚠️ 異常警告 | 溫濕度超過閾值時自動通知 |

## 📁 專案結構

```
期末專題程式碼/
├── README.md                    # 專題說明（本檔案）
├── CHANGELOG.md                 # 版本紀錄
├── arduino/
│   └── dht_sensor/
│       └── dht_sensor.ino       # Arduino 程式碼
├── python/
│   ├── requirements.txt         # Python 依賴套件
│   ├── config.py                # 設定檔
│   ├── database.py              # 資料庫模組
│   ├── serial_reader.py         # Serial 通訊模組
│   ├── discord_webhook.py       # Discord Webhook 模組
│   ├── discord_bot.py           # Discord Bot 模組
│   ├── web_server.py            # Web API 伺服器
│   └── main.py                  # 主程式
├── web/
│   ├── index.html               # 儀表板頁面
│   ├── style.css                # 樣式表
│   └── script.js                # JavaScript 邏輯
└── docs/
    ├── wiring.md                # 接線圖
    └── setup.md                 # 安裝指南
```

## 🔧 硬體需求

- Arduino Uno（或相容板）
- DHT11 或 DHT22 溫濕度感測器
- USB 傳輸線（連接 Arduino 與電腦）
- 杜邦線 × 3

## 💻 軟體需求

- [Arduino IDE](https://www.arduino.cc/en/software) 1.8+
- [Python](https://www.python.org/downloads/) 3.8+
- 現代瀏覽器（Chrome、Firefox、Edge）

## 🚀 快速開始 (Quick Start)

**詳細的跨平台安裝與部署教學，請參考 [📖 部署指南 (docs/DEPLOY.md)](docs/DEPLOY.md)。**

該指南包含：
- ✅ Windows / macOS / Linux 完整安裝步驟
- ✅ 硬體接線詳細說明
- ✅ Python 虛擬環境設定
- ✅ Discord Bot 與 Webhook 設定

### 5. 執行

```bash
# 執行主程式（需要 Arduino）
python main.py

# 或執行模擬器（不需要 Arduino）
python simulator.py
```

系統啟動後：
- 📊 儀表板網址：http://127.0.0.1:5000
- 📡 每分鐘會讀取感測器並發送到 Discord
- 🤖 Discord Bot 指令可用（如果有設定）

## 🎮 模擬模式

如果您手邊沒有 Arduino 或感測器，可以使用**模擬器**來測試系統：

```bash
cd python
python simulator.py
```

模擬器會：
- ✅ 產生逼真的溫濕度數據（使用正弦波模擬日夜變化）
- ✅ 儲存到資料庫
- ✅ 發送到 Discord（如果有設定 Webhook）
- ✅ 顯示在網頁儀表板

這讓您可以在沒有硬體的情況下完整測試所有功能！

## 🤖 Discord Bot 指令

| 指令 | 說明 |
|------|------|
| `!now` | 查詢目前溫濕度 |
| `!history [小時數]` | 查詢歷史數據（預設 24 小時） |
| `!stats [小時數]` | 查詢統計資料 |
| `!chart [小時數]` | 生成歷史圖表 |
| `!status` | 查詢系統狀態 |
| `!help` | 顯示幫助訊息 |

## 📝 設定說明

編輯 `python/config.py`：

```python
# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# Discord Bot Token（選用）
DISCORD_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Serial Port（Windows: COM3, COM4 等）
SERIAL_PORT = "COM3"

# 警告閾值
TEMP_WARNING_HIGH = 35.0   # 高溫警告
TEMP_WARNING_LOW = 10.0    # 低溫警告
HUMIDITY_WARNING_HIGH = 80.0  # 高濕警告
HUMIDITY_WARNING_LOW = 20.0   # 低濕警告
```

## 🔍 疑難排解

### Arduino 無法連接
1. 確認 USB 線有連接
2. 在裝置管理員查看 COM Port 編號
3. 修改 `config.py` 的 `SERIAL_PORT`

### Discord Webhook 無法發送
1. 確認 Webhook URL 正確
2. 確認網路連接正常
3. 檢查 Discord 伺服器設定

### 圖表無法顯示
1. 確認資料庫中有數據
2. 等待至少 2 筆數據後再檢視

## 📜 授權

本專案為學術用途，僅供學習參考。

## 👨‍🎓 開發資訊

- **課程**：生物機電工程概論
- **學期**：114-1
- **類型**：期末專題
