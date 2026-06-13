const state = {
  arduinoDirty: false,
  arduinoVerifyRunning: false,
  refreshPromise: null,
  arduinoFqbnFull: "",
  arduinoBoardName: "",
  themeHydrated: false,
  lastVerifyText: "Sandbox compile has not been run.",
  lastRefreshAt: 0,
};

const THEMES = ["light", "dark", "neutral"];
const THEME_KEY = "talos-theme";
const FAST_REFRESH_MS = 1000;
const IDLE_REFRESH_MS = 5000;
const REFRESH_TICK_MS = 250;

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(payload.error || text || response.statusText);
  return payload;
}

function setView(viewId) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === viewId));
  $$(".nav").forEach((button) => button.classList.toggle("active", button.dataset.view === viewId));
  if (viewId === "workspace") refresh();
}

function activeViewId() {
  return $(".view.active")?.id || "dashboard";
}

function currentTheme() {
  const checked = document.querySelector('input[name="theme"]:checked')?.value;
  if (THEMES.includes(checked)) return checked;
  const active = document.documentElement.dataset.theme;
  if (THEMES.includes(active)) return active;
  const stored = localStorage.getItem(THEME_KEY);
  return THEMES.includes(stored) ? stored : "light";
}

function applyTheme(theme) {
  const nextTheme = THEMES.includes(theme) ? theme : "light";
  document.documentElement.dataset.theme = nextTheme;
  localStorage.setItem(THEME_KEY, nextTheme);
  const input = document.querySelector(`input[name="theme"][value="${nextTheme}"]`);
  if (input) input.checked = true;
}

