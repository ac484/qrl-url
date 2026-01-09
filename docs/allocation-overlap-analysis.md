---
post_title: "Cloud Scheduler allocation overlap analysis"
author1: "copilot"
post_slug: "allocation-overlap-analysis"
microsoft_alias: "copilot"
featured_image: ""
categories: ["architecture"]
tags: ["cloud-run", "cloud-scheduler", "allocation", "performance"]
ai_note: "yes"
summary: "Root cause analysis of overlapping /tasks/allocation runs, options to cut duplicated TLS/HMAC work, and a recommended single-flight guard."
post_date: "2026-01-09"
---

## 現行流程（Scheduler → Application → Domain/Infra）
- Cloud Scheduler calls `POST /tasks/allocation` (or `/api/tasks/allocation`) on Cloud Run.
- FastAPI route → `interfaces/tasks/entrypoints.run_allocation` → `AllocationUseCase`.
- Use case builds a new `MexcService(MexcRestClient(MexcSettings))` per request and performs: `get_account` (signed), `get_price` (public), `get_depth` (public), optional `place_order` (signed).
- REST client enters/exits its own `httpx.AsyncClient` context per call; TLS sessions are not reused across requests.
- Cloud Run deployment (cloudbuild.yaml) sets `--concurrency=80`, `--max-instances=10`, so multiple scheduler attempts or manual triggers can run in parallel on the same or different instances.

## 根因：為何出現重疊與 CPU 放大
1) **缺少 single-flight/idempotency guard**：每個 HTTP 命中都會重新執行完整 allocation 流程，並行請求互不協調。  
2) **平台允許高並發**：Cloud Run concurrency=80、max-instances=10 讓 Scheduler 重試/手動觸發可能同時落在多個 worker。  
3) **每次執行都重建 TLS/HMAC 上下文**：`MexcRestClient` 在 `__aenter__` 內新建 AsyncClient；簽名 `_signed_params` 為每個 signed 呼叫計算 HMAC。當重疊發生時，同樣的帳戶查詢/下單被重複簽名與 TLS 握手，直接放大 CPU。

## 可行優化方案（不改 API contract、不加外部依賴）
**方案 A：Application 單飛（single-flight）守門**  
- 層級：Application entrypoint。  
- 作法：以 in-process task cache/lock 共享同一個 allocation 執行結果，並保留現有回傳結構。  
- 行為不變：路徑/回應 schema 不變；並行請求會拿到同一份 `AllocationResult`。  
- 效益：重疊請求只啟動一次 MexcService/REST client，TLS 握手與簽名只跑一次，CPU 峰值下降。

**方案 B：Platform 收斂並發**  
- 層級：Cloud Run 部署設定。  
- 作法：將 concurrency 下調至 1（或極低）並將 max-instances 鎖定為 1–2，專用於 Scheduler 任務；保持排程頻率不變。  
- 行為不變：同一路由/回應，但請求被序列化處理。  
- 效益：從平台阻擋重疊執行，避免跨實例重複 TLS/HMAC；配合 `TASK_TIMEOUT_SECONDS` 與 Scheduler deadline 一致可減少重試。

**方案 C：Infrastructure 連線重用**  
- 層級：Infrastructure REST client。  
- 作法：改為長存的 AsyncClient/keepalive（在單例 MexcService 中維護），減少 TLS 握手開銷；邏輯與回傳不變。  
- 效益：即便有重疊，TLS 建立次數下降；HMAC 仍會算，但 CPU/延遲較低。

## 推薦與取捨
- **推薦採用方案 A（已於 entrypoints.run_allocation 實作單飛守門），並在部署時調低 Cloud Run concurrency。**  
  - 理由：無外部依賴、不中斷 API schema，立即消除同一時間段的重複 Mexc 呼叫。  
  - Platform 限流（方案 B）建議同步執行以覆蓋跨實例重疊。  
- **未首選方案 C**：僅優化 TLS/連線，但無法阻止業務重複執行；適合作為後續細化而非主要治理手段。
