(() => {
  const cancelOrder = async (cfg, orderId) => {
    if (!orderId) throw new Error("orderId required");
    const url = `${cfg.cancelOrderBase || "/api/trading/orders"}/${orderId}/cancel`;
    const resp = await fetch(url, { method: "POST" });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      const detail = data.detail || JSON.stringify(data);
      throw new Error(detail);
    }
    return data;
  };

  window.orderDomain = { cancelOrder };
})();
