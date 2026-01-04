# 🔹 標準 DDD 分層對齊模板

## 1️⃣ Interface Layer（接口層 / Adapter Layer）

**責任**：

* 接收外部請求（REST / Websocket / CLI / Scheduler）
* 輸入驗證、DTO 轉換
* 呼叫 Application Service / Use Case
* 將結果包裝成輸出 DTO / Response

**典型位置**：

```
interfaces/http/
interfaces/tasks/
interfaces/websocket/
interfaces/cli/
```

**範例檔案**：

* `interfaces/http/order_routes.py`
* `interfaces/tasks/rebalance.py`
* `interfaces/http/test_orders.py`（重構後只呼叫 Application Service）

**行為規則**：

* 不做業務計算
* 不直接呼叫 Infrastructure
* 只做 Input → DTO → Application → Response

---

## 2️⃣ Application Layer（應用層 / Use Case Layer）

**責任**：

* 協調 Domain 行為
* 調用 Domain Aggregates / Domain Service / Ports
* 提供 Use Case 接口給 Interface Layer
* 不包含具體業務規則細節（放在 Domain）

**典型位置**：

```
application/trading/
application/account/
application/market/
```

**範例檔案**：

* `application/trading/execute_trade_usecase.py`
* `application/account/get_balance.py`
* `application/market/sync_price.py`

**行為規則**：

* 可以調用多個 Domain Aggregates
* 可以調用 Repository / Infrastructure Port
* 不直接操作 DB / Redis / 外部 API
* 不包含業務規則算法（交給 Domain）

---

## 3️⃣ Domain Layer（領域層 / 核心業務）

**責任**：

* 定義業務核心概念
* 封裝業務規則
* 提供不變性、行為與規則（Aggregate / Entity / Value Object / Domain Service）
* Domain Events

**典型位置**：

```
domain/aggregates/
domain/models/
domain/value_objects/
domain/events/
domain/strategies/
domain/risk/
domain/ports/  ← Domain 與 Infrastructure 依賴反轉介面
```

**範例檔案**：

* `domain/aggregates/order.py`（Aggregate Root）
* `domain/value_objects/price.py`（Value Object）
* `domain/models/trade.py`（Entity）
* `domain/events/trading_events.py`
* `domain/strategies/base.py`（策略規則）
* `domain/ports/trade_port.py`（Domain 呼叫 Infrastructure Port）

**行為規則**：

* 所有業務規則放這裡
* 不直接呼叫 Infrastructure
* Application Service 透過 Aggregate / Domain Service 呼叫

---

## 4️⃣ Infrastructure Layer（基礎設施 / Adapter Implementation）

**責任**：

* 實作 Domain Layer 定義的 Port / Repository
* 提供外部系統連接（DB、Redis、API、Message Broker）
* 不包含業務邏輯（只做資料持久化或外部交互）

**典型位置**：

```
infrastructure/persistence/
infrastructure/external/
infrastructure/config/
infrastructure/bot_runtime/
infrastructure/supabase/
```

**範例檔案**：

* `infrastructure/persistence/repos/trade_repository.py`
* `infrastructure/external/mexc/client.py`
* `infrastructure/persistence/redis/cache.py`

**行為規則**：

* 實作 Repository / Port
* 提供 Infrastructure API 給 Application / Domain 使用
* 不直接處理 Domain 行為邏輯

---

## 5️⃣ 典型依賴方向（箭頭示意）

```text
┌───────────────┐
│ Interface      │
│ (HTTP / WS)    │
└───────┬───────┘
        │ calls
┌───────▼───────┐
│ Application    │
│ Use Cases      │
└───────┬───────┘
        │ uses
┌───────▼───────┐
│ Domain         │
│ Aggregates /   │
│ Entities / VO  │
└───────┬───────┘
        │ ports
┌───────▼───────┐
│ Infrastructure │
│ DB / Redis /   │
│ External APIs  │
└───────────────┘
```

