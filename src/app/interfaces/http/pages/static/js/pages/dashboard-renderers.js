(() => {
  const $ = (id) => document.getElementById(id);
  const setText = (id, v = "") => {
    const el = $(id);
    if (el) el.textContent = v;
  };

  const chartEl = $("klineChart");
  const chart =
    window.Chart && chartEl
      ? new Chart(chartEl.getContext("2d"), {
          type: "line",
          data: { labels: [], datasets: [{ data: [], borderColor: "#2196f3", fill: false, tension: 0.2 }] },
        })
      : { data: { labels: [], datasets: [{ data: [] }] }, update() {} };

  const setPrice = (d) => {
    setText("price-error", "");
    setText("bid", d?.bid ?? "--");
    setText("ask", d?.ask ?? "--");
    setText("last", d?.last ?? "--");
    const raw = d?.timestamp;
    const parsed = typeof raw === "number" || typeof raw === "string" ? new Date(raw) : new Date();
    setText("timestamp", parsed.toISOString());
  };

  const setKlines = (items = []) => {
    chart.data.labels = items.map((k) => new Date(k.timestamp).toLocaleTimeString());
    chart.data.datasets[0].data = items.map((k) => Number(k.close));
    chart.update();
  };

  const setBalances = (payload = {}) => {
    setText("balance-error", "");
    const balances = payload.balances || [];
    const byAsset = (asset) => balances.find((b) => b.asset === asset) || { free: "--", locked: "--" };
    const qrl = byAsset("QRL");
    const usdt = byAsset("USDT");
    setText("bal-qrl-free", qrl.free);
    setText("bal-qrl-locked", qrl.locked);
    setText("bal-usdt-free", usdt.free);
    setText("bal-usdt-locked", usdt.locked);
  };

  const normalizeDepth = (item) => (Array.isArray(item) ? { price: item[0], qty: item[1] } : { price: item?.price ?? item?.p ?? "--", qty: item?.quantity ?? item?.q ?? "--" });

  const setDepth = (payload = {}) => {
    setText("depth-error", "");
    const bidsEl = $("depth-bids");
    const asksEl = $("depth-asks");
    const build = (items = []) =>
      items
        .slice(0, 10)
        .map((entry) => {
          const { price, qty } = normalizeDepth(entry);
          return `<li><span class="price">${price}</span><span class="qty">${qty}</span></li>`;
        })
        .join("");
    if (bidsEl) bidsEl.innerHTML = build(payload.bids);
    if (asksEl) asksEl.innerHTML = build(payload.asks);
  };

  const normalizeTrade = (t = {}) => {
    const side = t.side ?? (t.isBuyerMaker === true ? "SELL" : t.isBuyerMaker === false ? "BUY" : "--");
    const tsRaw = t.timestamp ?? t.time ?? Date.now();
    return { price: t.price ?? t.p ?? "--", qty: t.quantity ?? t.q ?? "--", side, ts: typeof tsRaw === "string" ? tsRaw : new Date(tsRaw).toISOString() };
  };

  const setTrades = (payload = []) => {
    setText("trades-error", "");
    const el = $("trades-list");
    if (!el) return;
    el.innerHTML = payload
      .slice(0, 20)
      .map((t) => {
        const n = normalizeTrade(t);
        return `<li><span class="side ${n.side === "BUY" ? "buy" : "sell"}">${n.side}</span><span class="price">${n.price}</span><span class="qty">${n.qty}</span><span class="ts">${n.ts}</span></li>`;
      })
      .join("");
  };

  const normalizeOrder = (o = {}) => ({ side: o.side ?? "--", status: o.status ?? "--", price: o.price ?? o.limit_price ?? "--", qty: o.quantity ?? o.orig_qty ?? "--", id: o.order_id ?? o.orderId ?? "--" });

  const setOrders = (payload = []) => {
    setText("orders-error", "");
    const el = $("orders-list");
    if (!el) return;
    el.innerHTML = payload
      .slice(0, 20)
      .map((o) => {
        const n = normalizeOrder(o);
        return `<li><span class="id">${n.id}</span><span class="side ${n.side === "BUY" ? "buy" : "sell"}">${n.side}</span><span class="price">${n.price}</span><span class="qty">${n.qty}</span><span class="status">${n.status}</span></li>`;
      })
      .join("");
  };

  window.dashboardUI = { setText, setPrice, setKlines, setBalances, setDepth, setTrades, setOrders };
})();
