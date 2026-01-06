(() => {
  const createLineChart = (ctx) => {
    if (!ctx || !window.Chart) {
      return { data: { labels: [], datasets: [{ data: [] }] }, update() {} };
    }
    return new Chart(ctx, {
      type: "line",
      data: { labels: [], datasets: [{ data: [], borderColor: "#2196f3", fill: false, tension: 0.2 }] },
      options: {
        animation: false,
        parsing: false,
        normalized: true,
        plugins: { legend: { display: false } },
        scales: { x: { display: true }, y: { display: true } },
      },
    });
  };

  const updateLine = (chart, points = []) => {
    if (!chart) return;
    chart.data.labels = points.map((p) => p.label);
    chart.data.datasets[0].data = points.map((p) => p.value);
    chart.update();
  };

  window.coreChart = { createLineChart, updateLine };
})();