* **箭頭方向 = 依賴方向**
* Domain 不依賴 Application / Infrastructure
* Application 依賴 Domain / Port
* Interface 依賴 Application
* Infrastructure 依賴 Port / 提供實作

---

## 6️⃣ 對照你目前結構的建議

* `interfaces/http/test_orders.py` → **Interface 層，不應計算價格或呼叫 Infrastructure**
* `application/trading/services/` → 應明確拆分：

  * **Application Service / Use Case**：協調 Aggregate / Domain Service
  * **Domain Service / VO / Aggregate**：核心業務規則
* `domain/value_objects` → Application Service 應使用 VO，不要用 primitive
* `infrastructure/external/mexc/*` → 只實作 Port，Application / Domain 不直接呼叫

---
完美，我幫你整理一個 **Interface Layer 下 template / static 檔案的分層合規檢查表**，重點是標註每個檔案是否**符合 DDD Interface Layer 原則**，以及是否**違規**（做了業務邏輯或直接呼叫 Infrastructure）。

---

# 🔹 Interface Layer Template / Static 分層檢查表

| 檔案 / 目錄                                           | 角色                   | 應做的事（Interface Layer）              | 可能違規行為                     | 合規性判斷                                 |
| ------------------------------------------------- | -------------------- | ---------------------------------- | -------------------------- | ------------------------------------- |
| `templates/`                                      | HTML template 根目錄    | 放置 HTML template / 前端頁面            | 放業務邏輯、直接呼叫 API             | ✅ 合規（只要模板只展示資料）                       |
| `templates/dashboard.html`                        | 頁面模板                 | 展示 dashboard 資料，透過 JS 呼叫 API       | 計算目標價格、決定下單、直接呼叫交易 API     | ⚠️ 需確認（如果有業務計算則違規）                    |
| `templates/static/`                               | 前端靜態資源根目錄            | JS/CSS/前端輔助工具                      | 將業務邏輯放在 JS 裡               | ⚠️ 需確認（如果 JS 做交易決策或價格計算則違規）           |
| `templates/static/js/api/account/get_balance.js`  | JS API 呼叫封裝          | 封裝 AJAX / fetch 呼叫 Application API | 直接呼叫 Infrastructure / 下單   | ⚠️ 需確認（應呼叫後端 Application Service）     |
| `templates/static/js/api/trading/place_order.js`  | JS API 呼叫封裝          | 發送下單請求給後端 API                      | 直接計算價格、風控、調用 mexc API      | ⚠️ 高風險違規（業務邏輯應在 Domain / Application） |
| `templates/static/js/dom/render_orders.js`        | DOM 操作 / View        | 渲染從 API 拿到的訂單資料                    | 做業務判斷或修改訂單狀態               | ⚠️ 需確認                                |
| `templates/static/js/pages/dashboard/handlers.js` | Page handler         | 綁定事件、呼叫 API                        | 在前端做交易決策、風控、數值計算           | ⚠️ 高風險違規                              |
| `templates/static/js/pages/dashboard/init.js`     | Page init            | 初始化頁面 / 綁定事件                       | 計算業務規則、直接呼叫 Infrastructure | ⚠️ 需確認                                |
| `templates/static/js/pages/dashboard/refresh.js`  | Page refresh handler | 定時刷新資料                             | 在前端做業務邏輯                   | ⚠️ 需確認                                |
| `templates/static/js/shared/errors.js`            | 共用錯誤處理               | 封裝錯誤訊息                             | 做業務判斷                      | ✅ 合規                                  |
| `templates/static/js/shared/http.js`              | 共用 HTTP wrapper      | 封裝 AJAX / fetch                    | 直接呼叫交易 API / DB            | ⚠️ 需確認                                |
| `templates/static/js/shared/time.js`              | 共用時間工具               | 封裝時間工具函數                           | 做業務計算                      | ⚠️ 需確認（業務計算應放 Domain）                 |
| `templates/static/js/state/store.js`              | 前端狀態管理               | 保存前端狀態                             | 保存業務決策結果、下單狀態              | ⚠️ 需確認                                |
| `templates/static/js/state/selectors.js`          | 前端狀態選取               | 選取資料給 View                         | 做業務計算                      | ⚠️ 需確認                                |

