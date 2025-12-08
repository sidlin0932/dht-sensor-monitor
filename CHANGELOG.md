# 📋 Changelog

本專案的所有重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
並遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## 🗺️ Roadmap (版本規劃)

- [ ] **[0.4.0]** ESP32 獨立運作版本
- [ ] **[0.5.0]** 手機 APP 通知 (Native/Flutter)
- [ ] **[0.6.0]** 雲端數據同步架構優化

---

##  [Unreleased]

### 🚧 正在進行中
- 優化 Arduino 錯誤處理機制
- ESP32 獨立運作版本開發

---

## [0.4.0] - 2025-12-08 23:10

### ☁️ Render 雲端部署

#### 新增功能
- **Render 雲端部署支援**
  - 建立 `render.yaml` 配置檔（Blueprint）
  - 建立 `render_start.py` 雲端啟動腳本
  - 支援兩種模式：
    - `--web-only`：僅 Web 伺服器（等待外部數據推送）
    - 無參數：完整系統（自動產生模擬數據）
  - 整合 Discord Bot、Webhook 和模擬數據產生器
  - 每 30 秒產生一筆模擬數據
  - 每 5 筆數據發送一次到 Discord

- **Discord Bot 優化**
  - 改用 **Guild Commands**（非 Global Commands）
  - 新增 `DISCORD_GUILD_ID` 環境變數支援
  - Guild Commands 立即生效（不需等待 1 小時）
  - 修正 `app_commands` import 問題

- **環境變數配置**
  - `config.py` 的 `WEB_HOST` 和 `WEB_PORT` 支援環境變數覆蓋
  - 更新 `.env.example` 加入雲端部署範例
  - 支援從環境變數讀取所有配置

- **文件**
  - 建立 `docs/CLOUD_DEPLOY.md` 完整雲端部署教學
  - 包含 Render 設定、UptimeRobot 設定、架構說明
  - 三種 Start Command 方案說明
  - 環境變數設定指南

#### 修復
- 修正 Render 無法找到 `requirements.txt` 的路徑問題
- 修正應用程式提前退出的問題（端口綁定）
- 修正 Discord Bot 在雲端環境的執行問題

#### 變更
- 部署架構改為混合模式：本地收集數據 + 雲端顯示

---

## [0.3.0] - 2025-12-08 17:35

### ⚡ Discord Hybrid Commands

#### 新增功能
- **Hybrid Commands 支援**
  - 支援 Slash Commands (`/`) 與傳統前綴指令 (`!`) 並存
  - 指令自帶說明與參數提示
  - 支援的指令：
    - `/now`：查詢目前數據
    - `/history [hours]`：查詢歷史紀錄
    - `/stats [hours]`：查詢統計
    - `/chart [hours]`：生成圖表
    - `/status`：系統狀態
  - 自動同步指令至 Discord (`setup_hook` 機制)

---

## [0.2.0] - 2025-12-08 15:04

### 🎨 RGB LED + 蜂鳴器警報

#### 新增功能
- **RGB LED 空氣品質指示**
  - 🟢 綠色：空氣品質良好（溫度 20-28°C，濕度 40-70%）
  - 🔵 藍色：空氣品質普通
  - 🔴 紅色：空氣品質差

- **蜂鳴器警報**
  - 空氣品質差時自動發出警報
  - 可透過指令關閉：`BUZZER_OFF`

- **新增 Arduino 指令**
  - `TEST_LED`：測試 RGB LED
  - `BUZZER_OFF`：關閉蜂鳴器

#### 硬體變更
- **新增接線**
  - RGB LED：D9 (R)、D10 (G)、D11 (B)
  - 蜂鳴器：D8

---

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
  - JSON/CSV 資料儲存
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
