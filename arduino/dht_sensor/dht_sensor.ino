/*
 * DHT 溫濕度感測器 + RGB LED + 蜂鳴器
 * 生物機電工程概論 期末專題 v0.2.0
 * 
 * 功能：
 *   - 讀取 DHT11/22 感測器數據
 *   - RGB LED 顯示空氣品質狀態
 *   - 蜂鳴器在空氣品質差時警報
 *   - 透過 Serial 傳送數據到電腦
 * 
 * 接線說明：
 *   DHT VCC  → Arduino 5V
 *   DHT GND  → Arduino GND
 *   DHT DATA → Arduino A5
 * 
 *   RGB LED:
 *     R → D9  (PWM)
 *     G → D10 (PWM)
 *     B → D11 (PWM)
 *     共陰極 → GND
 * 
 *   蜂鳴器:
 *     正極 → D8
 *     負極 → GND
 */

#include <DHT.h>

// ========== 感測器設定 ==========
#define DHTPIN A5           // DHT 感測器資料腳位
#define DHTTYPE DHT11       // DHT11 或 DHT22

// ========== RGB LED 設定 ==========
#define LED_R 9             // 紅色 LED (PWM)
#define LED_G 10            // 綠色 LED (PWM)
#define LED_B 11            // 藍色 LED (PWM)

// ========== 蜂鳴器設定 ==========
#define BUZZER_PIN 8        // 蜂鳴器腳位

// ========== 時間設定 ==========
#define READ_INTERVAL 60000 // 讀取間隔（毫秒）
#define BAUD_RATE 9600      // Serial 通訊速率

// ========== 空氣品質閾值 ==========
// 舒適範圍：溫度 20-28°C，濕度 40-70%
#define TEMP_GOOD_MIN 20.0
#define TEMP_GOOD_MAX 28.0
#define TEMP_BAD_MIN 15.0
#define TEMP_BAD_MAX 35.0

#define HUMIDITY_GOOD_MIN 40.0
#define HUMIDITY_GOOD_MAX 70.0
#define HUMIDITY_BAD_MIN 20.0
#define HUMIDITY_BAD_MAX 85.0

// ==============================

// 空氣品質等級
enum AirQuality {
  QUALITY_GOOD,    // 綠色
  QUALITY_NORMAL,  // 藍色
  QUALITY_BAD      // 紅色 + 蜂鳴器
};

// 初始化 DHT 感測器
DHT dht(DHTPIN, DHTTYPE);

// 變數
unsigned long lastReadTime = 0;
unsigned long readCount = 0;
AirQuality currentQuality = QUALITY_NORMAL;

void setup() {
  // 初始化 Serial 通訊
  Serial.begin(BAUD_RATE);
  
  // 初始化 DHT 感測器
  dht.begin();
  
  // 初始化 RGB LED
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  
  // 初始化蜂鳴器
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // 開機燈光測試
  testLED();
  
  // 等待感測器穩定
  delay(2000);
  
  // 設為藍色（待機）
  setRGB(0, 0, 255);
  
  // 啟動訊息
  Serial.println("{\"status\": \"ready\", \"version\": \"0.2.0\", \"sensor\": \"" + 
                 String(DHTTYPE == DHT11 ? "DHT11" : "DHT22") + 
                 "\", \"features\": [\"rgb_led\", \"buzzer\"]}");
  
  // 立即讀取一次
  readAndSendData();
}

void loop() {
  unsigned long currentTime = millis();
  
  // 定時讀取
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    readAndSendData();
  }
  
  // 處理 Serial 指令
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "READ") {
      readAndSendData();
    } else if (command == "STATUS") {
      sendStatus();
    } else if (command == "PING") {
      Serial.println("{\"pong\": true}");
    } else if (command == "TEST_LED") {
      testLED();
    } else if (command == "BUZZER_OFF") {
      digitalWrite(BUZZER_PIN, LOW);
    }
  }
}

