const state = {
  activeJobId: null,
  options: null,
  poller: null,
  promptTouched: false,
};

const elements = {
  form: document.getElementById("job-form"),
  archive: document.getElementById("archive"),
  archiveName: document.getElementById("archive-name"),
  language: document.getElementById("language"),
  model: document.getElementById("model"),
  prompt: document.getElementById("prompt"),
  keyFamily: document.getElementById("key-family"),
  apiKey: document.getElementById("api-key"),
  maxAttempts: document.getElementById("max-attempts"),
  packageDir: document.getElementById("package-dir"),
  testsDir: document.getElementById("tests-dir"),
  startButton: document.getElementById("start-button"),
  formStatus: document.getElementById("form-status"),
  statusPill: document.getElementById("status-pill"),
  runSummary: document.getElementById("run-summary"),
  generatedTests: document.getElementById("generated-tests"),
  downloadLink: document.getElementById("download-link"),
  recentJobs: document.getElementById("recent-jobs"),
  logOutput: document.getElementById("log-output"),
};

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function setFormStatus(message) {
  elements.formStatus.textContent = message;
}

function setActiveJob(job) {
  state.activeJobId = job ? job.id : null;
  if (state.poller) {
    clearInterval(state.poller);
    state.poller = null;
  }
  if (job && (job.status === "queued" || job.status === "running")) {
    state.poller = setInterval(() => refreshActiveJob(), 2500);
  }
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (_) {
      // ignore JSON parsing errors for non-JSON responses
    }
    throw new Error(detail);
  }
  return response.json();
}

async function loadOptions() {
  const options = await fetchJson("/api/options");
  state.options = options;

  elements.language.innerHTML = options.languages
    .map((language) => `<option value="${language}">${language.toUpperCase()}</option>`)
    .join("");

  elements.prompt.innerHTML = options.prompts
    .map((prompt) => `<option value="${prompt.value}">${prompt.label}</option>`)
    .join("");

  elements.model.innerHTML = options.models
    .map((model) => `<option value="${model.value}">${model.label}</option>`)
    .join("");

  elements.keyFamily.innerHTML = options.keyFamilies
    .map((family) => `<option value="${family.value}">${family.label}</option>`)
    .join("");

  if (options.defaultModel) {
    elements.model.value = options.defaultModel;
  }

  syncPromptRecommendation();
  syncKeyRecommendation();
}

function syncPromptRecommendation() {
  if (!state.options) return;
  const recommended = state.options.defaultPromptByLanguage[elements.language.value];
  if (!state.promptTouched && recommended) {
    elements.prompt.value = recommended;
  }
}

function syncKeyRecommendation() {
  if (!state.options) return;
  const selected = state.options.models.find((model) => model.value === elements.model.value);
  if (selected && elements.keyFamily.value === "auto") {
    elements.keyFamily.value = selected.provider || "auto";
  }
}

function updateArchiveName() {
  const file = elements.archive.files[0];
  elements.archiveName.textContent = file ? file.name : "No archive selected yet.";
}

function renderStatus(job) {
  elements.statusPill.className = `status-pill ${job ? job.status : "idle"}`;
  elements.statusPill.textContent = job ? job.status : "Idle";
}

function renderGeneratedTests(job) {
  const files = job?.generated_tests || [];
  if (!files.length) {
    elements.generatedTests.innerHTML = '<li class="muted">No generated tests yet.</li>';
  } else {
    elements.generatedTests.innerHTML = files
      .map((file) => `<li><code>${escapeHtml(file)}</code></li>`)
      .join("");
  }

  if (job?.download_url) {
    elements.downloadLink.href = job.download_url;
    elements.downloadLink.classList.remove("disabled");
    elements.downloadLink.setAttribute("aria-disabled", "false");
  } else {
    elements.downloadLink.href = "#";
    elements.downloadLink.classList.add("disabled");
    elements.downloadLink.setAttribute("aria-disabled", "true");
  }
}

function metricCard(label, value) {
  return `
    <div class="metric">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `;
}

