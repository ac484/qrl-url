(() => {
  const http = window.coreHttp || {};
  const ui = window.dashboardUI || {};
  const state = { cfg: {} };

  const setError = (id, detail, fallback) => {
    if (ui.setError) ui.setError(id, detail, fallback);
  };

  const call = (fn, payload) => {
    if (typeof fn === "function") fn(payload);
  };

  const refresh = async () => {
    const cfg = state.cfg;
    if (!http.fetchJson) return;
    try {
      const [price, kline, bal, depth, trades, orders] = await Promise.all([
        http.fetchJson(cfg.priceUrl),
        http.fetchJson(cfg.klineUrl),
        http.fetchJson(cfg.balanceUrl),
        http.fetchJson(cfg.depthUrl),
        http.fetchJson(cfg.tradesUrl),
        http.fetchJson(cfg.ordersUrl),
      ]);
      price.ok ? call(ui.setPrice, price.data) : setError("price-error", price.data.detail, "價格取得失敗");
      kline.ok && call(ui.setKlines, kline.data);
      bal.ok ? call(ui.setBalances, bal.data) : setError("balance-error", bal.data.detail, "餘額取得失敗");
      depth.ok ? call(ui.setDepth, depth.data) : setError("depth-error", depth.data.detail, "Depth 取得失敗");
      trades.ok ? call(ui.setTrades, trades.data) : setError("trades-error", trades.data.detail, "Trades 取得失敗");
      orders.ok ? call(ui.setOrders, orders.data) : setError("orders-error", orders.data.detail, "Orders 取得失敗");
    } catch (ex) {
      ["price", "balance", "depth", "trades", "orders"].forEach((key) => setError(`${key}-error`, null, "連線錯誤"));
      console.error(ex);
    }
  };

  const wireSideToggle = () => {
    document.querySelectorAll(".side-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".side-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const sideInput = document.querySelector('input[name="side"]');
        if (sideInput) sideInput.value = btn.dataset.side;
      });
    });
  };

  const wireOrderForm = () => {
    const form = document.getElementById("orderForm");
    const resultEl = document.getElementById("orderResult");
    if (!form || !resultEl) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        symbol: "QRLUSDT",
        side: form.side.value,
        order_type: form.order_type.value,
        quantity: form.quantity.value,
        price: form.price.value || null,
        time_in_force: form.time_in_force.value,
      };
      resultEl.textContent = "送出中...";
      try {
        const resp = await http.fetchJson(state.cfg.orderUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = resp.data || {};
        resultEl.textContent = resp.ok
          ? `成功: orderId=${data.order_id || data.orderId || "N/A"}`
          : `失敗: ${data.detail || JSON.stringify(data)}`;
      } catch (ex) {
        resultEl.textContent = `錯誤: ${ex}`;
      }
    });
  };

  const init = (cfg = {}) => {
    state.cfg = cfg;
    if (!http.fetchJson || !ui.setPrice) return;
    wireSideToggle();
    wireOrderForm();
    refresh();
    const interval = Number(cfg.refreshMs || 10000);
    if (interval > 0) setInterval(refresh, interval);
  };

  window.appDashboard = { init, refresh };
})();
