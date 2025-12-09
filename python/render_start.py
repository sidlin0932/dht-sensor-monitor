"""
Render 雲端啟動腳本
生物機電工程概論 期末專題
"""

import os
import sys
import time
import random
import threading
from pathlib import Path
from datetime import datetime

# 確保在正確的目錄
project_root = Path(__file__).parent.parent
os.chdir(project_root / 'python')

# 設定環境變數（Render 專用）
os.environ.setdefault('SIMULATE_MODE', 'true')
os.environ.setdefault('WEB_HOST', '0.0.0.0')
os.environ.setdefault('WEB_PORT', os.getenv('PORT', '5000'))

print("=" * 60)
print("🚀 Render 雲端部署啟動")
print("=" * 60)
print(f"📍 工作目錄: {os.getcwd()}")
print(f"🌐 Web Host: {os.environ['WEB_HOST']}")
print(f"🔌 Web Port: {os.environ['WEB_PORT']}")
print(f"🎮 模擬模式: {os.environ['SIMULATE_MODE']}")
print("=" * 60)

# 檢查啟動模式
# 如果是 --web-only 或者 SIMULATE_MODE=false，則不產生模擬數據
simulate_mode = os.environ.get('SIMULATE_MODE', 'true').lower() == 'true'

if '--web-only' in sys.argv or not simulate_mode:
    # 僅啟動 Web 伺服器（不產生數據）
    mode_str = "僅 Web 伺服器" if '--web-only' in sys.argv else "Cloud Receiver 模式 (SIMULATE_MODE=false)"
    print(f"📊 模式：{mode_str}（等待外部數據推送）\n")
    from web_server import run_server
    run_server(
        host=os.environ['WEB_HOST'],
        port=int(os.environ['WEB_PORT']),
        debug=False
    )

else:
    # 啟動完整系統（含模擬數據產生器）
    print("🎯 模式：完整系統（自動產生模擬數據）\n")
    
    import database as db
    import web_server
    from config import DISCORD_WEBHOOK_URL
    from discord_webhook import DiscordWebhook
    
    # 初始化資料庫
    print("📦 初始化資料庫...")
    db.init_database()
    
    # 初始化 Discord Webhook（如果有設定）
    webhook = None
    if DISCORD_WEBHOOK_URL and DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE":
        webhook = DiscordWebhook()
        print("✅ Discord Webhook 已啟用")
    else:
        print("⚠️  未設定 Discord Webhook，跳過通知功能")
    
    # 在背景執行緒啟動 Web 伺服器
    print("🌐 啟動 Web 伺服器（背景執行緒）...")
    web_thread = web_server.start_server_thread(
        host=os.environ['WEB_HOST'],
        port=int(os.environ['WEB_PORT'])
    )
    
    print("✅ Web 伺服器已啟動")
    print(f"🌍 儀表板網址: http://{os.environ['WEB_HOST']}:{os.environ['WEB_PORT']}")
    
    # 發送啟動通知到 Discord
    if webhook:
        print("📤 發送啟動通知到 Discord...")
        webhook.send_startup_message()
    
    # 啟動 Discord Bot（如果有設定）
    from config import DISCORD_BOT_TOKEN
    bot_thread = None
    if DISCORD_BOT_TOKEN and DISCORD_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        print("🤖 準備啟動 Discord Bot...")
        from discord_bot import SensorBot
        
        def run_bot():
            try:
                print("🔄 Discord Bot 連線中...")
                bot = SensorBot()
                bot.run(DISCORD_BOT_TOKEN)
            except Exception as e:
                print(f"❌ Discord Bot 啟動失敗: {e}")
                import traceback
                traceback.print_exc()
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("✅ Discord Bot 執行緒已啟動")
        time.sleep(2)  # 等待 Bot 初始化
    else:
        print("⚠️  未設定 Discord Bot Token，跳過 Bot 功能")
        print("   提示：在 Render 設定 DISCORD_BOT_TOKEN 環境變數以啟用 Bot")
    
    print("\n🎲 開始產生模擬數據（每 30 秒一筆）...")
    print("📊 Discord 通知：每 5 筆數據發送一次\n")
    
    # 模擬數據產生器（主執行緒）
    reading_count = 0
    base_temp = 25.0
    base_humidity = 60.0
    
    try:
        while True:
            # 產生模擬數據（帶有波動）
            temperature = round(base_temp + random.uniform(-5, 5), 1)
            humidity = round(base_humidity + random.uniform(-15, 15), 1)
            heat_index = round(temperature + random.uniform(0, 3), 1)
            air_quality = int(random.uniform(200, 800))
            
            # 儲存到資料庫
            db.insert_reading(temperature, humidity, heat_index, air_quality)
            
            # 更新 Web API 的即時數據
            web_server.update_current_reading(temperature, humidity, heat_index, air_quality)
            
            reading_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"[{timestamp}] 🌡️ {temperature:.1f}°C  💧 {humidity:.1f}%  🔥 {heat_index:.1f}°C  💨 {air_quality}ppm  (#{reading_count})")
            
            # 每 5 筆數據發送一次到 Discord（避免過於頻繁）
            if webhook and reading_count % 5 == 0:
                print(f"  📤 發送數據到 Discord...")
                webhook.send_sensor_data(temperature, humidity, heat_index, air_quality)
            
            # 每 30 秒產生一筆數據
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信號，正在關閉...")
        print(f"📊 總共產生 {reading_count} 筆模擬數據")
        
        # 發送關閉通知到 Discord
        if webhook:
            print("📤 發送關閉通知到 Discord...")
            webhook.send_shutdown_message()
        
        sys.exit(0)
