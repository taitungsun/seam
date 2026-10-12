# 特殊教育行政管理系統 SEAM

**Special Education Administration & Management · v1.5**

[![Version](https://img.shields.io/badge/version-1.5-blue)](../../releases/latest)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant)
[![Platform](https://img.shields.io/badge/Platform-Browser%20(Offline)-blue)](#技術說明)
[![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-FF5E5B?logo=ko-fi)](https://ko-fi.com/izensun)

SEAM 是一套為**高中職特殊教育教師與特教業務承辦人**設計的離線行政工具。整套系統就是一個 HTML 檔案，用瀏覽器開啟即可使用，不需要安裝、帳號、伺服器或網路連線，所有資料只存在自己的電腦裡。

它的定位介於「校內 IEP」與「特殊教育通報網」之間：把平時散落在多份 Excel 裡的學生、課表、成績與經費資料集中在一處，讓承辦人能快速掌握重要資訊，作為填報與撰寫 IEP 前的工作底稿。

---

## 功能模組

| 模組 | 說明 |
|------|------|
| 總覽 | 學生名單（含障礙類別、導師、輔導教師，一鍵快速檢視）、學生分布統計、年度經費執行率、待辦事項；身心障礙證明 90 天內到期自動提醒 |
| 學生資料 | 學生名冊依年級→班別→座號排序，可依科別、班級、類別篩選；保留畢業國中與入學管道供轉銜追蹤；學籍異動與歷屆封存；去識別化名冊 PDF 匯出 |
| 分組課表 | 課程分組（含學生名單）與教師課表分開管理，支援 PDF 匯出 |
| 成績管理 | 依科目建立成績表，可設定定期評量次數與加權比例；從名冊勾選匯入學生；原住民學生依年級標示及格標準（40／50／60 分）；成績冊列印 |
| 經費管理 | 多年度、多計畫經費追蹤，自動計算執行率與餘額，呈現歷年執行趨勢 |
| IEP 匯出 | 上傳 IEP .odt 模板，自動帶入 20 項學生資料（姓名、特教類別、鑑定文號等），可單筆或批次匯出 |
| 系統設定 | 學校基本資訊、科系設定、IEP 模板管理、資料使用量顯示 |

---

## 快速開始

1. 到 [Releases](../../releases) 下載最新版的 `SEAM_v1.5.html`（若要使用 IEP 匯出，請一併下載 `個別化教育計畫_模板.odt`，下載後的檔名是 `IEP_template.odt`）。
2. 用瀏覽器開啟 `SEAM_v1.5.html`。建議使用 Chrome 或 Edge，PDF 匯出的相容性最好。
3. 首次開啟時到「系統設定」填寫學校全名、簡稱、班型名稱與科系清單，儲存後即可開始使用。
4. 若要匯出 IEP，請在「系統設定 → IEP 模板管理」上傳模板。

---

## 資料備份與還原

所有資料存放在瀏覽器的 `localStorage`。**清除瀏覽器資料或更換電腦都會讓資料消失**，請養成定期備份的習慣。

| 操作 | 方式 |
|------|------|
| 備份 | 左側欄「⤓ 匯出系統備份」，儲存 `.json` 檔 |
| 還原 | 左側欄「⤒ 匯入系統備份」，選取備份的 `.json` 檔 |
| 僅匯入經費 | 匯入格式為 `{"__importType":"budgetOnly", ...}` 的 JSON，只更新經費資料，不影響學生與課表 |
| 清除資料 | 左側欄「↺ 清除所有資料」，恢復初始狀態（無法復原，請先備份） |

**升級版本時**：在同一台電腦、同一個瀏覽器開啟新版，通常會沿用原本的資料；但部分瀏覽器會依檔案存放位置分開儲存。請在升級前先匯出備份，若新版中看不到資料，再用「匯入系統備份」還原即可。

---

## 技術說明

- **架構**：單一 HTML 檔，原生 JavaScript，不依賴任何框架
- **內嵌套件**：JSZip（用於產生 IEP .odt 檔），已內建於檔案中，離線可用
- **儲存**：瀏覽器 `localStorage`（約 5 MB；系統設定頁可查看目前用量）
- **字體**：Noto Serif TC／Noto Sans TC，透過 Google Fonts 載入；離線時自動改用系統字體
- **隱私**：資料只存在使用者本機，不會傳送到任何伺服器

---

## 版本資訊

- 目前版本：**V1.5**
- 詳細版本更新內容請見 [Releases](../../releases)

---

## 授權

本系統採用 [創用 CC 姓名標示-非商業性-相同方式分享 4.0 國際授權條款（CC BY-NC-SA 4.0）](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant)。

- **姓名標示**：使用或改作時，須標示原作者。
- **非商業性**：不得用於商業目的。
- **相同方式分享**：改作後再散布，須採用相同授權條款。

完整條款請見 [LICENSE](LICENSE)。

---

## 支持開發

如果這個工具對您有幫助，歡迎透過 Ko-fi 請我喝杯咖啡

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/izensun)

---

## 作者

Designed by [@izensun](https://mastodon.social/@izensun)
Built with [Claude](https://claude.ai) (Anthropic)