---

### 🔹 判斷原則

1. **✅ 合規**

   * 只做展示 / UI 綁定 / AJAX 封裝
   * 不計算業務規則
   * 不直接呼叫 Infrastructure（DB/API/交易系統）

2. **⚠️ 需確認 / 高風險違規**

   * 前端 JS 計算目標價格、百分比
   * 前端直接決定下單 / 交易參數
   * 前端直接呼叫交易 API / Redis / DB

> 原則上，所有業務規則應該移到 **Domain Layer / Application Service**，Interface Layer 只做 **呈現 + API 呼叫**。

---

# 🔹 標準 DDD 分層對齊模板（完整邊界版）

## 1️⃣ Interface Layer（接口層 / Adapter Layer）

**責任**：

* 接收外部請求（REST / Websocket / CLI / Scheduler）
* 輸入驗證、DTO 轉換
* 呼叫 Application Service / Use Case
* 將結果包裝成輸出 DTO / Response
* **只做呈現與輸入/輸出轉換，不做業務計算**

**典型位置**：

```
interfaces/http/
interfaces/tasks/
interfaces/websocket/
interfaces/cli/
interfaces/templates/
```

**應做**：

* 渲染模板 (HTML / JS / CSS)
* 綁定事件，呼叫後端 API
* 前端狀態管理僅保存 UI 狀態
* 封裝共用工具（如時間、錯誤訊息）

**不得做**：

* 計算業務規則（價格、風控、下單量）
* 呼叫 Infrastructure（DB / Redis / 交易 API）
* 保存業務決策或 Domain 物件狀態

**典型檔案**：

* `interfaces/http/order_routes.py`
* `interfaces/tasks/rebalance.py`
* `interfaces/http/test_orders.py` → 重構後只呼叫 Application Service
* `interfaces/templates/dashboard.html`
* `interfaces/templates/static/js/shared/errors.js`

---

## 2️⃣ Application Layer（應用層 / Use Case Layer）

**責任**：

* 協調 Domain 行為
* 調用 Domain Aggregates / Domain Service / Ports
* 提供 Use Case 接口給 Interface Layer
* **不包含業務規則算法（放 Domain）**

**典型位置**：

```
application/trading/
application/account/
application/market/
application/common/
```

**應做**：

* 統一調用多個 Domain 物件
* 呼叫 Repository / Infrastructure Port
* 封裝 Use Case，讓 Interface 層統一呼叫

**不得做**：

* 實作業務規則（價格計算、風控判斷）
* 呼叫外部 API / DB / Redis 直接操作

**典型檔案**：

* `application/trading/execute_trade.py`
* `application/account/get_balance.py`
* `application/market/sync_price.py`

---

## 3️⃣ Domain Layer（領域層 / 核心業務）

**責任**：

* 定義核心業務概念
* 封裝業務規則（Aggregate / Entity / Value Object / Domain Service）
* Domain Events
* 提供 API 給 Application Service 使用

**典型位置**：

```
domain/aggregates/
domain/models/
domain/value_objects/
domain/events/
domain/strategies/
domain/risk/
domain/ports/
```

**應做**：

* 核心業務規則、不可變性、行為封裝
* Domain Service 或 Aggregate Root 封裝交易邏輯
* 準備與 Infrastructure Port 對接（不直接呼叫）

**不得做**：

* 呼叫 Interface 層
* 直接呼叫外部 API / DB / Redis

**典型檔案**：

* `domain/aggregates/order.py` → Aggregate Root
* `domain/value_objects/price.py` → VO
* `domain/models/trade.py` → Entity
* `domain/events/trading_events.py`
* `domain/strategies/base.py` → 策略規則

---

## 4️⃣ Infrastructure Layer（基礎設施 / Adapter Implementation）

**責任**：

