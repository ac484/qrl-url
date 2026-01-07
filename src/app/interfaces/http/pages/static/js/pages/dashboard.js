(() => {
  const cfg = window.dashboardConfig || {};
  const ui = window.dashboardUI || {};
  if (!ui.setPrice || !ui.setText) return;

  const load = async (url) => {
    const resp = await fetch(url);
    let data = {};
    try {
      data = await resp.json();
    } catch (_err) {
      data = {};
    }
    return { ok: resp.ok, data };
  };

  const err = (id, detail, fallback) => ui.setText(id, detail || fallback);
  const orderApi = window.orderDomain || {};
  const ordersList = document.getElementById("orders-list");
  const ordersError = document.getElementById("orders-error");

  const setOrdersMessage = (msg) => {
    if (ordersError) ordersError.textContent = msg || "";
  };

  const wireOrderCancel = () => {
    if (!ordersList || !orderApi.cancelOrder) return;
    ordersList.addEventListener("click", async (evt) => {
      const btn = evt.target.closest(".cancel-btn");
      if (!btn) return;
      const orderId = btn.dataset.id;
      if (!orderId) return;
      btn.disabled = true;
      btn.textContent = "取消中...";
      setOrdersMessage("");
      try {
        await orderApi.cancelOrder(cfg, orderId);
        btn.textContent = "已送出";
        await refresh();
      } catch (ex) {
        btn.disabled = false;
        btn.textContent = "取消";
        setOrdersMessage(ex.message || "取消失敗");
      }
    });
  };

  async function refresh() {
    try {
      const [price, kline, bal, depth, trades, orders] = await Promise.all([
        load(cfg.priceUrl),
        load(cfg.klineUrl),
        load(cfg.balanceUrl),
        load(cfg.depthUrl),
        load(cfg.tradesUrl),
        load(cfg.ordersUrl),
      ]);
      price.ok ? ui.setPrice(price.data) : err("price-error", price.data.detail, "價格取得失敗");
      kline.ok && ui.setKlines(kline.data);
      bal.ok ? ui.setBalances(bal.data) : err("balance-error", bal.data.detail, "餘額取得失敗");
      depth.ok ? ui.setDepth(depth.data) : err("depth-error", depth.data.detail, "Depth 取得失敗");
      trades.ok ? ui.setTrades(trades.data) : err("trades-error", trades.data.detail, "Trades 取得失敗");
      orders.ok ? ui.setOrders(orders.data) : err("orders-error", orders.data.detail, "Orders 取得失敗");
    } catch (ex) {
      ["price", "balance", "depth", "trades", "orders"].forEach((key) => err(`${key}-error`, null, "連線錯誤"));
      console.error(ex);
    }
  }

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
        const resp = await fetch(cfg.orderUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await resp.json().catch(() => ({}));
        resultEl.textContent = resp.ok
          ? `成功: orderId=${data.order_id || data.orderId || "N/A"}`
          : `失敗: ${data.detail || JSON.stringify(data)}`;
      } catch (ex) {
        resultEl.textContent = `錯誤: ${ex}`;
      }
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    wireSideToggle();
    wireOrderForm();
    wireOrderCancel();
    refresh();
    setInterval(refresh, cfg.refreshMs || 10000);
  });
})();
