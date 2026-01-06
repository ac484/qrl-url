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
    klineUrl: data.kline_url || "/api/qrl/kline?interval=1m&limit=50",
    orderUrl: data.order_url || "/api/qrl/orders",
    balanceUrl: data.balance_url || "/api/account/balance",
    depthUrl: data.depth_url || "/api/market/depth?limit=20",
    tradesUrl: data.trades_url || "/api/market/trades?limit=50",
    ordersUrl: data.orders_url || "/api/trading/orders",
    refreshMs: data.refresh_ms || 10000,
  };
})();
