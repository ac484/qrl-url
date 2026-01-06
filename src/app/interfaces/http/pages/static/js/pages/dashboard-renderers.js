(() => {
  const $ = (id) => document.getElementById(id);
  const setText = (id, v = "") => {
    const el = $(id);
    if (el) el.textContent = v;
  };

  const chartEl = $("klineChart");

  const priceChart =
    window.Chart && chartEl
      ? new Chart(chartEl.getContext("2d"), {
          type: "line",
          data: {
            labels: [],
            datasets: [
              { label: "Close", data: [], borderColor: "#2196f3", fill: false, tension: 0.2, pointRadius: 0, yAxisID: "y" },
              {
                label: "MA200 (1d)",
                data: [],
                borderColor: "#ff9800",
                fill: false,
                tension: 0.15,
                borderDash: [6, 3],
                pointRadius: 0,
                yAxisID: "y",
              },
              {
                label: "RSI 21",
                data: [],
                borderColor: "#673ab7",
                fill: false,
                pointRadius: 0,
                tension: 0.2,
                yAxisID: "y1",
              },
              {
                label: "Williams %R 21",
                data: [],
                borderColor: "#2e7d32",
                fill: false,
                pointRadius: 0,
                tension: 0.2,
                yAxisID: "y1",
              },
            ],
          },
          options: {
            responsive: true,
            interaction: { intersect: false, mode: "index" },
            plugins: { legend: { display: true } },
            scales: {
              y: { title: { display: true, text: "Price" } },
              y1: {
                position: "right",
                title: { display: true, text: "Oscillators" },
                suggestedMin: -100,
                suggestedMax: 100,
                grid: { drawOnChartArea: false },
              },
            },
          },
        })
      : { data: { labels: [], datasets: [{ data: [] }, { data: [] }, { data: [] }, { data: [] }] }, update() {} };

  const computeSMA = (values, period) => {
    const out = values.map(() => null);
    let sum = 0;
    for (let i = 0; i < values.length; i += 1) {
      sum += values[i];
      if (i >= period) sum -= values[i - period];
      if (i >= period - 1) out[i] = sum / period;
    }
    return out;
  };

  const computeRSI = (values, period) => {
    const out = values.map(() => null);
    if (values.length < period + 1) return out;
    let gainSum = 0;
    let lossSum = 0;
    for (let i = 1; i <= period; i += 1) {
      const change = values[i] - values[i - 1];
      if (change >= 0) gainSum += change;
      else lossSum -= change;
    }
    let avgGain = gainSum / period;
    let avgLoss = lossSum / period;
    const rs = avgLoss === 0 ? Number.POSITIVE_INFINITY : avgGain / avgLoss;
    out[period] = avgLoss === 0 ? 100 : 100 - 100 / (1 + rs);
    for (let i = period + 1; i < values.length; i += 1) {
      const change = values[i] - values[i - 1];
      const gain = Math.max(change, 0);
      const loss = Math.max(-change, 0);
      avgGain = ((avgGain * (period - 1)) + gain) / period;
      avgLoss = ((avgLoss * (period - 1)) + loss) / period;
      if (avgLoss === 0) out[i] = 100;
      else {
        const nextRs = avgGain / avgLoss;
        out[i] = 100 - 100 / (1 + nextRs);
      }
    }
    return out;
  };

  const computeWilliamsR = (highs, lows, closes, period) => {
    const out = closes.map(() => null);
    for (let i = period - 1; i < closes.length; i += 1) {
      let highest = highs[i];
      let lowest = lows[i];
      for (let j = i - period + 1; j <= i; j += 1) {
        if (highs[j] > highest) highest = highs[j];
        if (lows[j] < lowest) lowest = lows[j];
      }
      const range = highest - lowest;
      out[i] = range === 0 ? null : ((highest - closes[i]) / range) * -100;
    }
    return out;
  };

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
    const labels = items.map((k) => new Date(k.timestamp).toLocaleDateString());
    const closes = items.map((k) => Number(k.close));
    const highs = items.map((k) => Number(k.high));
    const lows = items.map((k) => Number(k.low));

    const ma200 = computeSMA(closes, 200);
    const rsi21 = computeRSI(closes, 21);
    const williams21 = computeWilliamsR(highs, lows, closes, 21);

    priceChart.data.labels = labels;
    priceChart.data.datasets[0].data = closes;
    priceChart.data.datasets[1].data = ma200;
    priceChart.data.datasets[2].data = rsi21;
    priceChart.data.datasets[3].data = williams21;
    priceChart.update();
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