* 實作 Domain Port / Repository
* 提供外部系統連接（DB、Redis、API、Message Broker）
* 不包含業務邏輯，只提供資料操作接口

**典型位置**：

```
infrastructure/persistence/
infrastructure/external/
infrastructure/config/
infrastructure/bot_runtime/
infrastructure/supabase/
```

**應做**：

* 實作 Repository / Port
* 提供 API / Client / DB / Redis 操作
* 為 Domain / Application 提供資料存取接口

**不得做**：

* 實作業務規則
* 呼叫 Interface 層

**典型檔案**：

* `infrastructure/persistence/repos/trade_repository.py`
* `infrastructure/external/mexc/client.py`
* `infrastructure/persistence/redis/cache.py`

---

## 5️⃣ 典型依賴方向

```text
┌───────────────┐
│ Interface      │
│ (HTTP / WS)    │
└───────┬───────┘
        │ calls
┌───────▼───────┐
│ Application    │
│ Use Cases      │
└───────┬───────┘
        │ uses
┌───────▼───────┐
│ Domain         │
│ Aggregates /   │
│ Entities / VO  │
└───────┬───────┘
        │ ports
┌───────▼───────┐
│ Infrastructure │
│ DB / Redis /   │
│ External APIs  │
└───────────────┘
```

---

# 🔹 Interface Layer Template / Static 分層檢查表（邊界明確版）

| 檔案 / 目錄                                 | 角色                   | 應做（Interface Layer）      | 不該做 / 違規行為                 | 判斷                            |
| --------------------------------------- | -------------------- | ------------------------ | -------------------------- | ----------------------------- |
| `templates/`                            | HTML template 根目錄    | 放置 HTML template / 前端頁面  | 放業務邏輯、直接呼叫 API             | ✅ 合規                          |
| `templates/dashboard.html`              | 頁面模板                 | 展示資料，透過 JS 呼叫 API        | 計算目標價格、決定下單、呼叫交易 API       | ⚠️ 需確認（如有計算業務則違規）             |
| `templates/static/`                     | 前端靜態資源根目錄            | JS/CSS/前端輔助工具            | 將業務邏輯放在 JS 裡               | ⚠️ 需確認（若做交易決策或價格計算則違規）        |
| `static/js/api/account/get_balance.js`  | JS API 封裝            | 呼叫後端 Application Service | 直接呼叫 Infrastructure / 下單   | ⚠️ 需確認                        |
| `static/js/api/trading/place_order.js`  | JS API 封裝            | 發送下單請求給後端 API            | 計算價格、風控、直接呼叫交易 API         | ✗ 違規（應在 Domain / Application） |
| `static/js/dom/render_orders.js`        | DOM 操作 / View        | 渲染從 API 拿到的資料            | 做業務判斷或修改訂單狀態               | ⚠️ 需確認                        |
| `static/js/pages/dashboard/handlers.js` | Page handler         | 綁定事件、呼叫 API              | 在前端做交易決策 / 風控 / 計算         | ✗ 違規                          |
| `static/js/pages/dashboard/init.js`     | Page init            | 初始化頁面 / 綁定事件             | 計算業務規則、直接呼叫 Infrastructure | ⚠️ 需確認                        |
| `static/js/pages/dashboard/refresh.js`  | Page refresh handler | 定時刷新資料                   | 在前端做業務邏輯                   | ⚠️ 需確認                        |
| `static/js/shared/errors.js`            | 共用錯誤處理               | 封裝錯誤訊息                   | 做業務判斷                      | ✅ 合規                          |
| `static/js/shared/http.js`              | 共用 HTTP wrapper      | 封裝 AJAX / fetch          | 直接呼叫交易 API / DB            | ⚠️ 需確認                        |
| `static/js/shared/time.js`              | 共用時間工具               | 封裝時間工具函數                 | 做業務計算                      | ⚠️ 需確認                        |
| `static/js/state/store.js`              | 前端狀態管理               | 保存 UI 狀態                 | 保存業務決策 / 下單狀態              | ⚠️ 需確認                        |
| `static/js/state/selectors.js`          | 前端狀態選取               | 選取資料給 View               | 做業務計算                      | ⚠️ 需確認                        |

