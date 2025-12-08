"""
資料儲存模組 - JSON/CSV 格式
生物機電工程概論 期末專題

這個模組使用 JSON 和 CSV 格式儲存數據，取代 SQLite。
- JSON：完整數據，適合程式讀取
- CSV：試算表格式，可用 Excel 開啟
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from config import DATABASE_PATH


# 取得資料目錄
DATA_DIR = Path(os.path.dirname(DATABASE_PATH)) if DATABASE_PATH != "sensor_data.db" else Path(".")
DATA_DIR = DATA_DIR / "data"

# 檔案路徑
JSON_FILE = DATA_DIR / "sensor_data.json"
CSV_FILE = DATA_DIR / "sensor_data.csv"


def init_database():
    """初始化資料儲存"""
    # 建立資料目錄
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 初始化 JSON 檔案
    if not JSON_FILE.exists():
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump({"readings": [], "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "0.1.0"
            }}, f, ensure_ascii=False, indent=2)
    
    # 初始化 CSV 檔案
    if not CSV_FILE.exists():
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'temperature', 'humidity', 'heat_index', 'recorded_at'])
    
    print(f"✅ 資料儲存初始化完成")
    print(f"   📄 JSON: {JSON_FILE}")
    print(f"   📊 CSV:  {CSV_FILE}")


def _load_json() -> Dict:
    """載入 JSON 數據"""
    if not JSON_FILE.exists():
        return {"readings": [], "metadata": {}}
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_json(data: Dict):
    """儲存 JSON 數據"""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _append_csv(reading: Dict):
    """附加一筆數據到 CSV"""
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            reading['id'],
            reading['temperature'],
            reading['humidity'],
            reading.get('heat_index', ''),
            reading['recorded_at']
        ])


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
    data = _load_json()
    
    # 產生新 ID
    if data['readings']:
        new_id = max(r['id'] for r in data['readings']) + 1
    else:
        new_id = 1
    
    # 建立新記錄
    reading = {
        'id': new_id,
        'temperature': round(temperature, 1),
        'humidity': round(humidity, 1),
        'heat_index': round(heat_index, 1) if heat_index else None,
        'recorded_at': datetime.now().isoformat()
    }
    
    # 加入 JSON
    data['readings'].append(reading)
    _save_json(data)
    
    # 附加到 CSV
    _append_csv(reading)
    
    return new_id


def get_latest_reading() -> Optional[Dict[str, Any]]:
    """取得最新一筆讀數"""
    data = _load_json()
    
    if data['readings']:
        return data['readings'][-1]
    return None


def get_readings_by_hours(hours: int = 24) -> List[Dict[str, Any]]:
    """
    取得過去 N 小時的所有讀數
    
    Args:
        hours: 要查詢的小時數
    
    Returns:
        讀數列表
    """
    data = _load_json()
    since = datetime.now() - timedelta(hours=hours)
    
    results = []
    for reading in data['readings']:
        recorded_at = datetime.fromisoformat(reading['recorded_at'])
        if recorded_at >= since:
            results.append(reading)
    
    return results


def get_statistics(hours: int = 24) -> Dict[str, Any]:
    """
    取得過去 N 小時的統計數據
    
    Args:
        hours: 要統計的小時數
    
    Returns:
        統計資料字典
    """
    readings = get_readings_by_hours(hours)
    
    if not readings:
        return {
            'count': 0,
            'temperature': {'avg': None, 'min': None, 'max': None},
            'humidity': {'avg': None, 'min': None, 'max': None},
            'hours': hours
        }
    
    temps = [r['temperature'] for r in readings]
    humids = [r['humidity'] for r in readings]
    
    return {
        'count': len(readings),
        'temperature': {
            'avg': round(sum(temps) / len(temps), 1),
            'min': min(temps),
            'max': max(temps)
        },
        'humidity': {
            'avg': round(sum(humids) / len(humids), 1),
            'min': min(humids),
            'max': max(humids)
        },
        'hours': hours
    }


def get_reading_count() -> int:
    """取得總讀數數量"""
    data = _load_json()
    return len(data['readings'])


def get_all_readings() -> List[Dict[str, Any]]:
    """取得所有讀數"""
    data = _load_json()
    return data['readings']


def cleanup_old_data(days: int = 30) -> int:
    """
    清理超過 N 天的舊數據
    
    Args:
        days: 保留的天數
    
    Returns:
        刪除的記錄數
    """
    data = _load_json()
    cutoff = datetime.now() - timedelta(days=days)
    
    original_count = len(data['readings'])
    
    # 過濾保留的數據
    data['readings'] = [
        r for r in data['readings']
        if datetime.fromisoformat(r['recorded_at']) >= cutoff
    ]
    
    deleted = original_count - len(data['readings'])
    
    if deleted > 0:
        _save_json(data)
        # 重建 CSV
        _rebuild_csv(data['readings'])
        print(f"🗑️ 已清理 {deleted} 筆超過 {days} 天的舊數據")
    
    return deleted


def _rebuild_csv(readings: List[Dict]):
    """重建 CSV 檔案"""
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'temperature', 'humidity', 'heat_index', 'recorded_at'])
        for reading in readings:
            writer.writerow([
                reading['id'],
                reading['temperature'],
                reading['humidity'],
                reading.get('heat_index', ''),
                reading['recorded_at']
            ])


def export_to_csv(filepath: str = None) -> str:
    """
    匯出數據到 CSV 檔案
    
    Args:
        filepath: 輸出路徑（預設使用標準 CSV 檔案）
    
    Returns:
        輸出的檔案路徑
    """
    if filepath is None:
        filepath = CSV_FILE
    
    data = _load_json()
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'temperature', 'humidity', 'heat_index', 'recorded_at'])
        for reading in data['readings']:
            writer.writerow([
                reading['id'],
                reading['temperature'],
                reading['humidity'],
                reading.get('heat_index', ''),
                reading['recorded_at']
            ])
    
    print(f"📊 已匯出 {len(data['readings'])} 筆數據到 {filepath}")
    return str(filepath)


def import_from_csv(filepath: str) -> int:
    """
    從 CSV 檔案匯入數據
    
    Args:
        filepath: CSV 檔案路徑
    
    Returns:
        匯入的記錄數
    """
    imported = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            insert_reading(
                float(row['temperature']),
                float(row['humidity']),
                float(row['heat_index']) if row.get('heat_index') else None
            )
            imported += 1
    
    print(f"📥 已匯入 {imported} 筆數據")
    return imported


if __name__ == "__main__":
    # 測試
    print("=== 資料儲存測試 ===")
    
    init_database()
    
    # 插入測試數據
    for i in range(5):
        temp = 20 + i * 2
        humidity = 50 + i * 5
        record_id = insert_reading(temp, humidity, temp + 1)
        print(f"  插入 ID {record_id}: {temp}°C, {humidity}%")
    
    # 查詢
    print(f"\n最新讀數: {get_latest_reading()}")
    print(f"總數量: {get_reading_count()}")
    print(f"統計: {get_statistics(24)}")
    
    print(f"\n📂 數據檔案位置:")
    print(f"   JSON: {JSON_FILE.absolute()}")
    print(f"   CSV:  {CSV_FILE.absolute()}")
