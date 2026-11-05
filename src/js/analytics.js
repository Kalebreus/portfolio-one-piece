(() => {
  const endpoint = window.PORTFOLIO_CONFIG?.analyticsEndpoint?.trim();
  const banner = document.querySelector("#consent-banner");
  if (!endpoint || !banner) return;

  const key = "portfolio-analytics-consent";
  const accept = document.querySelector("#consent-accept");
  const reject = document.querySelector("#consent-reject");

  const sendPageView = () => {
    fetch(endpoint, {
      method: "POST",
      mode: "cors",
      credentials: "omit",
      keepalive: true,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event: "page_view" })
    }).catch(() => {});
  };

  let choice = null;
  try { choice = localStorage.getItem(key); } catch {}
  if (choice === "accepted") sendPageView();
  if (choice !== "accepted" && choice !== "rejected") banner.hidden = false;

  accept?.addEventListener("click", () => {
    try { localStorage.setItem(key, "accepted"); } catch {}
    banner.hidden = true;
    sendPageView();
  });
  reject?.addEventListener("click", () => {
    try { localStorage.setItem(key, "rejected"); } catch {}
    banner.hidden = true;
  });
})();