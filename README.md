# tw-industry-chain 台灣產業價值鏈 · 關係網路圖

互動式力導向網路圖，資料來自櫃買中心「產業價值鏈資訊平台」（ic.tpex.org.tw）。
純靜態架構：stdlib-only Python 爬蟲 + vanilla HTML/CSS/JS，無任何第三方依賴、無 build step。

## 檔案結構

```
├── index.html                    # 圖形引擎（多產業切換、Logo、tooltip、側欄關聯）
├── build.py                      # 爬蟲：產出 data/chains.js
├── data/
│   ├── chains.js                 # window.CHAIN_DATA（初始含太空衛星科技種子資料）
│   └── domains.json              # 台灣公司官網域名快取（build.py 自動維護，可手動修正）
└── .github/workflows/update.yml  # 每週一 UTC 00:00 自動更新
```

## 部署步驟

1. 建立 GitHub repo，推上以上檔案
2. Settings → Pages → Deploy from branch → main / root
3. Settings → Actions → General → Workflow permissions → 勾選 "Read and write permissions"
4. Actions 頁手動觸發一次 `weekly-update` 確認可運作

## build.py 用法

```
python build.py                 # 只更新預設清單（4100 太空衛星科技）
python build.py --all           # 探索並更新全部產業鏈（首次約 40+ 次請求）
python build.py --ic 4100 D000  # 指定 ic 代碼
python build.py --dump          # 原始 HTML 存到 debug/ 供除錯
python build.py --no-domains    # 跳過台灣公司官網域名抓取
```

## 設計說明

- **增量更新**：解析失敗的產業保留舊資料，不會讓網站開天窗
- **域名快取**：台灣公司官網域名只抓一次，每次執行最多新抓 60 家（`MAX_DOMAIN_FETCH_PER_RUN`），逐週收斂；`data/domains.json` 可手動修正錯誤域名
- **Logo**：前端以 `https://www.google.com/s2/favicons?domain=<域名>&sz=64` 顯示公司官網 favicon；無域名時退回「色圓 + 名稱首字」，顏色依市場別（上市金/上櫃橘/興櫃紅/外國灰藍）

## 已知限制與除錯

- `parse_chain` 依賴頁面的線性文字結構（細項標籤「(N家)」計數對齊公司表、「共N家」關閉環節），已針對 ic=4100 實際結構設計並通過模擬測試；**其他產業鏈若解析異常**，執行 `python build.py --ic <代碼> --dump`，將 `debug/chain_<代碼>.html` 與錯誤訊息貼給 Claude 調整解析規則
- 台灣公司域名抓取採啟發式（公司基本資料頁第一個外部連結），少數公司可能誤判，直接改 `data/domains.json` 即可
- Google favicon 服務在少數公司網域無圖示時會回傳預設地球圖，屬正常現象
