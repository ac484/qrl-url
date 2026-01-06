(() => {
  const get = (id) => document.getElementById(id);

  const setText = (id, value = "") => {
    const el = get(id);
    if (el) el.textContent = value;
  };

  const setHTML = (id, value = "") => {
    const el = get(id);
    if (el) el.innerHTML = value;
  };

  const setError = (id, detail, fallback = "") => setText(id, detail || fallback);

  window.coreDom = { get, setText, setHTML, setError };
})();
