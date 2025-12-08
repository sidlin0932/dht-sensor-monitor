# 📋 Changelog

本專案的所有重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
並遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [0.1.0] - 2025-12-08 14:24

### 🎉 首次發布

#### 新增功能
- **Arduino 感測器程式**
  - DHT11/22 溫濕度讀取
  - JSON 格式 Serial 輸出
  - 支援手動指令（READ、STATUS、PING）
  - 可設定讀取間隔

- **Python 後端系統**
  - Serial 通訊模組（自動偵測 Arduino）
  - SQLite 資料庫儲存歷史數據
  - Discord Webhook 通知（含美觀 Embed）
  - Discord Bot 互動指令
  - Flask Web API 伺服器
  - 異常警告功能
  - 感測器模擬器（simulator.py）

- **Discord 整合**
  - Webhook 定時推送溫濕度
  - Bot 指令：`!now`、`!history`、`!stats`、`!chart`、`!status`
  - 溫濕度異常自動警告
  - 系統啟動/關閉通知

- **網頁儀表板**
  - 即時溫濕度顯示
  - 趨勢指示器
  - 舒適度評估
  - 24 小時統計
  - Chart.js 歷史圖表
  - 深色主題 + 毛玻璃效果
  - 響應式設計
  - **PWA 支援（可安裝到手機）**

- **文件**
  - 完整 README
  - 接線圖說明
  - 安裝設定指南

---

## 版本規劃

### [0.2.0] - 計畫中
- [ ] 新增多感測器支援
- [ ] 新增數據匯出功能（CSV）
- [ ] 新增儀表板更多圖表類型

### [0.3.0] - 計畫中
- [ ] ESP32 獨立運作版本
- [ ] 手機 APP 通知
- [ ] 雲端數據同步
