(() => {
  const normalize = (raw = {}) => {
    const side = raw.side ?? (raw.isBuyerMaker === true ? "SELL" : raw.isBuyerMaker === false ? "BUY" : "--");
    const ts = raw.timestamp ?? raw.time ?? Date.now();
    return {
      price: raw.price ?? raw.p ?? "--",
      qty: raw.quantity ?? raw.q ?? "--",
      side,
      timestamp: typeof ts === "string" ? ts : new Date(ts).toISOString(),
    };
  };

  const mapList = (items = []) => (Array.isArray(items) ? items : []).map(normalize);

  window.domainTrade = { normalize, mapList };
})();
