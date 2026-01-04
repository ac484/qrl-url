# QRL/USDT 自動交易機器人 DDD 架構文件

## 目錄
- [1. Domain Value Objects (VO)](#1-domain-value-objects-vo)
- [2. Domain Events](#2-domain-events)
- [3. Domain Entities / Aggregates](#3-domain-entities--aggregates)
- [4. DDD 架構圖](#4-ddd-架構圖)
- [5. 程式碼範例](#5-程式碼範例)

---

## 1. Domain Value Objects (VO)

| VO 名稱 | 說明 | 例子 / 備註 |
|---------|------|------------|
| `Symbol` | 交易對 | `"QRL/USDT"` |
| `OrderType` | 下單類型 | `"MARKET"` / `"LIMIT"` |
| `OrderSide` | 買/賣方向 | `"BUY"` / `"SELL"` |
| `Quantity` | 下單數量 | `Decimal('10')` QRL |
| `Price` | 限價單價格 | `Decimal('0.12')` USDT |
| `Percentage` | 部位比例 | `0.0 ~ 1.0` |
| `TimeFrame` | K線時間範圍 | `"1m"`, `"5m"`, `"1h"` |
| `Signal` | 交易訊號 | `"BUY"` / `"SELL"` / `"HOLD"` + 強度 0~1 |
| `PnL` | 損益 | 實現 / 未實現損益 |
| `Balance` | 帳戶資產數量 | QRL/USDT 數量 |
| `TradeId` | 交易唯一識別 | UUID |
| `Timestamp` | 事件發生時間 | datetime |
| `OrderStatus` | 訂單狀態 | `"NEW"`, `"FILLED"`, `"CANCELED"`, `"PARTIALLY_FILLED"` |
| `Leverage` | 槓桿倍數 | 若未使用現貨可忽略 |
| `Fee` | 手續費 | Decimal,用於計算盈虧 |
| `TickSize` | 最小價格變動 | 用於限價單調整 |
| `StepSize` | 最小下單量 | 下單前驗證合法數量 |
| `BalancePercentage` | 資金分配比例 | 0~1 |
| `OrderId` | 訂單唯一識別 | string / UUID |
| `KlineData` | K線資料 | open, high, low, close, volume |
| `SignalStrength` | 交易訊號強度 | 0~1,可用於模糊決策 |
| `Slippage` | 滑點 | Decimal,用於風控計算 |
| `MaxExposure` | 最大部位限制 | 0~1,風控用 |

---

## 2. Domain Events

| Event 名稱 | 說明 | 觸發時機 |
|-----------|------|---------|
| `OrderPlaced` | 訂單已成功下達 | OrderService 下單成功 |
| `OrderCancelled` | 訂單被取消 | 使用者取消或系統取消 |
| `OrderFilled` | 訂單成交 | 市場成交回報 |
| `OrderPartiallyFilled` | 訂單部分成交 | 市場回報 |
| `TradeExecuted` | 真正交易完成 | 包含成交數量、價格、手續費 |
| `PriceUpdated` | 最新市場價格更新 | Kline / Ticker 更新 |
| `SignalGenerated` | 交易訊號生成 | 交易策略觸發買/賣/持有 |
| `PositionUpdated` | 持倉變動 | 例如 QRL 部位增加/減少 |
| `PnLUpdated` | 損益更新 | 監控實時盈虧 |
| `RiskLimitBreached` | 風險限制觸發 | 部位過大或資金不足 |
| `BotStarted` | 機器人啟動 | 系統啟動事件 |
| `BotStopped` | 機器人停止 | 系統停止事件 |
| `OrderRejected` | 訂單被交易所拒絕 | API 回報錯誤 |
| `BalanceUpdated` | 帳戶餘額變化 | 每次資金變化觸發 |
| `RiskLimitUpdated` | 風控限制調整 | 動態調整最大部位或滑點 |
| `PriceAlertTriggered` | 價格達到預設區間 | 技術指標或價格監控觸發 |
| `PositionOpened` | 新持倉建立 | 市場成交後 |
| `PositionClosed` | 持倉平倉 | 全部賣出或策略平倉 |
| `StrategySignalGenerated` | 策略生成買/賣信號 | 例如均線交叉或 RSI 判斷 |
| `StopLossTriggered` | 停損事件 | 自動平倉 |
| `TakeProfitTriggered` | 止盈事件 | 自動平倉 |
| `TrailingStopUpdated` | 移動止損更新 | 根據最高價/最低價動態調整 |

---

## 3. Domain Entities / Aggregates

| Entity / Aggregate | 說明 | 包含 VO / Event |
|-------------------|------|----------------|
| `Order` | 訂單實體 | symbol, type, side, quantity, price, status, fee |
| `Position` | 持倉實體 | symbol, quantity, avg_price, unrealized_pnl |
| `Portfolio` | 聚合根 | 多個 Position,控制最大部位、風控 |
| `Trade` | 成交實體 | order_id, executed_qty, price, fee, timestamp |
| `Strategy` | 聚合根 / 行為 | 生成 StrategySignalGenerated Event,使用 KlineData / Indicator VO |
| `Bot` | 機器人實體 | 管理狀態 (running/stopped), risk limits, portfolio |

---

## 4. DDD 架構圖

```
+------------------------------------------------------+
|                      Application                     |
|  (Orchestrates domain logic & infrastructure)       |
|------------------------------------------------------|
|  OrderService         StrategyService                |
|  RiskManager          BotController                  |
|  - Receives signals   - Executes strategies         |
|  - Validates VO       - Generates Events            |
|  - Emits DomainEvents                                |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                       Domain                         |
|------------------------------------------------------|
|  Entities / Aggregates                               |
|  ---------------------                               |
|  Order                                               |
|    - symbol: Symbol                                  |
|    - type: OrderType                                 |
|    - side: OrderSide                                 |
|    - quantity: Quantity                              |
|    - price: Price                                    |
|    - status: OrderStatus                             |
|    - fee: Fee                                        |
|                                                      |
|  Position                                            |
|    - symbol: Symbol                                  |
|    - quantity: Quantity                              |
|    - avg_price: Price                                |
|    - unrealized_pnl: PnL                             |
|                                                      |
|  Portfolio (Aggregate Root)                          |
|    - positions: List[Position]                       |
|    - risk limits: MaxExposure                        |
|                                                      |
|  Trade                                               |
|    - order_id: OrderId                               |
|    - executed_qty: Quantity                          |
|    - price: Price                                    |
|    - fee: Fee                                        |
|    - timestamp: Timestamp                            |
|                                                      |
|  Bot                                                 |
|    - status: running/stopped                         |
|    - portfolio: Portfolio                            |
|    - risk_manager: RiskManager                       |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                   Domain Value Objects               |
|------------------------------------------------------|
|  Symbol, OrderType, OrderSide, Quantity, Price       |
|  Percentage, TimeFrame, Signal, SignalStrength       |
|  PnL, Balance, TradeId, Timestamp, Leverage          |
|  StepSize, TickSize, Slippage, MaxExposure, Fee      |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                     Domain Events                    |
|------------------------------------------------------|
|  OrderPlaced, OrderFilled, OrderPartiallyFilled      |
|  OrderCancelled, OrderRejected                       |
|  TradeExecuted                                       |
|  SignalGenerated, StrategySignalGenerated            |
|  PriceUpdated, BalanceUpdated                        |
|  PositionOpened, PositionClosed                      |
|  PnLUpdated                                          |
|  StopLossTriggered, TakeProfitTriggered              |
|  TrailingStopUpdated, RiskLimitUpdated               |
|  BotStarted, BotStopped                              |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                  Infrastructure                      |
|------------------------------------------------------|
|  MexcClient (API Wrapper)                            |
|    - place_order(symbol, side, quantity, price)      |
|    - cancel_order(order_id)                          |
|    - get_order_status(order_id)                      |
|    - get_balance(symbol)                             |
|    - subscribe_klines(symbol, timeframe)             |
|    - subscribe_ticker(symbol)                        |
+------------------------------------------------------+
```

### 架構說明

#### 1. Application Layer
- 只負責協調:接收策略信號、計算下單量、呼叫 Infrastructure API、發出 Domain Events
- 不包含商業邏輯

#### 2. Domain Layer
- Entities/Aggregates 保證一致性與商業規則
- Portfolio 聚合會檢查最大部位
- Position 聚合計算平均價格和未實現盈虧
- Bot Entity 管理機器人狀態

#### 3. Value Objects
- 封裝單一概念、不可變、具驗證
- 例如 Percentage、StepSize、TickSize

#### 4. Domain Events
- 描述 domain 內發生的事情,不做副作用
- Application Service 會監聽事件並做必要操作(下單、發通知等)

#### 5. Infrastructure
- 封裝 Mexc v3 API
- Domain 不直接呼叫 API,保持純粹性
- Application Service 使用 Infrastructure 來執行實際交易或訂閱行情

### 架構優勢

- ✅ **清楚分層**: Domain / Application / Infrastructure
- ✅ **完整事件流**: 從策略信號到下單、成交、風控
- ✅ **VO 驗證**: 防止錯誤參數導致 500
- ✅ **可擴展**: 新增策略、風控、其他交易對只需新增 VO/Events/Entities,不破壞現有架構

---

## 5. 程式碼範例

### 5.1 Value Objects 範例

#### Symbol
```python
# src/app/domain/value_objects/symbol.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Symbol:
    value: str

    def __post_init__(self):
        if "/" not in self.value:
            raise ValueError(f"Invalid symbol: {self.value}")
```

#### OrderType
```python
# src/app/domain/value_objects/order_type.py
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderType:
    value: str

    def __post_init__(self):
        if self.value not in ("MARKET", "LIMIT"):
            raise ValueError(f"Invalid OrderType: {self.value}")
```

#### OrderSide
```python
# src/app/domain/value_objects/order_side.py
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderSide:
    value: str

    def __post_init__(self):
        if self.value not in ("BUY", "SELL"):
            raise ValueError(f"Invalid OrderSide: {self.value}")
```

#### Quantity
```python
# src/app/domain/value_objects/quantity.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Quantity:
    value: Decimal

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity must be positive")
```

> **註**: 其他 VO 同理,例如 `Price`, `Percentage`, `Signal`, `TimeFrame`, `Balance`, `PnL`,都可以用 `dataclass(frozen=True)` 並加驗證。

---

### 5.2 Domain Events 範例

#### OrderPlaced
```python
# src/app/domain/events/order_placed.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.domain.value_objects.symbol import Symbol
from app.domain.value_objects.order_side import OrderSide
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.price import Price

@dataclass(frozen=True)
class OrderPlaced:
    order_id: UUID
    symbol: Symbol
    side: OrderSide
    quantity: Quantity
    price: Price
    timestamp: datetime
```

#### StrategySignalGenerated
```python
# src/app/domain/events/strategy_signal_generated.py
from dataclasses import dataclass
from datetime import datetime
from app.domain.value_objects.symbol import Symbol
from app.domain.value_objects.signal import Signal
from app.domain.value_objects.signal_strength import SignalStrength

@dataclass(frozen=True)
class StrategySignalGenerated:
    symbol: Symbol
    signal: Signal
    strength: SignalStrength
    timestamp: datetime
```

> **註**: 其他 Event 同理,例如 `OrderFilled`, `PositionUpdated`, `PnLUpdated`, `StopLossTriggered`。

---

### 5.3 Entities / Aggregates 範例

#### Order Entity
```python
# src/app/domain/entities/order.py
from dataclasses import dataclass
from uuid import UUID
from app.domain.value_objects import (
    Symbol, OrderType, OrderSide, 
    Quantity, Price, OrderStatus, Fee
)
from app.domain.events.order_placed import OrderPlaced
from datetime import datetime

@dataclass
class Order:
    order_id: UUID
    symbol: Symbol
    type: OrderType
    side: OrderSide
    quantity: Quantity
    price: Price
    status: OrderStatus
    fee: Fee

    def place(self) -> OrderPlaced:
        if self.status != OrderStatus.NEW:
            raise ValueError("Only new orders can be placed")
        self.status = OrderStatus.FILLED  # 簡化示例
        return OrderPlaced(
            order_id=self.order_id,
            symbol=self.symbol,
            side=self.side,
            quantity=self.quantity,
            price=self.price,
            timestamp=datetime.utcnow()
        )
```

#### Portfolio Aggregate
```python
# src/app/domain/entities/portfolio.py
from dataclasses import dataclass, field
from typing import List
from app.domain.entities.position import Position
from app.domain.value_objects import MaxExposure

@dataclass
class Portfolio:
    positions: List[Position] = field(default_factory=list)
    max_exposure: MaxExposure = MaxExposure(1.0)

    def add_position(self, position: Position):
        total_exposure = sum([p.quantity.value for p in self.positions]) + position.quantity.value
        if total_exposure > self.max_exposure.value:
            raise ValueError("Exceeds max exposure")
        self.positions.append(position)
```

> **註**: 其他 Entities / Aggregates 可依需求建立:`Trade`, `Strategy`, `Bot`,遵循同樣模式。

---

## 核心原則

### Value Objects
- ✅ Immutable (不可變)
- ✅ 帶驗證邏輯
- ✅ 封裝單一概念

### Domain Events
- ✅ Immutable (不可變)
- ✅ 只描述 domain 發生的事情
- ✅ 不包含業務邏輯

### Entities / Aggregates
- ✅ 封裝行為
- ✅ 管理 VO 和 Event
- ✅ 保證業務規則一致性

---

## 總結

此 DDD 架構為 QRL/USDT 自動交易機器人提供了:

1. **清晰的領域模型**: 通過 VO、Events 和 Entities 明確表達業務概念
2. **可測試性**: 每個元件都可獨立測試
3. **可維護性**: 分層架構讓程式碼職責清晰
4. **可擴展性**: 新增功能不影響現有架構
5. **型別安全**: 通過 Python 的 dataclass 和型別提示提供編譯時檢查
