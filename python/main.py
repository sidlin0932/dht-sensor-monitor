"""
主程式 - DHT 溫濕度監測系統
生物機電工程概論 期末專題

功能：
- 從 Arduino 讀取 DHT 感測器數據
- 儲存到 SQLite 資料庫
- 發送到 Discord Webhook
- 執行 Discord Bot
- 提供 Web API 與儀表板
"""

import time
import threading
import signal
import sys
from datetime import datetime

# 匯入模組
from config import (
    SERIAL_PORT, WEBHOOK_INTERVAL,
    DISCORD_WEBHOOK_URL, DISCORD_BOT_TOKEN,
    CLOUD_SYNC_ENABLED
)
import database as db
from serial_reader import ArduinoReader, find_arduino_port
from discord_webhook import DiscordWebhook
from discord_bot import SensorBot
import web_server
from cloud_sync import get_cloud_sync


class DHT_Monitor:
    """DHT 溫濕度監測系統主類別"""
    
    def __init__(self):
        self.is_running = False
        
        # 初始化各模組
        self.arduino: ArduinoReader = None
        self.webhook = DiscordWebhook()
        self.bot: SensorBot = None
        self.cloud_sync = get_cloud_sync()  # 雲端同步
        
        # 計時器
        self.last_webhook_time = 0
        
        # 統計
        self.total_readings = 0
        self.errors = 0
    
    def start(self):
        """啟動監測系統"""
        print("=" * 50)
        print("🌡️  DHT 溫濕度監測系統")
        print("   生物機電工程概論 期末專題")
        print("=" * 50)
        
        # 初始化資料庫
        print("\n📦 初始化資料庫...")
        db.init_database()
        
        # 連接 Arduino
        print("\n🔌 連接 Arduino...")
        self._connect_arduino()
        
        # 啟動 Web 伺服器
        print("\n🌐 啟動 Web 伺服器...")
        web_server.start_server_thread()
        
        # 啟動 Discord Bot（如果有設定）
        if DISCORD_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
            print("\n🤖 啟動 Discord Bot...")
            self._start_discord_bot()
        else:
            print("\n⚠️  未設定 Discord Bot Token，跳過 Bot 功能")
        
        # 發送啟動通知
        if DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE":
            print("\n📤 發送啟動通知到 Discord...")
            self.webhook.send_startup_message()
        
        # 雲端同步狀態
        if self.cloud_sync.enabled:
            print("\n☁️ 雲端同步已啟用")
            if self.cloud_sync.check_connection():
                print("   ✅ 雲端連接正常")
            else:
                print("   ⚠️ 無法連接雲端，將僅使用本機")
        
        # 開始監測
        print("\n" + "=" * 50)
        print("✅ 系統啟動完成！")
        print(f"📊 儀表板: http://127.0.0.1:5000")
        print(f"📡 監測間隔: {WEBHOOK_INTERVAL} 秒")
        if self.cloud_sync.enabled:
            print(f"☁️ 雲端同步: 已啟用")
        print("🛑 按 Ctrl+C 停止系統")
        print("=" * 50 + "\n")
        
        self.is_running = True
        self._main_loop()
    
    def _connect_arduino(self):
        """連接 Arduino"""
        # 嘗試自動偵測
        port = find_arduino_port()
        if port:
            print(f"🔍 自動偵測到 Arduino: {port}")
        else:
            port = SERIAL_PORT
            print(f"📌 使用設定的埠號: {port}")
        
        self.arduino = ArduinoReader(port=port)
        
        # 嘗試連接
        if not self.arduino.connect():
            print("\n⚠️  無法連接 Arduino，進入模擬模式")
            print("   程式會繼續運行，但會產生隨機數據")
            self.arduino = None
        else:
            # 設定回呼函數
            self.arduino.start_continuous_read(self._on_data_received)
    
    def _start_discord_bot(self):
        """在背景執行緒啟動 Discord Bot"""
        self.bot = SensorBot()
        
        def run_bot():
            try:
                self.bot.run(DISCORD_BOT_TOKEN)
            except Exception as e:
                print(f"❌ Discord Bot 錯誤: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
    
    def _on_data_received(self, data: dict):
        """處理從 Arduino 收到的數據"""
        try:
            temperature = data.get('temp')
            humidity = data.get('humidity')
            heat_index = data.get('heat_index')
            
            if temperature is None or humidity is None:
                return
            
            self.total_readings += 1
            
            # 顯示數據
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🌡️ {temperature:.1f}°C  💧 {humidity:.1f}%  (讀取 #{self.total_readings})")
            
            # 儲存到本地資料庫
            db.insert_reading(temperature, humidity, heat_index)
            
            # 更新本地 Web API
            web_server.update_current_reading(temperature, humidity, heat_index)
            
            # 同步到雲端（非同步，不阻塞）
            if self.cloud_sync.enabled:
                self.cloud_sync.push_reading(
                    temperature, humidity, heat_index,
                    send_discord=False  # 本地已發送 Discord
                )
            
            # 檢查是否需要發送 Webhook
            current_time = time.time()
            if current_time - self.last_webhook_time >= WEBHOOK_INTERVAL:
                self._send_webhook(temperature, humidity, heat_index)
                self.last_webhook_time = current_time
        
        except Exception as e:
            self.errors += 1
            print(f"❌ 處理數據錯誤: {e}")
    
    def _send_webhook(self, temperature: float, humidity: float, heat_index: float = None):
        """發送 Webhook 通知"""
        if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
            return
        
        try:
            # 發送數據
            self.webhook.send_sensor_data(temperature, humidity, heat_index)
            
            # 檢查是否需要發送警告
            self.webhook.check_and_send_warning(temperature, humidity)
            
        except Exception as e:
            print(f"❌ Webhook 發送失敗: {e}")
    
    def _main_loop(self):
        """主迴圈"""
        try:
            while self.is_running:
                # 如果沒有 Arduino，產生模擬數據
                if self.arduino is None:
                    self._simulate_data()
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 收到停止信號...")
            self.stop()
    
    def _simulate_data(self):
        """模擬數據（當沒有 Arduino 時使用）"""
        import random
        
        # 每 60 秒產生一筆模擬數據
        current_time = time.time()
        if current_time - self.last_webhook_time >= WEBHOOK_INTERVAL:
            # 產生隨機數據
            temperature = round(random.uniform(20, 30), 1)
            humidity = round(random.uniform(40, 70), 1)
            heat_index = round(temperature + random.uniform(0, 2), 1)
            
            # 處理數據
            self._on_data_received({
                'temp': temperature,
                'humidity': humidity,
                'heat_index': heat_index
            })
    
    def stop(self):
        """停止監測系統"""
        self.is_running = False
        
        print("\n正在關閉系統...")
        
        # 停止 Arduino 連線
        if self.arduino:
            self.arduino.stop_continuous_read()
            self.arduino.disconnect()
        
        # 發送關閉通知
        if DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE":
            self.webhook.send_shutdown_message()
        
        # 顯示統計
        print("\n📊 執行統計：")
        print(f"   總讀取次數: {self.total_readings}")
        print(f"   錯誤次數: {self.errors}")
        print(f"   資料庫總記錄: {db.get_reading_count()}")
        
        # 雲端同步統計
        if self.cloud_sync.enabled:
            stats = self.cloud_sync.get_stats()
            print(f"   ☁️ 雲端同步: {stats['successful_syncs']} 成功 / {stats['failed_syncs']} 失敗")
        
        print("\n👋 系統已關閉，再見！")


def main():
    """主程式進入點"""
    monitor = DHT_Monitor()
    
    # 設定信號處理
    def signal_handler(sig, frame):
        monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 啟動
    monitor.start()


if __name__ == "__main__":
    main()
