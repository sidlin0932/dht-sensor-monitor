"""
Serial 讀取模組 - 與 Arduino 通訊
生物機電工程概論 期末專題
"""

import serial
import serial.tools.list_ports
import json
import time
from typing import Optional, Dict, Any, Callable
import threading

from config import SERIAL_PORT, SERIAL_BAUD_RATE, SERIAL_TIMEOUT


class ArduinoReader:
    """Arduino Serial 讀取器"""
    
    def __init__(self, port: str = None, baud_rate: int = None):
        """
        初始化讀取器
        
        Args:
            port: Serial 埠號（預設使用 config.py 設定）
            baud_rate: 通訊速率（預設使用 config.py 設定）
        """
        self.port = port or SERIAL_PORT
        self.baud_rate = baud_rate or SERIAL_BAUD_RATE
        self.serial: Optional[serial.Serial] = None
        self.is_running = False
        self.read_thread: Optional[threading.Thread] = None
        self.on_data_callback: Optional[Callable[[Dict], None]] = None
        self.on_error_callback: Optional[Callable[[str], None]] = None
        self.last_data: Optional[Dict[str, Any]] = None
    
    @staticmethod
    def list_available_ports() -> list:
        """列出所有可用的 Serial 埠"""
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]
    
    def connect(self) -> bool:
        """
        連接到 Arduino
        
        Returns:
            是否連接成功
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=SERIAL_TIMEOUT
            )
            
            # 等待 Arduino 重置
            time.sleep(2)
            
            # 清空緩衝區
            self.serial.reset_input_buffer()
            
            print(f"[OK] Connected to Arduino: {self.port}")
            return True
            
        except serial.SerialException as e:
            print(f"[ERROR] Connection failed: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))
            return False
    
    def disconnect(self):
        """中斷連接"""
        self.is_running = False
        
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("[OK] Arduino disconnected")
    
    def send_command(self, command: str) -> bool:
        """
        發送指令到 Arduino
        
        Args:
            command: 指令字串（如 "READ", "STATUS", "PING"）
        
        Returns:
            是否發送成功
        """
        if not self.serial or not self.serial.is_open:
            return False
        
        try:
            self.serial.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"[ERROR] Send command failed: {e}")
            return False
    
    def read_line(self) -> Optional[Dict[str, Any]]:
        """
        讀取一行數據並解析 JSON
        
        Returns:
            解析後的數據字典，或 None
        """
        if not self.serial or not self.serial.is_open:
            return None
        
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                
                if line:
                    try:
                        data = json.loads(line)
                        self.last_data = data
                        return data
                    except json.JSONDecodeError:
                        print(f"[WARN] Cannot parse JSON: {line}")
                        return None
        
        except Exception as e:
            print(f"[ERROR] Read error: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))
        
        return None
    
    def read_blocking(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        等待並讀取一行數據
        
        Args:
            timeout: 等待逾時（秒）
        
        Returns:
            解析後的數據字典，或 None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            data = self.read_line()
            if data:
                return data
            time.sleep(0.1)
        
        return None
    
    def start_continuous_read(self, callback: Callable[[Dict], None]):
        """
        開始連續讀取模式
        
        Args:
            callback: 每次收到數據時呼叫的函數
        """
        self.on_data_callback = callback
        self.is_running = True
        
        self.read_thread = threading.Thread(target=self._continuous_read_loop, daemon=True)
        self.read_thread.start()
        
        print("[OK] Started listening to Arduino data...")
    
    def _continuous_read_loop(self):
        """連續讀取迴圈（在背景執行緒中運行）"""
        while self.is_running:
            try:
                data = self.read_line()
                
                if data and self.on_data_callback:
                    # 只處理包含溫濕度的數據
                    if 'temp' in data and 'humidity' in data:
                        self.on_data_callback(data)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[ERROR] Read loop error: {e}")
                time.sleep(1)
    
    def stop_continuous_read(self):
        """停止連續讀取"""
        self.is_running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        print("[STOP] Stopped listening")
    
    def get_last_data(self) -> Optional[Dict[str, Any]]:
        """取得最後一筆讀取的數據"""
        return self.last_data
    
    def request_reading(self) -> Optional[Dict[str, Any]]:
        """
        請求立即讀取數據
        
        Returns:
            讀取的數據，或 None
        """
        if self.send_command("READ"):
            return self.read_blocking(timeout=5.0)
        return None
    
    def ping(self) -> bool:
        """
        測試連接
        
        Returns:
            是否連接正常
        """
        if self.send_command("PING"):
            response = self.read_blocking(timeout=2.0)
            return response is not None and response.get('pong') == True
        return False


def find_arduino_port() -> Optional[str]:
    """
    自動尋找 Arduino 連接的埠號
    
    Returns:
        找到的埠號，或 None
    """
    ports = ArduinoReader.list_available_ports()
    
    for port, description in ports:
        # 常見的 Arduino 描述
        if any(keyword in description.lower() for keyword in ['arduino', 'ch340', 'usb serial', 'usb-serial']):
            print(f"[DETECT] Found possible Arduino: {port} - {description}")
            return port
    
    return None


if __name__ == "__main__":
    # 測試 Serial 讀取
    print("=== Serial 讀取測試 ===")
    
    # 列出可用埠
    print("\n可用的 Serial 埠：")
    ports = ArduinoReader.list_available_ports()
    for port, desc in ports:
        print(f"  {port}: {desc}")
    
    # 嘗試自動找到 Arduino
    auto_port = find_arduino_port()
    if auto_port:
        print(f"\n自動偵測到 Arduino: {auto_port}")
    
    # 連接測試
    reader = ArduinoReader()
    
    if reader.connect():
        print("\n等待數據...")
        
        # 嘗試讀取幾筆數據
        for i in range(5):
            data = reader.read_blocking(timeout=10)
            if data:
                print(f"收到數據: {data}")
            else:
                print("逾時，未收到數據")
        
        reader.disconnect()
    else:
        print("\n無法連接到 Arduino，請檢查：")
        print("  1. Arduino 是否已連接")
        print("  2. config.py 中的 SERIAL_PORT 設定是否正確")
        print("  3. Arduino 程式碼是否已上傳")
