"""
設定檔 - DHT 溫濕度監測系統
生物機電工程概論 期末專題

請在此填入您的設定值
"""

import os
from dotenv import load_dotenv

# 載入 .env 檔案（如果存在）
load_dotenv()

# ========== Discord 設定 ==========

# Discord Webhook URL
# 取得方式：Discord 伺服器設定 → 整合 → Webhook → 新增 Webhook → 複製 URL
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "YOUR_WEBHOOK_URL_HERE")

# Discord Bot Token
# 取得方式：https://discord.com/developers/applications → 新增應用程式 → Bot → Token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Discord Bot 指令前綴
BOT_COMMAND_PREFIX = "!"

# ========== Gemini AI 設定 ==========

# Gemini API Key
# 取得方式：https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# ========== Arduino Serial 設定 ==========

# Serial Port
# Windows: "COM3", "COM4" 等（請在裝置管理員查看）
# Mac/Linux: "/dev/ttyUSB0", "/dev/ttyACM0" 等
SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")

# Baud Rate（必須與 Arduino 程式碼一致）
SERIAL_BAUD_RATE = 9600

# Serial 讀取逾時（秒）
SERIAL_TIMEOUT = 2

# ========== 資料庫設定 ==========

# SQLite 資料庫檔案路徑
DATABASE_PATH = os.getenv("DATABASE_PATH", "sensor_data.db")

# ========== Web 伺服器設定 ==========

# Web 伺服器主機（本地: 127.0.0.1 / 雲端: 0.0.0.0）
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")

# Web 伺服器埠號（本地: 5000 / Render: $PORT）
WEB_PORT = int(os.getenv("WEB_PORT", "5000"))

# ========== 監測設定 ==========

# Webhook 發送間隔（秒），60 = 每分鐘
# 如果要快速測試，可改成 10 秒
WEBHOOK_INTERVAL = 60

# ========== 模擬模式設定 ==========
# 當沒有 Arduino 時，使用模擬數據

# 是否啟用模擬模式 (預設 false)
SIMULATE_MODE = os.getenv("SIMULATE_MODE", "false").lower() == "true"

# 模擬器基礎溫度（攝氏）
SIMULATOR_BASE_TEMP = 25.0

# 模擬器基礎濕度（%）
SIMULATOR_BASE_HUMIDITY = 55.0

# 模擬器溫度波動幅度
SIMULATOR_TEMP_AMPLITUDE = 5.0

# 模擬器濕度波動幅度
SIMULATOR_HUMIDITY_AMPLITUDE = 15.0

# 溫度警告閾值（攝氏）
TEMP_WARNING_HIGH = 35.0  # 高溫警告
TEMP_WARNING_LOW = 10.0   # 低溫警告

# 濕度警告閾值（%）
HUMIDITY_WARNING_HIGH = 80.0  # 高濕警告
HUMIDITY_WARNING_LOW = 20.0   # 低濕警告

# ========== 雲端同步設定 ==========
# 將數據同時推送到 Render 雲端

# 是否啟用雲端同步
CLOUD_SYNC_ENABLED = os.getenv("CLOUD_SYNC_ENABLED", "false").lower() == "true"

# 雲端 API URL（您的 Render 應用程式網址）
# 例如：https://dht-monitor.onrender.com
CLOUD_API_URL = os.getenv("CLOUD_API_URL", "YOUR_CLOUD_API_URL")

# 雲端 API 金鑰（在 Render 環境變數中設定）
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY", "YOUR_CLOUD_API_KEY")

# ========== 顯示設定 ==========

# 時區（用於顯示時間）
TIMEZONE = "Asia/Taipei"

# 溫度單位（C = 攝氏，F = 華氏）
TEMP_UNIT = "C"


def validate_config():
    """驗證設定是否完整"""
    errors = []
    
    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        errors.append("請設定 DISCORD_WEBHOOK_URL")
    
    if DISCORD_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("請設定 DISCORD_BOT_TOKEN（如果要使用 Bot 功能）")
    
    if SERIAL_PORT == "COM3" and os.name != 'nt':
        errors.append("請檢查 SERIAL_PORT 設定（目前設定為 Windows 格式）")
    
    return errors


if __name__ == "__main__":
    # 測試設定
    print("=== 設定檔驗證 ===")
    errors = validate_config()
    
    if errors:
        print("⚠️ 發現以下問題：")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 設定檔驗證通過！")
    
    print("\n=== 目前設定 ===")
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Web Server: http://{WEB_HOST}:{WEB_PORT}")
    print(f"Webhook Interval: {WEBHOOK_INTERVAL} 秒")
