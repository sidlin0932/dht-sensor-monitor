# 📦 安裝與設定指南

本指南將帶您完成 DHT 溫濕度監測系統的完整安裝與設定。

## 目錄

1. [前置需求](#前置需求)
2. [Arduino 設定](#arduino-設定)
3. [Python 環境設定](#python-環境設定)
4. [Discord 設定](#discord-設定)
5. [執行程式](#執行程式)
6. [疑難排解](#疑難排解)

---

## 前置需求

### 硬體
- [x] Arduino Uno（或相容板）
- [x] DHT11 或 DHT22 感測器
- [x] USB 傳輸線
- [x] 杜邦線 × 3

### 軟體
- [x] Windows 10/11
- [x] Arduino IDE 1.8+
- [x] Python 3.8+
- [x] 現代瀏覽器

---

## Arduino 設定

### 步驟 1：安裝 Arduino IDE

如果尚未安裝：
1. 前往 [Arduino 官網](https://www.arduino.cc/en/software)
2. 下載 Windows 版本
3. 執行安裝程式

### 步驟 2：安裝 DHT 函式庫

1. 開啟 Arduino IDE
2. 點擊 **工具** → **管理函式庫**
3. 搜尋 `DHT sensor library`
4. 找到 **DHT sensor library by Adafruit**
5. 點擊 **安裝**

同時也會提示安裝相依函式庫 `Adafruit Unified Sensor`，請一併安裝。

### 步驟 3：連接硬體

按照 [接線圖](wiring.md) 連接 DHT 感測器到 Arduino。

### 步驟 4：上傳程式碼

1. 開啟 `arduino/dht_sensor/dht_sensor.ino`
2. **重要**：如果您使用 DHT22，修改程式碼：
   ```cpp
   #define DHTTYPE DHT22  // 改成 DHT22
   ```
3. 選擇正確的開發板：**工具** → **開發板** → **Arduino Uno**
4. 選擇正確的 COM Port：**工具** → **序列埠** → **COM?**（請查看裝置管理員）
5. 點擊 **上傳** 按鈕（→）

### 步驟 5：測試 Arduino

1. 點擊 **工具** → **序列埠監控視窗**
2. 設定 Baud Rate 為 **9600**
3. 應該會看到類似以下的輸出：
   ```json
   {"status": "ready", "sensor": "DHT11", "pin": "A5"}
   {"temp": 25.0, "humidity": 60.0, "heat_index": 25.5, "count": 1}
   ```

---

## Python 環境設定

### 步驟 1：確認 Python 已安裝

開啟命令提示字元（CMD）或 PowerShell，輸入：
```bash
python --version
```

應該顯示 `Python 3.x.x`。如果沒有，請前往 [Python 官網](https://www.python.org/downloads/) 下載安裝。

> **重要**：安裝時請勾選 **Add Python to PATH**

### 步驟 2：進入專案目錄

```bash
cd "C:\Users\sid\台大\114-1\生物機電工程概論\期末專題程式碼\python"
```

### 步驟 3：安裝依賴套件

```bash
pip install -r requirements.txt
```

這會安裝以下套件：
- `pyserial` - Serial 通訊
- `discord.py` - Discord Bot
- `requests` - HTTP 請求
- `flask` - Web 伺服器
- `flask-cors` - 跨域支援
- `matplotlib` - 圖表生成
- `python-dotenv` - 環境變數

### 步驟 4：設定 Serial Port

1. 開啟 **裝置管理員**
2. 展開 **連接埠 (COM & LPT)**
3. 找到 Arduino 對應的 COM Port（如 `COM3`）
4. 編輯 `config.py`，修改：
   ```python
   SERIAL_PORT = "COM3"  # 改成你的 COM Port
   ```

---

## Discord 設定

### Webhook 設定（必要）

Webhook 用於發送即時通知到 Discord 頻道。

1. 開啟 Discord 應用程式
2. 進入您的伺服器
3. 點擊 **伺服器設定**（齒輪圖示）
4. 選擇 **整合** → **Webhook**
5. 點擊 **新增 Webhook**
6. 選擇要發送的頻道
7. 複製 **Webhook URL**
8. 編輯 `config.py`，貼上 URL：
   ```python
   DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
   ```

### Bot 設定（選用）

Bot 可以讓您用指令互動查詢數據。

#### 1. 建立應用程式

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 點擊 **New Application**
3. 輸入名稱（如「DHT 監測機器人」）
4. 點擊 **Create**

#### 2. 設定 Bot

1. 在左側選單點擊 **Bot**
2. 點擊 **Reset Token** 取得 Token
3. **複製 Token**（只會顯示一次！）
4. 在 **Privileged Gateway Intents** 區塊：
   - 開啟 **Message Content Intent**

#### 3. 邀請 Bot 到伺服器

1. 在左側選單點擊 **OAuth2** → **URL Generator**
2. 在 **Scopes** 勾選 `bot`
3. 在 **Bot Permissions** 勾選：
   - `Send Messages`
   - `Embed Links`
   - `Attach Files`
   - `Read Message History`
4. 複製底部的 URL
5. 在瀏覽器開啟該 URL
6. 選擇您的伺服器，點擊 **授權**

#### 4. 設定 Token

編輯 `config.py`，貼上 Bot Token：
```python
DISCORD_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

---

## 執行程式

### 啟動監測系統

```bash
cd "C:\Users\sid\台大\114-1\生物機電工程概論\期末專題程式碼\python"
python main.py
```

### 成功啟動應該會看到

```
==================================================
🌡️  DHT 溫濕度監測系統
   生物機電工程概論 期末專題
==================================================

📦 初始化資料庫...
✅ 資料庫初始化完成：sensor_data.db

🔌 連接 Arduino...
🔍 自動偵測到 Arduino: COM3
✅ 已連接到 Arduino: COM3

🌐 啟動 Web 伺服器...
📊 儀表板網址: http://127.0.0.1:5000

🤖 啟動 Discord Bot...

📤 發送啟動通知到 Discord...

==================================================
✅ 系統啟動完成！
📊 儀表板: http://127.0.0.1:5000
📡 監測間隔: 60 秒
🛑 按 Ctrl+C 停止系統
==================================================
```

### 開啟儀表板

在瀏覽器開啟：http://127.0.0.1:5000

---

## 疑難排解

### Arduino 無法連接

**症狀**：顯示 `❌ 連接失敗` 或找不到 COM Port

**解決方案**：
1. 確認 USB 線有連接
2. 在裝置管理員確認 COM Port
3. 確認沒有其他程式佔用 Serial Port（如 Arduino IDE 的序列埠監控視窗）
4. 嘗試拔插 USB 線

### DHT 感測器讀取失敗

**症狀**：Arduino Serial Monitor 顯示 `Failed to read from DHT sensor`

**解決方案**：
1. 檢查接線是否正確
2. 確認 DHT 型號設定正確（DHT11 或 DHT22）
3. 嘗試在 DATA 與 VCC 之間加 10K 上拉電阻

### Discord Webhook 無法發送

**症狀**：程式執行但 Discord 沒收到訊息

**解決方案**：
1. 確認 Webhook URL 正確
2. 確認網路連接正常
3. 檢查 Discord 頻道是否存在

### Discord Bot 無法啟動

**症狀**：顯示 `Improper token has been passed`

**解決方案**：
1. 確認 Token 正確
2. 在 Discord Developer Portal 重新生成 Token
3. 確認已啟用 Message Content Intent

### 網頁儀表板無法顯示

**症狀**：瀏覽器顯示錯誤

**解決方案**：
1. 確認 Python 程式正在執行
2. 確認瀏覽器網址是 `http://127.0.0.1:5000`
3. 嘗試清除瀏覽器快取

---

## 常用指令

```bash
# 啟動系統
python main.py

# 測試 Serial 連接
python serial_reader.py

# 測試資料庫
python database.py

# 測試 Webhook
python discord_webhook.py

# 單獨執行 Discord Bot
python discord_bot.py

# 單獨執行 Web 伺服器
python web_server.py
```

---

## 下一步

系統設定完成後，您可以：

1. 📊 在儀表板觀察即時數據
2. 🤖 在 Discord 使用 `!help` 查看 Bot 指令
3. 📈 等待收集足夠數據後查看歷史圖表
4. ⚙️ 調整 `config.py` 中的警告閾值

祝您專題順利！🎓
