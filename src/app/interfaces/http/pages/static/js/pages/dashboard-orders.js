(() => {
  const cfg = window.dashboardConfig || {};
  const ui = window.dashboardUI || {};
  const baseCancel = (cfg.cancelUrl || cfg.ordersUrl || "/api/trading/orders").replace(/\/$/, "");
  const normalizeOrder = (o = {}) => ({
    id: o.order_id ?? o.orderId ?? "--",
    side: o.side ?? "--",
    status: o.status ?? "--",
    price: o.price ?? o.limit_price ?? "--",
    qty: o.quantity ?? o.orig_qty ?? "--",
  });
  const cancelable = (status) => !["CANCELED", "FILLED", "REJECTED"].includes((status || "").toUpperCase());
  const actionCell = (id, status) =>
    cancelable(status)
      ? `<button type="button" data-cancel-id="${id}" aria-label="取消訂單 ${id}">取消</button>`
      : `<span class="muted">${status || "--"}</span>`;
  const setOrders = (payload = []) => {
    ui.setText && ui.setText("orders-error", "");
    const el = document.getElementById("orders-list");
    if (!el) return;
    el.innerHTML = (payload || [])
      .slice(0, 20)
      .map((o) => {
        const n = normalizeOrder(o);
        const sideClass = n.side === "BUY" ? "buy" : n.side === "SELL" ? "sell" : "";
        return `<li data-order-id="${n.id}"><span class="id">${n.id}</span><span class="side ${sideClass}">${n.side}</span><span class="price">${n.price}</span><span class="qty">${n.qty}</span><span class="status">${n.status}</span><span class="action">${actionCell(n.id, n.status)}</span></li>`;
      })
      .join("");
  };
  const cancelOrder = async (btn) => {
    const id = btn?.dataset?.cancelId;
    if (!id) return;
    btn.disabled = true;
    const original = btn.textContent;
    btn.textContent = "取消中...";
    try {
      const resp = await fetch(`${baseCancel}/${encodeURIComponent(id)}/cancel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        ui.setText && ui.setText("orders-error", data.detail || data.message || "取消失敗");
        btn.disabled = false;
        btn.textContent = original;
        return;
      }
      ui.setText && ui.setText("orders-error", "");
      window.dashboardRefresh && window.dashboardRefresh();
    } catch (err) {
      ui.setText && ui.setText("orders-error", `取消失敗: ${err}`);
      btn.disabled = false;
      btn.textContent = original;
    }
  };
  const wireCancel = () => {
    const el = document.getElementById("orders-list");
    if (!el) return;
    el.addEventListener("click", (event) => {
      const btn = event.target.closest("[data-cancel-id]");
      if (!btn) return;
      event.preventDefault();
      cancelOrder(btn);
    });
  };
  wireCancel();
  window.dashboardUI = { ...ui, setOrders };
})();
