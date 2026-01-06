(() => {
  const dom = window.coreDom || {};
  const chartCore = window.coreChart || {};
  const priceDomain = window.domainPrice || {};
  const depthDomain = window.domainDepth || {};
  const tradeDomain = window.domainTrade || {};
  const orderDomain = window.domainOrder || {};

  const get = dom.get ?? (() => null);
  const setText = dom.setText ?? (() => {});
  const setHTML = dom.setHTML ?? (() => {});
  const setError = dom.setError ?? (() => {});

  const chart = chartCore.createLineChart
    ? chartCore.createLineChart(get("klineChart")?.getContext("2d"))
    : { data: { labels: [], datasets: [{ data: [] }] }, update() {} };

  const setPrice = (payload) => {
    const d = priceDomain.toView ? priceDomain.toView(payload) : payload || {};
    setError("price-error", "");
    setText("bid", d.bid ?? "--");
    setText("ask", d.ask ?? "--");
    setText("last", d.last ?? "--");
    const parsed = typeof d.timestamp === "number" || typeof d.timestamp === "string" ? new Date(d.timestamp) : new Date();
    setText("timestamp", parsed.toISOString());
  };

  const setKlines = (items = []) => {
    const list = Array.isArray(items) ? items : [];
    const points = list.map((k) => ({ label: new Date(k.timestamp).toLocaleTimeString(), value: Number(k.close) }));
    if (chartCore.updateLine) chartCore.updateLine(chart, points);
  };

  const setBalances = (payload = {}) => {
    setError("balance-error", "");
    const balances = payload.balances || [];
    const byAsset = (asset) => balances.find((b) => b.asset === asset) || { free: "--", locked: "--" };
    const qrl = byAsset("QRL");
    const usdt = byAsset("USDT");
    setText("bal-qrl-free", qrl.free);
    setText("bal-qrl-locked", qrl.locked);
    setText("bal-usdt-free", usdt.free);
    setText("bal-usdt-locked", usdt.locked);
  };

  const setDepth = (payload = {}) => {
    setError("depth-error", "");
    const bids = depthDomain.mapList ? depthDomain.mapList(payload.bids) : payload.bids || [];
    const asks = depthDomain.mapList ? depthDomain.mapList(payload.asks) : payload.asks || [];
    const build = (items = []) =>
      items
        .slice(0, 10)
        .map((entry) => `<li><span class="price">${entry.price}</span><span class="qty">${entry.qty}</span></li>`)
        .join("");
    setHTML("depth-bids", build(bids));
    setHTML("depth-asks", build(asks));
  };

  const setTrades = (payload = []) => {
    setError("trades-error", "");
    const list = tradeDomain.mapList ? tradeDomain.mapList(payload) : payload;
    setHTML(
      "trades-list",
      list
        .slice(0, 20)
        .map(
          (t) =>
            `<li><span class="side ${t.side === "BUY" ? "buy" : "sell"}">${t.side}</span><span class="price">${t.price}</span><span class="qty">${t.qty}</span><span class="ts">${t.timestamp}</span></li>`,
        )
        .join(""),
    );
  };

  const setOrders = (payload = []) => {
    setError("orders-error", "");
    const list = orderDomain.mapList ? orderDomain.mapList(payload) : payload;
    setHTML(
      "orders-list",
      list
        .slice(0, 20)
        .map(
          (o) =>
            `<li><span class="id">${o.id}</span><span class="side ${o.side === "BUY" ? "buy" : "sell"}">${o.side}</span><span class="price">${o.price}</span><span class="qty">${o.qty}</span><span class="status">${o.status}</span></li>`,
        )
        .join(""),
    );
  };

  window.dashboardUI = { setText, setError, setPrice, setKlines, setBalances, setDepth, setTrades, setOrders };
})();
