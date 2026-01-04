---
post_title: 'MEXC V3 Context7 設計與規劃'
author1: 'ac484'
post_slug: 'mexc-v3-context7-design'
microsoft_alias: 'na'
featured_image: ''
categories: ['architecture']
tags: ['mexc', 'context7', 'ddd', 'fastapi']
ai_note: 'Generated with assistance from GitHub Copilot.'
summary: '設計以 Context7 查詢 MEXC V3 API 並符合 DDD 邊界的規劃文件與資料結構。'
post_date: '2026-01-04'
---

## 目標與範圍
- 用 Context7 取得並校驗 MEXC V3 API 規格，形成可重複更新的資料來源。
- 全程遵守 `.github/Boundary.md` 的分層與 async context 管理要求。
- 與 `qrl_usdt_trading_domain.md` 的 VO、事件、實體對齊，作為實作藍圖。

## Context7 查詢工作流
1) `resolve-library-id` 搜尋「mexc api v3」。  
2) `get-library-docs` 抽取 REST/WS 端點、簽名、速率限制、錯誤碼。  
3) 對應到 Infrastructure Ports（回傳 primitives），Application 轉 VO/Entities。  
4) Markdown 紀錄來源版本與拉取時間，供差異比對。

## 分層落地計畫
- Interface：僅處理 DTO/路由與 HTTP/Task 入口，不進行交易決策。
- Application：為每個 MEXC 功能提供 Use Case，內部 `async with mexc_client`。
- Domain：擴充 VO/Events 以覆蓋手續費、滑點、曝險、訂單狀態，保持純 Python 驗證。
- Infrastructure：`infrastructure/external/mexc` 客戶端與端點定義，簽名、重試、速率限制，回傳 primitives。

## MEXC V3 覆蓋清單（優先級）
1. 現貨交易：下單、查單、撤單、訂單列表、成交明細。  
2. 資金餘額：帳戶餘額、資產列表。  
3. 行情：深度、Ticker、Kline、24h 統計。  
4. 系統：時間同步、速率限制檢查與錯誤碼映射。  
5. WebSocket：Ticker/Kline/訂單回報的連線與自動重連策略。

## 文件與程式結構樹（規劃稿）
```
docs/
  mexc-context7-design.md        # 本文件
  api/
    mexc-v3-rest.md             # REST 端點摘要與欄位對應（後續拉取 Context7 後生成）
    mexc-v3-ws.md               # WS 訂閱與事件格式
  architecture/
    usecases.md                 # Interface→Application→Domain 對應表
    vo-mapping.md               # MEXC 回傳欄位 → VO/Entity 映射
src/app/
  interfaces/
    http/                       # 僅 DTO/路由
    tasks/                      # Scheduler/Jobs 入口
  application/
    market/                     # 行情 Use Cases
    trading/                    # 下單/撤單 Use Cases（管理 async context）
    account/                    # 餘額查詢 Use Cases
  domain/
    value_objects/              # Symbol/Price/Quantity/Slippage/TickSize/StepSize...
    aggregates/                 # Order/Position/Portfolio/Bot
    events/                     # OrderPlaced/OrderFilled/BalanceUpdated...
  infrastructure/
    external/mexc/
      client.py                 # MEXC REST/WS Client（簽名、重試、速率限制）
      endpoints.py              # 端點/路徑/簽名需求定義（primitives）
      websocket.py              # WS 連線管理與事件解析（primitives）
```

## 風險與緩解
- API 版本差異：記錄 Context7 抓取日期並預留 endpoint 版本欄位。  
- 速率限制：Infrastructure 實作退避；Application 暴露錯誤類型供上層處理。  
- VO 驗證：在 Domain 使用 dataclass + Decimal，避免浮點誤差。  
- 長度限制：拆分子文件，保持單檔 < 4000 chars。

## 下一步（未排程）
- 透過 Context7 拉取最新 MEXC V3 端點並生成 `docs/api/mexc-v3-rest.md`、`docs/api/mexc-v3-ws.md`。
- 為優先端點撰寫 VO 映射表與 Use Case 條目。
- 補充 WebSocket 事件流時序與錯誤恢復流程。
