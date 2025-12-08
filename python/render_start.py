"""
Render 雲端啟動腳本
生物機電工程概論 期末專題
"""

import os
import sys
from pathlib import Path

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
if '--web-only' in sys.argv:
    # 僅啟動 Web 伺服器
    print("📊 模式：僅 Web 伺服器")
    from web_server import run_server
    run_server(
        host=os.environ['WEB_HOST'],
        port=int(os.environ['WEB_PORT']),
        debug=False
    )
else:
    # 啟動完整系統（含模擬）
    print("🎯 模式：完整系統 (含模擬感測器)")
    import main
