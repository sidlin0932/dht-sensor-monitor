/*
 * DHT 溫濕度感測器 - Arduino 程式碼
 * 生物機電工程概論 期末專題
 * 
 * 功能：讀取 DHT11/22 感測器數據，透過 Serial 傳送到電腦
 * 
 * 接線說明：
 *   DHT VCC  → Arduino 5V
 *   DHT GND  → Arduino GND
 *   DHT DATA → Arduino A5 (Pin 19)
 * 
 * 注意：如果使用 DHT22，請將下方 DHTTYPE 改為 DHT22
 */

#include <DHT.h>

// ========== 設定區域 ==========
#define DHTPIN A5           // DHT 感測器資料腳位 (A5 = Digital Pin 19)
#define DHTTYPE DHT11       // 使用 DHT11，如果是 DHT22 請改成 DHT22

#define READ_INTERVAL 60000 // 讀取間隔（毫秒），60000 = 1 分鐘
#define BAUD_RATE 9600      // Serial 通訊速率
// ==============================

// 初始化 DHT 感測器
DHT dht(DHTPIN, DHTTYPE);

// 上次讀取時間
unsigned long lastReadTime = 0;

// 讀取計數器
unsigned long readCount = 0;

void setup() {
  // 初始化 Serial 通訊
  Serial.begin(BAUD_RATE);
  
  // 初始化 DHT 感測器
  dht.begin();
  
  // 等待感測器穩定
  delay(2000);
  
  // 啟動訊息
  Serial.println("{\"status\": \"ready\", \"sensor\": \"" + String(DHTTYPE == DHT11 ? "DHT11" : "DHT22") + "\", \"pin\": \"A5\"}");
  
  // 立即讀取一次
  readAndSendData();
}

void loop() {
  unsigned long currentTime = millis();
  
  // 檢查是否到達讀取間隔
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    readAndSendData();
  }
  
  // 檢查是否有來自電腦的指令
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "READ") {
      // 手動觸發讀取
      readAndSendData();
    } else if (command == "STATUS") {
      // 回報狀態
      sendStatus();
    } else if (command == "PING") {
      // 連線測試
      Serial.println("{\"pong\": true}");
    }
  }
}

void readAndSendData() {
  // 讀取濕度
  float humidity = dht.readHumidity();
  
  // 讀取溫度（攝氏）
  float temperature = dht.readTemperature();
  
  // 讀取計數增加
  readCount++;
  
  // 檢查讀取是否成功
  if (isnan(humidity) || isnan(temperature)) {
    // 讀取失敗
    Serial.println("{\"error\": \"Failed to read from DHT sensor\", \"count\": " + String(readCount) + "}");
    return;
  }
  
  // 計算體感溫度（熱指數）
  float heatIndex = dht.computeHeatIndex(temperature, humidity, false);
  
  // 輸出 JSON 格式數據
  String jsonOutput = "{";
  jsonOutput += "\"temp\": " + String(temperature, 1) + ", ";
  jsonOutput += "\"humidity\": " + String(humidity, 1) + ", ";
  jsonOutput += "\"heat_index\": " + String(heatIndex, 1) + ", ";
  jsonOutput += "\"count\": " + String(readCount);
  jsonOutput += "}";
  
  Serial.println(jsonOutput);
}

void sendStatus() {
  String statusJson = "{";
  statusJson += "\"status\": \"running\", ";
  statusJson += "\"sensor\": \"" + String(DHTTYPE == DHT11 ? "DHT11" : "DHT22") + "\", ";
  statusJson += "\"pin\": \"A5\", ";
  statusJson += "\"interval_ms\": " + String(READ_INTERVAL) + ", ";
  statusJson += "\"read_count\": " + String(readCount) + ", ";
  statusJson += "\"uptime_ms\": " + String(millis());
  statusJson += "}";
  
  Serial.println(statusJson);
}
