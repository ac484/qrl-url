# DDD 分層邊界檢查指南

> **文件目的**：作為專案 DDD 分層的檢查指南，確保各層職責清晰、邊界明確，便於快速審查與維護。

---

## 📋 目錄

1. [概述](#概述)
2. [核心 DDD 分層定義](#核心-ddd-分層定義)
3. [依賴方向規則](#依賴方向規則)
4. [分層合規檢查表](#分層合規檢查表)
5. [專案結構視覺圖](#專案結構視覺圖)
6. [快速檢查指引](#快速檢查指引)

---

## 概述

本文件定義 DDD（Domain-Driven Design）四層架構的邊界規則，包括：
- **Interface Layer**（接口層）：處理外部請求與響應
- **Application Layer**（應用層）：協調業務流程
- **Domain Layer**（領域層）：核心業務邏輯
- **Infrastructure Layer**（基礎設施層）：外部系統連接

**核心原則**：
- 各層職責單一，不越界
- 依賴方向由外向內（Infrastructure → Domain ← Application ← Interface）
- Domain 層不依賴任何外部層

---

## 核心 DDD 分層定義

### 1️⃣ Interface Layer（接口層 / Adapter Layer）

**責任**：
- 接收外部請求（REST / WebSocket / CLI / Scheduler）
- 輸入驗證、DTO 轉換
- 呼叫 Application Service / Use Case
- 將結果包裝成輸出 DTO / Response
- **只做呈現與輸入/輸出轉換，不做業務計算**

**典型位置**：
```
interfaces/http/
interfaces/tasks/
interfaces/websocket/
interfaces/cli/
interfaces/templates/
```

**✅ 應做**：
- 渲染模板 (HTML / JS / CSS)
- 綁定事件，呼叫後端 API
- 前端狀態管理僅保存 UI 狀態
- 封裝共用工具（如時間、錯誤訊息）

**❌ 不得做**：
- 計算業務規則（價格、風控、下單量）
- 呼叫 Infrastructure（DB / Redis / 交易 API）
- 保存業務決策或 Domain 物件狀態

**範例檔案**：
- `interfaces/http/order_routes.py`
- `interfaces/tasks/rebalance.py`
- `interfaces/http/test_orders.py` → 重構後只呼叫 Application Service
- `interfaces/templates/dashboard.html`

---

### 2️⃣ Application Layer（應用層 / Use Case Layer）

**責任**：
- 協調 Domain 行為
- 調用 Domain Aggregates / Domain Service / Ports
- 提供 Use Case 接口給 Interface Layer
- **不包含業務規則算法（放 Domain）**

**典型位置**：
```
application/trading/
application/account/
application/market/
application/common/
```

**✅ 應做**：
- 統一調用多個 Domain 物件
- 呼叫 Repository / Infrastructure Port
- 封裝 Use Case，讓 Interface 層統一呼叫

**❌ 不得做**：
- 實作業務規則（價格計算、風控判斷）
- 直接操作外部 API / DB / Redis

**範例檔案**：
- `application/trading/execute_trade.py`
- `application/account/get_balance.py`
- `application/market/sync_price.py`

---

### 3️⃣ Domain Layer（領域層 / 核心業務）

**責任**：
- 定義核心業務概念
- 封裝業務規則（Aggregate / Entity / Value Object / Domain Service）
- Domain Events
- 提供 API 給 Application Service 使用

**典型位置**：
```
domain/aggregates/
domain/models/
domain/value_objects/
domain/events/
domain/strategies/
domain/risk/
domain/ports/  ← Domain 與 Infrastructure 依賴反轉接口
```

**✅ 應做**：
- 核心業務規則、不可變性、行為封裝
- Domain Service 或 Aggregate Root 封裝交易邏輯
- 定義 Infrastructure Port（不直接呼叫實作）

**❌ 不得做**：
- 呼叫 Interface 層
- 直接呼叫外部 API / DB / Redis

**範例檔案**：
- `domain/aggregates/order.py` → Aggregate Root
- `domain/value_objects/price.py` → Value Object
- `domain/models/trade.py` → Entity
- `domain/events/trading_events.py`
- `domain/strategies/base.py` → 策略規則
- `domain/ports/trade_port.py` → Infrastructure Port 定義

---

### 4️⃣ Infrastructure Layer（基礎設施 / Adapter Implementation）

**責任**：
- 實作 Domain Port / Repository
- 提供外部系統連接（DB、Redis、API、Message Broker）
- 不包含業務邏輯，只提供資料操作接口

**典型位置**：
```
infrastructure/persistence/
infrastructure/external/
infrastructure/config/
infrastructure/bot_runtime/
infrastructure/supabase/
```

**✅ 應做**：
- 實作 Repository / Port
- 提供 API / Client / DB / Redis 操作
- 為 Domain / Application 提供資料存取接口

**❌ 不得做**：
- 實作業務規則
- 呼叫 Interface 層

**範例檔案**：
- `infrastructure/persistence/repos/trade_repository.py`
- `infrastructure/external/mexc/client.py`
- `infrastructure/persistence/redis/cache.py`

---

## 依賴方向規則

### 依賴流向圖

```text
┌───────────────┐
│ Interface      │  ← 最外層：接收請求
│ (HTTP / WS)    │
└───────┬───────┘
        │ calls
┌───────▼───────┐
│ Application    │  ← 協調層：編排業務流程
│ Use Cases      │
└───────┬───────┘
        │ uses
┌───────▼───────┐
│ Domain         │  ← 核心層：業務規則
│ Aggregates /   │
│ Entities / VO  │
└───────┬───────┘
        │ ports (依賴反轉)
┌───────▼───────┐
│ Infrastructure │  ← 最內層：外部系統連接
│ DB / Redis /   │
│ External APIs  │
└───────────────┘
```

### 依賴原則

| 層次 | 可依賴 | 不可依賴 |
|------|--------|----------|
| **Interface** | Application | Domain, Infrastructure |
| **Application** | Domain, Infrastructure Ports | Interface, Infrastructure 具體實作 |
| **Domain** | 無（完全獨立） | Application, Interface, Infrastructure |
| **Infrastructure** | Domain Ports | Application, Interface |

**核心規則**：
- **箭頭方向 = 依賴方向**
- Domain 不依賴任何外層（保持純淨）
- Application 依賴 Domain + Port（不依賴具體實作）
- Interface 只依賴 Application（不跨層呼叫）
- Infrastructure 實作 Port（供 Application 使用）

---

## 分層合規檢查表

### Interface Layer 檔案檢查表

#### Python 後端檔案

| 檔案路徑 | 角色 | 合規性 | 檢查重點 |
|---------|------|--------|----------|
| `interfaces/http/order_routes.py` | HTTP Routes | ✅ 合規 | 只呼叫 Application Service |
| `interfaces/http/test_orders.py` | Test Routes | ⚠️ 需重構 | 不應計算價格或直接呼叫 MEXC |
| `interfaces/tasks/rebalance.py` | Scheduler Task | ⚠️ 檢查 | 確保無業務邏輯 |
| `interfaces/websocket/handlers.py` | WebSocket Handler | ✅ 合規 | 僅轉發到 Application |

#### Frontend 靜態檔案檢查表

| 檔案路徑 | 角色 | 合規狀態 | 違規風險 |
|---------|------|----------|----------|
| `templates/dashboard.html` | 頁面模板 | ✅ 合規 | 只展示資料 |
| `static/js/api/account/get_balance.js` | API 封裝 | ⚠️ 需確認 | 應呼叫後端 API，不直接呼叫 Infrastructure |
| `static/js/api/trading/place_order.js` | API 封裝 | ✗ 違規 | 不得計算價格、風控、直接呼叫交易 API |
| `static/js/dom/render_orders.js` | DOM 操作 | ⚠️ 需確認 | 只渲染資料，不做業務判斷 |
| `static/js/pages/dashboard/handlers.js` | 事件處理 | ✗ 違規 | 不得在前端做交易決策 / 風控 / 計算 |
| `static/js/pages/dashboard/init.js` | 頁面初始化 | ⚠️ 需確認 | 只綁定事件，不做業務計算 |
| `static/js/pages/dashboard/refresh.js` | 刷新處理 | ⚠️ 需確認 | 定時刷新資料，不做業務邏輯 |
| `static/js/shared/errors.js` | 錯誤處理 | ✅ 合規 | 只封裝錯誤訊息 |
| `static/js/shared/http.js` | HTTP 封裝 | ⚠️ 需確認 | 只封裝 AJAX，不直接呼叫交易 API |
| `static/js/shared/time.js` | 時間工具 | ⚠️ 需確認 | 工具函數，不做業務計算 |
| `static/js/state/store.js` | 狀態管理 | ⚠️ 需確認 | 只保存 UI 狀態，不保存業務決策 |
| `static/js/state/selectors.js` | 狀態選取 | ⚠️ 需確認 | 選取資料，不做業務計算 |

#### 合規判斷原則

| 符號 | 意義 | 說明 |
|------|------|------|
| ✅ | 完全合規 | 只做展示 / UI 綁定 / API 封裝，無業務邏輯 |
| ⚠️ | 需確認 / 高風險 | 可能包含業務計算、決策或 Infrastructure 直接呼叫 |
| ✗ | 違規 | Interface 層直接實作業務邏輯、交易決策或呼叫交易 API |

---

## 專案結構視覺圖

### 完整分層結構圖

```text
src/app/
│
├─ interfaces/                    Interface Layer
│   ├─ http/
│   │   ├─ order_routes.py        ✅ 合規
│   │   ├─ test_orders.py         ⚠️ 需重構（計算價格/直接呼叫 MEXC）
│   │   └─ ...
│   ├─ tasks/
│   │   └─ rebalance.py           ⚠️ 檢查業務邏輯
│   └─ templates/
│       ├─ dashboard.html         ✅ 合規
│       └─ static/
│           ├─ js/
│           │   ├─ api/
│           │   │   ├─ account/get_balance.js    ⚠️ 需確認
│           │   │   ├─ trading/place_order.js    ✗ 違規
│           │   │   └─ market/get_price.js       ✅ 合規
│           │   ├─ dom/render_orders.js          ⚠️ 需確認
│           │   ├─ pages/dashboard/
│           │   │   ├─ handlers.js               ✗ 違規
│           │   │   ├─ init.js                   ⚠️ 需確認
│           │   │   └─ refresh.js                ⚠️ 需確認
│           │   ├─ shared/
│           │   │   ├─ errors.js                 ✅ 合規
│           │   │   ├─ http.js                   ⚠️ 需確認
│           │   │   └─ time.js                   ⚠️ 需確認
│           │   └─ state/
│           │       ├─ store.js                  ⚠️ 需確認
│           │       └─ selectors.js              ⚠️ 需確認
│           └─ css/                             ✅ 合規
│
├─ application/                  Application Layer
│   ├─ account/
│   │   ├─ get_balance.py        ✅ 合規
│   │   ├─ list_orders.py        ✅ 合規
│   │   └─ ...
│   ├─ bot/
│   │   ├─ start.py              ✅ 合規
│   │   └─ ...
│   ├─ trading/
│   │   ├─ execute_trade.py      ✅ 合規
│   │   ├─ validate_trade.py     ✅ 合規
│   │   └─ services/
│   │       ├─ trading_service.py ✅ 合規
│   │       └─ ...
│   └─ market/
│       ├─ get_price.py          ✅ 合規
│       └─ sync_price.py         ✅ 合規
│
├─ domain/                       Domain Layer
│   ├─ aggregates/
│   │   ├─ portfolio.py          ✅ 合規
│   │   ├─ strategy.py           ✅ 合規
│   │   └─ trade_batch.py        ✅ 合規
│   ├─ models/
│   │   ├─ order.py              ✅ 合規
│   │   └─ trade.py              ✅ 合規
│   ├─ value_objects/
│   │   ├─ price.py              ✅ 合規
│   │   ├─ quantity.py           ✅ 合規
│   │   ├─ symbol.py             ✅ 合規
│   │   └─ ...
│   ├─ events/
│   │   └─ trading_events.py     ✅ 合規
│   ├─ strategies/
│   │   └─ base.py               ✅ 合規
│   ├─ risk/
│   │   └─ manager.py            ✅ 合規
│   └─ ports/                    ✅ 合規（定義接口）
│
├─ infrastructure/               Infrastructure Layer
│   ├─ persistence/
│   │   ├─ repos/
│   │   │   ├─ trade_repository.py ✅ 合規
│   │   │   └─ position_repository.py ✅ 合規
│   │   └─ redis/
│   │       └─ cache.py          ✅ 合規
│   ├─ external/
│   │   └─ mexc/
│   │       ├─ client.py         ✅ 合規
│   │       ├─ market_endpoints.py ✅ 合規
│   │       └─ repos/
│   │           └─ trade_repo.py ✅ 合規
│   └─ config/                   ✅ 合規
│
└─ shared/                       共用工具
    ├─ clock.py                  ✅ 合規
    ├─ errors.py                 ✅ 合規
    ├─ ids.py                    ✅ 合規
    └─ typing.py                 ✅ 合規
```

---

## 快速檢查指引

### 🔍 檢查步驟

#### Step 1: Interface Layer 檢查
```bash
# 檢查 Interface 層是否包含業務邏輯
grep -r "calculate\|compute\|validate.*business\|risk.*check" interfaces/
```

**違規範例**：
```python
# ❌ 錯誤：Interface 層計算價格
@router.post("/test-order")
def test_order(request: OrderRequest):
    # 不應在此計算價格
    target_price = current_price * (1 + percentage / 100)
    mexc_client.create_order(price=target_price)  # 不應直接呼叫
```

**正確範例**：
```python
# ✅ 正確：Interface 層只呼叫 Application
@router.post("/test-order")
def test_order(request: OrderRequest):
    # 呼叫 Application Use Case
    result = place_test_order_usecase.execute(request)
    return result
```

#### Step 2: Application Layer 檢查
```bash
# 檢查 Application 層是否直接操作外部系統
grep -r "mexc_client\|redis_client\|supabase_client" application/
```

**違規範例**：
```python
# ❌ 錯誤：Application 直接呼叫 Infrastructure
class PlaceOrderUseCase:
    def execute(self, order_data):
        # 不應直接呼叫 MEXC
        mexc_client.create_order(order_data)
```

**正確範例**：
```python
# ✅ 正確：Application 透過 Port 呼叫
class PlaceOrderUseCase:
    def __init__(self, trade_port: TradePort):
        self.trade_port = trade_port
    
    def execute(self, order_data):
        # 透過 Domain Port 呼叫
        self.trade_port.place_order(order_data)
```

#### Step 3: Domain Layer 檢查
```bash
# 檢查 Domain 層是否依賴外層
grep -r "from.*application\|from.*infrastructure\|from.*interfaces" domain/
```

**關鍵原則**：
- Domain 層應該 **完全獨立**
- 只定義 Port，不依賴實作
- 所有業務規則封裝在 Domain

#### Step 4: Frontend 檢查
```bash
# 檢查 JS 是否包含業務邏輯
grep -r "calculate.*price\|compute.*quantity\|risk.*check" templates/static/js/
```

**違規範例**：
```javascript
// ❌ 錯誤：前端計算價格
function placeOrder(symbol, percentage) {
    const currentPrice = getCurrentPrice(symbol);
    const targetPrice = currentPrice * (1 + percentage / 100);  // 業務計算
    apiClient.createOrder(symbol, targetPrice);
}
```

**正確範例**：
```javascript
// ✅ 正確：前端只呼叫 API
function placeOrder(symbol, percentage) {
    // 呼叫後端 API，由 Domain 計算價格
    apiClient.placeTestOrder(symbol, percentage);
}
```

---

### 🎯 重構優先級

#### 🔴 高優先級（立即重構）

**違規檔案**：
1. `interfaces/http/test_orders.py` → 移除價格計算、風控判斷
2. `static/js/api/trading/place_order.js` → 移除業務邏輯
3. `static/js/pages/dashboard/handlers.js` → 移除交易決策

**重構方向**：
- 將業務邏輯移至 Domain Layer
- 在 Application Layer 建立 Use Case
- Interface Layer 只呼叫 Use Case

#### 🟡 中優先級（審查確認）

**需檢查檔案**：
- `static/js/api/account/get_balance.js`
- `static/js/dom/render_orders.js`
- `static/js/pages/dashboard/init.js`
- `static/js/pages/dashboard/refresh.js`
- `static/js/shared/http.js`
- `static/js/shared/time.js`
- `static/js/state/store.js`
- `static/js/state/selectors.js`

**檢查重點**：
- 是否包含業務計算？
- 是否直接呼叫 Infrastructure？
- 是否保存業務狀態？

---

### ✅ 合規檢查清單

使用此清單快速檢查檔案是否符合 DDD 分層原則：

**Interface Layer**：
- [ ] 只處理 HTTP 請求/響應
- [ ] 使用 Pydantic DTO 驗證輸入
- [ ] 呼叫 Application Use Case
- [ ] 不包含業務邏輯
- [ ] 不直接呼叫 Infrastructure

**Application Layer**：
- [ ] 協調 Domain 物件
- [ ] 透過 Port 呼叫 Infrastructure
- [ ] 不包含業務規則算法
- [ ] 不直接操作 DB/Redis/API

**Domain Layer**：
- [ ] 定義核心業務概念
- [ ] 封裝業務規則
- [ ] 完全獨立（無外部依賴）
- [ ] 使用 Value Object 而非 primitive

**Infrastructure Layer**：
- [ ] 實作 Domain Port
- [ ] 提供外部系統連接
- [ ] 不包含業務邏輯
- [ ] 不呼叫上層（Application/Interface）

---

## 附錄

### 常見問題

**Q1: 前端可以做簡單的格式化或計算嗎（如顯示千分位、百分比）？**
A: 可以。**純展示層的格式化**不屬於業務邏輯。但若涉及業務決策（如計算目標價格、下單量）則必須移至後端 Domain。

**Q2: Application 層可以直接呼叫 Repository 嗎？**
A: 可以。Repository 實作 Domain Port，Application 透過 Port 呼叫是正確的。但不應直接呼叫 `mexc_client` 等具體實作。

**Q3: 如何判斷一個計算是「業務邏輯」還是「工具函數」？**
A: 若計算結果影響業務決策（如訂單價格、風控判斷），即為業務邏輯，應放 Domain。若僅為格式轉換（如時間格式、JSON 序列化），可為工具函數。

---

### 參考資源

- [DDD Architecture Documentation](./docs/architecture/DDD_ARCHITECTURE.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Value Objects Implementation](./src/app/domain/value_objects/)
- [Application Use Cases](./src/app/application/)

---

**最後更新**：2026-01-04  
**文件版本**：v2.0  
**維護者**：開發團隊