function renderRunSummary(job) {
  if (!job) {
    elements.runSummary.className = "run-summary empty-state";
    elements.runSummary.innerHTML =
      "<p>No job started yet. Once a run begins, coverage delta, counters, and generated test files will appear here.</p>";
    return;
  }

  const counters = job.summary?.counters || {};
  const coverageBefore = job.initial_coverage_text || "n/a";
  const coverageAfter = job.final_coverage_text || "n/a";
  const cost = job.summary?.cost_usd != null ? `$${job.summary.cost_usd.toFixed(3)}` : "n/a";
  const meta = [
    `Job ${job.id}`,
    `${job.language.toUpperCase()} / ${job.prompt || "default prompt"}`,
    job.model ? `Model ${job.model}` : "Model from environment defaults",
    job.key_family && job.key_family !== "auto" ? `Key ${job.key_family}` : null,
    job.package_dir ? `Package ${job.package_dir}` : null,
    job.tests_dir ? `Tests ${job.tests_dir}` : null,
  ].filter(Boolean);

  const errorHtml = job.error
    ? `<div class="meta-pill" style="background: rgba(203,90,50,0.12); color: #9f3518;">${escapeHtml(job.error)}</div>`
    : "";

  elements.runSummary.className = "run-summary";
  elements.runSummary.innerHTML = `
    <div class="meta-strip">
      ${meta.map((item) => `<div class="meta-pill">${escapeHtml(item)}</div>`).join("")}
      ${errorHtml}
    </div>
    <div class="metric-grid">
      ${metricCard("Coverage start", coverageBefore)}
      ${metricCard("Coverage end", coverageAfter)}
      ${metricCard("Good", String(counters.G ?? 0))}
      ${metricCard("Failed", String(counters.F ?? 0))}
      ${metricCard("Cost", cost)}
    </div>
    <p class="muted">${escapeHtml(job.message || "")}</p>
  `;
}

function renderLog(job) {
  const text = job?.log_tail || "No log output yet.";
  elements.logOutput.textContent = text;
  elements.logOutput.scrollTop = elements.logOutput.scrollHeight;
}

function renderRecentJobs(jobs) {
  if (!jobs.length) {
    elements.recentJobs.innerHTML = '<li class="muted">No runs recorded yet.</li>';
    return;
  }

  elements.recentJobs.innerHTML = jobs
    .slice(0, 8)
    .map((job) => {
      const coverage = [job.initial_coverage_text, job.final_coverage_text]
        .filter(Boolean)
        .join(" -> ") || "coverage pending";
      return `
        <li>
          <strong>${escapeHtml(job.id)}</strong><br />
          <span class="muted">${escapeHtml(job.language.toUpperCase())} / ${escapeHtml(job.status)} / ${escapeHtml(coverage)}</span>
        </li>
      `;
    })
    .join("");
}

async function refreshJobLists() {
  const jobs = await fetchJson("/api/jobs");
  renderRecentJobs(jobs);
}

async function refreshActiveJob() {
  if (!state.activeJobId) return;
  const job = await fetchJson(`/api/jobs/${state.activeJobId}`);
  renderStatus(job);
  renderRunSummary(job);
  renderGeneratedTests(job);
  renderLog(job);
  await refreshJobLists();
  if (job.status !== "queued" && job.status !== "running") {
    setActiveJob(job);
    elements.startButton.disabled = false;
    setFormStatus(job.status === "finished" ? "Run finished." : "Run ended with a failure.");
  }
}

async function submitJob(event) {
  event.preventDefault();

  if (!elements.archive.files[0]) {
    setFormStatus("Choose a repository archive before starting.");
    return;
  }

  const formData = new FormData(elements.form);
  elements.startButton.disabled = true;
  setFormStatus("Uploading repository and preparing the run...");

  try {
    const job = await fetchJson("/api/jobs", {
      method: "POST",
      body: formData,
    });

    renderStatus(job);
    renderRunSummary(job);
    renderGeneratedTests(job);
    renderLog(job);
    setActiveJob(job);
    await refreshJobLists();
    setFormStatus("Run started. Live updates are streaming below.");
  } catch (error) {
    elements.startButton.disabled = false;
    setFormStatus(error.message);
  }
}

elements.archive.addEventListener("change", updateArchiveName);
elements.language.addEventListener("change", syncPromptRecommendation);
elements.model.addEventListener("change", syncKeyRecommendation);
elements.prompt.addEventListener("change", () => {
  state.promptTouched = true;
});
elements.form.addEventListener("submit", submitJob);

async function boot() {
  try {
    await loadOptions();
    await refreshJobLists();
  } catch (error) {
    setFormStatus(error.message);
  }
}

boot();
