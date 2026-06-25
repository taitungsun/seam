# 特殊教育行政管理系統

**Special Education Administration & Management (SEAM) · v1.2**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgreen.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude-orange.svg)](https://claude.ai)
![Platform](https://img.shields.io/badge/Platform-Browser%20%28Offline%29-blue)
[![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-FF5E5B?logo=ko-fi)](https://ko-fi.com/izensun)

SEAM 是一套專為**高中職特殊教育教師**設計的免安裝行政管理工具，以單一 HTML 檔案發布，開啟即用，資料存於本機瀏覽器，無需帳號、伺服器或網路連線。

---

## 功能模組

| 模組 | 說明 |
|------|------|
| 學生資料 | 建立完整學生名冊；支援鑑定資料、家庭背景、身心障礙證明等欄位（對應特教通報網）；到期提醒、快速查看、IEP 草稿匯出、去識別化 PDF 匯出 |
| IEP 匯出 | 上傳含佔位符的 `.odt` 模板後，一鍵下載預填學生基本資料的 IEP 草稿文件（支援 30 個佔位符） |
| 分組課表 | 課程分組（含學生名單）與教師課表分開管理，節次時間預設帶入，支援 PDF 匯出 |
| 成績管理 | 依科目建立成績表，自動計算日常考查 40% 與定期評量 60%，與學生名冊連動同步 |
| 經費管理 | 多年度、多計畫經費追蹤，自動計算執行率與餘額 |
| 待辦事項 | 整合自訂待辦與身心障礙證明到期通知 |
| 系統設定 | 設定學校名稱、班型、科系清單、IEP 模板，套用至所有頁面標題與匯出報表 |

---

## 快速開始

**1. 下載檔案**

至 [Releases](../../releases) 頁面下載最新版 `SEAM_v1.2.html`，或直接 Clone 本儲存庫。

**2. 開啟系統**

以瀏覽器（Chrome、Edge、Firefox、Safari）開啟 `SEAM_v1.2.html`，不需要任何安裝步驟。

> 建議使用 Chrome 或 Edge 以獲得最佳相容性，尤其是 PDF 匯出功能。

**3. 初次設定**

首次開啟時，系統會自動引導至「系統設定」頁，請填寫：
- 學校全名（例：國立臺東高級商業職業學校）
- 學校簡稱（例：臺東高商）— 用於側欄與報表顯示
- 特殊教育班班型（例：分散式資源班）
- 科系清單（系統預設高職常見科系，可自行新增或刪除）

填寫完畢後點選「儲存所有設定」，即可開始使用各功能模組。

---

## 資料備份與還原

SEAM 將所有資料存於瀏覽器的 `localStorage`，**清除瀏覽器資料可能導致資料遺失**，請定期備份。

| 操作 | 方式 |
|------|------|
| **備份** | 左側欄 →「匯出完整備份」→ 儲存 `.json` 檔案至本機 |
| **還原** | 左側欄 →「匯入備份檔」→ 選取備份的 `.json` 檔案 |
| **僅匯入經費** | 同上，選取格式為 `{"__importType":"budgetOnly", ...}` 的 JSON，只更新經費資料，學生與課表不受影響 |
| **清除資料** | 左側欄 →「清除所有資料」→ 恢復出廠預設 |

---

## 匯出格式

各模組支援的匯出格式如下：

- **PDF**：透過瀏覽器列印功能（Ctrl+P / Cmd+P）產生，可選擇「另存為 PDF」。適用於學生去識別化名冊、成績表、教師課表。
- **CSV**：學生名冊可匯出 CSV 供 Excel 開啟進行進一步處理。
---

## 技術說明

- **架構**：純前端 Vanilla JavaScript，無任何框架或外部套件依賴
- **儲存**：瀏覽器 `localStorage`（上限約 5–10 MB，一般使用綽綽有餘）
- **字體**：Noto Serif TC / Noto Sans TC（透過 Google Fonts CDN 載入，初次開啟需網路；離線時退回系統字體）
- **隱私**：所有資料僅存於使用者本機，不傳送至任何伺服器

---

## 適用對象

本系統設計適用對象為國教署轄署高中職特殊教育教師，主要功能對應以下實務需求：

- 普通班身心障礙生輔導經費結報管理
- 資源班課程分組與教師排課
- IEP 相關學生資料管理與歷屆追蹤

各縣市國中小或其他階段學校亦可自行調整科系設定後使用。

---

## 授權

本系統採 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 授權。您可自由使用、修改與散布，惟需保留原始作者署名，且不得用於商業目的，衍生作品須以相同授權條款發布。

---

## 支持開發

如果這個工具對您有幫助，歡迎透過 Ko-fi 請我喝杯咖啡 ☕

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/izensun)
