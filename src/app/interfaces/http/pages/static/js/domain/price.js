(() => {
  const toView = (raw = {}) => ({
    bid: raw.bid ?? raw.bidPrice ?? raw.bid_price ?? "--",
    ask: raw.ask ?? raw.askPrice ?? raw.ask_price ?? "--",
    last: raw.last ?? raw.lastPrice ?? raw.last_price ?? "--",
    timestamp: raw.timestamp ?? raw.ts ?? Date.now(),
  });

  window.domainPrice = { toView };
})();
