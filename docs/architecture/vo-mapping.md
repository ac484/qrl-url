## VO Mapping（骨架）

- 來源：docs/mexc-context7-design.md
- 範圍：QRL/USDT、子帳戶
- 已定義 VO/Entity：Symbol, Price, Quantity, Side, OrderId, TradeId, OrderStatus, Timestamp, Ticker, Order, Trade
- MEXC ↔ Domain 對應（位置）：
  - application/trading/mappers/mexc.py（REST/WS order, trade → domain）
  - application/market/mappers/mexc.py（REST/WS ticker → domain）
- Domain 層無映射邏輯；所有 DTO 映射留在 Application / Infrastructure
- TODO：補充 MEXC DTO ↔ Domain VO/Entity 對應欄位與型別細節
