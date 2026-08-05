# Onboarding：怎麼開一個新的 Claude session 接手這個專案

## 快速開始

1. 開新的 Claude 對話 / session。
2. 確認工作目錄指向 `/Users/ling/Desktop/project`(或至少是 `webapp/` 這個子目錄)。
3. 跟它說一句類似「幫我看一下這個 MiniERP 專案」就好——它會自動讀到：
   - 專案根目錄的 [`CLAUDE.md`](CLAUDE.md) / [`SKILL.md`](SKILL.md)：SQL Server 教學用資料庫
     `biz00` 與練習用的 `lalala`(FK 補建練習)。
   - [`webapp/CLAUDE.md`](webapp/CLAUDE.md) / [`webapp/SKILL.md`](webapp/SKILL.md)：候糖主題
     MiniERP 網頁版(Flask + SQL Server),架構、schema、業務規則、部署方式都寫在裡面。

這兩組文件的目的就是讓新 session 不需要額外解釋就能掌握專案架構、規則、怎麼跑、密碼機制等等。

## 文件裡沒寫、但新 session 可能需要的東西

- **本機測試用的共用登入密碼**：機制寫在 `webapp/CLAUDE.md` 的 Access control
  章節與 `webapp/SKILL.md` 的 Run the app 章節(`Config.SITE_PASSWORD`,從 `.env`
  讀,`hmac.compare_digest` 比對),但實際密碼值刻意不寫進任何有進 git 的檔案。
  新 session 若要在本機實際測試登入,請直接讀 `webapp/.env`(該檔案存在但不在 git
  裡,所以新 session 除非主動去讀,不會自動知道)。

## 待補

目前只確認了「本機測試密碼」這一項不在文件裡。原始草稿提到「兩件事」但第二件事的內容還沒補上——之後想到時再補進這份文件。
