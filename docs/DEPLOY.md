# 🚀 部署教學 (Deployment Guide)

本指南將協助您在個人電腦（Windows / macOS / Linux）上架設此溫濕度監控系統。

## 📋 事前準備 (Prerequisites)

在開始之前，請確保您的電腦已安裝以下軟體：

1.  **Python 3.8 或以上版本**
    *   [下載 Python](https://www.python.org/downloads/)
    *   *Windows 用戶安裝時請務必勾選 "Add Python to PATH"*
2.  **Arduino IDE**
    *   [下載 Arduino IDE](https://www.arduino.cc/en/software)
3.  **Git** (非必要，但建議使用)
    *   [下載 Git](https://git-scm.com/downloads)

---

## 🛠️ 硬體架設 (Hardware Setup)

### 備料
*   Arduino Uno (或其他相容開發板)
*   DHT11 或 DHT22 溫濕度感測器
*   RGB LED (共陰極)
*   蜂鳴器 (Active Buzzer)
*   杜邦線數條

### 接線圖
請依照以下腳位進行連接：

| 元件腳位 | Arduino 腳位 | 說明 |
| :--- | :--- | :--- |
| **DHT VCC** | 5V | 電源正極 |
| **DHT GND** | GND | 接地 |
| **DHT DATA** | **A5** | 訊號讀取 |
| **LED R** | **D9** (PWM) | 紅光 |
| **LED G** | **D10** (PWM) | 綠光 |
| **LED B** | **D11** (PWM) | 藍光 |
| **LED COM** | GND | 共陰極接地 |
| **Buzzer +** | **D8** | 蜂鳴器正極 |
| **Buzzer -** | GND | 蜂鳴器接地 |

---

## 💻 軟體安裝與執行 (Software Installation)

### 步驟 1：燒錄 Arduino 程式

1.  開啟 **Arduino IDE**。
2.  安裝 DHT Library：
    *   點選 `Sketch` -> `Include Library` -> `Manage Libraries...`
    *   搜尋 `DHT sensor library` (by Adafruit) 並安裝。
    *   (若提示安裝 Adafruit Unified Sensor，請一併安裝)
3.  開啟專案中的 `arduino/dht_sensor/dht_sensor.ino` 檔案。
4.  將 Arduino 連接到電腦 USB。
5.  選擇對應的 Port 和 Board (Arduino Uno)。
6.  點擊 **Upload (上傳)** 按鈕。

### 步驟 2：設定 Python 環境

開啟終端機 (Terminal) 或命令提示字元 (Command Prompt)，並移動到專案資料夾：

```bash
cd path/to/project
```

#### Windows 用戶
```powershell
# 建立虛擬環境 (建議)
python -m venv venv

# 啟動虛擬環境
.\venv\Scripts\activate

# 安裝套件
pip install -r python/requirements.txt
```

#### macOS / Linux 用戶
```bash
# 建立虛擬環境 (建議)
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate

# 安裝套件
pip install -r python/requirements.txt
```

### 步驟 3：設定環境變數

1.  進入 `python` 資料夾。
2.  複製 `.env.example` 並重新命名為 `.env`。
3.  使用文字編輯器開啟 `.env`，填入您的設定：

```ini
# Discord 設定 (若不需要 Bot 可留預設)
DISCORD_BOT_TOKEN=你的_DC_BOT_TOKEN
DISCORD_WEBHOOK_URL=你的_WEBHOOK_URL

# Arduino 連接埠 (重要！)
# Windows 範例: COM3
# Mac/Linux 範例: /dev/tty.usbmodem14101
SERIAL_PORT=COM3 
```

> **如何查看 Serial Port?**
> *   **Windows**: 裝置管理員 -> 連接埠 (COM & LPT)
> *   **Mac/Linux**: 在終端機輸入 `ls /dev/tty.*`

### 步驟 4：啟動系統

確保 Arduino 已連接，在終端機執行：

```bash
# 確保您在專案根目錄
python python/main.py
```

若看見類似以下的輸出，即代表成功：
```text
=== 生物機電期末專題 - 環境監測系統 ===
✅ 設定檔驗證通過！
🔌 正在連接 Arduino (COM3)...
✅ Arduino 連線成功！
🤖 Discord Bot 已上線
🚀 Web Server running at http://127.0.0.1:5000
```

現在可以打開瀏覽器訪問 `http://127.0.0.1:5000` 查看儀表板！

---

## ❓ 常見問題 (Troubleshooting)

**Q: 程式顯示 "找不到指定的模組" 或 "ImportError"?**
A: 請確保您已執行 `pip install -r python/requirements.txt` 並且虛擬環境已啟動。

**Q: Arduino 連接失敗 (Timeout)?**
A:
1. 檢查 `.env` 中的 `SERIAL_PORT` 是否正確。
2. 確認 Arduino IDE 的 Serial Monitor 是否已關閉 (Com Port 不能同時被兩個程式佔用)。
3. 檢查 USB 線是否接觸不良。

**Q: Discord Bot 沒有上線?**
A: 請確認 `.env` 中的 `DISCORD_BOT_TOKEN` 正確，且 Bot 需在開發者後台開啟 `Message Content Intent` 權限。