---

### 🔹 判斷原則（完整版）

1. **✅ 合規**

   * 只做展示 / UI 綁定 / API 封裝
   * 不計算業務規則
   * 不直接呼叫 Infrastructure

2. **⚠️ 需確認 / 高風險違規**

   * 前端做價格計算、下單決策、風控判斷
   * 保存業務決策 / Domain 物件狀態
   * 直接呼叫交易 API / Redis / DB

3. **✗ 違規**

   * 業務邏輯直接在前端或 Interface 層實作
   * 直接決定交易價格 / 下單量 / 風控判斷

> **原則**：所有業務規則移到 Domain / Application 層，Interface 只負責展示 + API 呼叫。

---

## 🔹 Interface Layer 視覺化分層圖（邊界明確版）

```text
interfaces/templates/
│
├─ dashboard.html                 ✅ 合規
│
└─ static/
    ├─ js/
    │   ├─ api/
    │   │   ├─ account/
    │   │   │   └─ get_balance.js        ⚠️ 需確認
    │   │   ├─ trading/
    │   │   │   └─ place_order.js        ✗ 違規
    │   │   └─ market/
    │   │       └─ get_price.js          ✅ 合規
    │   │
    │   ├─ dom/
    │   │   └─ render_orders.js          ⚠️ 需確認
    │   │
    │   ├─ pages/
    │   │   └─ dashboard/
    │   │       ├─ handlers.js           ✗ 違規
    │   │       ├─ init.js               ⚠️ 需確認
    │   │       └─ refresh.js            ⚠️ 需確認
    │   │
    │   ├─ shared/
    │   │   ├─ errors.js                  ✅ 合規
    │   │   ├─ http.js                    ⚠️ 需確認
    │   │   └─ time.js                    ⚠️ 需確認
    │   │
    │   └─ state/
    │       ├─ store.js                   ⚠️ 需確認
    │       └─ selectors.js               ⚠️ 需確認
```

---

### 🔹 顏色/符號說明

| 符號 | 意義                                   |
| -- | ------------------------------------ |
| ✅  | 完全合規（只做展示 / API 封裝 / UI 綁定）          |
| ⚠️ | 需確認 / 高風險（可能做了業務計算或決策）               |
| ✗  | 違規（Interface 層直接做交易決策、價格計算、呼叫交易 API） |

---

### 🔹 建議行動

1. **立即重構違規檔案**

   * `place_order.js`、`handlers.js` → 將價格計算、風控、下單決策移到 **Domain / Application Service**
2. **檢查需確認檔案**

   * `get_balance.js`、`render_orders.js`、`init.js`、`refresh.js`、`http.js`、`time.js`、`store.js`、`selectors.js`
   * 確認是否有業務邏輯或 Domain 職責，如果有 → 搬到 Application / Domain
3. **Interface 層只保留**

   * UI 綁定、事件觸發
   * API 請求與回傳處理
   * 工具函數（非業務邏輯）

---


---

## 🔹 完整專案 DDD 分層視覺圖（邊界明確）

