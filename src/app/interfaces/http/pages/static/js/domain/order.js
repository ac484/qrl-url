(() => {
  const normalize = (raw = {}) => ({
    id: raw.order_id ?? raw.orderId ?? "--",
    side: raw.side ?? "--",
    price: raw.price ?? raw.limit_price ?? "--",
    qty: raw.quantity ?? raw.orig_qty ?? "--",
    status: raw.status ?? "--",
  });

  const mapList = (items = []) => (Array.isArray(items) ? items : []).map(normalize);

  window.domainOrder = { normalize, mapList };
})();
