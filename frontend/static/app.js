/* PowerGuard v3 — Full Frontend */

const PAGE_META = {
  dashboard: { title: "Dashboard", subtitle: "Real-time electricity theft monitoring overview" },
  search: { title: "Search Consumers", subtitle: "Search 15,000 records by ID, name, CNIC, or meter number" },
  consumers: { title: "All Consumers", subtitle: "Browse and filter the full consumer directory" },
  analytics: { title: "Analytics", subtitle: "Regional insights and distribution company breakdown" },
  cloud: { title: "Cloud Architecture", subtitle: "How cloud computing powers this theft detection system" },
  data: { title: "Data Management", subtitle: "Data collection, storage, indexing, and ML processing pipeline" },
  models: { title: "ML Models", subtitle: "Decision Tree, Random Forest, and Logistic Regression comparison" },
  batch: { title: "Batch Analysis", subtitle: "Bulk CSV upload processed on cloud compute" },
};

let charts = {};
let currentPage = 1;
let searchCurrentPage = 1;
let currentSearchType = "all";
let currentSearchQuery = "";
let consumptionChartInstance = null;
let acDebounce = null;

// ── Navigation ──────────────────────────────────────────

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => navigateTo(btn.dataset.page));
});

function navigateTo(page) {
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
  document.querySelectorAll(".page").forEach((p) => p.classList.toggle("active", p.id === `page-${page}`));
  const meta = PAGE_META[page];
  document.getElementById("pageTitle").textContent = meta.title;
  document.getElementById("pageSubtitle").textContent = meta.subtitle;

  if (page === "dashboard") loadDashboard();
  if (page === "analytics") loadAnalytics();
  if (page === "models") loadModels();
  if (page === "consumers") loadConsumers(1);
  if (page === "cloud") loadCloud();
  if (page === "data") loadDataManagement();
  if (page === "search") document.getElementById("mainSearchInput").focus();
}

// ── API ─────────────────────────────────────────────────

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : "Request failed");
  }
  return res.json();
}

const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 }));
const fmtCurrency = (n) => `PKR ${fmt(n)}`;

// ── Autocomplete ────────────────────────────────────────

function setupAutocomplete(inputEl, dropdownEl, onSelect) {
  inputEl.addEventListener("input", () => {
    clearTimeout(acDebounce);
    const q = inputEl.value.trim();
    if (q.length < 1) { dropdownEl.classList.add("hidden"); return; }
    acDebounce = setTimeout(() => fetchAutocomplete(q, currentSearchType, dropdownEl, onSelect), 250);
  });

  inputEl.addEventListener("keydown", (e) => {
    const items = dropdownEl.querySelectorAll(".ac-item");
    const focused = dropdownEl.querySelector(".ac-item.focused");
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!focused) items[0]?.classList.add("focused");
      else { focused.classList.remove("focused"); items[[...items].indexOf(focused) + 1]?.classList.add("focused"); }
    } else if (e.key === "ArrowUp" && focused) {
      e.preventDefault();
      focused.classList.remove("focused");
      items[[...items].indexOf(focused) - 1]?.classList.add("focused");
    } else if (e.key === "Enter" && focused) {
      e.preventDefault();
      onSelect(focused.dataset.id);
    } else if (e.key === "Escape") {
      dropdownEl.classList.add("hidden");
    }
  });

  document.addEventListener("click", (e) => {
    if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
      dropdownEl.classList.add("hidden");
    }
  });
}

async function fetchAutocomplete(q, type, dropdownEl, onSelect) {
  try {
    const data = await fetchJson(`/api/search/autocomplete?q=${encodeURIComponent(q)}&type=${type}&limit=10`);
    if (!data.results.length) {
      dropdownEl.innerHTML = `<div class="ac-empty">No results for "${q}"</div>`;
    } else {
      dropdownEl.innerHTML = data.results.map((r) => `
        <div class="ac-item" data-id="${r.consumer_id}" tabindex="0">
          <div class="ac-item-left">
            <strong>${r.full_name}</strong>
            <small>${r.region} · ${r.connection_type} · ${fmt(r.monthly_consumption)} units</small>
          </div>
          <div>
            <div class="ac-item-id">${r.consumer_id}</div>
            <span class="badge ${r.label.toLowerCase()}">${r.label}</span>
          </div>
        </div>
      `).join("");
      dropdownEl.querySelectorAll(".ac-item").forEach((item) => {
        item.addEventListener("click", () => onSelect(item.dataset.id));
      });
    }
    dropdownEl.classList.remove("hidden");
  } catch { dropdownEl.classList.add("hidden"); }
}

// Global search autocomplete
setupAutocomplete(
  document.getElementById("globalSearchInput"),
  document.getElementById("globalAutocomplete"),
  (id) => { navigateTo("search"); openConsumer(id); }
);