```text
src/app/
│
├─ application/                  Application Layer
│   ├─ account/                  ⚡ Use Cases / Application Services
│   │   ├─ get_balance.py        ✅ 合規
│   │   ├─ list_orders.py        ✅ 合規
│   │   └─ ... 
│   │
│   ├─ bot/
│   │   ├─ start.py              ✅ 合規
│   │   └─ ...
│   │
│   ├─ trading/
│   │   ├─ execute_trade.py      ✅ 合規
│   │   ├─ validate_trade.py     ✅ 合規
│   │   └─ services/
│   │       ├─ trading_service.py ✅ 合規
│   │       └─ ... 
│   │
│   └─ market/
│       ├─ get_price.py          ✅ 合規
│       └─ sync_price.py         ✅ 合規
│
├─ domain/                       Domain Layer
│   ├─ aggregates/
│   │   ├─ portfolio.py          ✅ 合規
│   │   └─ trade_batch.py        ✅ 合規
│   │
│   ├─ models/
│   │   ├─ order.py              ✅ 合規
│   │   └─ trade.py              ✅ 合規
│   │
│   ├─ value_objects/
│   │   ├─ price.py              ✅ 合規
│   │   └─ quantity.py           ✅ 合規
│   │
│   ├─ strategies/               ✅ 合規
│   ├─ risk/                      ✅ 合規
│   └─ ports/                     ✅ 合規 (實作在 Infrastructure)
│
├─ infrastructure/               Infrastructure Layer
│   ├─ persistence/
│   │   ├─ repos/
│   │   │   ├─ trade_repository.py ✅ 合規
│   │   │   └─ position_repository.py ✅ 合規
│   │   └─ redis/
│   │       └─ cache.py          ✅ 合規
│   │
│   ├─ external/
│   │   └─ mexc/
│   │       ├─ client.py         ✅ 合規
│   │       └─ endpoints/        ✅ 合規
│   └─ config/                    ✅ 合規
│
├─ interfaces/                    Interface Layer
│   ├─ http/
│   │   ├─ test_orders.py         ⚠️ 需確認（目前直接計算價格/下單）
│   │   ├─ order_routes.py        ✅ 合規（呼叫 Application）
│   │   └─ ... 
│   │
│   ├─ tasks/                     ⚠️ 檢查是否有業務邏輯
│   └─ templates/
│       ├─ dashboard.html          ✅ 合規（只展示資料）
│       └─ static/
│           ├─ js/
│           │   ├─ api/
│           │   │   ├─ account/get_balance.js  ⚠️ 需確認
│           │   │   ├─ trading/place_order.js  ✗ 違規
│           │   │   └─ market/get_price.js    ✅ 合規
│           │   ├─ dom/render_orders.js        ⚠️ 需確認
│           │   ├─ pages/dashboard/
│           │   │   ├─ handlers.js           ✗ 違規
│           │   │   ├─ init.js               ⚠️ 需確認
│           │   │   └─ refresh.js            ⚠️ 需確認
│           │   ├─ shared/
│           │   │   ├─ errors.js             ✅ 合規
│           │   │   ├─ http.js               ⚠️ 需確認
│           │   │   └─ time.js               ⚠️ 需確認
│           │   └─ state/
│           │       ├─ store.js              ⚠️ 需確認
│           │       └─ selectors.js          ⚠️ 需確認
│           └─ css/                       ✅ 合規
│
└─ shared/                         共用工具 / helper
    ├─ clock.py                     ✅ 合規
    ├─ errors.py                    ✅ 合規
    ├─ ids.py                       ✅ 合規
    └─ typing.py                    ✅ 合規
```

---

### 🔹 標註說明

| 符號 | 意義                                                                            |
| -- | ----------------------------------------------------------------------------- |
| ✅  | 完全合規：Interface 呼叫 Application，Application 調用 Domain，Infrastructure 提供 Port 實作 |
| ⚠️ | 高風險 / 需確認：Interface 層有業務邏輯或直接呼叫 Infrastructure                                |
| ✗  | 違規：Interface 層直接做 Domain 責任（價格計算、下單、風控決策）                                     |

---

### 🔹 分層邊界重點

1. **Interface 層**

   * 僅呈現、事件綁定、呼叫 Application
   * **不得做價格計算、下單決策、風控判斷**
2. **Application 層**

   * Use Case / Service 協調 Domain
   * **不得實作業務規則**
3. **Domain 層**

   * 核心業務概念、規則、Aggregate、Entity、VO、Domain Service
   * **不直接呼叫 Infrastructure**
4. **Infrastructure 層**

   * 提供 Port / Repository / 外部系統連接
   * **不包含業務規則**
5. **Shared**

   * 工具函數，無業務邏輯
   * 可以 Interface / Application / Domain 共用

---