function hydrateTheme(config = {}) {
  if (state.themeHydrated) return;
  state.themeHydrated = true;
  if (THEMES.includes(config.theme)) {
    applyTheme(config.theme);
    return;
  }
  const stored = localStorage.getItem(THEME_KEY);
  if (THEMES.includes(stored)) applyTheme(stored);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

function compactBoardLabel(fqbn, boardName = "") {
  if (boardName) return boardName;
  if (!fqbn) return "";
  return fqbn.split(":").slice(0, 3).join(":") || fqbn;
}

function boardInfoText(fqbn, boardName = "") {
  if (!fqbn) return "No board details available.";
  const parts = fqbn.split(":");
  const base = parts.slice(0, 3).join(":");
  const options = parts.slice(3).join(":");
  const lines = [];
  if (boardName) lines.push(`Board: ${boardName}`);
  if (base) lines.push(`FQBN: ${base}`);
  if (options) {
    lines.push("", "Options:");
    options.split(",").forEach((option) => lines.push(`- ${option}`));
  }
  return lines.join("\n");
}

function commandBaseName(command = "") {
  const head = String(command).trim().split(/\s+/)[0] || "";
  return head.split(/[\\/]/).pop() || head;
}

function formatBytes(value = 0) {
  const number = Number(value || 0);
  if (number >= 1024 * 1024) return `${(number / (1024 * 1024)).toFixed(1)} MB`;
  if (number >= 1024) return `${(number / 1024).toFixed(1)} KB`;
  return `${number} B`;
}

function memorySummary(memory = {}) {
  const rows = [];
  if (memory.program) {
    rows.push(["Program", `${formatBytes(memory.program.used)} / ${formatBytes(memory.program.maximum)} (${memory.program.percent}%)`]);
  }
  if (memory.dynamic) {
    rows.push(["Dynamic", `${formatBytes(memory.dynamic.used)} / ${formatBytes(memory.dynamic.maximum)} (${memory.dynamic.percent}%)`]);
  }
  return rows;
}

function verifySummaryHtml(result = {}) {
  const rows = memorySummary(result.memory || {});
  const libraries = result.libraries || [];
  const platforms = result.platforms || [];
  const issues = result.issues || [];
  if (!rows.length && !libraries.length && !platforms.length && !issues.length) return "";
  return `
    <div class="verify-summary">
      ${rows.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`).join("")}
      ${libraries.length ? `<div><span>Libraries</span><b>${escapeHtml(libraries.map((item) => `${item.name} ${item.version}`.trim()).join(", "))}</b></div>` : ""}
      ${platforms.length ? `<div><span>Platform</span><b>${escapeHtml(platforms.map((item) => `${item.name} ${item.version}`.trim()).join(", "))}</b></div>` : ""}
      ${issues.length ? `<div><span>Issues</span><b>${escapeHtml(String(issues.length))}</b></div>` : ""}
    </div>
  `;
}

function renderVerifyOutput(result = null, pendingText = "") {
  const output = $("#arduinoOutput");
  if (!result) {
    output.className = `verify-output ${pendingText ? "pending" : "empty"}`;
    state.lastVerifyText = pendingText || "Sandbox compile has not been run.";
    output.textContent = state.lastVerifyText;
    return;
  }
  const ok = Boolean(result.ok);
  const status = result.status || (ok ? "passed" : "failed");
  const command = result.command || "";
  const sandbox = result.sandbox || "";
  state.lastVerifyText = [
    `Status: ${status}`,
    command ? `Command: ${command}` : "",
    sandbox ? `Sandbox: ${sandbox}` : "",
    "",
    result.output || "No compiler output.",
  ].filter(Boolean).join("\n");
  output.className = `verify-output ${ok ? "passed" : "failed"}`;
  output.innerHTML = `
    <div class="verify-head">
      <span class="verify-badge">${escapeHtml(status)}</span>
      <span class="verify-command-name">${escapeHtml(commandBaseName(command) || "arduino-cli")}</span>
    </div>
    ${command ? `<div class="verify-field"><span>Command</span><code>${escapeHtml(command)}</code></div>` : ""}
    ${sandbox ? `<div class="verify-field"><span>Sandbox</span><code>${escapeHtml(sandbox)}</code></div>` : ""}
    ${verifySummaryHtml(result)}
    <pre class="verify-log">${escapeHtml(result.output || "No compiler output.")}</pre>
  `;
}

async function copyText(text, statusSelector = "") {
  const value = String(text || "").trim();
  if (!value) return;
  await navigator.clipboard.writeText(value);
  if (statusSelector) {
    const status = $(statusSelector);
    if (status) {
      const previous = status.textContent;
      status.textContent = "Copied.";
      window.setTimeout(() => {
        status.textContent = previous;
      }, 1200);
    }
  }
}

function fileListText() {
  return $$("#arduinoFiles tr").map((row) => [...row.children].map((cell) => cell.textContent.trim()).join("\t")).join("\n");
}

function setBoardField(fqbn = "", boardName = "") {
  state.arduinoFqbnFull = fqbn || "";
  state.arduinoBoardName = boardName || "";
  $("#arduinoFqbnInput").value = compactBoardLabel(state.arduinoFqbnFull, state.arduinoBoardName);
  $("#boardInfoPanel").textContent = boardInfoText(state.arduinoFqbnFull, state.arduinoBoardName);
  $("#boardInfoBtn").disabled = !state.arduinoFqbnFull;
}

function normalizedWindowsPath(value = "") {
  return String(value).trim().replaceAll("/", "\\").replace(/\\+$/, "").toLowerCase();
}

function renderStats(payload) {
  const arduino = payload.arduino || {};
  const projects = payload.arduino_projects || [];
  const rows = [
    ["Role", payload.role || "Tool server"],
    ["Native C", payload.native_available ? "Loaded" : "Not built"],
    ["Open sketches", String(projects.length)],
    ["Arduino", arduino.valid ? "Ready" : "Not ready"],
  ];
  $("#stats").innerHTML = rows
    .map(([label, value]) => `<div class="stat"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`)
    .join("");
}

function renderArduino(arduino, force = false, ide = {}) {
  if (!arduino) return;
  if (!state.arduinoDirty || force) {
    $("#arduinoPathInput").value = arduino.path || "";
  }
  const detectedFqbn = ide.fqbn || arduino.fqbn || "";
  const detectedBoardName = ide.board_name || (detectedFqbn === arduino.fqbn ? state.arduinoBoardName : "");
  if (
    force
    || detectedFqbn !== state.arduinoFqbnFull
    || detectedBoardName !== state.arduinoBoardName
  ) {
    setBoardField(detectedFqbn, detectedBoardName);
  }
  $("#arduinoStatus").textContent = arduino.message || "No Arduino sketch folder configured.";
  $("#arduinoMeta").textContent = arduino.valid
    ? `${arduino.files.length} file(s) | main sketch: ${arduino.main_sketch}`
    : "Set a sketch folder that contains at least one .ino file.";
  $("#verifyArduinoBtn").disabled = state.arduinoVerifyRunning || !arduino.configured;
  $("#arduinoFiles").innerHTML = (arduino.files || []).map((file) => `
    <tr>
      <td>${escapeHtml(file.path)}</td>
      <td>${Number(file.lines || 0)}</td>
      <td>${Number(file.bytes || 0)}</td>
    </tr>
  `).join("");
}

function renderArduinoProjects(projects = []) {
  if (!projects.length) {
    $("#arduinoProjects").innerHTML = `<div class="project-row"><div><div class="project-title">No open Arduino sketches detected</div><div class="project-path">Open one or more .ino sketches in Arduino IDE, then refresh.</div></div></div>`;
    return;
  }
  $("#arduinoProjects").innerHTML = projects.map((project, index) => `
    <div class="project-row ${project.unsaved ? "unsaved" : ""}">
      <div>
        <div class="project-title">
          ${escapeHtml(project.sketch || "Arduino sketch")}
          ${project.unsaved ? '<span class="project-badge">Unsaved</span>' : ""}
          ${!project.valid && !project.unsaved ? '<span class="project-badge warning">Folder not found</span>' : ""}
        </div>
        ${project.unsaved ? '<div class="project-path">Save this sketch in Arduino IDE to create a selectable workspace.</div>' : ""}
      </div>
      <button class="button ghost select-project" data-index="${index}" ${project.valid ? "" : "disabled"}>Select</button>
    </div>
  `).join("");
  $$(".select-project").forEach((button) => {
    button.addEventListener("click", async () => {
      const project = projects[Number(button.dataset.index)];
      if (!project?.path) return;
      $("#arduinoPathInput").value = project.path;
      if (project.fqbn) setBoardField(project.fqbn, project.board_name || "");
      state.arduinoDirty = true;
      await saveArduinoWorkspace();
    });
  });
}

function render(payload) {
  hydrateTheme(payload.config || {});
  const projects = payload.arduino_projects || [];
  const arduino = payload.arduino || {};
  const selectedPath = normalizedWindowsPath(arduino.path);
  const selectedProject = projects.find((project) => (
    normalizedWindowsPath(project.path) === selectedPath && project.fqbn === arduino.fqbn
  ))
    || projects.find((project) => normalizedWindowsPath(project.path) === selectedPath)
    || {};
  $("#modeLine").textContent = `${payload.role} | ${payload.root}`;
  $("#toolList").textContent = (payload.tools || []).join("\n");
  renderStats(payload);
  renderArduino(arduino, false, selectedProject);
  renderArduinoProjects(projects);
  $("#logText").textContent = (payload.events || []).join("\n");
}

async function refresh() {
  if (state.refreshPromise) return state.refreshPromise;
  state.refreshPromise = api("/api/state")
    .then((payload) => {
      render(payload);
      state.lastRefreshAt = Date.now();
      return payload;
    })
    .finally(() => {
      state.refreshPromise = null;
    });
  return state.refreshPromise;
}

function maybeRefresh() {
  if (document.hidden) return;
  const interval = activeViewId() === "workspace" ? FAST_REFRESH_MS : IDLE_REFRESH_MS;
  if (Date.now() - state.lastRefreshAt >= interval) refresh();
}

async function saveArduinoWorkspace() {
  const result = await api("/api/arduino_workspace", {
    method: "POST",
    body: JSON.stringify({
      path: $("#arduinoPathInput").value,
      fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value,
    }),
  });
  state.arduinoDirty = false;
  renderArduino(result.arduino, true);
  await refresh();
  return result;
}

async function verifyArduinoWorkspace() {
  renderVerifyOutput(null, "Copying sketch folder to sandbox and running arduino-cli compile...");
  state.arduinoVerifyRunning = true;
  $("#verifyArduinoBtn").disabled = true;
  try {
    const result = await api("/api/arduino_verify", {
      method: "POST",
      body: JSON.stringify({
        path: $("#arduinoPathInput").value,
        fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value,
      }),
    });
    renderVerifyOutput(result);
    state.arduinoDirty = false;
    await refresh();
    return result;
  } finally {
    state.arduinoVerifyRunning = false;
    $("#verifyArduinoBtn").disabled = false;
  }
}

async function saveSettings() {
  const result = await api("/api/settings", {
    method: "POST",
    body: JSON.stringify({ theme: currentTheme() }),
  });
  $("#settingsStatus").textContent = `Saved ${result.config?.theme || currentTheme()} theme.`;
  return result;
}

function setMaximizeIcon(maximized) {
  const button = $("#maximizeBtn");
  if (!button) return;
  button.innerHTML = maximized ? "&#10064;" : "&#9633;";
  button.title = maximized ? "Restore" : "Maximize";
  button.setAttribute("aria-label", button.title);
}

async function syncWindowState() {
  const stateInfo = await window.pywebview?.api?.get_window_state?.();
  if (stateInfo) setMaximizeIcon(Boolean(stateInfo.maximized));
}

async function toggleMaximize() {
  const maximized = await window.pywebview?.api?.toggle_maximize?.();
  setMaximizeIcon(Boolean(maximized));
}

function snapTarget(kind) {
  const screenInfo = window.screen;
  const left = Number(screenInfo.availLeft ?? 0);
  const top = Number(screenInfo.availTop ?? 0);
  const width = Number(screenInfo.availWidth || screenInfo.width || 1200);
  const height = Number(screenInfo.availHeight || screenInfo.height || 800);
  const halfW = Math.round(width / 2);
  const halfH = Math.round(height / 2);
  const thirdW = Math.round(width / 3);
  const targets = {
    left: [left, top, halfW, height],
    right: [left + width - halfW, top, halfW, height],
    "third-left": [left, top, thirdW, height],
    "third-center": [left + thirdW, top, width - thirdW * 2, height],
    "top-left": [left, top, halfW, halfH],
    "bottom-right": [left + width - halfW, top + height - halfH, halfW, halfH],
  };
  return targets[kind] || targets.left;
}

async function snapWindow(kind) {
  const [x, y, width, height] = snapTarget(kind);
  await window.pywebview?.api?.snap_to?.(x, y, width, height);
  setMaximizeIcon(false);
  $("#snapMenu")?.classList.remove("open");
}

function bindEvents() {
  $$(".nav").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $("#refreshBtn").addEventListener("click", refresh);
  $("#saveArduinoBtn").addEventListener("click", saveArduinoWorkspace);
  $("#verifyArduinoBtn").addEventListener("click", verifyArduinoWorkspace);
  $("#saveSettingsBtn").addEventListener("click", saveSettings);
  $("#copyFilesBtn").addEventListener("click", () => copyText(fileListText(), "#arduinoMeta"));
  $("#copyVerifyBtn").addEventListener("click", () => copyText(state.lastVerifyText));
  $("#boardInfoBtn").addEventListener("click", () => {
    const panel = $("#boardInfoPanel");
    const isHidden = panel.hidden;
    panel.hidden = !isHidden;
    $("#boardInfoBtn").classList.toggle("active", isHidden);
  });
  $$("#workspace input").forEach((input) => {
    input.addEventListener("input", () => {
      state.arduinoDirty = true;
      $("#verifyArduinoBtn").disabled = false;
    });
  });
  $$('input[name="theme"]').forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) applyTheme(input.value);
      $("#settingsStatus").textContent = "Theme changed. Save to keep it for next launch.";
    });
  });
  $(".app-chrome").addEventListener("dblclick", (event) => {
    if (event.target.closest(".chrome-actions")) return;
    toggleMaximize();
  });
  $("#minimizeBtn").addEventListener("click", () => window.pywebview?.api?.minimize?.());
  $("#maximizeBtn").addEventListener("click", toggleMaximize);
  $("#maximizeBtn").addEventListener("pointerdown", () => $("#snapMenu")?.classList.add("open"));
  $$(".snap-option").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      snapWindow(button.dataset.snap);
    });
  });
  $("#closeBtn").addEventListener("click", () => window.pywebview?.api?.close?.());
  syncWindowState();
}

bindEvents();
refresh();
setInterval(maybeRefresh, REFRESH_TICK_MS);