// Main search autocomplete
setupAutocomplete(
  document.getElementById("mainSearchInput"),
  document.getElementById("mainAutocomplete"),
  (id) => openConsumer(id)
);

// Search type tabs
document.querySelectorAll(".search-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".search-tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    currentSearchType = tab.dataset.type;
    const placeholders = {
      all: "Type to search... e.g. CONS-10001 or Ahmed Khan",
      id: "Enter Consumer ID... e.g. CONS-10001",
      name: "Enter full or partial name... e.g. Ahmed Khan",
      cnic: "Enter CNIC... e.g. 35201-1234567-1",
      meter: "Enter meter number... e.g. MTR-123456",
    };
    document.getElementById("mainSearchInput").placeholder = placeholders[currentSearchType];
  });
});

// Example chips
document.querySelectorAll(".chip-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const q = btn.dataset.query;
    const type = btn.dataset.type || "all";
    if (type !== "all") {
      document.querySelectorAll(".search-tab").forEach((t) => t.classList.toggle("active", t.dataset.type === type));
      currentSearchType = type;
    }
    document.getElementById("mainSearchInput").value = q;
    runSearch(q, 1);
  });
});

document.getElementById("mainSearchBtn").addEventListener("click", () => {
  runSearch(document.getElementById("mainSearchInput").value.trim(), 1);
});

document.getElementById("mainSearchInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !document.getElementById("mainAutocomplete").querySelector(".ac-item.focused")) {
    e.preventDefault();
    runSearch(e.target.value.trim(), 1);
  }
});

document.getElementById("globalSearchForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = document.getElementById("globalSearchInput").value.trim();
  if (!q) return;
  navigateTo("search");
  document.getElementById("mainSearchInput").value = q;
  runSearch(q, 1);
});

// ── Search Flow ─────────────────────────────────────────

async function runSearch(query, page = 1) {
  if (!query) return;
  currentSearchQuery = query;
  searchCurrentPage = page;

  document.getElementById("lookupResult").classList.add("hidden");
  document.getElementById("lookupError").classList.add("hidden");
  document.getElementById("mainAutocomplete").classList.add("hidden");

  const panel = document.getElementById("searchResultsPanel");
  panel.classList.remove("hidden");

  const params = new URLSearchParams({ q: query, page, page_size: 12 });
  if (currentSearchType !== "all") params.set("type", currentSearchType);

  // Use consumers search API for paginated results
  const data = await fetchJson(`/api/consumers/search?${params}`);

  document.getElementById("searchResultsTitle").textContent = `Results for "${query}"`;
  document.getElementById("searchResultsCount").textContent = `${data.total.toLocaleString()} found`;

  if (data.total === 1) {
    openConsumer(data.results[0].consumer_id);
    return;
  }

  document.getElementById("searchResultsGrid").innerHTML = data.results.map((c) => `
    <div class="result-card" data-id="${c.consumer_id}">
      <div class="result-card-top">
        <div>
          <h4>${c.full_name}</h4>
          <div class="rc-id">${c.consumer_id}</div>
        </div>
        <span class="badge ${c.label.toLowerCase()}">${c.label}</span>
      </div>
      <div class="rc-meta">
        ${c.region} · ${c.city}<br>
        ${c.connection_type} · ${fmt(c.monthly_consumption)} units<br>
        Bill: ${fmtCurrency(c.billing_amount)} · ${c.payment_status}
      </div>
    </div>
  `).join("") || `<div class="ac-empty">No consumers found for "${query}"</div>`;

  document.querySelectorAll(".result-card").forEach((card) => {
    card.addEventListener("click", () => openConsumer(card.dataset.id));
  });

  renderSearchPagination(data);
}

function renderSearchPagination(data) {
  const el = document.getElementById("searchPagination");
  if (data.total_pages <= 1) { el.innerHTML = ""; return; }
  el.innerHTML = `
    <button ${data.page <= 1 ? "disabled" : ""} id="searchPrev">← Previous</button>
    <span>Page ${data.page} of ${data.total_pages}</span>
    <button ${data.page >= data.total_pages ? "disabled" : ""} id="searchNext">Next →</button>
  `;
  document.getElementById("searchPrev")?.addEventListener("click", () => runSearch(currentSearchQuery, searchCurrentPage - 1));
  document.getElementById("searchNext")?.addEventListener("click", () => runSearch(currentSearchQuery, searchCurrentPage + 1));
}

async function openConsumer(consumerId) {
  document.getElementById("globalSearchInput").value = consumerId;
  document.getElementById("mainSearchInput").value = consumerId;
  document.getElementById("searchResultsPanel").classList.add("hidden");
  document.getElementById("globalAutocomplete").classList.add("hidden");
  document.getElementById("mainAutocomplete").classList.add("hidden");

  const loading = document.getElementById("lookupLoading");
  const error = document.getElementById("lookupError");
  const result = document.getElementById("lookupResult");

  loading.classList.remove("hidden");
  error.classList.add("hidden");
  result.classList.add("hidden");

  try {
    const data = await fetchJson(`/api/consumers/${encodeURIComponent(consumerId)}`);
    renderConsumerDetail(data);
    result.classList.remove("hidden");
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
  }
}

