"""
雲端 API 伺服器 - Render 部署版本
生物機電工程概論 期末專題

這個程式部署到 Render，接收來自本機的數據並提供雲端儀表板。
"""

import os
from datetime import datetime, timedelta, timezone

# 定義台北時區 (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# ========== Flask App ==========
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)

# ========== 設定 ==========
DATABASE_URL = os.environ.get('DATABASE_URL')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
API_KEY = os.environ.get('API_KEY', 'your-secret-api-key')

# 警告閾值
TEMP_WARNING_HIGH = float(os.environ.get('TEMP_WARNING_HIGH', 35.0))
TEMP_WARNING_LOW = float(os.environ.get('TEMP_WARNING_LOW', 10.0))
HUMIDITY_WARNING_HIGH = float(os.environ.get('HUMIDITY_WARNING_HIGH', 80.0))
HUMIDITY_WARNING_LOW = float(os.environ.get('HUMIDITY_WARNING_LOW', 20.0))

# 儲存最新數據（記憶體快取）
current_reading = {
    'temperature': None,
    'humidity': None,
    'heat_index': None,
    'timestamp': None
}


# ========== 資料庫函數 ==========
def get_db_connection():
    """取得資料庫連線"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_database():
    """初始化資料庫表格"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id SERIAL PRIMARY KEY,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            heat_index REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_recorded_at 
        ON sensor_readings(recorded_at)
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ 資料庫初始化完成")


