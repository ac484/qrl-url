(() => {
  document.addEventListener("DOMContentLoaded", () => {
    if (window.appDashboard && window.dashboardConfig) {
      window.appDashboard.init(window.dashboardConfig);
    }
  });
})();