function renderConsumerDetail(data) {
  const { profile, consumption, billing, detection } = data;
  const isTheft = detection.prediction === "Theft";

  document.getElementById("lookupResult").innerHTML = `
    <button class="back-btn" id="backToResults">← Back to search results</button>
    <div class="consumer-detail">
      <div class="detail-header">
        <div>
          <h2>${profile.full_name}</h2>
          <div class="consumer-id">${profile.consumer_id}</div>
          <div class="meta-line">${profile.address} · ${profile.city}, ${profile.region}</div>
          <div class="meta-line">${profile.distribution_company} · Meter: ${profile.meter_number} (${profile.meter_type})</div>
        </div>
        <div class="detection-banner ${isTheft ? "theft" : "normal"}">
          <div class="result-label">${isTheft ? "⚠ THEFT DETECTED" : "✓ NORMAL ACCOUNT"}</div>
          <div class="confidence">${detection.confidence}% confidence · ${detection.risk_level} risk</div>
          <div class="match-indicator">${detection.model_match ? "✓ Model agrees with ground truth" : "✗ Model differs from label (" + detection.actual_label + ")"}</div>
        </div>
      </div>
      <div class="detail-grid">
        <div class="detail-section"><h3>Personal Information</h3>
          ${detailRow("Full Name", profile.full_name)}
          ${detailRow("CNIC", profile.cnic)}
          ${detailRow("Phone", profile.phone)}
          ${detailRow("Email", profile.email)}
          ${detailRow("Address", profile.address)}
          ${detailRow("City / Region", `${profile.city}, ${profile.region}`)}
          ${detailRow("Registered", profile.registration_date)}
        </div>
        <div class="detail-section"><h3>Account & Meter</h3>
          ${detailRow("Distribution Co.", profile.distribution_company)}
          ${detailRow("Meter Number", profile.meter_number)}
          ${detailRow("Meter Type", profile.meter_type)}
          ${detailRow("Connection Type", profile.connection_type)}
          ${detailRow("Tariff", profile.tariff_category)}
          ${detailRow("Sanctioned Load", `${profile.sanctioned_load_kw} kW`)}
          ${detailRow("Status", `<span class="badge ${profile.account_status.toLowerCase().replace(/\s+/g, "-")}">${profile.account_status}</span>`)}
        </div>
        <div class="detail-section"><h3>Consumption Data</h3>
          ${detailRow("Current Month", `${fmt(consumption.monthly_consumption)} units`)}
          ${detailRow("Previous Month", `${fmt(consumption.previous_month_consumption)} units`)}
          ${detailRow("Change", `${consumption.consumption_change > 0 ? "+" : ""}${fmt(consumption.consumption_change)} units`)}
          ${detailRow("Area Average", `${fmt(consumption.area_average_consumption)} units`)}
          ${detailRow("vs Area Avg", `${consumption.usage_vs_area_average > 0 ? "+" : ""}${fmt(consumption.usage_vs_area_average)} units`)}
          ${detailRow("Peak Load", `${consumption.peak_load_kw} kW`)}
          ${detailRow("Power Factor", consumption.power_factor)}
          ${detailRow("Meter Diff", fmt(consumption.meter_reading_difference))}
        </div>
        <div class="detail-section"><h3>Billing</h3>
          ${detailRow("Current Bill", fmtCurrency(billing.current_bill))}
          ${detailRow("Previous Bill", fmtCurrency(billing.previous_bill))}
          ${detailRow("Change", fmtCurrency(billing.bill_change))}
          ${detailRow("Payment", `<span class="badge ${billing.payment_status.toLowerCase()}">${billing.payment_status}</span>`)}
          ${detailRow("Outstanding", fmtCurrency(billing.outstanding_balance))}
        </div>
        <div class="detail-section"><h3>ML Detection</h3>
          ${detailRow("Prediction", `<span class="badge ${detection.prediction.toLowerCase()}">${detection.prediction}</span>`)}
          ${detailRow("Confidence", `${detection.confidence}%`)}
          ${detailRow("Risk Level", `<span class="badge ${detection.risk_level.toLowerCase()}">${detection.risk_level}</span>`)}
          ${detailRow("Normal Prob.", `${detection.probability_normal}%`)}
          ${detailRow("Theft Prob.", `${detection.probability_theft}%`)}
          ${detailRow("Model", detection.model_used.replaceAll("_", " "))}
          ${detailRow("Ground Truth", `<span class="badge ${detection.actual_label.toLowerCase()}">${detection.actual_label}</span>`)}
        </div>
        <div class="detail-section"><h3>Risk Factors</h3>
          <div class="risk-factors">${detection.risk_factors.map((f) => `
            <div class="risk-item"><div class="risk-dot ${f.severity}"></div>
              <div><strong>${f.factor}</strong><br><span style="color:var(--muted)">${f.detail}</span></div>
            </div>`).join("")}
          </div>
        </div>
      </div>
      <div class="detail-section">
        <h3>6-Month Consumption History</h3>
        <div class="chart-container"><canvas id="consumptionChart"></canvas></div>
      </div>
    </div>
  `;

  document.getElementById("backToResults")?.addEventListener("click", () => {
    document.getElementById("lookupResult").classList.add("hidden");
    if (currentSearchQuery) {
      document.getElementById("searchResultsPanel").classList.remove("hidden");
    }
  });

  if (consumptionChartInstance) consumptionChartInstance.destroy();
  consumptionChartInstance = new Chart(document.getElementById("consumptionChart"), {
    type: "line",
    data: {
      labels: consumption.history.map((h) => h.month).reverse(),
      datasets: [{
        label: "Units (kWh)", data: consumption.history.map((h) => h.units).reverse(),
        borderColor: isTheft ? "#ef4444" : "#3b82f6",
        backgroundColor: isTheft ? "rgba(239,68,68,0.1)" : "rgba(59,130,246,0.1)",
        fill: true, tension: 0.3, pointRadius: 5,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#8fa3c7" }, grid: { color: "rgba(148,163,184,0.08)" } },
        y: { ticks: { color: "#8fa3c7" }, grid: { color: "rgba(148,163,184,0.08)" } },
      },
      plugins: { legend: { labels: { color: "#8fa3c7" } } },
    },
  });
}

function detailRow(key, val) {
  return `<div class="detail-row"><span class="key">${key}</span><span class="val">${val}</span></div>`;
}

// ── Dashboard ───────────────────────────────────────────

async function loadDashboard() {
  const [analytics, metrics, history] = await Promise.all([
    fetchJson("/api/analytics"), fetchJson("/api/metrics"), fetchJson("/api/predictions/history"),
  ]);

  document.getElementById("sidebarRecordCount").textContent = `${analytics.total_consumers.toLocaleString()} records`;

  document.getElementById("statsRow").innerHTML = `
    <div class="stat-box"><span class="value">${analytics.total_consumers.toLocaleString()}</span><span class="label">Total Consumers</span></div>
    <div class="stat-box danger"><span class="value">${analytics.theft_cases.toLocaleString()}</span><span class="label">Theft Cases (${analytics.theft_percentage}%)</span></div>
    <div class="stat-box success"><span class="value">${analytics.normal_cases.toLocaleString()}</span><span class="label">Normal Accounts</span></div>
    <div class="stat-box"><span class="value">${metrics.accuracy}%</span><span class="label">ML Accuracy</span></div>
    <div class="stat-box warning"><span class="value">${analytics.overdue_accounts.toLocaleString()}</span><span class="label">Overdue Accounts</span></div>
  `;

  document.getElementById("modelChip").textContent = metrics.model.replaceAll("_", " ").toUpperCase();
  document.getElementById("metricsRow").innerHTML = renderMetricCards(metrics);
  renderRegionChart("regionChart", analytics.by_region);
  renderHistory(history);
}

function renderMetricCards(m) {
  return ["accuracy", "precision", "recall", "f1_score"].map((k) =>
    `<div class="metric-card"><strong>${m[k]}%</strong><span>${k.replace("_", " ").replace("f1", "F1")}</span></div>`
  ).join("");
}

function renderHistory(rows) {
  const body = document.getElementById("historyBody");
  body.innerHTML = rows.length ? rows.slice(0, 10).map((r) => `
    <tr style="cursor:pointer" onclick="openConsumer('${r.consumer_id}')">
      <td><code>${r.consumer_id}</code></td><td>${r.region}</td>
      <td><span class="badge ${r.prediction.toLowerCase()}">${r.prediction}</span></td>
      <td>${r.confidence}%</td>
      <td><span class="badge ${(r.risk_level || "low").toLowerCase()}">${r.risk_level || "—"}</span></td>
    </tr>`).join("") : `<tr><td colspan="5" style="text-align:center;color:var(--muted)">Search a consumer to see detections here</td></tr>`;
}

function renderRegionChart(id, data) {
  destroyChart(id);
  const ctx = document.getElementById(id);
  if (!ctx) return;
  charts[id] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map((d) => d.region),
      datasets: [
        { label: "Theft", data: data.map((d) => d.theft_count), backgroundColor: "rgba(239,68,68,0.75)", borderRadius: 6 },
        { label: "Normal", data: data.map((d) => d.count - d.theft_count), backgroundColor: "rgba(16,185,129,0.5)", borderRadius: 6 },
      ],
    },
    options: chartOpts(true),
  });
}

