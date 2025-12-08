"""
雲端同步模組 - 將本機數據推送到雲端
生物機電工程概論 期末專題
"""

import requests
import threading
import time
from typing import Optional
from datetime import datetime

from config import (
    CLOUD_API_URL,
    CLOUD_API_KEY,
    CLOUD_SYNC_ENABLED
)


class CloudSync:
    """雲端同步器"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        初始化同步器
        
        Args:
            api_url: 雲端 API URL（如 https://your-app.onrender.com）
            api_key: API 金鑰
        """
        self.api_url = api_url or CLOUD_API_URL
        self.api_key = api_key or CLOUD_API_KEY
        self.enabled = CLOUD_SYNC_ENABLED and self.api_url != "YOUR_CLOUD_API_URL"
        
        # 統計
        self.successful_syncs = 0
        self.failed_syncs = 0
        self.last_sync_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
    
    def push_reading(
        self,
        temperature: float,
        humidity: float,
        heat_index: float = None,
        send_discord: bool = True,
        async_mode: bool = True
    ) -> bool:
        """
        推送讀數到雲端
        
        Args:
            temperature: 溫度
            humidity: 濕度
            heat_index: 體感溫度
            send_discord: 是否讓雲端發送 Discord 通知
            async_mode: 是否非同步執行（不阻塞主程式）
        
        Returns:
            是否成功（async_mode 時總是返回 True）
        """
        if not self.enabled:
            return False
        
        if async_mode:
            thread = threading.Thread(
                target=self._push_reading_sync,
                args=(temperature, humidity, heat_index, send_discord),
                daemon=True
            )
            thread.start()
            return True
        else:
            return self._push_reading_sync(temperature, humidity, heat_index, send_discord)
    
    def _push_reading_sync(
        self,
        temperature: float,
        humidity: float,
        heat_index: float = None,
        send_discord: bool = True
    ) -> bool:
        """同步推送數據"""
        try:
            response = requests.post(
                f"{self.api_url}/api/push",
                json={
                    'temperature': temperature,
                    'humidity': humidity,
                    'heat_index': heat_index,
                    'send_discord': send_discord
                },
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.successful_syncs += 1
                self.last_sync_time = datetime.now()
                self.last_error = None
                return True
            else:
                self.failed_syncs += 1
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                print(f"☁️❌ 雲端同步失敗: {self.last_error}")
                return False
        
        except requests.Timeout:
            self.failed_syncs += 1
            self.last_error = "請求逾時"
            print("☁️❌ 雲端同步逾時")
            return False
        
        except requests.ConnectionError:
            self.failed_syncs += 1
            self.last_error = "無法連接到雲端"
            return False  # 靜默失敗，不印出（可能沒網路）
        
        except Exception as e:
            self.failed_syncs += 1
            self.last_error = str(e)
            print(f"☁️❌ 雲端同步錯誤: {e}")
            return False
    
    def check_connection(self) -> bool:
        """
        檢查雲端連接
        
        Returns:
            是否可以連接
        """
        if not self.enabled:
            return False
        
        try:
            response = requests.get(
                f"{self.api_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> dict:
        """取得同步統計"""
        return {
            'enabled': self.enabled,
            'api_url': self.api_url if self.enabled else None,
            'successful_syncs': self.successful_syncs,
            'failed_syncs': self.failed_syncs,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'last_error': self.last_error
        }


# 全域同步器實例
_cloud_sync: Optional[CloudSync] = None


def get_cloud_sync() -> CloudSync:
    """取得雲端同步器實例"""
    global _cloud_sync
    if _cloud_sync is None:
        _cloud_sync = CloudSync()
    return _cloud_sync


def push_to_cloud(temperature: float, humidity: float, heat_index: float = None):
    """
    便捷函數：推送數據到雲端
    
    使用方式：
        from cloud_sync import push_to_cloud
        push_to_cloud(25.5, 60.2)
    """
    sync = get_cloud_sync()
    sync.push_reading(temperature, humidity, heat_index)


if __name__ == "__main__":
    # 測試雲端同步
    print("=== 雲端同步測試 ===")
    
    sync = CloudSync()
    
    print(f"同步已啟用: {sync.enabled}")
    print(f"API URL: {sync.api_url}")
    
    if sync.enabled:
        print("\n檢查連接...")
        if sync.check_connection():
            print("✅ 雲端連接正常")
            
            print("\n推送測試數據...")
            result = sync.push_reading(25.5, 60.2, 26.1, send_discord=False, async_mode=False)
            
            if result:
                print("✅ 數據推送成功")
            else:
                print(f"❌ 數據推送失敗: {sync.last_error}")
        else:
            print("❌ 無法連接到雲端")
    else:
        print("\n⚠️ 雲端同步未啟用")
        print("請在 config.py 設定 CLOUD_API_URL 和 CLOUD_API_KEY")
