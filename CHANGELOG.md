# Changelog

本專案的所有重大變更都將記錄在此文件中。

格式基於 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
且本專案遵守 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 語意化版本規範。

> **注意**: Issue 編號 (`#`) 代表 GitHub Issues/Bugs。Task 編號 (`ABP-`) 代表內部任務 (Internal Tasks)。

## [Unreleased]

---

## [0.5.8] - 2025-12-22
### Changed
- **Doc**: 將 Issue 編號與 GitHub Issues 同步 (#005 - #037)
- **Doc**: 修正 `ISSUES.md` 編號錯誤 (#038 → #034) 並統一編號格式

---

## [0.5.7] - 2025-12-22
### Added
- **Doc**: 專案歷史重建 (Project History Reconstruction) (ABP-019)
- **Doc**: 實作 `ISSUES.md` 與 `TASK_LOG.md`
- **Meta**: 初始化 Issue 編號體系

---

## [0.5.6] - 2025-12-21
### Fixed
- **AI**: Gemini 1.5 模型已棄用/找不到，更新至 `gemini-2.5-flash-lite` (Fixes #023)

## [0.5.5] - 2025-12-10
### Fixed
- **Config**: 修復因 Windows UTF-8 BOM 導致 `.env` 讀取失敗的問題 (ABP-018) (Fixes #019)

## [0.5.4] - 2025-12-10
### Fixed
- **Arduino**: 解決 `currentQuality` 重複宣告的編譯錯誤 (ABP-017) (Fixes #018)
- **Web**: 修復無歷史資料時圖表導致前端崩潰的問題 (Fixes #020)

## [0.5.3] - 2025-12-09
### Added
- **Cloud**: 實作地端至雲端資料同步功能 (`cloud_sync.py`) (ABP-016)
- **Security**: 為同步端點 (Sync Endpoint) 增加基礎 API Key 驗證

### Fixed
- **Bug**: 修正模擬器 (Simulator) 未發送正確 Auth Header 導致雲端驗證失敗的問題 (Fixes #016)

## [0.5.2] - 2025-12-09
### Added
- **Discord**: 新增 `/silent` 靜音模式以關閉蜂鳴器通知 (ABP-015)

## [0.4.1] - 2025-12-06
### Added
- **Discord**: 新增 `/buzz` 指令以支援遠端蜂鳴器控制 (ABP-011)

### Fixed
- **Discord**: 修復 Bot 啟動時發生 Silent Crash (無 Log) 的問題 (Fixes #013)

## [0.5.1] - 2025-12-09
### Added
- **Web**: 行動版優化的全新 1x4 單行卡片版面 (ABP-013)
- **Web**: PPM (空氣品質) 歷史趨勢圖表 (ABP-014)

## [0.5.0] - 2025-12-09
### Added
- **Hardware**: MQ135 氣體感測器整合 (讀取 PPM 數值) (ABP-012)
- **Python**: 增強 `serial_reader.py` 以解析第四個數值 (Air Quality)

### Fixed
- **Security**: 移除工具腳本中的硬編碼絕對路徑 (Fixes #014)

## [0.4.0] - 2025-12-05
### Added
- **Cloud**: Render 雲端部署配置 (`render.yaml`) (ABP-009)
- **Doc**: 雲端部署教學文件 (ABP-010)

### Fixed
- **Build**: 修復 Render 上找不到 `requirements.txt` 路徑的問題 (Fixes #006)
- **Deploy**: 修復端口綁定 (Port Binding) 錯誤 (改用 `$PORT`) (Fixes #007)

## [0.3.0] - 2025-12-01
### Added
- **Discord**: 遷移至 Hybrid Commands (Slash Commands) 支援 (ABP-008)

### Fixed
- **Bugs**: 修復指令處理中的競爭條件 (Race conditions)

## [0.2.0] - 2025-11-25
### Added
- **Feature**: RGB LED 狀態指示燈 (ABP-006)
- **Feature**: 蜂鳴器警報邏輯 (> 30°C) (ABP-007)

### Fixed
- **Windows**: 修復 `cp950` 編碼導致 Emoji 輸出崩潰的問題 (Fixes #005)

## [0.1.0] - 2025-11-20
### Added
- **Init**: 專案結構初始化 (ABP-001)
- **Arduino**: DHT11 讀取與 JSON Serial 輸出 (ABP-002)
- **Python**: Serial Monitor 與 SQLite/JSON 資料庫 (ABP-003)
- **Discord**: 基礎 Webhook 通知 (ABP-004)
- **Web**: Flask 儀表板初版發布 (ABP-005)

### Known Issues
- 藍牙 HC-05 連線不穩定 (Won't Fix #001)
