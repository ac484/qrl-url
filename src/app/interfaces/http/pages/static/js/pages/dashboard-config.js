(() => {
  const el = document.getElementById("dashboard-config");
  let data = {};
  if (el) {
    try {
      data = JSON.parse(el.textContent || "{}");
    } catch (err) {
      console.error("Invalid dashboard config", err);
    }
  }

  window.dashboardConfig = {
    priceUrl: data.price_url || "/api/qrl/price",
    // Use daily klines with enough history to compute MA200/RSI/Williams %R
    klineUrl: data.kline_url || "/api/qrl/kline?interval=1d&limit=260",
    orderUrl: data.order_url || "/api/qrl/orders",
    balanceUrl: data.balance_url || "/api/account/balance",
    depthUrl: data.depth_url || "/api/market/depth?limit=20",
    tradesUrl: data.trades_url || "/api/market/trades?limit=50",
    ordersUrl: data.orders_url || "/api/trading/orders",
    refreshMs: data.refresh_ms || 10000,
  };
})();