void readAndSendData() {
  // 讀取感測器
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  readCount++;
  
  // 檢查讀取結果
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("{\"error\": \"Failed to read from DHT sensor\", \"count\": " + String(readCount) + "}");
    // 讀取失敗閃爍紅燈
    blinkRGB(255, 0, 0, 3);
    return;
  }
  
  // 計算體感溫度
  float heatIndex = dht.computeHeatIndex(temperature, humidity, false);
  
  // 判斷空氣品質
  AirQuality quality = evaluateAirQuality(temperature, humidity);
  currentQuality = quality;
  
  // 設定 LED 顏色
  updateLED(quality);
  
  // 處理蜂鳴器
  if (quality == QUALITY_BAD) {
    buzz(3);  // 警報 3 次
  }
  
  // 輸出 JSON
  String qualityStr = (quality == QUALITY_GOOD) ? "good" : 
                      (quality == QUALITY_NORMAL) ? "normal" : "bad";
  
  String jsonOutput = "{";
  jsonOutput += "\"temp\": " + String(temperature, 1) + ", ";
  jsonOutput += "\"humidity\": " + String(humidity, 1) + ", ";
  jsonOutput += "\"heat_index\": " + String(heatIndex, 1) + ", ";
  jsonOutput += "\"quality\": \"" + qualityStr + "\", ";
  jsonOutput += "\"count\": " + String(readCount);
  jsonOutput += "}";
  
  Serial.println(jsonOutput);
}

AirQuality evaluateAirQuality(float temp, float humidity) {
  // 判斷是否在舒適範圍內
  bool tempGood = (temp >= TEMP_GOOD_MIN && temp <= TEMP_GOOD_MAX);
  bool tempBad = (temp < TEMP_BAD_MIN || temp > TEMP_BAD_MAX);
  
  bool humidityGood = (humidity >= HUMIDITY_GOOD_MIN && humidity <= HUMIDITY_GOOD_MAX);
  bool humidityBad = (humidity < HUMIDITY_BAD_MIN || humidity > HUMIDITY_BAD_MAX);
  
  // 判斷品質
  if (tempBad || humidityBad) {
    return QUALITY_BAD;     // 紅色
  } else if (tempGood && humidityGood) {
    return QUALITY_GOOD;    // 綠色
  } else {
    return QUALITY_NORMAL;  // 藍色
  }
}

void setRGB(int r, int g, int b) {
  analogWrite(LED_R, r);
  analogWrite(LED_G, g);
  analogWrite(LED_B, b);
}

void updateLED(AirQuality quality) {
  switch (quality) {
    case QUALITY_GOOD:
      setRGB(0, 255, 0);    // 綠色
      break;
    case QUALITY_NORMAL:
      setRGB(0, 0, 255);    // 藍色
      break;
    case QUALITY_BAD:
      setRGB(255, 0, 0);    // 紅色
      break;
  }
}

void blinkRGB(int r, int g, int b, int times) {
  for (int i = 0; i < times; i++) {
    setRGB(r, g, b);
    delay(200);
    setRGB(0, 0, 0);
    delay(200);
  }
}

void testLED() {
  // 紅
  setRGB(255, 0, 0);
  delay(500);
  // 綠
  setRGB(0, 255, 0);
  delay(500);
  // 藍
  setRGB(0, 0, 255);
  delay(500);
  // 關閉
  setRGB(0, 0, 0);
}

void buzz(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

void sendStatus() {
  String qualityStr = (currentQuality == QUALITY_GOOD) ? "good" : 
                      (currentQuality == QUALITY_NORMAL) ? "normal" : "bad";
  
  String statusJson = "{";
  statusJson += "\"status\": \"running\", ";
  statusJson += "\"version\": \"0.2.0\", ";
  statusJson += "\"sensor\": \"" + String(DHTTYPE == DHT11 ? "DHT11" : "DHT22") + "\", ";
  statusJson += "\"pin\": \"A5\", ";
  statusJson += "\"interval_ms\": " + String(READ_INTERVAL) + ", ";
  statusJson += "\"read_count\": " + String(readCount) + ", ";
  statusJson += "\"current_quality\": \"" + qualityStr + "\", ";
  statusJson += "\"uptime_ms\": " + String(millis());
  statusJson += "}";
  
  Serial.println(statusJson);
}