def insert_reading(temperature, humidity, heat_index=None):
    """新增讀數"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO sensor_readings (temperature, humidity, heat_index, recorded_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    ''', (temperature, humidity, heat_index, datetime.now(TAIPEI_TZ)))
    
    record_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    
    return record_id


def get_latest_reading():
    """取得最新讀數"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT * FROM sensor_readings 
        ORDER BY recorded_at DESC 
        LIMIT 1
    ''')
    
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    return dict(row) if row else None


def get_readings_by_hours(hours=24):
    """取得過去 N 小時的讀數"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    since = datetime.now(TAIPEI_TZ) - timedelta(hours=hours)
    
    cur.execute('''
        SELECT * FROM sensor_readings 
        WHERE recorded_at >= %s
        ORDER BY recorded_at ASC
    ''', (since,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(row) for row in rows]


def get_statistics(hours=24):
    """取得統計數據"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    since = datetime.now(TAIPEI_TZ) - timedelta(hours=hours)
    
    cur.execute('''
        SELECT 
            COUNT(*) as count,
            AVG(temperature) as avg_temp,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(humidity) as avg_humidity,
            MIN(humidity) as min_humidity,
            MAX(humidity) as max_humidity
        FROM sensor_readings 
        WHERE recorded_at >= %s
    ''', (since,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row and row['count'] > 0:
        return {
            'count': row['count'],
            'temperature': {
                'avg': round(float(row['avg_temp']), 1),
                'min': float(row['min_temp']),
                'max': float(row['max_temp'])
            },
            'humidity': {
                'avg': round(float(row['avg_humidity']), 1),
                'min': float(row['min_humidity']),
                'max': float(row['max_humidity'])
            },
            'hours': hours
        }
    
    return {'count': 0, 'hours': hours}


def get_reading_count():
    """取得總讀數"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*) as count FROM sensor_readings')
    count = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return count


# ========== Discord 函數 ==========
def send_discord_notification(temperature, humidity, heat_index=None):
    """發送 Discord 通知"""
    if not DISCORD_WEBHOOK_URL:
        return
    
    # 判斷狀態
    status = "✅ 正常"
    color = 0x00FF00
    
    if temperature >= TEMP_WARNING_HIGH or temperature <= TEMP_WARNING_LOW:
        status = "⚠️ 溫度異常"
        color = 0xFF0000
    elif humidity >= HUMIDITY_WARNING_HIGH or humidity <= HUMIDITY_WARNING_LOW:
        status = "⚠️ 濕度異常"
        color = 0xFF6600
    
    embed = {
        "title": "🌡️ 溫濕度監測報告",
        "color": color,
        "fields": [
            {"name": "🌡️ 溫度", "value": f"**{temperature:.1f}°C**", "inline": True},
            {"name": "💧 濕度", "value": f"**{humidity:.1f}%**", "inline": True},
            {"name": "📊 狀態", "value": status, "inline": True}
        ],
        "footer": {"text": "DHT 感測器監測系統 (雲端)"},
        "timestamp": datetime.now(TAIPEI_TZ).isoformat()
    }
    
    if heat_index:
        embed["fields"].insert(2, {
            "name": "🔥 體感溫度", 
            "value": f"**{heat_index:.1f}°C**", 
            "inline": True
        })
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
    except Exception as e:
        print(f"Discord 發送失敗: {e}")


# ========== 網頁路由 ==========
@app.route('/')
def index():
    """首頁"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """靜態檔案"""
    return send_from_directory(app.static_folder, path)


# ========== API 路由 ==========
@app.route('/api/push', methods=['POST'])
def api_push():
    """接收來自本機的數據推送"""
    # 驗證 API Key
    auth_header = request.headers.get('Authorization', '')
    if auth_header != f'Bearer {API_KEY}':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data'}), 400
    
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    heat_index = data.get('heat_index')
    
    if temperature is None or humidity is None:
        return jsonify({'success': False, 'error': 'Missing temperature or humidity'}), 400
    
    # 儲存到資料庫
    record_id = insert_reading(temperature, humidity, heat_index)
    
    # 更新記憶體快取
    global current_reading
    current_reading = {
        'temperature': temperature,
        'humidity': humidity,
        'heat_index': heat_index,
        'timestamp': datetime.now(TAIPEI_TZ).isoformat()
    }
    
    # 發送 Discord 通知（如果有設定）
    send_to_discord = data.get('send_discord', True)
    if send_to_discord:
        send_discord_notification(temperature, humidity, heat_index)
    
    return jsonify({
        'success': True,
        'id': record_id,
        'message': 'Data received'
    })


@app.route('/api/current')
def api_current():
    """取得目前數據"""
    if current_reading['timestamp']:
        return jsonify({'success': True, 'data': current_reading})
    
    latest = get_latest_reading()
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
    
    return jsonify({'success': False, 'error': 'No data'})


@app.route('/api/history')
def api_history():
    """取得歷史數據"""
    hours = request.args.get('hours', 24, type=int)
    hours = max(1, min(168, hours))
    
    readings = get_readings_by_hours(hours)
    
    data = [{
        'temperature': r['temperature'],
        'humidity': r['humidity'],
        'heat_index': r.get('heat_index'),
        'timestamp': str(r['recorded_at'])
    } for r in readings]
    
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
    hours = max(1, min(168, hours))
    
    stats = get_statistics(hours)
    
    return jsonify({
        'success': True,
        'hours': hours,
        'stats': stats
    })


@app.route('/api/status')
def api_status():
    """取得系統狀態"""
    total_count = get_reading_count()
    latest = get_latest_reading()
    
    status_data = {
        'total_readings': total_count,
        'server_time': datetime.now(TAIPEI_TZ).isoformat(),
        'version': '0.1.0',
        'mode': 'cloud'
    }
    
    if latest:
        recorded_at = latest['recorded_at']
        if isinstance(recorded_at, str):
            recorded_at = datetime.fromisoformat(recorded_at)
        
        time_diff = datetime.now(TAIPEI_TZ).replace(tzinfo=None) - recorded_at
        minutes_ago = time_diff.total_seconds() / 60
        
        status_data['last_reading'] = {
            'temperature': latest['temperature'],
            'humidity': latest['humidity'],
            'timestamp': str(latest['recorded_at']),
            'minutes_ago': round(minutes_ago, 1)
        }
        
        if minutes_ago < 5:
            status_data['sensor_status'] = 'online'
        elif minutes_ago < 15:
            status_data['sensor_status'] = 'delayed'
        else:
            status_data['sensor_status'] = 'offline'
    else:
        status_data['sensor_status'] = 'no_data'
    
    return jsonify({'success': True, **status_data})


@app.route('/api/health')
def api_health():
    """健康檢查（Render 使用）"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now(TAIPEI_TZ).isoformat()})


# ========== 啟動 ==========
if __name__ == '__main__':
    # 初始化資料庫
    if DATABASE_URL:
        init_database()
    else:
        print("⚠️ 未設定 DATABASE_URL")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
