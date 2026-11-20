/* Shared helpers for the ProviderGate practice portal (fake data only). */
(function () {
  var AUTH_KEY = "pg_auth";
  var USER = { username: "provider.admin", password: "Enroll@2026", otp: "482913", displayName: "Provider Admin" };

  function rid(base) {
    // Realistic-looking DYNAMIC id, different on every page load (selector trap!)
    return base + "_" + Math.random().toString(36).slice(2, 7) + Date.now().toString(36).slice(-4);
  }

  function isAuthed() {
    try {
      var a = JSON.parse(localStorage.getItem(AUTH_KEY));
      return !!(a && a.expires > Date.now());
    } catch (e) { return false; }
  }

  function requireAuth() {
    if (!isAuthed()) {
      var here = location.pathname.split("/").pop() + location.search;
      location.replace("index.html?next=" + encodeURIComponent(here));
      return false;
    }
    return true;
  }

  function signIn() {
    localStorage.setItem(AUTH_KEY, JSON.stringify({ user: USER.username, name: USER.displayName, expires: Date.now() + 8 * 3600 * 1000 }));
  }

  function signOut() { localStorage.removeItem(AUTH_KEY); location.href = "index.html"; }

  function randomizeIds(root) {
    // Every element with data-dyn="ctl00_Main_txtX" gets a random id like ctl00_Main_txtX_k3j9a1xyz
    (root || document).querySelectorAll("[data-dyn]").forEach(function (el) {
      var base = el.getAttribute("data-dyn");
      el.id = rid(base);
      document.querySelectorAll('label[data-dyn-for="' + base + '"]').forEach(function (l) { l.htmlFor = el.id; });
    });
  }

  function header(active) {
    var links = [
      ["dashboard.html", "Dashboard", "nav-dashboard"],
      ["providers.html", "Provider search", "nav-providers"],
      ["license-lookup.html", "License lookup", "nav-license"],
      ["enroll.html", "Enrollment", "nav-enroll"],
      ["downloads.html", "Downloads", "nav-downloads"],
      ["status-queue.html", "Status queue", "nav-slow"],
      ["tools.html", "Help & tools", "nav-tools"]
    ];
    var nav = links.map(function (l) {
      return '<a href="' + l[0] + '" data-testid="' + l[2] + '"' + (l[0] === active ? ' class="active" aria-current="page"' : "") + ">" + l[1] + "</a>";
    }).join("");
    var h = document.createElement("div");
    h.innerHTML =
      '<div class="banner" role="note">Practice portal for learning automation. All data is FAKE. Not affiliated with CMS, PECOS or any payer.</div>' +
      '<header class="topbar"><div class="logo">Provider<span>Gate</span></div><nav aria-label="Main">' + nav + "</nav>" +
      '<div class="who" data-testid="signed-in-user">Signed in as provider.admin</div>' +
      '<button class="ghost" data-testid="logout-button" type="button">Log out</button></header>';
    document.body.insertBefore(h, document.body.firstChild);
    h.querySelector("[data-testid=logout-button]").addEventListener("click", signOut);
  }

  function providerByNpi(npi) {
    return (window.PROVIDERS || []).find(function (p) { return p.npi === String(npi); });
  }

  function expiryDate(p) {
    if (p.licenseStatus === "Pending") return null;
    var d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + p.expiryOffsetDays);
    return d;
  }

  function fmtUS(d) { // MM/DD/YYYY like most US portals
    if (!d) return "";
    return String(d.getMonth() + 1).padStart(2, "0") + "/" + String(d.getDate()).padStart(2, "0") + "/" + d.getFullYear();
  }

  function badge(text) {
    return '<span class="badge b-' + String(text).toLowerCase().replace(/[^a-z]+/g, "-") + '" data-testid="status-badge">' + text + "</span>";
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function qs(name) { return new URLSearchParams(location.search).get(name); }

  window.Portal = { USER: USER, rid: rid, isAuthed: isAuthed, requireAuth: requireAuth, signIn: signIn, signOut: signOut,
    randomizeIds: randomizeIds, header: header, providerByNpi: providerByNpi, expiryDate: expiryDate, fmtUS: fmtUS,
    badge: badge, esc: esc, qs: qs };
})();
