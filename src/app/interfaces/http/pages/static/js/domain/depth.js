(() => {
  const normalize = (raw = {}) => {
    if (Array.isArray(raw)) {
      return { price: raw[0] ?? "--", qty: raw[1] ?? "--" };
    }
    return { price: raw.price ?? raw.p ?? "--", qty: raw.quantity ?? raw.q ?? "--" };
  };

  const mapList = (items = []) => (Array.isArray(items) ? items : []).map(normalize);

  window.domainDepth = { normalize, mapList };
})();
