# 📊 葡文新聞 RSS 項目

![Update Status](https://github.com)

呢個專案係一個自動化數據採集工具，專門用嚟爬取澳門嘅三份葡文報紙(Hoje Macau, Jornla Tribunal de Macau, Ponto Final)，並自動更新資料庫同埋產生 RSS 訂閱源。
另外仲會透過Google Tranlsate 翻譯葡文英文對照嘅嘅RSS XML訂閱源，但由於Google Translate API不穩定，所以暫時係本地運行再上載，無將佢自動化。

## 🚀 功能特點
- **自動化更新**：每日透過 GitHub Actions 定時執行腳本。
- **數據持久化**：自動更新資料庫檔案（DB）。
- **RSS 輸出**：產生 XML 檔案，方便即時追蹤數據變動。
- **自動同步**：改動會自動 Commit 同 Push 返去儲存庫。

## 🛠️ 技術棧
- **Python**: 核心爬蟲同數據處理。
- **GitHub Actions**: 定時任務 (Cron Job) 執行平台。
- **Git**: 版本控制同自動化部署。

## 📂 檔案結構
- `update_db.py`: 核心更新邏輯。
- `.github/workflows/`: 自動化任務設定檔。

---
*Last updated by GitHub Actions bot.*
