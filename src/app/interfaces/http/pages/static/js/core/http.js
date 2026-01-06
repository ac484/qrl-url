(() => {
  const fetchJson = async (url, options = {}) => {
    const resp = await fetch(url, options);
    let data = {};
    try {
      data = await resp.json();
    } catch (_err) {
      data = {};
    }
    return { ok: resp.ok, data };
  };

  window.coreHttp = { fetchJson };
})();
