"""
資料庫模組 - SQLite 數據儲存
生物機電工程概論 期末專題
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os

from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """取得資料庫連線"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 讓結果可以用欄位名稱存取
    return conn


def init_database():
    """初始化資料庫，建立資料表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 建立感測器數據表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            heat_index REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 建立索引以加速查詢
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_recorded_at 
        ON sensor_readings(recorded_at)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ 資料庫初始化完成：{DATABASE_PATH}")


def insert_reading(temperature: float, humidity: float, heat_index: float = None) -> int:
    """
    新增一筆感測器讀數
    
    Args:
        temperature: 溫度（攝氏）
        humidity: 濕度（%）
        heat_index: 體感溫度（可選）
    
    Returns:
        新增的記錄 ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sensor_readings (temperature, humidity, heat_index, recorded_at)
        VALUES (?, ?, ?, ?)
    ''', (temperature, humidity, heat_index, datetime.now()))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def get_latest_reading() -> Optional[Dict[str, Any]]:
    """取得最新一筆讀數"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM sensor_readings 
        ORDER BY recorded_at DESC 
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_readings_by_hours(hours: int = 24) -> List[Dict[str, Any]]:
    """
    取得過去 N 小時的所有讀數
    
    Args:
        hours: 要查詢的小時數
    
    Returns:
        讀數列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    
    cursor.execute('''
        SELECT * FROM sensor_readings 
        WHERE recorded_at >= ?
        ORDER BY recorded_at ASC
    ''', (since,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_statistics(hours: int = 24) -> Dict[str, Any]:
    """
    取得過去 N 小時的統計數據
    
    Args:
        hours: 要統計的小時數
    
    Returns:
        統計資料字典
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    
    cursor.execute('''
        SELECT 
            COUNT(*) as count,
            AVG(temperature) as avg_temp,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(humidity) as avg_humidity,
            MIN(humidity) as min_humidity,
            MAX(humidity) as max_humidity
        FROM sensor_readings 
        WHERE recorded_at >= ?
    ''', (since,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row['count'] > 0:
        return {
            'count': row['count'],
            'temperature': {
                'avg': round(row['avg_temp'], 1),
                'min': row['min_temp'],
                'max': row['max_temp']
            },
            'humidity': {
                'avg': round(row['avg_humidity'], 1),
                'min': row['min_humidity'],
                'max': row['max_humidity']
            },
            'hours': hours
        }
    
    return {
        'count': 0,
        'temperature': {'avg': None, 'min': None, 'max': None},
        'humidity': {'avg': None, 'min': None, 'max': None},
        'hours': hours
    }


def get_reading_count() -> int:
    """取得總讀數數量"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM sensor_readings')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


def cleanup_old_data(days: int = 30):
    """
    清理超過 N 天的舊數據
    
    Args:
        days: 保留的天數
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    
    cursor.execute('''
        DELETE FROM sensor_readings 
        WHERE recorded_at < ?
    ''', (cutoff,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"🗑️ 已清理 {deleted} 筆超過 {days} 天的舊數據")
    return deleted


if __name__ == "__main__":
    # 測試資料庫功能
    print("=== 資料庫測試 ===")
    
    # 初始化
    init_database()
    
    # 插入測試數據
    test_id = insert_reading(25.5, 60.2, 26.1)
    print(f"✅ 插入測試數據，ID: {test_id}")
    
    # 查詢最新數據
    latest = get_latest_reading()
    print(f"📊 最新讀數: {latest}")
    
    # 統計數據
    stats = get_statistics(24)
    print(f"📈 統計數據: {stats}")
    
    # 總數量
    count = get_reading_count()
    print(f"📝 總讀數: {count}")
