# 📋 Internal Task Log (內部任務流水號)

> **Auto-generated** from `CHANGELOG.md` history and Git Log (v0.1.0 - v0.5.6).

## 🔢 下一個可用編號

**Next ID: ABP-029**

---

## 📊 Dashboard (狀態總覽)

| 狀態 | 數量 | 說明 |
|------|------|------|
| 🆕 **New** | 0 | 待處理 |
| 🟡 **WIP** | 1 | 進行中 |
| ✅ **Done** | 27 | 已完成 |
| 🛑 **Blocked**| 0 | 被卡住 |
| ❌ **Cancelled**| 0 | 取消 |

---

## 📝 任務列表

| ID | Tag | 標題 (Title) | 狀態 | 優先級 | 負責人 | 版本貢獻 | Context / Details |
|----|-----|--------------|------|--------|--------|----------|-------------------|
| `ABP-001` | Init | 專案初始化 (Python/Arduino/Web) | Done | High | @Sid | v0.1.0 | 包含 27 個新增檔案，建立專案基礎架構 |
| `ABP-002` | Arduino | DHT11 讀取與 JSON Serial 輸出 | Done | High | @Sid | v0.1.0 | `dht_sensor.ino` 初始實作 |
| `ABP-003` | Python | Serial Reader 與資料庫串接 | Done | High | @Sid | v0.1.0 | `serial_reader.py`, `database.py` |
| `ABP-004` | Discord | Webhook 通知系統 | Done | High | @Sid | v0.1.0 | `discord_webhook.py` 初始實作 |
| `ABP-005` | Web | 儀表板 Dashboard 設計 (PWA) | Done | Medium | @Sid | v0.1.0 | `index.html`, `style.css`, `sw.js` |
| `ABP-006` | Hard | RGB LED 空氣品質指示燈 | Done | Medium | @Sid | v0.2.0 | Arduino GRB 腳位修正 (Commit `b791e71`) |
| `ABP-007` | Hard | 蜂鳴器警報與 Serial 指令 | Done | Medium | @Sid | v0.2.0 | 改用 `tone()` 函數 (Commit `b791e71`) |
| `ABP-008` | Discord | Hybrid Commands 支援 | Done | Medium | @Sid | v0.3.0, v0.4.0 | Slash Command + Guild Command (Commit `040456b`) |
| `ABP-009` | Cloud | Render 雲端部署配置 | Done | High | @Sid | v0.4.0 | 含 `render_start.py`, `render.yaml` (多個 Commit 組成) |
| `ABP-010` | Doc | 建立雲端部署教學文件 | Done | Low | @Sid | v0.4.0 | `DEPLOY.md`, `CLOUD_DEPLOY.md` |
| `ABP-011` | Discord | 遠端蜂鳴器控制 (`/buzz`) | Done | Low | @Sid | v0.4.1 | Commit `564bf6f` |
| `ABP-012` | Hard | MQ135 感測器硬體整合 | Done | High | @Sid | v0.5.0 | PPM 數值、sensor card 整合 (Commit `988f8ad`, `b791e71`) |
| `ABP-013` | Web | 1x4 單行版面優化 | Done | Low | @Sid | v0.5.1 | 改 Flex layout (Commit `f892f04`) |
| `ABP-014` | Web | PPM 歷史趨勢圖表 | Done | Medium | @Sid | v0.5.0, v0.5.1 | 圖表新增第三條 PPM 曲線 (Commit `36d374f`) |
| `ABP-015` | Discord | 靜音模式 (`/silent`) | Done | Low | @Sid | v0.5.2 | Arduino 新增 `SILENT_ON/OFF` 指令 (Commit `f01626a`) |
| `ABP-016` | Sync | 雲端同步功能 (Local to Cloud) | Done | High | @Sid | v0.5.3 | `/api/push` endpoint + PPM sync (Commit `3400171`) |
| `ABP-017` | Fix | Arduino 編譯變數重複宣告 | Done | Critical | @Sid | v0.5.4 | Fixes #018, 移除 `currentQuality` 重複宣告 (Commit `8c5fa42`) |
| `ABP-018` | Fix | Windows UTF-8 BOM 環境變數問題 | Done | Critical | @Sid | v0.5.5 | Fixes #019, 改用 `utf-8-sig` 讀取 (Commit `f4dd9de`) |
| `ABP-019` | Task | 還原專案歷史與文件補全 | WIP | Medium | @Bot | v0.6.0 | 本次審計任務 |
| `ABP-020` | Fix | Windows cp950 編碼錯誤 (emoji) | Done | Medium | @Sid | v0.4.0 | Fixes #005, 移除 emoji 輸出 (Commit `bc29f81`) |
| `ABP-021` | Fix | Render Port Binding 失敗 | Done | High | @Sid | v0.4.0 | Fixes #006/#007, 新增 `os.getenv("PORT")` (Commit `abd5633`) |
| `ABP-022` | Fix | Discord Bot 啟動靜默崩潰 | Done | Medium | @Sid | v0.4.1 | Fixes #013, 加入 `traceback.print_exc()` (Commit `5519623`) |
| `ABP-023` | Fix | Simulator 雲端認證失敗 | Done | Critical | @Sid | v0.5.3 | Fixes #016, 修正 Auth Header 格式 (Commit `0f455ef`) |
| `ABP-024` | Fix | 空歷史資料時圖表崩潰 | Done | Low | @Sid | v0.5.5 | Fixes #020, 加入 `if (data.history)` 檢查 (Commit `f4dd9de`) |
| `ABP-025` | Fix | Render 資料夾不存在崩潰 | Done | Medium | @Sid | v0.5.5 | Fixes #017, 確保 `data/` 目錄存在 (Commit `304b548`) |
| `ABP-026` | Fix | AI 模型過期 (gemini-1.5) | Done | Medium | @Sid | v0.5.6 | Fixes #023, 更新為 `gemini-2.5-flash-lite` (Commit `dcd6bdb`) |
| `ABP-027` | Fix | 雲端時區顯示錯誤 | Done | Medium | @Sid | v0.5.5+ | Partial fix #021, Server-side pytz 轉為台北時間 (Commit `6a659c9`) |
| `ABP-028` | Refactor | 資料庫改用 JSON/CSV | Done | Medium | @Sid | v0.1.1 | 取代 SQLite，改為人類可讀格式 (Commit `7b76b64`) |