function chartOpts(stacked = false) {
  return {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { stacked, ticks: { color: "#8fa3c7" }, grid: { color: "rgba(148,163,184,0.08)" } },
      y: { stacked, ticks: { color: "#8fa3c7" }, grid: { color: "rgba(148,163,184,0.08)" } },
    },
    plugins: { legend: { labels: { color: "#8fa3c7" } } },
  };
}

function destroyChart(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

// ── Cloud Architecture ──────────────────────────────────

let cloudConceptsCache = null;
let activeConceptSection = "overview";

async function loadCloud() {
  const data = await fetchJson("/api/system/cloud");
  cloudConceptsCache = data;

  const dep = data.deployment;
  const banner = document.getElementById("deploymentBanner");
  if (dep.environment === "cloud") {
    banner.className = "deployment-banner cloud";
    banner.innerHTML = `☁️ <strong>Running on ${dep.platform}</strong> — ${dep.service_url}`;
  } else {
    banner.className = "deployment-banner local";
    banner.innerHTML = `💻 <strong>Local Development Mode</strong> — Deploy to Render.com for cloud URL (see Deployment tab). Cloud concepts below apply to production deployment.`;
  }

  document.querySelectorAll(".concept-tab").forEach((tab) => {
    tab.onclick = () => {
      document.querySelectorAll(".concept-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      activeConceptSection = tab.dataset.section;
      renderConceptSection(activeConceptSection, data);
    };
  });

  renderConceptSection("overview", data);
}

function renderConceptSection(section, data) {
  const concepts = data.course_concepts;
  const el = document.getElementById("cloudContent");
  const icons = { cpu: "🖥️", storage: "💾", database: "🗄️", brain: "🧠", web: "🌐", api: "🔗" };
  const classes = { cpu: "compute", storage: "storage", database: "database", brain: "brain", web: "web", api: "api" };

  if (section === "overview") {
    el.innerHTML = `
      <div class="cloud-grid">${data.services.map((s) => `
        <div class="cloud-service-card ${classes[s.icon]}">
          <div class="csc-icon">${icons[s.icon]}</div>
          <h3>${s.name}</h3>
          <div class="csc-tech">${s.technology}</div>
          <p class="csc-role">${s.role}</p>
          <div class="csc-meta"><strong>Local:</strong> ${s.local_equivalent}<br><strong>Scale:</strong> ${s.scalability}</div>
        </div>`).join("")}
      </div>
      <div class="grid-2">
        <article class="card"><div class="card-head"><h2>Architecture Diagram</h2></div>
          <div class="arch-diagram">
            <div class="arch-row"><div class="arch-box">Smart Meters & Billing Systems</div></div>
            <div class="arch-row"><div class="arch-arrow">↓</div></div>
            <div class="arch-row"><div class="arch-box highlight">Cloud Storage (CSV/S3)</div><div class="arch-arrow">→</div><div class="arch-box highlight">Cloud Database (SQLite/PostgreSQL)</div></div>
            <div class="arch-row"><div class="arch-arrow">↓</div></div>
            <div class="arch-row"><div class="arch-box highlight">Cloud Compute — Docker VM (FastAPI + ML)</div></div>
            <div class="arch-row"><div class="arch-arrow">↓</div></div>
            <div class="arch-row"><div class="arch-box">REST API</div><div class="arch-arrow">→</div><div class="arch-box">Web Dashboard (Remote Access)</div></div>
            <div class="arch-row"><div class="arch-arrow">↓</div></div>
            <div class="arch-row"><div class="arch-box" style="border-color:var(--danger);color:var(--danger)">Theft Alerts → WAPDA / K-Electric</div></div>
          </div>
        </article>
        <article class="card"><div class="card-head"><h2>Cloud Benefits</h2></div>
          <ul class="benefit-list">${data.benefits.map((b) => `<li>${b}</li>`).join("")}</ul>
          <div class="provider-tags" style="margin-top:14px">${data.supported_providers.map((p) => `<span class="provider-tag">${p}</span>`).join("")}</div>
        </article>
      </div>`;
    return;
  }

  const c = concepts[section];
  if (!c) { el.innerHTML = ""; return; }

  let html = `<article class="card concept-section"><h2>${c.title}</h2>`;

  if (section === "designing_phase") {
    html += `<p class="desc">${c.architecture_decision}</p><div class="tradeoff-grid">`;
    c.content.forEach((opt) => {
      const sel = opt.verdict.includes("SELECTED");
      html += `<div class="tradeoff-card ${sel ? "selected" : ""}"><h4>${opt.option}${sel ? " ✓" : ""}</h4>
        <ul class="pros">${opt.pros.map((p) => `<li>${p}</li>`).join("")}</ul>
        <ul class="cons">${opt.cons.map((p) => `<li>${p}</li>`).join("")}</ul>
        <div class="verdict">${opt.verdict}</div></div>`;
    });
    html += `</div>`;
  } else if (section === "economic_structure") {
    html += `<table class="cost-table"><thead><tr><th>Service</th><th>Cost</th><th>Usage</th></tr></thead><tbody>`;
    c.cost_breakdown.forEach((r) => { html += `<tr><td>${r.service}</td><td><strong>${r.cost_usd}</strong></td><td>${r.usage}</td></tr>`; });
    html += `</tbody></table><p class="desc" style="margin-top:14px"><strong>Total: ${c.total_monthly_cost}</strong></p>`;
    html += `<h3 style="margin-top:18px;font-size:0.95rem">Cost Optimization</h3><ul class="concept-list">${c.cost_optimization.map((i) => `<li>${i}</li>`).join("")}</ul>`;
  } else if (section === "data_handling") {
    ["data_handling", "optimization", "scheduling", "virtual_machines"].forEach((key) => {
      html += `<h3 style="margin-top:14px;font-size:0.92rem">${key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}</h3>`;
      html += `<ul class="concept-list">${c[key].map((i) => `<li>${i}</li>`).join("")}</ul>`;
    });
  } else if (section === "elasticity_scalability") {
    html += `<h3 style="margin-top:10px;font-size:0.92rem">Support Services</h3>`;
    c.support_services.forEach((s) => { html += `<div class="integration-card"><strong>${s.service}</strong><div class="int-how">${s.description}</div></div>`; });
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Elasticity</h3><ul class="concept-list">${c.elasticity.map((i) => `<li>${i}</li>`).join("")}</ul>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Scalability</h3><ul class="concept-list">${c.scalability.map((i) => `<li>${i}</li>`).join("")}</ul>`;
  } else if (section === "system_integration") {
    html += `<p class="desc">${c.diagram_flow}</p>`;
    c.integrations.forEach((i) => {
      html += `<div class="integration-card"><div class="int-flow">${i.from} → ${i.to}</div><div class="int-how">${i.how}</div><div class="int-protocol">Protocol: ${i.protocol}</div></div>`;
    });
  } else if (section === "technical_phase") {
    html += `<div class="layer-stack">${Object.entries(c.stack).map(([k, v]) => `<div class="layer-item"><span>${k}</span><strong>${v}</strong></div>`).join("")}</div>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">ML Pipeline</h3><ul class="concept-list">${c.ml_pipeline.map((i) => `<li>${i}</li>`).join("")}</ul>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Performance</h3><div class="metrics-row">${Object.entries(c.performance).map(([k, v]) => `<div class="metric-card"><strong>${v}</strong><span>${k.replace(/_/g, " ")}</span></div>`).join("")}</div>`;
  } else if (section === "implementation_phase") {
    html += `<h3 style="font-size:0.92rem">Modules</h3>`;
    c.modules.forEach((m) => { html += `<div class="integration-card"><strong>${m.module}</strong><div class="int-how">${m.purpose}</div></div>`; });
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Weekly Progress Timeline</h3>`;
    c.timeline.forEach((t) => { html += `<div class="timeline-item"><span class="week">${t.week}</span><span>${t.task}</span></div>`; });
  } else if (section === "deployment_phase") {
    html += `<ul class="concept-list">${c.steps.map((s) => `<li>${s}</li>`).join("")}</ul>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Environments</h3>`;
    c.environments.forEach((e) => { html += `<div class="integration-card"><strong>${e.env}</strong> — <code>${e.url}</code><div class="int-how">${e.purpose}</div></div>`; });
    html += `<p class="desc"><strong>CI/CD:</strong> ${c.cicd}</p>`;
  } else if (section === "optimized_architecture") {
    html += `<div class="layer-stack">${c.layers.map((l) => `<div class="layer-item"><span>${l.layer}: ${l.component}</span><strong>${l.cloud_service}</strong></div>`).join("")}</div>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Optimizations</h3><ul class="concept-list">${c.optimizations.map((i) => `<li>${i}</li>`).join("")}</ul>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Future Improvements</h3><ul class="concept-list">${c.future_improvements.map((i) => `<li>${i}</li>`).join("")}</ul>`;
  } else if (section === "research_component") {
    html += `<p class="desc"><strong>Problem:</strong> ${c.problem}</p><p class="desc"><strong>Research Question:</strong> ${c.research_question}</p><p class="desc"><strong>Methodology:</strong> ${c.methodology}</p>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Findings</h3><ul class="concept-list">${c.findings.map((i) => `<li>${i}</li>`).join("")}</ul>`;
    html += `<h3 style="margin-top:14px;font-size:0.92rem">Comparison</h3><table class="compare-table"><thead><tr><th>Approach</th><th>Accuracy</th><th>Cost</th><th>Scale</th></tr></thead><tbody>`;
    Object.entries(c.comparison).forEach(([k, v]) => {
      const hl = k === "ml_cloud_proposed" ? "highlight-col" : "";
      html += `<tr><td class="${hl}">${k.replace(/_/g, " ")}</td><td class="${hl}">${v.accuracy}</td><td class="${hl}">${v.cost}</td><td class="${hl}">${v.scale}</td></tr>`;
    });
    html += `</tbody></table>`;
  }

  html += `</article>`;
  el.innerHTML = html;
}

// ── Data Management ─────────────────────────────────────

async function loadDataManagement() {
  const data = await fetchJson("/api/system/data");
  const s = data.storage;

  document.getElementById("dataStatsRow").innerHTML = `
    <div class="stat-box"><span class="value">${s.consumer_records.toLocaleString()}</span><span class="label">Database Records</span></div>
    <div class="stat-box"><span class="value">${s.dataset_file_mb} MB</span><span class="label">CSV Dataset Size</span></div>
    <div class="stat-box"><span class="value">${s.database_file_mb} MB</span><span class="label">Database Size</span></div>
    <div class="stat-box"><span class="value">${s.prediction_logs}</span><span class="label">Predictions Logged</span></div>
    <div class="stat-box"><span class="value">${s.total_storage_mb} MB</span><span class="label">Total Storage</span></div>
  `;

  document.getElementById("pipelineStages").innerHTML = data.stages.map((stage) => `
    <div class="pipeline-stage">
      <div class="ps-num">${stage.step}</div>
      <div class="ps-content">
        <h3>${stage.title}</h3>
        <p>${stage.description}</p>
        <div class="ps-tags">
          <span class="ps-tag">Source: ${stage.source}</span>
          <span class="ps-tag">Output: ${stage.output}</span>
          ${stage.fields.map((f) => `<span class="ps-tag">${f}</span>`).join("")}
        </div>
      </div>
    </div>
  `).join("");

  const sc = data.search_capabilities;
  document.getElementById("searchCapabilities").innerHTML = `
    <div class="capability-grid">
      <div class="capability-item"><strong>Searchable Fields</strong><ul>${sc.fields.map((f) => `<li>${f}</li>`).join("")}</ul></div>
      <div class="capability-item"><strong>Filters</strong><ul>${sc.filters.map((f) => `<li>${f}</li>`).join("")}</ul></div>
    </div>
    <p class="note" style="margin-top:12px">${sc.performance}</p>
  `;

  document.getElementById("storageDetails").innerHTML = `
    <div class="storage-row"><span>Dataset CSV</span><span>${s.dataset_path} (${s.dataset_file_mb} MB)</span></div>
    <div class="storage-row"><span>Database</span><span>${s.database_path} (${s.database_file_mb} MB)</span></div>
    <div class="storage-row"><span>ML Model</span><span>${s.model_path} (${s.model_file_mb} MB)</span></div>
    <div class="storage-row"><span>Columns per record</span><span>${s.dataset_columns} attributes</span></div>
  `;

  destroyChart("storageChart");
  charts.storageChart = new Chart(document.getElementById("storageChart"), {
    type: "doughnut",
    data: {
      labels: ["CSV Dataset", "Database", "ML Model"],
      datasets: [{ data: [s.dataset_file_mb, s.database_file_mb, s.model_file_mb], backgroundColor: ["#3b82f6", "#10b981", "#8b5cf6"], borderWidth: 0 }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom", labels: { color: "#8fa3c7" } } } },
  });
}

// ── All Consumers ───────────────────────────────────────

async function loadConsumers(page = 1) {
  currentPage = page;
  const params = new URLSearchParams({ page, page_size: 25 });
  ["consumerSearch:q", "filterRegion:region", "filterLabel:label", "filterConnection:connection_type"].forEach((pair) => {
    const [elId, param] = pair.split(":");
    const val = document.getElementById(elId)?.value;
    if (val) params.set(param, val);
  });

  const data = await fetchJson(`/api/consumers/search?${params}`);
  document.getElementById("directoryCount").textContent = `${data.total.toLocaleString()} total`;

  document.getElementById("consumersBody").innerHTML = data.results.map((c) => `
    <tr>
      <td><code>${c.consumer_id}</code></td><td>${c.full_name}</td><td>${c.region}</td>
      <td>${c.city || "—"}</td><td>${c.connection_type}</td>
      <td>${fmt(c.monthly_consumption)}</td><td>${fmtCurrency(c.billing_amount)}</td>
      <td><span class="badge ${c.label.toLowerCase()}">${c.label}</span></td>
      <td><button class="btn sm primary" onclick="openConsumer('${c.consumer_id}')">View</button></td>
    </tr>
  `).join("") || `<tr><td colspan="9" style="text-align:center">No results</td></tr>`;

  const el = document.getElementById("pagination");
  el.innerHTML = data.total_pages > 1 ? `
    <button ${data.page <= 1 ? "disabled" : ""} id="prevPage">← Previous</button>
    <span>Page ${data.page} of ${data.total_pages} (${data.total.toLocaleString()} records)</span>
    <button ${data.page >= data.total_pages ? "disabled" : ""} id="nextPage">Next →</button>
  ` : "";
  document.getElementById("prevPage")?.addEventListener("click", () => loadConsumers(currentPage - 1));
  document.getElementById("nextPage")?.addEventListener("click", () => loadConsumers(currentPage + 1));
}

document.getElementById("applyFilters")?.addEventListener("click", () => loadConsumers(1));

async function populateRegionFilters() {
  const analytics = await fetchJson("/api/analytics");
  const select = document.getElementById("filterRegion");
  analytics.by_region.forEach((r) => {
    const opt = document.createElement("option");
    opt.value = r.region; opt.textContent = r.region;
    select.appendChild(opt);
  });
}

// ── Analytics & Models ──────────────────────────────────

async function loadAnalytics() {
  const analytics = await fetchJson("/api/analytics");
  document.getElementById("analyticsStats").innerHTML = `
    <div class="stat-box"><span class="value">${fmt(analytics.avg_monthly_consumption)}</span><span class="label">Avg Consumption (units)</span></div>
    <div class="stat-box"><span class="value">${fmtCurrency(analytics.avg_billing_amount)}</span><span class="label">Avg Bill</span></div>
    <div class="stat-box danger"><span class="value">${analytics.theft_percentage}%</span><span class="label">Theft Rate</span></div>
    <div class="stat-box warning"><span class="value">${analytics.overdue_accounts.toLocaleString()}</span><span class="label">Overdue</span></div>
  `;
  renderRegionChart("analyticsRegionChart", analytics.by_region);
  destroyChart("paymentChart");
  charts.paymentChart = new Chart(document.getElementById("paymentChart"), {
    type: "pie",
    data: { labels: analytics.payment_breakdown.map((p) => p.payment_status), datasets: [{ data: analytics.payment_breakdown.map((p) => p.count), backgroundColor: ["#10b981", "#f59e0b", "#ef4444"], borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom", labels: { color: "#8fa3c7" } } } },
  });
  document.getElementById("companyGrid").innerHTML = analytics.by_distribution_company.map((c) =>
    `<div class="company-card"><strong>${c.count.toLocaleString()}</strong><span>${c.distribution_company}</span></div>`
  ).join("");
}

async function loadModels() {
  const [metrics, comparison] = await Promise.all([fetchJson("/api/metrics"), fetchJson("/api/comparison")]);
  document.getElementById("modelDetailMetrics").innerHTML = renderMetricCards(metrics);
  const cm = metrics.confusion_matrix;
  document.getElementById("confusionMatrix").innerHTML = `
    <div class="cm-cell"><strong>${cm[0][0]}</strong><span>True Normal</span></div>
    <div class="cm-cell"><strong>${cm[0][1]}</strong><span>False Alarm</span></div>
    <div class="cm-cell"><strong>${cm[1][0]}</strong><span>Missed Theft</span></div>
    <div class="cm-cell"><strong>${cm[1][1]}</strong><span>True Theft</span></div>`;
  document.getElementById("comparisonBody").innerHTML = Object.entries(comparison).map(([n, d]) =>
    `<tr><td>${n.replaceAll("_", " ")}</td><td>${d.accuracy}%</td><td>${d.precision}%</td><td>${d.recall}%</td><td>${d.f1_score}%</td></tr>`
  ).join("");
}

// ── Batch ───────────────────────────────────────────────

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const file = document.getElementById("csvFile");
  if (!file.files.length) { alert("Select a CSV file first."); return; }
  document.getElementById("batchProgress").classList.remove("hidden");
  document.getElementById("batchResult").classList.add("hidden");
  try {
    const fd = new FormData(); fd.append("file", file.files[0]);
    const data = await fetchJson("/api/predict/batch", { method: "POST", body: fd });
    document.getElementById("batchResult").classList.remove("hidden");
    document.getElementById("batchResult").innerHTML = `
      <h3>Batch Complete</h3><p>Processed <strong>${data.total_processed.toLocaleString()}</strong> records on cloud compute.</p>
      <div class="stats-row" style="margin-top:12px">
        <div class="stat-box danger"><span class="value">${data.theft_detected}</span><span class="label">Theft</span></div>
        <div class="stat-box success"><span class="value">${data.normal_detected}</span><span class="label">Normal</span></div>
      </div>`;
  } catch (err) { alert(err.message); }
  finally { document.getElementById("batchProgress").classList.add("hidden"); }
});

document.getElementById("refreshHistory").addEventListener("click", loadDashboard);

// Make openConsumer global for inline onclick
window.openConsumer = openConsumer;
window.navigateTo = navigateTo;

// ── Init ────────────────────────────────────────────────
Promise.all([loadDashboard(), populateRegionFilters()]).catch((err) => {
  console.error(err);
  alert("Cannot connect to server. Run run.bat first, then open http://127.0.0.1:8000");
});
