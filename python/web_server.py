"""
Web 伺服器模組 - API 與儀表板
生物機電工程概論 期末專題
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import datetime
import os
import threading

from config import WEB_HOST, WEB_PORT
import database as db


# 建立 Flask 應用
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)  # 允許跨域請求

# 儲存最新的即時數據
current_reading = {
    'temperature': None,
    'humidity': None,
    'heat_index': None,
    'timestamp': None
}


# ========== 網頁路由 ==========

@app.route('/')
def index():
    """首頁 - 儀表板"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """靜態檔案"""
    return send_from_directory(app.static_folder, path)


# ========== API 路由 ==========

@app.route('/api/current')
def api_current():
    """取得目前數據"""
    # 優先使用即時數據
    if current_reading['timestamp']:
        return jsonify({
            'success': True,
            'data': current_reading
        })
    
    # 否則從資料庫取得最新數據
    latest = db.get_latest_reading()
    
    if latest:
        return jsonify({
            'success': True,
            'data': {
                'temperature': latest['temperature'],
                'humidity': latest['humidity'],
                'heat_index': latest.get('heat_index'),
                'timestamp': str(latest['recorded_at'])
            }
        })
    
    return jsonify({
        'success': False,
        'error': 'No data available'
    })


@app.route('/api/history')
def api_history():
    """取得歷史數據"""
    hours = request.args.get('hours', 24, type=int)
    
    if hours < 1:
        hours = 1
    elif hours > 168:  # 最多 7 天
        hours = 168
    
    readings = db.get_readings_by_hours(hours)
    
    # 格式化數據
    data = []
    for reading in readings:
        data.append({
            'temperature': reading['temperature'],
            'humidity': reading['humidity'],
            'heat_index': reading.get('heat_index'),
            'timestamp': str(reading['recorded_at'])
        })
    
    return jsonify({
        'success': True,
        'hours': hours,
        'count': len(data),
        'data': data
    })


@app.route('/api/stats')
def api_stats():
    """取得統計數據"""
    hours = request.args.get('hours', 24, type=int)
    
    if hours < 1:
        hours = 1
    elif hours > 168:
        hours = 168
    
    stats = db.get_statistics(hours)
    
    return jsonify({
        'success': True,
        'hours': hours,
        'stats': stats
    })


@app.route('/api/status')
def api_status():
    """取得系統狀態"""
    total_count = db.get_reading_count()
    latest = db.get_latest_reading()
    
    status_data = {
        'total_readings': total_count,
        'server_time': datetime.now().isoformat()
    }
    
    if latest:
        recorded_at = datetime.fromisoformat(str(latest['recorded_at']))
        time_diff = datetime.now() - recorded_at
        minutes_ago = time_diff.total_seconds() / 60
        
        status_data['last_reading'] = {
            'temperature': latest['temperature'],
            'humidity': latest['humidity'],
            'timestamp': str(latest['recorded_at']),
            'minutes_ago': round(minutes_ago, 1)
        }
        
        # 判斷狀態
        if minutes_ago < 5:
            status_data['sensor_status'] = 'online'
        elif minutes_ago < 15:
            status_data['sensor_status'] = 'delayed'
        else:
            status_data['sensor_status'] = 'offline'
    else:
        status_data['sensor_status'] = 'no_data'
    
    return jsonify({
        'success': True,
        **status_data
    })


@app.route('/api/clear/soft', methods=['POST'])
def api_clear_soft():
    """暫時清空 - 只重置前端即時數據"""
    global current_reading
    current_reading = {
        'temperature': None,
        'humidity': None,
        'heat_index': None,
        'timestamp': None
    }
    
    return jsonify({
        'success': True,
        'message': 'Soft clear completed. Display data reset.',
        'type': 'soft'
    })


@app.route('/api/clear/hard', methods=['POST'])
def api_clear_hard():
    """永久清空 - 刪除資料庫中的所有數據"""
    # 從請求中獲取確認碼（防止誤操作）
    data = request.get_json() or {}
    confirm = data.get('confirm', False)
    
    if not confirm:
        return jsonify({
            'success': False,
            'error': 'Confirmation required. Send {"confirm": true} to proceed.'
        }), 400
    
    deleted_count = db.clear_all_data()
    
    # 同時重置即時數據
    global current_reading
    current_reading = {
        'temperature': None,
        'humidity': None,
        'heat_index': None,
        'timestamp': None
    }
    
    return jsonify({
        'success': True,
        'message': f'Hard clear completed. {deleted_count} records permanently deleted.',
        'deleted_count': deleted_count,
        'type': 'hard'
    })


# ========== 供外部呼叫的函數 ==========

def update_current_reading(temperature: float, humidity: float, heat_index: float = None):
    """更新即時數據（供 main.py 呼叫）"""
    global current_reading
    current_reading = {
        'temperature': temperature,
        'humidity': humidity,
        'heat_index': heat_index,
        'timestamp': datetime.now().isoformat()
    }


def run_server(host: str = None, port: int = None, debug: bool = False):
    """執行 Web 伺服器"""
    host = host or WEB_HOST
    port = port or WEB_PORT
    
    print(f"[WEB] Starting web server...")
    print(f"[URL] Dashboard: http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)


def start_server_thread(host: str = None, port: int = None):
    """在背景執行緒啟動 Web 伺服器"""
    server_thread = threading.Thread(
        target=run_server,
        args=(host, port, False),
        daemon=True
    )
    server_thread.start()
    return server_thread


if __name__ == "__main__":
    # 初始化資料庫
    db.init_database()
    
    # 插入一些測試數據
    print("Inserting test data...")
    for i in range(10):
        temp = 20 + i * 0.5
        humidity = 50 + i * 2
        db.insert_reading(temp, humidity, temp + 1)
    
    # 啟動伺服器
    run_server(debug=True)

