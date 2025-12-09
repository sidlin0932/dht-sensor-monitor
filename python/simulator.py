"""
感測器模擬器 - 模擬 DHT 感測器產生數據
生物機電工程概論 期末專題

這個程式可以在沒有 Arduino 的情況下模擬感測器數據，
讓您可以測試 Discord 通知和網頁儀表板功能。

使用方式：python simulator.py
"""

import time
import random
import math
import threading
from datetime import datetime

# 匯入模組
from config import WEBHOOK_INTERVAL, DISCORD_WEBHOOK_URL, DISCORD_BOT_TOKEN
import database as db
from discord_webhook import DiscordWebhook
from discord_bot import SensorBot
import web_server


class SensorSimulator:
    """感測器模擬器"""
    
    def __init__(self):
        self.is_running = False
        
        # 模擬參數
        self.base_temp = 25.0       # 基礎溫度
        self.base_humidity = 55.0   # 基礎濕度
        self.temp_amplitude = 3.0   # 溫度波動幅度
        self.humidity_amplitude = 10.0  # 濕度波動幅度
        self.noise_level = 0.5      # 隨機噪音程度
        
        # 時間計數
        self.time_counter = 0
        
        # 模組
        self.webhook = DiscordWebhook()
        self.bot: SensorBot = None
        
        # 統計
        self.total_readings = 0
    
    def generate_reading(self) -> dict:
        """
        產生模擬的感測器讀數
        
        使用正弦波模擬日夜溫差，加上隨機噪音
        """
        self.time_counter += 1
        
        # 使用正弦波模擬溫度變化（模擬一天的溫度變化）
        # 每 1440 分鐘（24小時）為一個週期
        cycle_position = (self.time_counter % 1440) / 1440 * 2 * math.pi
        
        # 溫度：中午最高，凌晨最低
        temp_variation = math.sin(cycle_position - math.pi/2) * self.temp_amplitude
        temperature = self.base_temp + temp_variation + random.uniform(-self.noise_level, self.noise_level)
        
        # 濕度：與溫度相反（溫度高時濕度低）
        humidity_variation = -math.sin(cycle_position - math.pi/2) * self.humidity_amplitude
        humidity = self.base_humidity + humidity_variation + random.uniform(-self.noise_level * 2, self.noise_level * 2)
        
        # 確保在合理範圍內
        temperature = max(10, min(40, temperature))
        humidity = max(20, min(90, humidity))
        
        # 計算體感溫度（簡化公式）
        heat_index = temperature + 0.5 * (humidity / 100) * (temperature - 14.5)
        
        # 模擬 PPM 空氣品質（MQ135 感測器）
        # 正常室內空氣：300-500 ppm
        # 根據時間和隨機因素波動
        base_ppm = 350
        ppm_variation = math.sin(cycle_position) * 100  # 日間變化
        air_quality = base_ppm + ppm_variation + random.uniform(-50, 50)
        air_quality = max(100, min(1000, air_quality))  # 限制範圍
        
        return {
            'temp': round(temperature, 1),
            'humidity': round(humidity, 1),
            'heat_index': round(heat_index, 1),
            'air_quality': round(air_quality, 0)
        }
    
    def start(self):
        """啟動模擬器"""
        print("=" * 50)
        print("🎮  DHT 感測器模擬器")
        print("   生物機電工程概論 期末專題")
        print("=" * 50)
        print("\n📝 這是模擬模式，使用虛擬數據進行測試")
        
        # 初始化資料庫
        print("\n📦 初始化資料庫...")
        db.init_database()
        
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
        else:
            print("\n⚠️  未設定 Discord Webhook URL，跳過 Webhook 功能")
        
        # 開始模擬
        print("\n" + "=" * 50)
        print("✅ 模擬器啟動完成！")
        print(f"📊 儀表板: http://127.0.0.1:5000")
        print(f"📡 模擬間隔: {WEBHOOK_INTERVAL} 秒")
        print("🛑 按 Ctrl+C 停止模擬器")
        print("=" * 50 + "\n")
        
        self.is_running = True
        self._main_loop()
    
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
    
    def _main_loop(self):
        """主迴圈"""
        last_webhook_time = 0
        
        try:
            while self.is_running:
                current_time = time.time()
                
                # 每隔指定時間產生一筆數據
                if current_time - last_webhook_time >= WEBHOOK_INTERVAL:
                    last_webhook_time = current_time
                    
                    # 產生模擬數據
                    reading = self.generate_reading()
                    self.total_readings += 1
                    
                    # 顯示數據
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 🎮 模擬: 🌡️ {reading['temp']:.1f}°C  💧 {reading['humidity']:.1f}%  💨 {reading['air_quality']:.0f}ppm  (#{self.total_readings})")
                    
                    # 儲存到資料庫
                    db.insert_reading(
                        reading['temp'],
                        reading['humidity'],
                        reading['heat_index'],
                        reading['air_quality']
                    )
                    
                    # 更新 Web API
                    web_server.update_current_reading(
                        reading['temp'],
                        reading['humidity'],
                        reading['heat_index'],
                        reading['air_quality']
                    )
                    
                    # 發送 Webhook
                    if DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE":
                        self.webhook.send_sensor_data(
                            reading['temp'],
                            reading['humidity'],
                            reading['heat_index'],
                            reading['air_quality']
                        )
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 收到停止信號...")
            self.stop()
    
    def stop(self):
        """停止模擬器"""
        self.is_running = False
        
        print("\n正在關閉模擬器...")
        
        # 發送關閉通知
        if DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE":
            self.webhook.send_shutdown_message()
        
        # 顯示統計
        print("\n📊 模擬統計：")
        print(f"   產生讀數: {self.total_readings}")
        print(f"   資料庫總記錄: {db.get_reading_count()}")
        
        print("\n👋 模擬器已關閉，再見！")


def main():
    """主程式進入點"""
    import signal
    import sys
    
    simulator = SensorSimulator()
    
    # 設定信號處理
    def signal_handler(sig, frame):
        simulator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 啟動
    simulator.start()


if __name__ == "__main__":
    main()
