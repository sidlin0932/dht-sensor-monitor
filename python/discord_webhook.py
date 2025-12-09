"""
Discord Webhook 模組 - 發送通知
生物機電工程概論 期末專題
"""

import requests
from datetime import datetime
from typing import Optional, Dict, Any

from config import (
    DISCORD_WEBHOOK_URL,
    TEMP_WARNING_HIGH, TEMP_WARNING_LOW,
    HUMIDITY_WARNING_HIGH, HUMIDITY_WARNING_LOW
)


class DiscordWebhook:
    """Discord Webhook 發送器"""
    
    def __init__(self, webhook_url: str = None):
        """
        初始化 Webhook 發送器
        
        Args:
            webhook_url: Webhook URL（預設使用 config.py 設定）
        """
        self.webhook_url = webhook_url or DISCORD_WEBHOOK_URL
    
    def send_message(self, content: str) -> bool:
        """
        發送純文字訊息
        
        Args:
            content: 訊息內容
        
        Returns:
            是否發送成功
        """
        try:
            response = requests.post(
                self.webhook_url,
                json={"content": content},
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Webhook 發送失敗: {e}")
            return False
    
    def send_embed(self, embed: Dict[str, Any], content: str = None) -> bool:
        """
        發送 Embed 訊息
        
        Args:
            embed: Embed 資料
            content: 額外的純文字內容
        
        Returns:
            是否發送成功
        """
        try:
            payload = {"embeds": [embed]}
            if content:
                payload["content"] = content
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Webhook 發送失敗: {e}")
            return False
    
    def send_sensor_data(
        self,
        temperature: float,
        humidity: float,
        heat_index: float = None,
        air_quality: float = None
    ) -> bool:
        """
        發送感測器數據
        
        Args:
            temperature: 溫度（攝氏）
            humidity: 濕度（%）
            heat_index: 體感溫度（可選）
            air_quality: 空氣品質 PPM（可選）
        
        Returns:
            是否發送成功
        """
        # 判斷狀態和顏色
        status, color = self._get_status_and_color(temperature, humidity, air_quality)
        
        # 建立單行數據字串 (一字排開)
        data_text = f"🌡️ **{temperature:.1f}°C** | 💧 **{humidity:.1f}%**"
        
        if heat_index is not None:
            data_text += f" | 🔥 **{heat_index:.1f}°C**"
            
        if air_quality is not None:
            ppm_status = self._get_ppm_status(air_quality)
            data_text += f" | 💨 **{air_quality:.0f} ppm**" # ({ppm_status})
            
            # 將狀態放在括號或其他地方? 
            # 用戶希望一字排開，簡單一點比較好。 PPM 狀態可以放在下一行或同一行
            # 讓狀態顯示在最後
            # data_text += f" ({ppm_status})"

        # 建立 Embed
        embed = {
            "title": "🌡️ 溫濕度監測報告",
            "description": data_text, # 使用 description 放單行數據
            "color": color,
            "fields": [
                {
                    "name": "📊 狀態",
                    "value": f"{status}" + (f" ({self._get_ppm_status(air_quality)})" if air_quality else ""),
                    "inline": False # 狀態放下面一行
                }
            ],
            "footer": {
                "text": "DHT 感測器監測系統"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.send_embed(embed)
    
    def _get_ppm_status(self, ppm: float) -> str:
        """根據 PPM 值判斷空氣品質狀態"""
        if ppm <= 400:
            return "優良 🌿"
        elif ppm <= 600:
            return "良好 👍"
        elif ppm <= 1000:
            return "普通 😐"
        elif ppm <= 2000:
            return "不良 ⚠️"
        else:
            return "危險 🚨"
    
    def send_warning(
        self,
        warning_type: str,
        temperature: float,
        humidity: float,
        message: str
    ) -> bool:
        """
        發送警告通知
        
        Args:
            warning_type: 警告類型（如 "高溫", "低溫", "高濕", "低濕"）
            temperature: 溫度
            humidity: 濕度
            message: 警告訊息
        
        Returns:
            是否發送成功
        """
        embed = {
            "title": f"⚠️ 警告：{warning_type}",
            "description": message,
            "color": 0xFF0000,  # 紅色
            "fields": [
                {
                    "name": "🌡️ 目前溫度",
                    "value": f"**{temperature:.1f}°C**",
                    "inline": True
                },
                {
                    "name": "💧 目前濕度",
                    "value": f"**{humidity:.1f}%**",
                    "inline": True
                }
            ],
            "footer": {
                "text": "DHT 感測器監測系統 - 警告通知"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.send_embed(embed, content="@here ⚠️ 環境異常警告！")
    
    def send_startup_message(self) -> bool:
        """發送系統啟動通知"""
        embed = {
            "title": "🚀 監測系統已啟動",
            "description": "DHT 溫濕度監測系統已開始運行",
            "color": 0x00FF00,  # 綠色
            "fields": [
                {
                    "name": "📡 狀態",
                    "value": "正常運行中",
                    "inline": True
                },
                {
                    "name": "⏱️ 監測間隔",
                    "value": "每分鐘",
                    "inline": True
                }
            ],
            "footer": {
                "text": "DHT 感測器監測系統"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.send_embed(embed)
    
    def send_shutdown_message(self) -> bool:
        """發送系統關閉通知"""
        embed = {
            "title": "🔴 監測系統已停止",
            "description": "DHT 溫濕度監測系統已停止運行",
            "color": 0x808080,  # 灰色
            "footer": {
                "text": "DHT 感測器監測系統"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.send_embed(embed)
    
    def _get_status_and_color(self, temperature: float, humidity: float, air_quality: float = None) -> tuple:
        """
        根據溫濕度判斷狀態和顏色
        
        Returns:
            (狀態文字, 顏色代碼)
        """
        warnings = []
        
        if temperature >= TEMP_WARNING_HIGH:
            warnings.append("🔴 高溫")
        elif temperature <= TEMP_WARNING_LOW:
            warnings.append("🔵 低溫")
        
        if humidity >= HUMIDITY_WARNING_HIGH:
            warnings.append("💦 高濕")
        elif humidity <= HUMIDITY_WARNING_LOW:
            warnings.append("🏜️ 乾燥")
        
        # 檢查空氣品質 (PPM > 1000 為警告)
        if air_quality is not None and air_quality > 1000:
            warnings.append("💨 空氣差")
        
        if warnings:
            return " | ".join(warnings), 0xFF6600  # 橘色警告
        
        return "✅ 正常", 0x00FF00  # 綠色正常
    
    def check_and_send_warning(
        self,
        temperature: float,
        humidity: float
    ) -> bool:
        """
        檢查是否需要發送警告
        
        Args:
            temperature: 溫度
            humidity: 濕度
        
        Returns:
            是否發送了警告
        """
        warnings_sent = False
        
        if temperature >= TEMP_WARNING_HIGH:
            self.send_warning(
                "高溫警告",
                temperature, humidity,
                f"溫度已達 {temperature:.1f}°C，超過 {TEMP_WARNING_HIGH}°C 警戒值！"
            )
            warnings_sent = True
        
        elif temperature <= TEMP_WARNING_LOW:
            self.send_warning(
                "低溫警告",
                temperature, humidity,
                f"溫度已降至 {temperature:.1f}°C，低於 {TEMP_WARNING_LOW}°C 警戒值！"
            )
            warnings_sent = True
        
        if humidity >= HUMIDITY_WARNING_HIGH:
            self.send_warning(
                "高濕警告",
                temperature, humidity,
                f"濕度已達 {humidity:.1f}%，超過 {HUMIDITY_WARNING_HIGH}% 警戒值！"
            )
            warnings_sent = True
        
        elif humidity <= HUMIDITY_WARNING_LOW:
            self.send_warning(
                "低濕警告",
                temperature, humidity,
                f"濕度已降至 {humidity:.1f}%，低於 {HUMIDITY_WARNING_LOW}% 警戒值！"
            )
            warnings_sent = True
        
        return warnings_sent


if __name__ == "__main__":
    # 測試 Webhook
    print("=== Discord Webhook 測試 ===")
    
    webhook = DiscordWebhook()
    
    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        print("⚠️ 請先在 config.py 設定 DISCORD_WEBHOOK_URL")
        print("\n模擬發送數據...")
        print("溫度: 25.5°C, 濕度: 60.2%")
    else:
        # 發送測試訊息
        print("發送啟動訊息...")
        webhook.send_startup_message()
        
        print("發送感測器數據...")
        webhook.send_sensor_data(25.5, 60.2, 26.1)
        
        print("✅ 測試完成！請檢查 Discord 頻道")
