"""
打包腳本 - 將 DHT Monitor 打包成獨立 .exe
"""

import subprocess
import os
import shutil

def build():
    print("=" * 50)
    print("DHT Monitor - EXE 打包工具")
    print("=" * 50)
    
    # PyInstaller 參數
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成單一檔案
        "--name", "DHT_Monitor",        # 執行檔名稱
        "--icon", "NONE",               # 無圖示
        "--console",                    # 顯示控制台視窗
        "--add-data", "../web;web",     # 包含網頁檔案
        "--hidden-import", "flask",
        "--hidden-import", "serial",
        "--hidden-import", "serial.tools.list_ports",
        "--hidden-import", "discord",
        "--hidden-import", "discord.ext.commands",
        "--hidden-import", "requests",
        "--hidden-import", "matplotlib",
        "--hidden-import", "matplotlib.pyplot",
        "--hidden-import", "google.generativeai",
        "main.py"                       # 主程式進入點
    ]
    
    print("\n[BUILD] 開始打包...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n[OK] 打包完成!")
        print(f"[OUTPUT] 執行檔位置: dist/DHT_Monitor.exe")
        
        # 複製 .env.example 到 dist
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", "dist/.env.example")
            print("[COPY] 已複製 .env.example 到 dist/")
        
        print("\n" + "=" * 50)
        print("使用說明:")
        print("1. 將 dist/DHT_Monitor.exe 複製到目標電腦")
        print("2. 將 .env.example 改名為 .env 並設定參數")
        print("3. 插上 Arduino USB")
        print("4. 雙擊 DHT_Monitor.exe 即可執行")
        print("=" * 50)
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] 打包失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build()
