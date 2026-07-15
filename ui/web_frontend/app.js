const state = {
  arduinoDirty: false,
  arduinoVerifyRunning: false,
  arduinoEventRevision: 0,
  arduinoEventPolling: false,
  refreshPromise: null,
  arduinoFqbnFull: "",
  arduinoBoardName: "",
  themeHydrated: false,
  lastVerifyText: "Sandbox compile has not been run.",
  lastIssueText: "",
  lastRefreshAt: 0,
  workspaceMutationVersion: 0,
  workspaceMutationRunning: false,
  workspaceSelectionRunning: false,
  selectedWorkspacePath: "",
  workspaceMap: {},
  environmentProfile: {},
  profileReadiness: {},
  lastVerifyResult: null,
  lastVerifySignature: "",
  lastVerifyOk: false,
  lastVerifyContext: null,
  activeFileByWorkspace: {},
  activeFilePath: "",
  editorOriginalContent: "",
  editorFileMtimeNs: 0,
  editorDirty: false,
  editorWriteGuard: null,
  localEditMode: false,
  editorLoading: false,
  editorSaving: false,
  editorDiskChecking: false,
  lastCheckpoint: null,
  codexBusy: false,
  codexMessagesSignature: "",
  codexRefreshPromise: null,
  codexRefreshTimer: null,
  codexPatchRevision: 0,
  codexPatchEventRevision: null,
  codexChangedFiles: new Set(),
  conflictedFilePaths: new Set(),
  codexPreviewRevision: 0,
  codexPreviewPath: "",
  codexPreviewStreaming: false,
  codexPreviewTimer: null,
  codexPreviewCommitted: false,
  codexPreviewBaseContent: "",
  codexPreviewContent: "",
  codexReviewPatch: null,
  codexPatches: [],
  codexApplyingPatchId: "",
  codexPatchVerifyRunning: false,
  codexConversationSignature: "",
  codexHistoryExpanded: false,
  codexConversations: [],
  codexTasksVisible: true,
  runHistorySignature: "",
  runHistoryFilter: "all",
  runHistorySketchOnly: true,
  appBuild: {},
  diagnostics: { enabled: false, allow_remote_upload: false },
  editorFindQuery: "",
  editorFindMatches: [],
  editorFindIndex: -1,
  commandPaletteQuery: "",
  commandPaletteIndex: 0,
};

const THEMES = ["light", "dark", "neutral"];
const THEME_KEY = "talos-theme";
const SYSTEM_THEME_KEY = "talos-system-theme";
const HIGH_CONTRAST_KEY = "talos-high-contrast";
const EDITOR_FONT_SIZE_KEY = "talos-editor-font-size";
const EDITOR_DENSITY_KEY = "talos-editor-density";
const CODEX_PANEL_KEY = "talos-codex-panel-open";
const EXPLORER_PANEL_KEY = "talos-explorer-panel-open";
const EXPLORER_WIDTH_KEY = "talos-explorer-pane-width";
const CODEX_WIDTH_KEY = "talos-codex-pane-width";
const VERIFY_HEIGHT_KEY = "talos-verify-pane-height";
const FAST_REFRESH_MS = 1000;
const IDLE_REFRESH_MS = 5000;
const REFRESH_TICK_MS = 250;
const CODEX_BUSY_REFRESH_MS = 400;
const CODEX_IDLE_REFRESH_MS = 3000;
const CODEX_HIDDEN_REFRESH_MS = 8000;
const ACTIVE_FILE_POLL_MS = 700;
const ARDUINO_EVENT_POLL_MS = 300;
const TALOS_WRITE_DEBOUNCE_MS = 1500;
const WINDOW_MIN_WIDTH = 640;
const WINDOW_MIN_HEIGHT = 460;
const APP_MENU_COMMANDS = {
  refresh: "#refreshWorkspaceBtn",
  "save-file": "#saveFileBtn",
  "save-verify": "#saveAndVerifyBtn",
  rollback: "#rollbackFileBtn",
  verify: "#verifyArduinoBtn",
  "cancel-verify": "#cancelArduinoVerifyBtn",
  "clear-cache": "#clearVerifyCacheBtn",
  "record-evidence": "#recordEvidenceBtn",
  "toggle-codex": "#toggleCodexBtn",
  "new-codex": "#newCodexThreadBtn",
  "copy-context": "#copyCodexContextBtn",
  "reconnect-codex": "#reconnectCodexBtn",
  "support-bundle": "#copySupportBundleBtn",
};
const COMMAND_PALETTE_ITEMS = [
  { label: "Refresh Workspace", command: "refresh", shortcut: "F5", group: "File" },
  { label: "Save File", command: "save-file", shortcut: "Ctrl+S", group: "File" },
  { label: "Save + Verify", command: "save-verify", shortcut: "Ctrl+Shift+S", group: "File" },
  { label: "Undo Saved File", command: "rollback", shortcut: "Ctrl+Z", group: "Edit" },
  { label: "Find In File", command: "find", shortcut: "Ctrl+F", group: "Edit" },
  { label: "Copy Current Line", command: "copy-line", shortcut: "Ctrl+C", group: "Edit" },
  { label: "Cut Current Line", command: "cut-line", shortcut: "Ctrl+X", group: "Edit" },
  { label: "Toggle Line Comment", command: "comment-line", shortcut: "Ctrl+/", group: "Edit" },
  { label: "Select Current Line", command: "select-line", shortcut: "Ctrl+L", group: "Selection" },
  { label: "Duplicate Line Up", command: "duplicate-line-up", shortcut: "Shift+Alt+Up", group: "Selection" },
  { label: "Duplicate Line Down", command: "duplicate-line-down", shortcut: "Shift+Alt+Down", group: "Selection" },
  { label: "Move Line Up", command: "move-line-up", shortcut: "Alt+Up", group: "Selection" },
  { label: "Move Line Down", command: "move-line-down", shortcut: "Alt+Down", group: "Selection" },
  { label: "Go To Server Overview", command: "server-view", group: "Go" },
  { label: "Go To Arduino Workspace", command: "workspace-view", group: "Go" },
  { label: "Go To Logs", command: "logs-view", group: "Go" },
  { label: "Go To Settings", command: "settings-view", group: "Go" },
  { label: "Toggle Explorer", command: "toggle-explorer", shortcut: "Ctrl+B", group: "View" },
  { label: "Toggle Codex Column", command: "toggle-codex", shortcut: "Ctrl+Alt+C", group: "View" },
  { label: "Show Verify Output", command: "verify-output", group: "View" },
  { label: "Show Run History", command: "run-history", group: "View" },
  { label: "Reset Pane Layout", command: "reset-layout", group: "View" },
  { label: "Verify Sandbox", command: "verify", shortcut: "Ctrl+Enter", group: "Run" },
  { label: "Cancel Verify", command: "cancel-verify", shortcut: "Esc", group: "Run" },
  { label: "Clear Verify Cache", command: "clear-cache", group: "Run" },
  { label: "Record Release Evidence", command: "record-evidence", group: "Run" },
  { label: "New Codex Thread", command: "new-codex", group: "Codex" },
  { label: "Copy Codex Context Package", command: "copy-context", group: "Codex" },
  { label: "Reconnect Codex", command: "reconnect-codex", group: "Codex" },
  { label: "Copy Support Bundle", command: "support-bundle", group: "Help" },
];

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
  document.body.classList.toggle("workbench-mode", viewId === "workspace");
  if (viewId === "workspace") {
    refresh();
    refreshCodex();
  }
}

function codexPanelOpen() {
  return localStorage.getItem(CODEX_PANEL_KEY) !== "false";
}

function explorerPanelOpen() {
  return localStorage.getItem(EXPLORER_PANEL_KEY) !== "false";
}

function closeAppMenus() {
  $$(".app-menu").forEach((menu) => menu.classList.remove("open"));
  $$("[data-menu-button]").forEach((button) => button.setAttribute("aria-expanded", "false"));
  $$("[data-menu-panel]").forEach((panel) => {
    panel.hidden = true;
  });
}

function toggleAppMenu(menuName) {
  const menu = $(`.app-menu[data-menu="${menuName}"]`);
  const button = $(`[data-menu-button="${menuName}"]`);
  const panel = $(`[data-menu-panel="${menuName}"]`);
  if (!menu || !button || !panel) return;
  const shouldOpen = panel.hidden;
  closeAppMenus();
  if (!shouldOpen) return;
  syncAppMenuState();
  menu.classList.add("open");
  button.setAttribute("aria-expanded", "true");
  panel.hidden = false;
}

function syncAppMenuState() {
  Object.entries(APP_MENU_COMMANDS).forEach(([command, selector]) => {
    const source = selector ? $(selector) : null;
    $$(`[data-command="${command}"]`).forEach((button) => {
      if (source) button.disabled = Boolean(source.disabled);
    });
  });
}

function runAppMenuCommand(command) {
  const selector = APP_MENU_COMMANDS[command];
  if (selector) {
    $(selector)?.click();
    return;
  }
  if (command === "command-palette") showCommandPalette();
  else if (command === "find") showEditorFind();
  else if (command === "copy-line") copyCurrentEditorLine(false);
  else if (command === "cut-line") copyCurrentEditorLine(true);
  else if (command === "comment-line") toggleEditorLineComment();
  else if (command === "select-line") selectEditorLine(editorCursorLineIndex() + 1);
  else if (command === "duplicate-line-up") duplicateEditorLine("up");
  else if (command === "duplicate-line-down") duplicateEditorLine("down");
  else if (command === "move-line-up") moveEditorLine("up");
  else if (command === "move-line-down") moveEditorLine("down");
  else if (command === "toggle-explorer") applyExplorerPanel(!explorerPanelOpen());
  else if (command === "reset-layout") {
    resetExplorerWidth();
    resetCodexWidth();
    resetVerifyHeight();
  } else if (command === "server-view") setView("dashboard");
  else if (command === "workspace-view") setView("workspace");
  else if (command === "logs-view") setView("logs");
  else if (command === "settings-view") setView("settings");
  else if (command === "verify-output") setOutputView("verify");
  else if (command === "run-history") {
    setOutputView("history");
    refreshRunHistory();
  }
}

function commandPaletteOpen() {
  const overlay = $("#commandPaletteOverlay");
  return Boolean(overlay && !overlay.hidden);
}

function commandPaletteItemDisabled(item) {
  const selector = APP_MENU_COMMANDS[item.command];
  return selector ? Boolean($(selector)?.disabled) : false;
}

function commandPaletteMatches(query = "") {
  const normalized = query.trim().toLowerCase();
  const items = COMMAND_PALETTE_ITEMS.map((item) => ({
    ...item,
    disabled: commandPaletteItemDisabled(item),
    searchText: `${item.group} ${item.label} ${item.command} ${item.shortcut || ""}`.toLowerCase(),
  }));
  if (!normalized) return items;
  const terms = normalized.split(/\s+/).filter(Boolean);
  return items
    .filter((item) => terms.every((term) => item.searchText.includes(term)))
    .sort((a, b) => {
      const aStarts = a.label.toLowerCase().startsWith(normalized) ? 0 : 1;
      const bStarts = b.label.toLowerCase().startsWith(normalized) ? 0 : 1;
      return aStarts - bStarts || a.label.localeCompare(b.label);
    });
}

function renderCommandPalette() {
  const input = $("#commandPaletteInput");
  const list = $("#commandPaletteList");
  if (!input || !list) return;
  state.commandPaletteQuery = input.value || "";
  const items = commandPaletteMatches(state.commandPaletteQuery);
  if (state.commandPaletteIndex >= items.length) state.commandPaletteIndex = Math.max(0, items.length - 1);
  if (!items.length) {
    list.innerHTML = `<div class="command-palette-empty">No commands match "${escapeHtml(state.commandPaletteQuery)}".</div>`;
    return;
  }
  list.innerHTML = items.map((item, index) => `
    <button
      class="command-palette-item ${index === state.commandPaletteIndex ? "active" : ""}"
      type="button"
      role="option"
      aria-selected="${index === state.commandPaletteIndex}"
      data-command="${escapeHtml(item.command)}"
      data-index="${index}"
      ${item.disabled ? "disabled" : ""}
    >
      <span>${escapeHtml(item.label)}</span>
      <small>${escapeHtml(item.shortcut || item.group)}</small>
    </button>
  `).join("");
  $$(".command-palette-item").forEach((button) => {
    button.addEventListener("mouseenter", () => {
      state.commandPaletteIndex = Number(button.dataset.index || 0);
      renderCommandPalette();
    });
    button.addEventListener("click", () => runCommandPaletteSelection());
  });
}

function showCommandPalette(seed = "") {
  closeAppMenus();
  const overlay = $("#commandPaletteOverlay");
  const input = $("#commandPaletteInput");
  if (!overlay || !input) return false;
  overlay.hidden = false;
  input.value = seed;
  state.commandPaletteIndex = 0;
  renderCommandPalette();
  input.focus();
  input.select();
  return true;
}

function hideCommandPalette() {
  const overlay = $("#commandPaletteOverlay");
  if (overlay) overlay.hidden = true;
  state.commandPaletteIndex = 0;
  $("#sourceEditor")?.focus({ preventScroll: true });
}

function moveCommandPaletteSelection(delta) {
  const items = commandPaletteMatches($("#commandPaletteInput")?.value || "");
  if (!items.length) return;
  state.commandPaletteIndex = (state.commandPaletteIndex + delta + items.length) % items.length;
  renderCommandPalette();
  $(`.command-palette-item[data-index="${state.commandPaletteIndex}"]`)?.scrollIntoView({ block: "nearest" });
}

function runCommandPaletteSelection() {
  const items = commandPaletteMatches($("#commandPaletteInput")?.value || "");
  const item = items[state.commandPaletteIndex];
  if (!item || commandPaletteItemDisabled(item)) return;
  hideCommandPalette();
  runAppMenuCommand(item.command);
}

function applyExplorerPanel(open) {
  $(".ide-workbench")?.classList.toggle("explorer-hidden", !open);
  const workspaceButton = $('.nav[data-view="workspace"]');
  workspaceButton?.classList.toggle("panel-open", open);
  workspaceButton?.setAttribute("aria-pressed", String(Boolean(open)));
  localStorage.setItem(EXPLORER_PANEL_KEY, String(Boolean(open)));
  renderStatusBar();
}

function applyCodexPanel(open) {
  $(".ide-workbench")?.classList.toggle("codex-hidden", !open);
  $("#toggleCodexBtn")?.classList.toggle("active", open);
  $("#toggleCodexBtn")?.setAttribute("aria-pressed", String(Boolean(open)));
  localStorage.setItem(CODEX_PANEL_KEY, String(Boolean(open)));
  scheduleCodexRefresh(0);
  renderStatusBar();
}

function clampPaneWidth(value, minimum, maximum) {
  return Math.min(Math.max(Number(value) || minimum, minimum), maximum);
}

function restorePaneWidths() {
  const root = document.documentElement;
  const explorer = Number(localStorage.getItem(EXPLORER_WIDTH_KEY));
  if (Number.isFinite(explorer) && explorer > 0) {
    root.style.setProperty("--explorer-pane-width", `${clampPaneWidth(explorer, 240, 420)}px`);
  }
  const codex = Number(localStorage.getItem(CODEX_WIDTH_KEY));
  if (Number.isFinite(codex) && codex > 0) {
    root.style.setProperty("--codex-pane-width", `${clampPaneWidth(codex, 280, 680)}px`);
  }
  const verify = Number(localStorage.getItem(VERIFY_HEIGHT_KEY));
  if (Number.isFinite(verify) && verify > 0) {
    root.style.setProperty("--verify-pane-height", `${clampPaneWidth(verify, 140, 520)}px`);
  }
}

function resetExplorerWidth() {
  document.documentElement.style.removeProperty("--explorer-pane-width");
  localStorage.removeItem(EXPLORER_WIDTH_KEY);
}

function resetCodexWidth() {
  document.documentElement.style.removeProperty("--codex-pane-width");
  localStorage.removeItem(CODEX_WIDTH_KEY);
}

function resetVerifyHeight() {
  document.documentElement.style.removeProperty("--verify-pane-height");
  localStorage.removeItem(VERIFY_HEIGHT_KEY);
}

function bindExplorerSplitter(selector) {
  const splitter = $(selector);
  if (!splitter) return;
  splitter.addEventListener("dblclick", resetExplorerWidth);
  splitter.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || window.innerWidth <= 900 || !explorerPanelOpen()) return;
    const workbench = splitter.closest(".ide-workbench");
    if (!workbench) return;
    event.preventDefault();
    splitter.setPointerCapture(event.pointerId);
    splitter.classList.add("dragging");
    const bounds = workbench.getBoundingClientRect();
    const update = (clientX) => {
      const available = bounds.width;
      const minimumEditor = Math.min(520, Math.max(360, available * 0.38));
      const maximum = Math.max(240, available - minimumEditor - 320 - 8);
      const width = clampPaneWidth(clientX - bounds.left, 240, maximum);
      document.documentElement.style.setProperty("--explorer-pane-width", `${Math.round(width)}px`);
      localStorage.setItem(EXPLORER_WIDTH_KEY, String(Math.round(width)));
    };
    const move = (moveEvent) => update(moveEvent.clientX);
    const finish = () => {
      splitter.classList.remove("dragging");
      splitter.removeEventListener("pointermove", move);
      splitter.removeEventListener("pointerup", finish);
      splitter.removeEventListener("pointercancel", finish);
    };
    splitter.addEventListener("pointermove", move);
    splitter.addEventListener("pointerup", finish);
    splitter.addEventListener("pointercancel", finish);
    update(event.clientX);
  });
}

function bindCodexSplitter(selector) {
  const splitter = $(selector);
  if (!splitter) return;
  splitter.addEventListener("dblclick", resetCodexWidth);
  splitter.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || window.innerWidth <= 900 || !codexPanelOpen()) return;
    const workbench = splitter.closest(".ide-workbench");
    if (!workbench) return;
    event.preventDefault();
    splitter.setPointerCapture(event.pointerId);
    splitter.classList.add("dragging");
    const bounds = workbench.getBoundingClientRect();
    const update = (clientX) => {
      const available = bounds.width;
      const minimumEditor = Math.min(520, Math.max(360, available * 0.32));
      const explorerWidth = explorerPanelOpen()
        ? Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--explorer-pane-width")) || 248
        : 0;
      const maximum = Math.max(280, available - explorerWidth - minimumEditor - 12);
      const width = clampPaneWidth(bounds.right - clientX, 280, maximum);
      document.documentElement.style.setProperty("--codex-pane-width", `${Math.round(width)}px`);
      localStorage.setItem(CODEX_WIDTH_KEY, String(Math.round(width)));
    };
    const move = (moveEvent) => update(moveEvent.clientX);
    const finish = () => {
      splitter.classList.remove("dragging");
      splitter.removeEventListener("pointermove", move);
      splitter.removeEventListener("pointerup", finish);
      splitter.removeEventListener("pointercancel", finish);
    };
    splitter.addEventListener("pointermove", move);
    splitter.addEventListener("pointerup", finish);
    splitter.addEventListener("pointercancel", finish);
    update(event.clientX);
  });
}

function bindVerifySplitter(selector) {
  const splitter = $(selector);
  if (!splitter) return;
  splitter.addEventListener("dblclick", resetVerifyHeight);
  splitter.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    const editorArea = splitter.closest(".ide-editor-area");
    if (!editorArea) return;
    event.preventDefault();
    splitter.setPointerCapture(event.pointerId);
    splitter.classList.add("dragging");
    const bounds = editorArea.getBoundingClientRect();
    const update = (clientY) => {
      const toolbarHeight = $(".editor-tabbar")?.getBoundingClientRect().height || 48;
      const available = Math.max(0, bounds.height - toolbarHeight - 12);
      const minimumEditor = Math.min(260, Math.max(180, available * 0.4));
      const maximum = Math.max(140, available - minimumEditor);
      const height = clampPaneWidth(bounds.bottom - clientY, 140, maximum);
      document.documentElement.style.setProperty("--verify-pane-height", `${Math.round(height)}px`);
      localStorage.setItem(VERIFY_HEIGHT_KEY, String(Math.round(height)));
    };
    const move = (moveEvent) => update(moveEvent.clientY);
    const finish = () => {
      splitter.classList.remove("dragging");
      splitter.removeEventListener("pointermove", move);
      splitter.removeEventListener("pointerup", finish);
      splitter.removeEventListener("pointercancel", finish);
    };
    splitter.addEventListener("pointermove", move);
    splitter.addEventListener("pointerup", finish);
    splitter.addEventListener("pointercancel", finish);
    update(event.clientY);
  });
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

function systemTheme() {
  return window.matchMedia?.("(prefers-color-scheme: dark)")?.matches ? "dark" : "light";
}

function applySystemThemePreference(enabled) {
  localStorage.setItem(SYSTEM_THEME_KEY, String(Boolean(enabled)));
  const input = $("#systemThemeInput");
  if (input) input.checked = Boolean(enabled);
  if (enabled) applyTheme(systemTheme());
}

function appearancePreference(key, fallback, allowed = null) {
  const value = localStorage.getItem(key) || fallback;
  return !allowed || allowed.includes(value) ? value : fallback;
}

function applyAppearancePreferences() {
  const highContrast = localStorage.getItem(HIGH_CONTRAST_KEY) === "true";
  const fontSize = appearancePreference(EDITOR_FONT_SIZE_KEY, "14", ["13", "14", "15", "16"]);
  const density = appearancePreference(EDITOR_DENSITY_KEY, "comfortable", ["compact", "comfortable", "spacious"]);
  document.documentElement.dataset.contrast = highContrast ? "high" : "normal";
  document.documentElement.dataset.editorDensity = density;
  document.documentElement.style.setProperty("--editor-font-size", `${fontSize}px`);
  const contrastInput = $("#highContrastInput");
  const fontInput = $("#editorFontSizeInput");
  const densityInput = $("#editorDensityInput");
  if (contrastInput) contrastInput.checked = highContrast;
  if (fontInput) fontInput.value = fontSize;
  if (densityInput) densityInput.value = density;
}

function hydrateAppearance(config = {}) {
  const systemSync = localStorage.getItem(SYSTEM_THEME_KEY) === "true";
  if (systemSync) {
    applySystemThemePreference(true);
  } else {
    const input = $("#systemThemeInput");
    if (input) input.checked = false;
    hydrateTheme(config);
  }
  applyAppearancePreferences();
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

function renderDiagnosticsSettings(config = {}) {
  const diagnostics = config.diagnostics || {};
  state.diagnostics = diagnostics;
  const enabled = Boolean(diagnostics.enabled);
  const input = $("#diagnosticsEnabledInput");
  if (input) input.checked = enabled;
  const storage = diagnostics.storage ? ` Storage: ${diagnostics.storage}` : "";
  $("#diagnosticsStatus").textContent = enabled
    ? `Diagnostics enabled locally. Remote upload is disabled.${storage}`
    : "Diagnostics are disabled until you opt in and save.";
}

function versionLabel(app = {}) {
  const channel = app.channel ? ` ${app.channel}` : "";
  return app.version ? `v${app.version}${channel}` : channel.trim();
}

function buildModeLabel(build = {}) {
  if (build.release) return `${build.mode || "packaged"} | ${build.release}`;
  return build.mode || "source";
}

function hydrateAppIdentity(app = {}, build = {}) {
  const displayName = app.display_name || app.app_name || "Talos";
  const version = versionLabel(app);
  document.title = displayName;
  $("#chromeAppName").textContent = displayName;
  $("#chromeVersion").textContent = version;
  $("#heroAppName").textContent = displayName;
  $("#modeLine").dataset.version = version || "";
  state.appBuild = build || {};
  renderReleaseDetails(app, build || {});
}

function renderReleaseDetails(app = {}, build = {}) {
  const release = build.release || `${app.display_name || app.app_name || "Talos"}-${app.version || ""}-${String(app.channel || "").toLowerCase()}`;
  const builtAt = build.built_at || "Source/debug build";
  const installerBuiltAt = build.installer_built_at || "Not packaged by installer";
  const artifacts = Array.isArray(build.artifacts) ? build.artifacts : [];
  $("#releaseDetails").innerHTML = `
    <div><span>Version</span><b>${escapeHtml(versionLabel(app) || "Unknown")}</b></div>
    <div><span>Release</span><b>${escapeHtml(release)}</b></div>
    <div><span>Mode</span><b>${escapeHtml(buildModeLabel(build))}</b></div>
    <div><span>Built</span><b>${escapeHtml(builtAt)}</b></div>
    <div><span>Installer</span><b>${escapeHtml(installerBuiltAt)}</b></div>
    <div><span>App data</span><b>${escapeHtml(build.app_data || "")}</b></div>
    <div><span>Artifacts</span><b>${escapeHtml(String(artifacts.length))}</b></div>
  `;
  const summary = $("#dashboardReleaseDetails");
  if (summary) {
    summary.innerHTML = `
      <div><span>Version</span><b>${escapeHtml(versionLabel(app) || "Unknown")}</b></div>
      <div><span>Release</span><b>${escapeHtml(release)}</b></div>
      <div><span>Mode</span><b>${escapeHtml(buildModeLabel(build))}</b></div>
      <div><span>Artifacts</span><b>${escapeHtml(String(artifacts.length))}</b></div>
    `;
  }
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

function formatDuration(value = 0) {
  const seconds = Number(value || 0);
  if (!Number.isFinite(seconds)) return "";
  if (seconds < 1) return `${Math.round(seconds * 1000)} ms`;
  return `${seconds.toFixed(2)} s`;
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
  const timings = result.timings || {};
  const libraries = result.libraries || [];
  const platforms = result.platforms || [];
  const issues = result.issues || [];
  const cache = result.cache || {};
  const timingRows = [
    ["Prepare", timings.prepare],
    ["Sandbox copy", timings.sandbox_copy],
    ["Compile", timings.compile],
    ["Total", timings.total],
  ].filter(([, value]) => Number.isFinite(Number(value)));
  if (!rows.length && !timingRows.length && !libraries.length && !platforms.length && !issues.length && !cache.hit) return "";
  return `
    <div class="verify-summary">
      ${rows.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`).join("")}
      ${timingRows.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><b>${escapeHtml(formatDuration(value))}</b></div>`).join("")}
      ${libraries.length ? `<div><span>Libraries</span><b>${escapeHtml(libraries.map((item) => `${item.name} ${item.version}`.trim()).join(", "))}</b></div>` : ""}
      ${platforms.length ? `<div><span>Platform</span><b>${escapeHtml(platforms.map((item) => `${item.name} ${item.version}`.trim()).join(", "))}</b></div>` : ""}
      ${issues.length ? `<div><span>Issues</span><b>${escapeHtml(String(issues.length))}</b></div>` : ""}
      ${cache.hit ? `<div><span>Cache</span><b>Reused result (${escapeHtml(formatDuration(cache.age_seconds))} old)</b></div>` : ""}
    </div>
  `;
}

function issueFileLabel(file = "") {
  const parts = String(file).split(/[\\/]/);
  return parts.pop() || String(file);
}

function verifyIssuesHtml(issues = []) {
  if (!issues.length) return "";
  return `
    <section class="verify-issues" aria-label="Compile issues">
      <div class="verify-section-title">Compile issues</div>
      <div class="verify-issue-list">
        ${issues.map((issue) => {
          const level = String(issue.level || "error").toLowerCase();
          const location = [
            issueFileLabel(issue.file),
            Number(issue.line || 0) || "",
            Number(issue.column || 0) || "",
          ].filter((value) => value !== "").join(":");
          return `
            <div class="verify-issue ${level === "warning" ? "warning" : "error"}">
              <span class="verify-issue-level">${escapeHtml(level)}</span>
              <code class="verify-issue-location" title="${escapeHtml(issue.file || "")}">${escapeHtml(location || "Compiler")}</code>
              <span class="verify-issue-message">${escapeHtml(issue.message || "Unknown compiler issue.")}</span>
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
}

function verifySourceLabel(source = "manual") {
  return source === "codex_patch" ? "Codex-applied edit" : "Manual edit";
}

function currentVerifyContext(source = verifySource()) {
  return {
    workspace: normalizedWindowsPath(state.selectedWorkspacePath),
    active_file: state.activeFilePath || "",
    fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value || "",
    source,
    editor_override: Boolean(state.activeFilePath && state.editorDirty),
    content: state.activeFilePath && state.editorDirty ? $("#sourceEditor").value : "",
  };
}

function currentVerifySignature(source = verifySource()) {
  return JSON.stringify(currentVerifyContext(source));
}

function verifyContextLabel(context = {}) {
  const parts = [
    verifySourceLabel(context.source || "manual"),
    context.active_file || "",
    context.fqbn || "",
    context.editor_override ? "unsaved editor draft" : "saved Arduino workspace",
  ].filter(Boolean);
  return parts.join(" | ");
}

function rememberVerifyResult(result = {}, signature = "", context = {}) {
  state.lastVerifyResult = result;
  state.lastVerifySignature = signature;
  state.lastVerifyOk = Boolean(result.ok);
  state.lastVerifyContext = { ...context, content: undefined };
}

function currentVerifyIsFresh(source = verifySource()) {
  return state.lastVerifyOk && state.lastVerifySignature === currentVerifySignature(source);
}

function renderVerifyOutput(result = null, pendingText = "") {
  const output = $("#arduinoOutput");
  if (!result) {
    output.className = `verify-output ${pendingText ? "pending" : "empty"}`;
    state.lastVerifyText = pendingText || "Sandbox compile has not been run.";
    state.lastIssueText = "";
    $("#copyIssuesBtn").disabled = true;
    output.textContent = state.lastVerifyText;
    renderStatusBar();
    return;
  }
  const ok = Boolean(result.ok);
  const status = result.status || (ok ? "passed" : "failed");
  const command = result.command || "";
  const sandbox = result.sandbox || "";
  const context = result.verify_context || state.lastVerifyContext || {};
  const contextText = verifyContextLabel(context);
  state.lastVerifyText = [
    `Status: ${status}`,
    contextText ? `Context: ${contextText}` : "",
    command ? `Command: ${command}` : "",
    sandbox ? `Sandbox: ${sandbox}` : "",
    "",
    result.output || "No compiler output.",
  ].filter(Boolean).join("\n");
  state.lastIssueText = result.issue_context || "";
  $("#copyIssuesBtn").disabled = !state.lastIssueText;
  output.className = `verify-output ${ok ? "passed" : "failed"}`;
  output.innerHTML = `
    <div class="verify-head">
      <span class="verify-badge">${escapeHtml(status)}</span>
      <span class="verify-command-name">${escapeHtml(commandBaseName(command) || "arduino-cli")}</span>
      ${result.cache?.hit ? '<span class="verify-command-name">cached</span>' : ""}
    </div>
    ${contextText ? `<div class="verify-field"><span>Context</span><code>${escapeHtml(contextText)}</code></div>` : ""}
    ${command ? `<div class="verify-field"><span>Command</span><code>${escapeHtml(command)}</code></div>` : ""}
    ${sandbox ? `<div class="verify-field"><span>Sandbox</span><code>${escapeHtml(sandbox)}</code></div>` : ""}
    ${verifySummaryHtml(result)}
    ${verifyIssuesHtml(result.issues || [])}
    <section class="verify-raw" aria-label="Compiler output">
      <div class="verify-section-title">Compiler output</div>
      <pre class="verify-log">${escapeHtml(result.output || "No compiler output.")}</pre>
    </section>
  `;
  renderStatusBar();
}

function setOutputView(view) {
  const historyVisible = view === "history";
  $("#arduinoOutput").toggleAttribute("hidden", historyVisible);
  $("#runHistory").toggleAttribute("hidden", !historyVisible);
  $("#arduinoOutput").setAttribute("aria-hidden", String(historyVisible));
  $("#runHistory").setAttribute("aria-hidden", String(!historyVisible));
  $("#verifyOutputTab").classList.toggle("active", !historyVisible);
  $("#runHistoryTab").classList.toggle("active", historyVisible);
  $("#verifyOutputTab").setAttribute("aria-selected", String(!historyVisible));
  $("#runHistoryTab").setAttribute("aria-selected", String(historyVisible));
  $("#copyIssuesBtn").hidden = historyVisible;
  $("#copyVerifyBtn").hidden = historyVisible;
  $("#recordEvidenceBtn").hidden = historyVisible;
  $("#runHistoryFilter").hidden = !historyVisible;
  $("#runHistorySketchLabel").hidden = !historyVisible;
  $("#copySupportBundleBtn").hidden = !historyVisible;
}

function eventKindLabel(event) {
  if (event.type === "verify") return event.source === "codex_patch" ? "VERIFY CODEX" : "VERIFY";
  if (event.type === "codex_turn") return "CODEX";
  if (event.type === "release_evidence") return "EVIDENCE";
  if (event.type !== "patch") return String(event.type || "EVENT").toUpperCase();
  const actions = (event.timeline || []).map((entry) => String(entry.action || "").toLowerCase());
  if (actions.some((action) => action.includes("rolled-back"))) return "ROLLBACK";
  if (actions.some((action) => action.includes("conflict"))) return "CONFLICT";
  if (actions.some((action) => action === "saved")) return "SAVED";
  return "PATCH";
}

function renderRunHistory(events = []) {
  const signature = JSON.stringify(events);
  if (signature === state.runHistorySignature) return;
  state.runHistorySignature = signature;
  $("#runHistory").innerHTML = events.length
    ? events.map((event) => {
        if (event.type === "patch") {
          const files = event.files || [];
          const timeline = event.timeline || [];
          return `
            <article class="run-history-item patch">
              <div class="run-history-main">
                <span class="run-history-badge">${eventKindLabel(event)}</span>
                <div>
                  <strong>${files.length} file(s) from Codex</strong>
                  <span>${escapeHtml(event.status || "staged")} | ${escapeHtml(event.time || "")}</span>
                </div>
              </div>
              <div class="run-history-files">
                ${files.map((file) => `<code>${escapeHtml(file.kind || "update")} ${escapeHtml(file.path || "")} | ${Number(file.hunks || 0)} hunk(s) | ${escapeHtml(file.status || "staged")}</code>`).join("")}
              </div>
              <ol class="patch-timeline">
                ${timeline.map((entry) => `<li><strong>${escapeHtml(String(entry.action || "updated").replaceAll("-", " "))}</strong><span>${escapeHtml(entry.path || entry.detail?.status || "")} ${escapeHtml(entry.time || "")}</span></li>`).join("")}
              </ol>
            </article>`;
        }
        if (event.type === "codex_turn") {
          return `
            <article class="run-history-item codex-turn">
              <div class="run-history-main">
                <span class="run-history-badge">${eventKindLabel(event)}</span>
                <div>
                  <strong>${escapeHtml(event.status || "updated")}</strong>
                  <span>${escapeHtml(event.workspace || "no workspace")} | ${escapeHtml(event.time || "")}</span>
                </div>
              </div>
              ${event.message ? `<p>${escapeHtml(event.message)}</p>` : ""}
            </article>`;
        }
        if (event.type === "release_evidence") {
          return `
            <article class="run-history-item verify ${event.ok ? "passed" : "failed"}">
              <span class="run-history-badge">EVIDENCE</span>
              <span class="run-history-copy">
                <strong>${escapeHtml(event.main_sketch || "Arduino MVP")}</strong>
                <span>${escapeHtml(event.release || "0.1.0-beta")} | profile ${event.profile_ready ? "ready" : "blocked"} | ${escapeHtml(event.time || "")}</span>
              </span>
            </article>`;
        }
        const source = event.source === "codex_patch" ? "After Codex patch" : "Manual verify";
        return `
          <button class="run-history-item verify ${event.ok ? "passed" : "failed"}" type="button" data-verify-history-id="${escapeHtml(event.id || "")}">
            <span class="run-history-badge">${escapeHtml(event.status || "failed")}</span>
            <span class="run-history-copy">
              <strong>${escapeHtml(event.main_sketch || "Arduino sketch")}</strong>
              <span>${escapeHtml(source)} | ${escapeHtml(event.time || "")}</span>
            </span>
          </button>`;
      }).join("")
    : '<div class="run-history-empty">No verify attempts or Codex patches recorded yet.</div>';
  $$("[data-verify-history-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const event = events.find((item) => item.id === button.dataset.verifyHistoryId);
      if (!event?.result) return;
      renderVerifyOutput(event.result);
      setOutputView("verify");
    });
  });
}

function verifySource() {
  const patch = state.codexPatches.find((item) => (
    normalizedWindowsPath(item.workspace || "") === normalizedWindowsPath(state.selectedWorkspacePath)
    && (item.files || []).some((file) => (
      file.path === state.activeFilePath
      && ["applied-to-editor", "saved"].includes(file.review_status || "")
    ))
  ));
  return patch ? "codex_patch" : "manual";
}

async function refreshRunHistory() {
  const params = new URLSearchParams();
  if (state.selectedWorkspacePath) params.set("workspace", state.selectedWorkspacePath);
  if (state.runHistorySketchOnly && state.activeFilePath) params.set("sketch", state.activeFilePath);
  if (state.runHistoryFilter) params.set("kind", state.runHistoryFilter);
  const payload = await api(`/api/run_history?${params.toString()}`);
  renderRunHistory(payload.events || []);
  return payload;
}

async function copySupportBundle() {
  const result = await api("/api/support_bundle?redact=1");
  await copyText(JSON.stringify(result.bundle || {}, null, 2), "#editorStatus");
  await recordDiagnosticEvent("support_bundle_copied", { workspace: state.selectedWorkspacePath, redacted: true });
  $("#editorStatus").textContent = "Copied redacted support bundle.";
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

async function copyRawText(text) {
  await navigator.clipboard.writeText(String(text ?? ""));
}

function fileListText() {
  return $$("#arduinoFiles tr").map((row) => [...row.children].map((cell) => cell.textContent.trim()).join("\t")).join("\n");
}

function setEditorDirty(dirty) {
  state.editorDirty = Boolean(dirty);
  $("#editorDirtyBadge").hidden = !state.editorDirty;
  const conflicted = state.conflictedFilePaths.has(state.activeFilePath);
  $("#saveFileBtn").disabled = !state.activeFilePath || !state.editorDirty || state.editorSaving || conflicted;
  $("#saveAndVerifyBtn").disabled = !state.activeFilePath || !state.editorDirty || state.editorSaving || conflicted;
  $("#rollbackFileBtn").disabled = !state.activeFilePath || !state.lastCheckpoint || state.editorSaving || conflicted;
  renderStatusBar();
}

function setCheckpoint(checkpoint = null, history = [], retention = {}) {
  state.lastCheckpoint = checkpoint || null;
  const button = $("#rollbackFileBtn");
  const available = Boolean(state.activeFilePath && state.lastCheckpoint && !state.editorSaving && !state.conflictedFilePaths.has(state.activeFilePath));
  const historyText = history.length
    ? ` | ${history.length}/${Number(retention.history_limit || history.length)} rollback point(s) retained`
    : "";
  button.disabled = !available;
  button.title = available
    ? `Restore ${state.activeFilePath} to its state before Talos saved it at ${state.lastCheckpoint.created_at || "the last checkpoint"}${historyText}`
    : "No safe Talos checkpoint is available for this file";
}

async function refreshCheckpoint() {
  if (!state.activeFilePath) {
    setCheckpoint();
    return;
  }
  try {
    const result = await api(`/api/arduino_checkpoint?path=${encodeURIComponent(state.activeFilePath)}`);
    setCheckpoint(result.checkpoint, result.history || [], result.retention || {});
  } catch (_error) {
    setCheckpoint();
  }
}

function updateEditorAccess() {
  const editor = $("#sourceEditor");
  const reviewOpen = $(".source-editor").classList.contains("reviewing");
  const canEdit = Boolean(state.activeFilePath && state.localEditMode && !reviewOpen);
  editor.disabled = !canEdit;
  $(".source-editor").classList.toggle("viewing", Boolean(state.activeFilePath && !canEdit && !reviewOpen));
  const button = $("#editInTalosBtn");
  button.disabled = !state.activeFilePath || reviewOpen;
  button.classList.toggle("active", canEdit);
  button.textContent = canEdit ? "Review" : "Edit";
  button.title = canEdit
    ? "Return to review mode; local changes remain until saved or discarded"
    : "Enable local editing in Talos; Arduino IDE is not updated until Save File";
  button.setAttribute("aria-pressed", String(canEdit));
  $("#editorModeBadge").textContent = reviewOpen ? "Reviewing" : canEdit ? "Local edit" : "Review";
}

function setLocalEditMode(enabled) {
  if (!state.activeFilePath || $(".source-editor").classList.contains("reviewing")) return;
  state.localEditMode = Boolean(enabled);
  updateEditorAccess();
  if (state.localEditMode) {
    $("#editorStatus").textContent = "Local edit mode. Save File is required to update Arduino IDE.";
    $("#sourceEditor").focus();
  } else if (state.editorDirty) {
    $("#editorStatus").textContent = "Review mode. Local changes are retained; Save File updates Arduino IDE.";
  } else {
    $("#editorStatus").textContent = "Review mode. Arduino IDE owns the saved sketch.";
  }
}

function renderEditorLineNumbers() {
  const editor = $("#sourceEditor");
  const lineCount = Math.max(1, editor.value.split("\n").length);
  $("#editorLineNumbers").textContent = Array.from(
    { length: lineCount },
    (_value, index) => String(index + 1),
  ).join("\n");
  updateEditorCursorLine();
}

function applyEditorFileResult(result, statusText = "") {
  state.activeFilePath = result.path;
  state.localEditMode = false;
  if (state.selectedWorkspacePath && result.path) {
    state.activeFileByWorkspace[normalizedWindowsPath(state.selectedWorkspacePath)] = result.path;
  }
  state.editorOriginalContent = result.content || "";
  setCheckpoint();
  state.editorFileMtimeNs = Number(result.mtime_ns || 0);
  state.codexPreviewPath = "";
  state.codexPreviewStreaming = false;
  state.codexPreviewCommitted = false;
  state.codexPreviewBaseContent = "";
  state.codexPreviewContent = "";
  state.codexReviewPatch = null;
  if (state.codexPreviewTimer) window.clearTimeout(state.codexPreviewTimer);
  state.codexPreviewTimer = null;
  $("#editorFileName").textContent = result.path;
  setCodexReviewMode(null);
  $("#sourceEditor").value = state.editorOriginalContent;
  renderEditorLineNumbers();
  updateEditorAccess();
  $("#editorStatus").textContent = statusText || `Review mode | ${Number(result.bytes || 0)} bytes | Arduino IDE owns the saved sketch.`;
  setEditorDirty(false);
  renderStatusBar();
}

function markTalosWrite(path, content, mtimeNs = 0) {
  state.editorWriteGuard = {
    path: String(path || ""),
    content: String(content || ""),
    mtimeNs: Number(mtimeNs || 0),
    until: Date.now() + TALOS_WRITE_DEBOUNCE_MS,
  };
}

function recentTalosWriteMatches(path) {
  const guard = state.editorWriteGuard;
  if (!guard || guard.path !== path) return false;
  if (Date.now() > guard.until) {
    state.editorWriteGuard = null;
    return false;
  }
  return true;
}

function applyStoredCodexDraft() {
  const workspace = normalizedWindowsPath(state.selectedWorkspacePath);
  const draft = [...state.codexPatches].reverse().flatMap((patch) => (
    normalizedWindowsPath(patch.workspace || "") === workspace ? patch.files || [] : []
  )).find((file) => (
    file.path === state.activeFilePath
    && file.review_status === "applied-to-editor"
    && Object.hasOwn(file, "editor_content")
  ));
  if (!draft) return;
  $("#sourceEditor").value = String(draft.editor_content || "");
  renderEditorLineNumbers();
  setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
  $("#editorStatus").textContent = "Applied Codex draft. Save File is required to update Arduino IDE.";
}

function activeCodexAppliedFile() {
  return [...state.codexPatches].reverse().flatMap((patch) => (
    normalizedWindowsPath(patch.workspace || "") === normalizedWindowsPath(state.selectedWorkspacePath) ? patch.files || [] : []
  )).find((file) => (
    file.path === state.activeFilePath
    && file.review_status === "applied-to-editor"
  ));
}

function shouldWarnUnverifiedCodexSave() {
  return Boolean(state.editorDirty && activeCodexAppliedFile() && !currentVerifyIsFresh("codex_patch"));
}

function resetEditor(message = "No file selected.") {
  state.activeFilePath = "";
  setCheckpoint();
  state.localEditMode = false;
  state.editorOriginalContent = "";
  state.editorFileMtimeNs = 0;
  state.editorWriteGuard = null;
  state.editorLoading = false;
  state.editorSaving = false;
  state.editorDiskChecking = false;
  state.codexPreviewPath = "";
  state.codexPreviewStreaming = false;
  state.codexPreviewCommitted = false;
  state.codexPreviewBaseContent = "";
  state.codexPreviewContent = "";
  state.codexReviewPatch = null;
  if (state.codexPreviewTimer) window.clearTimeout(state.codexPreviewTimer);
  state.codexPreviewTimer = null;
  $("#editorFileName").textContent = "Select a source file";
  setCodexReviewMode(null);
  $("#sourceEditor").value = "";
  renderEditorLineNumbers();
  $("#sourceEditor").disabled = true;
  updateEditorAccess();
  $("#editorStatus").textContent = message;
  setEditorDirty(false);
  renderStatusBar();
}

function canDiscardEditorChanges() {
  return !state.editorDirty || window.confirm("Discard unsaved changes in the current source file?");
}

async function openWorkspaceFile(path) {
  if (!path || path === state.activeFilePath || state.editorLoading) return;
  if (!canDiscardEditorChanges()) return;
  state.editorLoading = true;
  $("#editorStatus").textContent = `Loading ${path}...`;
  try {
    const result = await api(`/api/arduino_file?path=${encodeURIComponent(path)}`);
    applyEditorFileResult(result);
    applyStoredCodexDraft();
    renderActiveFileRow();
    refreshCodexReview(state.codexPatches);
    await refreshCheckpoint();
  } catch (error) {
    $("#editorStatus").textContent = `Open failed: ${error.message}`;
  } finally {
    state.editorLoading = false;
  }
}

function renderActiveFileRow() {
  $$("#arduinoFiles tr").forEach((row) => {
    row.classList.toggle("active", row.dataset.path === state.activeFilePath);
  });
}

async function saveWorkspaceFile(options = {}) {
  if (!state.activeFilePath || !state.editorDirty || state.editorSaving) return false;
  if (state.conflictedFilePaths.has(state.activeFilePath)) {
    $("#editorStatus").textContent = "Save blocked: this file changed outside Talos and requires conflict resolution.";
    return false;
  }
  if (!options.skipVerifyWarning && shouldWarnUnverifiedCodexSave()) {
    const confirmed = window.confirm(
      "This Codex-applied editor draft has not passed a current Verify Sandbox run. Save to Arduino IDE anyway?",
    );
    if (!confirmed) {
      $("#editorStatus").textContent = "Save paused. Run Save + Verify or Verify Sandbox before saving the Codex draft.";
      return false;
    }
  }
  state.editorSaving = true;
  $("#saveFileBtn").disabled = true;
  $("#editorStatus").textContent = `Saving ${state.activeFilePath}...`;
  try {
    const content = $("#sourceEditor").value;
    const result = await api("/api/arduino_file", {
      method: "POST",
      body: JSON.stringify({ path: state.activeFilePath, content }),
    });
    markTalosWrite(result.path || state.activeFilePath, content, result.mtime_ns);
    state.editorOriginalContent = content;
    state.editorFileMtimeNs = Number(result.mtime_ns || 0);
    state.localEditMode = false;
    $("#editorStatus").textContent = `Saved ${result.path} (${Number(result.bytes || 0)} bytes).`;
    setEditorDirty(false);
    setCheckpoint(result.checkpoint);
    updateEditorAccess();
    void api("/api/codex_save_patch", {
      method: "POST",
      body: JSON.stringify({ path: state.activeFilePath }),
    }).then(() => refreshCodex()).catch((error) => {
      $("#codexStatus").textContent = `File saved, but change status could not be synced: ${error.message}`;
    });
    await refresh();
    return true;
  } catch (error) {
    $("#editorStatus").textContent = `Save failed: ${error.message}`;
    return false;
  } finally {
    state.editorSaving = false;
    setEditorDirty(state.editorDirty);
  }
}

async function saveAndVerifyWorkspace() {
  if (!state.activeFilePath || !state.editorDirty) return;
  $("#editorStatus").textContent = "Save + Verify runs sandbox compile before saving to Arduino IDE.";
  const result = await verifyArduinoWorkspace(verifySource());
  if (!result?.ok) {
    $("#editorStatus").textContent = "Save + Verify stopped because sandbox verify did not pass. Arduino IDE was not changed.";
    return;
  }
  await saveWorkspaceFile({ skipVerifyWarning: true });
}

async function rollbackWorkspaceFile() {
  if (!state.activeFilePath || !state.lastCheckpoint || state.editorSaving) return;
  if (!window.confirm(`Restore ${state.activeFilePath} to the state before Talos's last save?`)) return;
  state.editorSaving = true;
  setEditorDirty(state.editorDirty);
  try {
    await api("/api/arduino_rollback", {
      method: "POST",
      body: JSON.stringify({ path: state.activeFilePath }),
    });
    const restored = await api(`/api/arduino_file?path=${encodeURIComponent(state.activeFilePath)}`);
    markTalosWrite(restored.path || state.activeFilePath, restored.content || "", restored.mtime_ns);
    applyEditorFileResult(restored, "Restored the file from the Talos checkpoint. Arduino IDE now has the restored version.");
    setCheckpoint();
    await refresh();
  } catch (error) {
    $("#editorStatus").textContent = `Rollback failed: ${error.message}`;
  } finally {
    state.editorSaving = false;
    setEditorDirty(state.editorDirty);
  }
}

function selectEditorLine(lineNumber) {
  const editor = $("#sourceEditor");
  if (!lineNumber || editor.disabled) return;
  const lines = editor.value.split("\n");
  const lineIndex = Math.min(Math.max(lineNumber - 1, 0), lines.length - 1);
  let start = 0;
  for (let index = 0; index < lineIndex; index += 1) {
    start += lines[index].length + 1;
  }
  const end = Math.min(editor.value.length, start + lines[lineIndex].length);
  editor.focus();
  editor.setSelectionRange(start, end);
}

function editorLineBoundsAt(position, includeLineBreak = false) {
  const editor = $("#sourceEditor");
  const value = editor.value;
  const cursor = Math.min(Math.max(Number(position || 0), 0), value.length);
  const start = value.lastIndexOf("\n", Math.max(0, cursor - 1)) + 1;
  const newline = value.indexOf("\n", cursor);
  const lineEnd = newline === -1 ? value.length : newline;
  const end = includeLineBreak && newline !== -1 ? newline + 1 : lineEnd;
  return { start, end, lineEnd };
}

function editorSelectionLineBounds() {
  const editor = $("#sourceEditor");
  const value = editor.value;
  const start = value.lastIndexOf("\n", Math.max(0, editor.selectionStart - 1)) + 1;
  const selectionEnd = editor.selectionEnd > editor.selectionStart ? editor.selectionEnd - 1 : editor.selectionEnd;
  const newline = value.indexOf("\n", selectionEnd);
  const end = newline === -1 ? value.length : newline;
  return { start, end };
}

function markEditorShortcutChange(message) {
  renderEditorLineNumbers();
  setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
  $("#editorStatus").textContent = message;
  renderCodexContextPreview();
}

function replaceEditorRangeNative(start, end, text, selectionStart, selectionEnd, message) {
  const editor = $("#sourceEditor");
  editor.focus();
  editor.setSelectionRange(start, end);
  const inserted = document.execCommand?.("insertText", false, text);
  if (!inserted) {
    editor.setRangeText(text, start, end, "end");
  }
  editor.setSelectionRange(selectionStart, selectionEnd);
  markEditorShortcutChange(message);
}

function copyCurrentEditorLine(cut = false) {
  const editor = $("#sourceEditor");
  if (!state.activeFilePath || editor.selectionStart !== editor.selectionEnd) return false;
  const { start, end } = editorLineBoundsAt(editor.selectionStart, true);
  const text = editor.value.slice(start, end);
  if (cut && !editor.disabled) {
    editor.focus();
    editor.setSelectionRange(start, end);
    const cutDone = document.execCommand?.("cut");
    if (!cutDone) {
      copyRawText(text).catch((error) => {
        $("#editorStatus").textContent = `Copy failed: ${error.message}`;
      });
      replaceEditorRangeNative(start, end, "", start, start, "Cut current line.");
      return true;
    }
    markEditorShortcutChange("Cut current line.");
  } else {
    copyRawText(text).catch((error) => {
      $("#editorStatus").textContent = `Copy failed: ${error.message}`;
    });
    $("#editorStatus").textContent = "Copied current line.";
  }
  return true;
}

function duplicateEditorLine(direction = "down") {
  const editor = $("#sourceEditor");
  if (!state.activeFilePath || editor.disabled) return false;
  const { start, lineEnd } = editorLineBoundsAt(editor.selectionStart, false);
  const line = editor.value.slice(start, lineEnd);
  if (direction === "up") {
    replaceEditorRangeNative(start, start, `${line}\n`, start, start + line.length, "Duplicated current line.");
  } else {
    const insertAt = lineEnd < editor.value.length ? lineEnd + 1 : lineEnd;
    const prefix = lineEnd < editor.value.length ? "" : "\n";
    const nextStart = insertAt + prefix.length;
    replaceEditorRangeNative(insertAt, insertAt, `${prefix}${line}\n`, nextStart, nextStart + line.length, "Duplicated current line.");
  }
  return true;
}

function moveEditorLine(direction = "down") {
  const editor = $("#sourceEditor");
  if (!state.activeFilePath || editor.disabled) return false;
  const value = editor.value;
  const current = editorLineBoundsAt(editor.selectionStart, true);
  if (direction === "up") {
    if (current.start === 0) return true;
    const previousEnd = current.start - 1;
    const previousStart = value.lastIndexOf("\n", Math.max(0, previousEnd - 1)) + 1;
    const previous = value.slice(previousStart, current.start);
    const line = value.slice(current.start, current.end);
    replaceEditorRangeNative(
      previousStart,
      current.end,
      line + previous,
      previousStart,
      previousStart + Math.max(0, line.length - 1),
      "Moved current line up.",
    );
  } else {
    if (current.end >= value.length) return true;
    const nextEndNewline = value.indexOf("\n", current.end);
    const nextEnd = nextEndNewline === -1 ? value.length : nextEndNewline + 1;
    const line = value.slice(current.start, current.end);
    const next = value.slice(current.end, nextEnd);
    const nextStart = current.start + next.length;
    replaceEditorRangeNative(
      current.start,
      nextEnd,
      next + line,
      nextStart,
      nextStart + Math.max(0, line.length - 1),
      "Moved current line down.",
    );
  }
  return true;
}

function toggleEditorLineComment() {
  const editor = $("#sourceEditor");
  if (!state.activeFilePath || editor.disabled) return false;
  const { start, end } = editorSelectionLineBounds();
  const block = editor.value.slice(start, end);
  const lines = block.split("\n");
  const commentable = lines.filter((line) => line.trim().length);
  const shouldUncomment = commentable.length && commentable.every((line) => /^\s*\/\//.test(line));
  const nextLines = lines.map((line) => {
    if (!line.trim()) return line;
    if (shouldUncomment) return line.replace(/^(\s*)\/\/\s?/, "$1");
    return line.replace(/^(\s*)/, "$1// ");
  });
  const nextBlock = nextLines.join("\n");
  replaceEditorRangeNative(
    start,
    end,
    nextBlock,
    start,
    start + nextBlock.length,
    shouldUncomment ? "Uncommented selected line(s)." : "Commented selected line(s).",
  );
  return true;
}

function updateFindStatus() {
  const status = $("#editorFindStatus");
  if (!status) return;
  if (!state.editorFindQuery) {
    status.textContent = "";
  } else if (!state.editorFindMatches.length) {
    status.textContent = "No results";
  } else {
    status.textContent = `${state.editorFindIndex + 1}/${state.editorFindMatches.length}`;
  }
}

function collectEditorFindMatches(query) {
  const editor = $("#sourceEditor");
  const matches = [];
  if (!query) return matches;
  const haystack = editor.value.toLowerCase();
  const needle = query.toLowerCase();
  let index = haystack.indexOf(needle);
  while (index !== -1) {
    matches.push({ start: index, end: index + query.length });
    index = haystack.indexOf(needle, index + Math.max(1, query.length));
  }
  return matches;
}

function editorCursorLineIndex() {
  const editor = $("#sourceEditor");
  if (!editor) return 0;
  return editor.value.slice(0, Math.max(0, editor.selectionStart || 0)).split("\n").length - 1;
}

function updateEditorCursorLine() {
  const editor = $("#sourceEditor");
  const canvas = $(".editor-canvas");
  if (!editor || !canvas || !state.activeFilePath) {
    canvas?.classList.remove("has-cursor-line");
    return;
  }
  const style = window.getComputedStyle(editor);
  const lineHeight = Number.parseFloat(style.lineHeight) || 20;
  const paddingTop = Number.parseFloat(style.paddingTop) || 0;
  const top = paddingTop + (editorCursorLineIndex() * lineHeight) - editor.scrollTop;
  canvas.style.setProperty("--cursor-line-top", `${top}px`);
  canvas.style.setProperty("--cursor-line-height", `${lineHeight}px`);
  canvas.classList.add("has-cursor-line");
  renderEditorFindLayer();
}

function syncEditorFindRenderScroll() {
  const editor = $("#sourceEditor");
  const render = $("#editorFindRender");
  if (!editor || !render || render.hidden) return;
  render.style.transform = `translate(${-editor.scrollLeft}px, ${-editor.scrollTop}px)`;
}

function renderEditorFindLayer() {
  const editor = $("#sourceEditor");
  const render = $("#editorFindRender");
  const canvas = $(".editor-canvas");
  if (!editor || !render || !canvas) return;
  const active = !$("#editorFindBar").hidden && Boolean(state.editorFindQuery);
  if (!active) {
    render.hidden = true;
    render.innerHTML = "";
    render.style.transform = "";
    canvas.classList.remove("finding");
    return;
  }

  const value = editor.value || "";
  const matches = state.editorFindMatches || [];
  const current = matches[state.editorFindIndex] || null;
  const cursorLineIndex = editorCursorLineIndex();
  const lines = value.split("\n");
  let cursor = 0;
  render.innerHTML = lines.map((line, index) => {
    const lineStart = cursor;
    const lineEnd = lineStart + line.length;
    const activeLine = index === cursorLineIndex;
    const lineMatches = matches.filter((match) => match.start < lineEnd && match.end > lineStart);
    let lineCursor = 0;
    const html = lineMatches.map((match) => {
      const start = Math.max(0, match.start - lineStart);
      const end = Math.min(line.length, match.end - lineStart);
      if (end <= lineCursor) return "";
      const before = escapeHtml(line.slice(lineCursor, start));
      const text = escapeHtml(line.slice(start, end)) || "&nbsp;";
      lineCursor = end;
      const currentClass = current && match.start === current.start && match.end === current.end ? " current" : "";
      return `${before}<span class="editor-find-match${currentClass}">${text}</span>`;
    }).join("");
    const tail = escapeHtml(line.slice(lineCursor)) || (line.length ? "" : "&#8203;");
    cursor = lineEnd + 1;
    return `<span class="editor-find-line${activeLine ? " cursor-line" : ""}">${html}${tail}</span>`;
  }).join("");
  render.hidden = false;
  canvas.classList.add("finding");
  syncEditorFindRenderScroll();
}

function scrollEditorToPosition(position) {
  const editor = $("#sourceEditor");
  const valueBefore = editor.value.slice(0, Math.max(0, position));
  const lineIndex = valueBefore.split("\n").length - 1;
  const lineStart = valueBefore.lastIndexOf("\n") + 1;
  const columnIndex = Math.max(0, valueBefore.length - lineStart);
  const style = window.getComputedStyle(editor);
  const lineHeight = Number.parseFloat(style.lineHeight) || 20;
  const fontSize = Number.parseFloat(style.fontSize) || 14;
  const targetTop = Math.max(0, (lineIndex * lineHeight) - (editor.clientHeight * 0.35));
  const targetLeft = Math.max(0, (columnIndex * fontSize * 0.62) - (editor.clientWidth * 0.25));
  editor.scrollTop = targetTop;
  editor.scrollLeft = targetLeft;
  $("#editorLineNumbers").scrollTop = editor.scrollTop;
  syncEditorFindRenderScroll();
  updateEditorCursorLine();
}

function selectEditorFindMatch(index) {
  const editor = $("#sourceEditor");
  if (!state.editorFindMatches.length) {
    updateFindStatus();
    return;
  }
  state.editorFindIndex = (index + state.editorFindMatches.length) % state.editorFindMatches.length;
  const match = state.editorFindMatches[state.editorFindIndex];
  scrollEditorToPosition(match.start);
  editor.focus({ preventScroll: true });
  editor.setSelectionRange(match.start, match.end);
  updateFindStatus();
  updateEditorCursorLine();
  renderEditorFindLayer();
}

function runEditorFind(direction = 1, keepCurrent = false) {
  const input = $("#editorFindInput");
  const editor = $("#sourceEditor");
  state.editorFindQuery = input.value;
  state.editorFindMatches = collectEditorFindMatches(state.editorFindQuery);
  if (!state.editorFindMatches.length) {
    state.editorFindIndex = -1;
    updateFindStatus();
    renderEditorFindLayer();
    input.focus();
    return;
  }
  const current = state.editorFindMatches.findIndex((match) => (
    match.start === editor.selectionStart && match.end === editor.selectionEnd
  ));
  if (keepCurrent && current !== -1) {
    selectEditorFindMatch(current);
    return;
  }
  const startIndex = current === -1
    ? state.editorFindMatches.findIndex((match) => match.start >= editor.selectionEnd)
    : current + direction;
  selectEditorFindMatch(startIndex === -1 ? 0 : startIndex);
}

function showEditorFind() {
  const editor = $("#sourceEditor");
  if (!state.activeFilePath) return false;
  const selected = editor.value.slice(editor.selectionStart, editor.selectionEnd).trim();
  const input = $("#editorFindInput");
  $("#editorFindBar").hidden = false;
  input.value = selected || state.editorFindQuery || "";
  input.focus();
  input.select();
  if (input.value) runEditorFind(1, Boolean(selected));
  else updateFindStatus();
  renderEditorFindLayer();
  return true;
}

function hideEditorFind() {
  $("#editorFindBar").hidden = true;
  state.editorFindIndex = -1;
  renderEditorFindLayer();
  $("#sourceEditor").focus();
  return true;
}

function redirectEditorFindKeystroke(event) {
  if ($("#editorFindBar").hidden) return false;
  if (event.ctrlKey || event.metaKey || event.altKey) return false;
  const input = $("#editorFindInput");
  const key = event.key;
  if (key === "Escape") {
    event.preventDefault();
    hideEditorFind();
    return true;
  }
  if (key === "Enter") {
    event.preventDefault();
    runEditorFind(event.shiftKey ? -1 : 1);
    return true;
  }
  if (key === "Backspace") {
    event.preventDefault();
    input.value = input.value.slice(0, -1);
    runEditorFind(1);
    return true;
  }
  if (key.length === 1) {
    event.preventDefault();
    input.value += key;
    runEditorFind(1);
    return true;
  }
  return false;
}

function handleEditorShortcut(event) {
  if (redirectEditorFindKeystroke(event)) return;
  const key = event.key.toLowerCase();
  const command = event.ctrlKey || event.metaKey;
  if (command && key === "s") {
    event.preventDefault();
    saveWorkspaceFile();
    return;
  }
  if (command && event.shiftKey && key === "b") {
    event.preventDefault();
    verifyArduinoWorkspace();
    return;
  }
  if (command && key === "f") {
    event.preventDefault();
    showEditorFind();
    return;
  }
  if (command && key === "/" && toggleEditorLineComment()) {
    event.preventDefault();
    return;
  }
  if (command && key === "c" && copyCurrentEditorLine(false)) {
    event.preventDefault();
    return;
  }
  if (command && key === "x" && copyCurrentEditorLine(true)) {
    event.preventDefault();
    return;
  }
  if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === "ArrowUp" || event.key === "ArrowDown")) {
    event.preventDefault();
    const direction = event.key === "ArrowUp" ? "up" : "down";
    if (event.shiftKey) duplicateEditorLine(direction);
    else moveEditorLine(direction);
  }
}

function lineFromGutterEvent(event) {
  const gutter = $("#editorLineNumbers");
  const style = window.getComputedStyle(gutter);
  const lineHeight = Number.parseFloat(style.lineHeight) || 20;
  const paddingTop = Number.parseFloat(style.paddingTop) || 0;
  const y = event.clientY - gutter.getBoundingClientRect().top + gutter.scrollTop - paddingTop;
  return Math.floor(Math.max(0, y) / lineHeight) + 1;
}

async function checkActiveFileOnDisk() {
  if (
    document.hidden
    || activeViewId() !== "workspace"
    || !state.activeFilePath
    || state.editorDirty
    || state.editorLoading
    || state.editorSaving
    || state.editorDiskChecking
    || state.codexPreviewStreaming
    || state.codexPreviewCommitted
  ) {
    return;
  }
  if (recentTalosWriteMatches(state.activeFilePath)) {
    return;
  }
  state.editorDiskChecking = true;
  try {
    const result = await api(`/api/arduino_file?path=${encodeURIComponent(state.activeFilePath)}`);
    const nextMtime = Number(result.mtime_ns || 0);
    if (nextMtime && state.editorFileMtimeNs && nextMtime === state.editorFileMtimeNs) return;
    if ((result.content || "") === state.editorOriginalContent) {
      state.editorFileMtimeNs = nextMtime;
      return;
    }
    applyEditorFileResult(result, `Reloaded from disk (${Number(result.bytes || 0)} bytes).`);
    renderActiveFileRow();
    await refreshCheckpoint();
  } catch (error) {
    resetEditor(`Active file reload failed: ${error.message}`);
  } finally {
    state.editorDiskChecking = false;
  }
}

function setBoardField(fqbn = "", boardName = "") {
  state.arduinoFqbnFull = fqbn || "";
  state.arduinoBoardName = boardName || "";
  $("#arduinoFqbnInput").value = compactBoardLabel(state.arduinoFqbnFull, state.arduinoBoardName);
  $("#boardInfoPanel").textContent = boardInfoText(state.arduinoFqbnFull, state.arduinoBoardName);
  $("#boardInfoBtn").disabled = !state.arduinoFqbnFull;
  renderCodexContextPreview();
}

function normalizedWindowsPath(value = "") {
  return String(value).trim().replaceAll("/", "\\").replace(/\\+$/, "").toLowerCase();
}

function applyUnifiedDiff(original, diffText) {
  const diffLines = String(diffText || "").split("\n");
  const originalLines = String(original || "").split("\n");
  const output = [];
  let oldIndex = 0;
  let sawHunk = false;

  for (let index = 0; index < diffLines.length; index += 1) {
    const header = diffLines[index].match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
    if (!header) continue;
    sawHunk = true;
    const oldStart = Math.max(0, Number(header[1]) - 1);
    while (oldIndex < oldStart && oldIndex < originalLines.length) {
      output.push(originalLines[oldIndex]);
      oldIndex += 1;
    }
    index += 1;
    while (index < diffLines.length && !diffLines[index].startsWith("@@ ")) {
      const line = diffLines[index];
      if (line.startsWith(" ")) {
        output.push(line.slice(1));
        oldIndex += 1;
      } else if (line.startsWith("-")) {
        oldIndex += 1;
      } else if (line.startsWith("+")) {
        output.push(line.slice(1));
      } else if (line.startsWith("--- ") || line.startsWith("+++ ") || line.startsWith("diff ")) {
        index -= 1;
        break;
      }
      index += 1;
    }
    index -= 1;
  }

  if (!sawHunk) return null;
  while (oldIndex < originalLines.length) {
    output.push(originalLines[oldIndex]);
    oldIndex += 1;
  }
  return output.join("\n");
}

function streamEditorContent(targetContent, path) {
  if (!path || path !== state.activeFilePath) return;
  if ($("#sourceEditor").value === targetContent) return;
  if (state.codexPreviewTimer) window.clearTimeout(state.codexPreviewTimer);
  state.codexPreviewPath = path;
  state.codexPreviewStreaming = true;
  state.codexPreviewCommitted = false;
  state.codexPreviewBaseContent = state.editorOriginalContent;
  state.codexPreviewContent = String(targetContent || "");
  $("#editorStatus").textContent = `Preparing Codex change review for ${path}...`;
  setCodexReviewMode({
    streaming: true,
    workspace: state.selectedWorkspacePath,
    files: [{ path, content: state.codexPreviewContent, review_status: "reviewing" }],
  });
  state.codexPreviewStreaming = false;
  state.codexPreviewCommitted = true;
}

function previewPendingCodexPatch(pendingPatch = {}) {
  const revision = Number(pendingPatch.revision || 0);
  if (!revision || revision === state.codexPreviewRevision || !state.activeFilePath || state.editorDirty) return;
  const patchWorkspace = normalizedWindowsPath(pendingPatch.workspace || "");
  const selectedWorkspace = normalizedWindowsPath(state.selectedWorkspacePath);
  if (patchWorkspace && selectedWorkspace && patchWorkspace !== selectedWorkspace) return;
  const activePath = normalizedWindowsPath(state.activeFilePath);
  const change = (pendingPatch.files || []).find((file) => normalizedWindowsPath(file.path) === activePath);
  if (!change?.diff) return;
  const targetContent = applyUnifiedDiff(state.editorOriginalContent, change.diff);
  if (targetContent === null || targetContent === state.editorOriginalContent) return;
  state.codexPreviewRevision = revision;
  streamEditorContent(targetContent, state.activeFilePath);
}

function codexDiffRows(editorContent = "", proposedContent = "") {
  const before = String(editorContent).split("\n");
  const after = String(proposedContent).split("\n");
  let prefix = 0;
  while (prefix < before.length && prefix < after.length && before[prefix] === after[prefix]) prefix += 1;
  let suffix = 0;
  while (
    suffix < before.length - prefix
    && suffix < after.length - prefix
    && before[before.length - suffix - 1] === after[after.length - suffix - 1]
  ) suffix += 1;
  const rows = [
    { kind: "meta", text: "--- Talos editor" },
    { kind: "meta", text: "+++ Codex proposed change" },
    { kind: "meta", text: `@@ -1,${before.length} +1,${after.length} @@` },
  ];
  let oldLine = 1;
  let newLine = 1;
  before.slice(0, prefix).forEach((text) => {
    rows.push({ kind: "context", text, oldLine: oldLine++, newLine: newLine++ });
  });
  before.slice(prefix, before.length - suffix).forEach((text) => {
    rows.push({ kind: "remove", text, oldLine: oldLine++ });
  });
  after.slice(prefix, after.length - suffix).forEach((text) => {
    rows.push({ kind: "add", text, newLine: newLine++ });
  });
  before.slice(before.length - suffix).forEach((text) => {
    rows.push({ kind: "context", text, oldLine: oldLine++, newLine: newLine++ });
  });
  return rows;
}

function selectDiffLine(row) {
  $$(".codex-diff-line.selected").forEach((item) => item.classList.remove("selected"));
  row.classList.add("selected");
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(row.querySelector(".codex-diff-content") || row);
  selection.removeAllRanges();
  selection.addRange(range);
}

function contentWithAppliedHunks(originalContent = "", hunks = []) {
  const trailingNewline = String(originalContent).endsWith("\n");
  const originalLines = String(originalContent).split("\n");
  if (trailingNewline) originalLines.pop();
  const output = [];
  let cursor = 0;
  [...hunks].sort((left, right) => Number(left.old_start || 0) - Number(right.old_start || 0)).forEach((hunk) => {
    const start = Number(hunk.old_start || 0);
    const end = Number(hunk.old_end || start);
    output.push(...originalLines.slice(cursor, start));
    output.push(...(
      hunk.review_status === "applied-to-editor"
        ? (hunk.new_lines || [])
        : originalLines.slice(start, end)
    ));
    cursor = end;
  });
  output.push(...originalLines.slice(cursor));
  return `${output.join("\n")}${trailingNewline ? "\n" : ""}`;
}

function reviewStatusLabel(status = "staged") {
  const labels = {
    staged: "Pending",
    reviewing: "Pending",
    "applied-to-editor": "Applied to editor",
    rejected: "Rejected",
    saved: "Saved",
    conflict: "Conflict",
    recovered: "Recovered",
  };
  return labels[status] || status;
}

function reviewSummaryText(summary = {}) {
  const parts = [
    ["Pending", summary.pending],
    ["Applied", summary.applied_to_editor],
    ["Rejected", summary.rejected],
    ["Saved", summary.saved],
    ["Conflict", summary.conflict],
    ["Recovered", summary.recovered],
  ].filter(([, value]) => Number(value || 0) > 0);
  const total = Number(summary.total || summary.files || 0);
  return parts.length
    ? `${parts.map(([label, value]) => `${label}: ${Number(value)}`).join(" | ")} | Total: ${total}`
    : `Total: ${total}`;
}

function hunkRange(start = 0, end = 0) {
  const first = Number(start || 0) + 1;
  const last = Math.max(first, Number(end || start || 0));
  return `${first}-${last}`;
}

function renderCodexDiff(editorContent = "", proposedContent = "", file = {}) {
  const preview = $("#codexDiffPreview");
  const hunks = file.hunks || [];
  if (hunks.length) {
    preview.innerHTML = hunks.map((hunk, index) => {
      const status = hunk.review_status || "staged";
      const reviewable = ["staged", "reviewing"].includes(status);
      const oldRange = hunkRange(hunk.old_start, hunk.old_end);
      const newRange = hunkRange(hunk.new_start, hunk.new_end);
      const rows = [
        ...(hunk.old_lines || []).map((text, line) => ({ kind: "remove", text, line: Number(hunk.old_start || 0) + line + 1 })),
        ...(hunk.new_lines || []).map((text, line) => ({ kind: "add", text, line: Number(hunk.new_start || 0) + line + 1 })),
      ];
      return `
        <section class="codex-diff-hunk ${escapeHtml(status)}">
          <header>
            <span>Hunk ${index + 1} | ${escapeHtml(oldRange)} -> ${escapeHtml(newRange)} <b class="review-status-chip ${escapeHtml(status)}">${escapeHtml(reviewStatusLabel(status))}</b></span>
            <div>
              <button class="icon-button hunk-action" type="button" data-hunk-action="reject" data-hunk-id="${escapeHtml(hunk.id || "")}" ${reviewable ? "" : "disabled"}>Reject this hunk</button>
              <button class="button primary hunk-action" type="button" data-hunk-action="apply" data-hunk-id="${escapeHtml(hunk.id || "")}" ${reviewable ? "" : "disabled"}>Apply this hunk</button>
            </div>
          </header>
          ${rows.map((row) => `<button class="codex-diff-line ${row.kind}" type="button"><span class="codex-diff-number">${row.line}</span><span class="codex-diff-content">${escapeHtml(`${row.kind === "add" ? "+" : "-"}${row.text || ""}`)}</span></button>`).join("")}
        </section>`;
    }).join("");
    $$(".hunk-action").forEach((button) => button.addEventListener("click", () => {
      reviewCodexHunk(button.dataset.hunkAction, button.dataset.hunkId);
    }));
    $$(".codex-diff-line").forEach((row) => row.addEventListener("click", () => selectDiffLine(row)));
    return;
  }
  preview.innerHTML = `
    <section class="codex-diff-hunk ${escapeHtml(file.review_status || "staged")}">
      <header>
        <span>File change <b class="review-status-chip ${escapeHtml(file.review_status || "staged")}">${escapeHtml(reviewStatusLabel(file.review_status || "staged"))}</b></span>
        <div></div>
      </header>
    </section>
  ${codexDiffRows(editorContent, proposedContent).map((row) => {
    const lineNumber = row.newLine || row.oldLine || "";
    const prefix = row.kind === "add" ? "+" : row.kind === "remove" ? "-" : " ";
    return `<button class="codex-diff-line ${row.kind}" type="button"><span class="codex-diff-number">${lineNumber}</span><span class="codex-diff-content">${escapeHtml(`${prefix}${row.text || ""}`)}</span></button>`;
  }).join("")}`;
  $$(".codex-diff-line").forEach((row) => row.addEventListener("click", () => selectDiffLine(row)));
}

function setCodexConflictMode(patch = null, file = null) {
  const visible = Boolean(patch && file && file.review_status === "conflict");
  const view = $("#codexConflictView");
  view.hidden = !visible;
  $(".source-editor").classList.toggle("conflicting", visible);
  if (!visible) return;
  $("#codexConflictLabel").textContent = `Resolve conflict: ${file.path}`;
  $("#codexConflictTime").textContent = file.conflict_detected_at || "";
  $("#codexConflictBase").textContent = String(file.base_content || "");
  $("#codexConflictCurrent").textContent = String(file.conflict_current_content || "");
  $("#codexConflictProposed").textContent = String(file.content || "");
}

function activeConflictPatch() {
  return state.codexPatches.find((item) => (
    normalizedWindowsPath(item.workspace || "") === normalizedWindowsPath(state.selectedWorkspacePath)
    && (item.files || []).some((file) => file.path === state.activeFilePath && file.review_status === "conflict")
  ));
}

async function applyConflictToEditor() {
  const patch = activeConflictPatch();
  if (!patch?.id || !state.activeFilePath) return;
  try {
    const result = await api("/api/codex_apply_conflict", {
      method: "POST",
      body: JSON.stringify({ id: patch.id, path: state.activeFilePath }),
    });
    const file = result.file || {};
    $("#sourceEditor").value = String(file.editor_content || file.content || "");
    renderEditorLineNumbers();
    state.conflictedFilePaths.delete(state.activeFilePath);
    setCodexConflictMode();
    setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
    state.localEditMode = false;
    updateEditorAccess();
    $("#editorStatus").textContent = "Codex conflict applied to Talos editor only. Review and Save File to update Arduino IDE.";
    $("#codexStatus").textContent = "Codex version is now in the Talos editor; Arduino IDE has not been changed.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not apply conflicted Codex change: ${error.message}`;
  }
}

async function rejectConflictCodex() {
  const patch = activeConflictPatch();
  if (!patch?.id || !state.activeFilePath) return;
  state.codexReviewPatch = patch;
  await rejectCodexPatch();
}

async function keepExternalConflict() {
  const patch = activeConflictPatch();
  if (!patch?.id || !state.activeFilePath) return;
  try {
    await api("/api/codex_keep_external", {
      method: "POST",
      body: JSON.stringify({ id: patch.id, path: state.activeFilePath }),
    });
    const current = await api(`/api/arduino_file?path=${encodeURIComponent(state.activeFilePath)}`);
    applyEditorFileResult(current, "Kept the current Arduino file. The conflicting Codex change was rejected.");
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not keep the Arduino version: ${error.message}`;
  }
}

async function draftConflictMerge() {
  const patch = activeConflictPatch();
  if (!patch?.id || !state.activeFilePath) return;
  try {
    const result = await api("/api/codex_merge_draft", {
      method: "POST",
      body: JSON.stringify({ id: patch.id, path: state.activeFilePath }),
    });
    const file = result.file || {};
    $("#sourceEditor").value = String(file.editor_content || "");
    renderEditorLineNumbers();
    state.conflictedFilePaths.delete(state.activeFilePath);
    setCodexConflictMode();
    setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
    state.localEditMode = true;
    updateEditorAccess();
    $("#editorStatus").textContent = "Three-way merge draft created in Talos. Review it, then Save File to update Arduino IDE.";
    $("#codexStatus").textContent = "Merge draft is ready in the Talos editor; Arduino IDE has not been changed.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not create merge draft: ${error.message}`;
  }
}

function setCodexReviewMode(patch = null) {
  setCodexConflictMode();
  state.codexReviewPatch = patch;
  const activeFile = state.activeFilePath;
  const file = patch && (patch.files || []).find((item) => item.path === activeFile);
  const proposedContent = file && Object.hasOwn(file, "content") ? String(file.content || "") : null;
  const differsFromEditor = proposedContent !== null && $("#sourceEditor").value !== proposedContent;
  const reviewing = Boolean(
    patch
    && file
    && ["staged", "reviewing"].includes(file.review_status || "staged")
    && file.kind !== "delete"
    && differsFromEditor
  );
  $(".source-editor").classList.toggle("reviewing", reviewing);
  $("#codexReviewBar").hidden = !reviewing;
  $("#codexDiffPreview").hidden = !reviewing;
  if (!reviewing) {
    $("#codexDiffPreview").innerHTML = "";
    $("#codexReviewScope").textContent = "";
    $("#applyCodexTurnBtn").hidden = true;
    $("#rejectCodexTurnBtn").hidden = true;
    $("#rejectCodexPatchBtn").hidden = false;
    $("#applyCodexPatchBtn").textContent = "Apply To Editor";
    updateEditorAccess();
    return;
  }
  const reviewable = ["staged", "reviewing"].includes(file.review_status || "staged");
  const streaming = Boolean(patch.streaming);
  $("#codexReviewLabel").textContent = streaming
    ? `Streaming Codex change: ${file.path}`
    : `Codex change review: ${file.path}`;
  const fileIndex = (patch.files || []).findIndex((item) => item.path === file.path) + 1;
  $("#codexReviewScope").textContent = `File ${fileIndex}/${(patch.files || []).length} | ${reviewSummaryText(file.review_summary || {})}`;
  $("#applyCodexPatchBtn").textContent = reviewable ? "Apply File To Editor" : "Restore Proposed Change";
  $("#applyCodexPatchBtn").disabled = false;
  $("#verifyCodexPatchBtn").disabled = streaming;
  $("#applyCodexTurnBtn").hidden = false;
  $("#rejectCodexTurnBtn").hidden = false;
  $("#applyCodexTurnBtn").textContent = "Apply All Pending";
  $("#rejectCodexTurnBtn").textContent = "Reject All Pending";
  $("#applyCodexTurnBtn").disabled = !reviewable || streaming;
  $("#rejectCodexTurnBtn").disabled = !reviewable || streaming;
  $("#rejectCodexPatchBtn").hidden = !reviewable || streaming;
  $("#rejectCodexPatchBtn").textContent = "Reject File";
  renderCodexDiff($("#sourceEditor").value, proposedContent, file);
  updateEditorAccess();
  $("#saveFileBtn").disabled = true;
}

function refreshCodexReview(patches = []) {
  state.codexPatches = patches;
  const workspacePatches = patches.filter((patch) => (
    normalizedWindowsPath(patch.workspace || "") === normalizedWindowsPath(state.selectedWorkspacePath)
  ));
  renderArduinoFilesAfterCodexPatch();
  state.conflictedFilePaths = new Set(workspacePatches.flatMap((patch) => (
    (patch.files || [])
      .filter((file) => file.review_status === "conflict")
      .map((file) => file.path)
  )));
  setEditorDirty(state.editorDirty);
  const conflict = workspacePatches.find((patch) => (
    (patch.files || []).some((file) => file.path === state.activeFilePath && file.review_status === "conflict")
  ));
  if (conflict) {
    setCodexReviewMode(null);
    const conflictFile = (conflict.files || []).find((file) => file.path === state.activeFilePath);
    setCodexConflictMode(conflict, conflictFile);
    $("#editorStatus").textContent = "External source change detected. Resolve the Codex conflict before applying or saving this draft.";
    $("#codexStatus").textContent = "Codex change conflict detected.";
    return;
  }
  const pending = workspacePatches.find((patch) => (
    (patch.files || []).some((file) => (
      file.path === state.activeFilePath
      && ["staged", "reviewing"].includes(file.review_status || "staged")
      && file.kind !== "delete"
      && Object.hasOwn(file, "content")
      && $("#sourceEditor").value !== String(file.content || "")
    ))
  ));
  setCodexReviewMode(pending || null);
  const reviewingFile = pending && (pending.files || []).find((file) => file.path === state.activeFilePath);
  if (pending?.id && reviewingFile?.review_status === "staged") {
    void api("/api/codex_review_patch", {
      method: "POST",
      body: JSON.stringify({ id: pending.id, path: state.activeFilePath }),
    }).then(() => refreshCodex()).catch((error) => {
      $("#codexStatus").textContent = `Change review could not be recorded: ${error.message}`;
    });
  }
}

function renderCodexReviewRecovery(recovery = {}) {
  const pending = Boolean(recovery.pending && Number(recovery.count || 0) > 0);
  $("#codexReviewRecovery").hidden = !pending;
  if (!pending) return;
  $("#codexReviewRecoveryLabel").textContent = `${Number(recovery.count || 0)} unfinished Codex review(s) can be restored.`;
}

async function applyCodexPatch(patch = state.codexReviewPatch) {
  if (!patch) return;
  const proposedFile = (patch.files || []).find((file) => file.path === state.activeFilePath);
  if (!proposedFile || !Object.hasOwn(proposedFile, "content")) return;
  const acceptedHunks = (proposedFile.hunks || []).map((hunk) => ({
    ...hunk,
    review_status: ["staged", "reviewing"].includes(hunk.review_status || "staged")
      ? "applied-to-editor"
      : hunk.review_status,
  }));
  const content = acceptedHunks.length
    ? contentWithAppliedHunks(state.editorOriginalContent, acceptedHunks)
    : String(proposedFile.content || "");
  setCodexReviewMode(null);
  $("#sourceEditor").value = content;
  renderEditorLineNumbers();
  state.codexPreviewBaseContent = "";
  state.codexPreviewContent = "";
  state.codexPreviewCommitted = false;
  setEditorDirty(content !== state.editorOriginalContent);
  state.localEditMode = false;
  updateEditorAccess();
  $("#editorStatus").textContent = "Codex change applied to Talos editor. Verify before Save File when possible.";
  $("#codexStatus").textContent = "Codex change applied to editor; verify before saving to Arduino IDE.";

  const reviewable = patch.id && ["staged", "reviewing"].includes(proposedFile.review_status || "staged");
  if (!reviewable) return;
  state.codexApplyingPatchId = patch.id;
  void api("/api/codex_apply_patch", {
    method: "POST",
    body: JSON.stringify({ id: patch.id, path: state.activeFilePath }),
  }).then(() => refreshCodex()).catch((error) => {
    $("#codexStatus").textContent = `Editor updated, but patch state could not be synced: ${error.message}`;
  }).finally(() => {
    state.codexApplyingPatchId = "";
  });
}

async function verifyCodexPatch() {
  const patch = state.codexReviewPatch;
  if (!patch?.id || state.codexPatchVerifyRunning) return;
  state.codexPatchVerifyRunning = true;
  setArduinoVerifyRunning(true);
  $("#verifyCodexPatchBtn").disabled = true;
  setOutputView("verify");
  renderVerifyOutput(null, "Compiling the staged Codex change in an isolated Arduino sandbox...");
  try {
    const result = await api("/api/codex_verify_patch", {
      method: "POST",
      body: JSON.stringify({ id: patch.id }),
    });
    renderVerifyOutput(result);
    $("#codexStatus").textContent = result.ok
      ? "Staged Codex change compiled successfully. Review and Save File when ready."
      : "Staged Codex change did not compile. Arduino IDE files were not changed.";
    await refreshRunHistory();
  } catch (error) {
    renderVerifyOutput(null, `Staged Codex verify failed: ${error.message}`);
    $("#codexStatus").textContent = `Could not verify staged Codex change: ${error.message}`;
  } finally {
    state.codexPatchVerifyRunning = false;
    setArduinoVerifyRunning(false);
    if (state.codexReviewPatch?.id === patch.id) $("#verifyCodexPatchBtn").disabled = false;
  }
}

async function reviewCodexHunk(action, hunkId) {
  const patch = state.codexReviewPatch;
  const file = patch && (patch.files || []).find((item) => item.path === state.activeFilePath);
  if (!patch?.id || !file || !hunkId || !["apply", "reject"].includes(action)) return;
  const endpoint = action === "apply" ? "/api/codex_apply_hunk" : "/api/codex_reject_hunk";
  try {
    const result = await api(endpoint, {
      method: "POST",
      body: JSON.stringify({ id: patch.id, path: state.activeFilePath, hunk_id: hunkId }),
    });
    const updatedPatch = result.patch || patch;
    const updatedFile = result.file || file;
    $("#sourceEditor").value = contentWithAppliedHunks(state.editorOriginalContent, updatedFile.hunks || []);
    renderEditorLineNumbers();
    setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
    state.localEditMode = false;
    setCodexReviewMode(updatedPatch);
    $("#editorStatus").textContent = action === "apply"
        ? "Codex hunk applied to Talos editor. Review remaining hunks, verify, then Save File when complete."
      : "Codex hunk rejected. The Arduino sketch was not changed.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not ${action} Codex hunk: ${error.message}`;
  }
}

async function resolveCodexTurn(action) {
  const patch = state.codexReviewPatch;
  if (!patch?.id || !["apply", "reject"].includes(action)) return;
  const endpoint = action === "apply" ? "/api/codex_apply_all" : "/api/codex_reject_all";
  try {
    const result = await api(endpoint, {
      method: "POST",
      body: JSON.stringify({ id: patch.id }),
    });
    const updatedPatch = result.patch || patch;
    const updatedFile = (updatedPatch.files || []).find((file) => file.path === state.activeFilePath);
    if (updatedFile?.editor_content !== undefined) {
      $("#sourceEditor").value = String(updatedFile.editor_content || "");
    } else if (updatedFile?.review_status === "rejected") {
      $("#sourceEditor").value = state.editorOriginalContent;
    }
    renderEditorLineNumbers();
    setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
    state.localEditMode = false;
    setCodexReviewMode(updatedPatch);
    $("#editorStatus").textContent = action === "apply"
      ? `Applied ${Number(result.changed || 0)} Codex hunk(s) to Talos drafts. Verify before Save File when possible.`
      : `Rejected ${Number(result.changed || 0)} pending Codex hunk(s). The Arduino sketch was not changed.`;
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not ${action} this Codex turn: ${error.message}`;
  }
}

async function rejectCodexPatch() {
  const patch = state.codexReviewPatch;
  if (!patch?.id) return;
  try {
    await api("/api/codex_reject_patch", {
      method: "POST",
      body: JSON.stringify({ id: patch.id, path: state.activeFilePath }),
    });
    if (state.codexPreviewBaseContent) {
      $("#sourceEditor").value = state.codexPreviewBaseContent;
      renderEditorLineNumbers();
    }
    state.codexPreviewBaseContent = "";
    state.codexPreviewContent = "";
    state.codexPreviewCommitted = false;
    setCodexReviewMode(null);
    $("#editorStatus").textContent = "Codex change rejected. The Arduino sketch was not changed.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not reject Codex patch: ${error.message}`;
  }
}

function renderStats(payload) {
  const arduino = payload.arduino || {};
  const projects = payload.arduino_projects || [];
  const rows = [
    ["Role", payload.role || "Tool server"],
    ["Native C", payload.native_available ? "Loaded" : "Fallback"],
    ["Open sketches", String(projects.length)],
    ["Arduino", arduino.valid ? "Ready" : "Not ready"],
  ];
  $("#stats").innerHTML = rows
    .map(([label, value]) => `<div class="stat"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`)
    .join("");
}

function readinessItem(label, ready, detail = "") {
  return `
    <div class="readiness-item ${ready ? "ready" : "blocked"}">
      <span class="readiness-dot" aria-hidden="true"></span>
      <div>
        <strong>${escapeHtml(label)}</strong>
        <small>${escapeHtml(detail)}</small>
      </div>
    </div>
  `;
}

function renderDashboard(payload) {
  const arduino = payload.arduino || {};
  const projects = payload.arduino_projects || [];
  const codex = payload.codex || {};
  const diagnostics = payload.config?.diagnostics || {};
  const workspaceReady = Boolean(arduino.valid);
  const codexReady = codex.ok !== false;
  const nativeReady = Boolean(payload.native_available);
  const profile = payload.arduino_profile_readiness || {};
  const profileReady = profile.ready !== false;
  const readyCount = [workspaceReady, codexReady, nativeReady, profileReady].filter(Boolean).length;
  $("#serverSummary").textContent = `${readyCount}/4 core surfaces ready. Arduino sketches detected: ${projects.length}.`;
  $("#readinessList").innerHTML = [
    readinessItem("Arduino workspace", workspaceReady, workspaceReady ? arduino.path || "Workspace selected" : "Select a valid Arduino sketch folder."),
    readinessItem("Codex bridge", codexReady, codexReady ? "Ready to receive workspace context." : "Reconnect Codex before asking for code changes."),
    readinessItem("Native C helper", nativeReady, nativeReady ? "Loaded for faster local detection." : "Python fallback is active."),
    readinessItem("Profile and diagnostics", profileReady, diagnostics.enabled ? "Profile ready. Local diagnostics enabled." : "Profile ready. Diagnostics remain local and opt-in."),
  ].join("");
}

function logCategory(line = "") {
  const text = String(line).toLowerCase();
  if (text.includes("arduino") || text.includes(".ino") || text.includes("sketch")) return "arduino";
  if (text.includes("codex")) return "codex";
  if (text.includes("verify") || text.includes("compile") || text.includes("sandbox")) return "verify";
  if (text.includes("diagnostic")) return "diagnostics";
  return "app";
}

function renderLogs(events = []) {
  const filter = $("#logFilter")?.value || "all";
  const rows = events
    .map((event) => String(event || "").trim())
    .filter(Boolean)
    .map((event) => ({ text: event, category: logCategory(event) }))
    .filter((event) => filter === "all" || event.category === filter);
  $("#logSummary").textContent = rows.length
    ? `${rows.length} event(s) shown${filter === "all" ? "" : ` for ${filter}`}.`
    : "No matching runtime events yet.";
  $("#logText").innerHTML = rows.length
    ? rows.map((event) => `
        <article class="event-log-item ${escapeHtml(event.category)}">
          <span>${escapeHtml(event.category)}</span>
          <p>${escapeHtml(event.text)}</p>
        </article>
      `).join("")
    : `<div class="event-empty">
        <strong>No events yet</strong>
        <p>Open an Arduino sketch, run Verify, or start a Codex turn to populate this stream.</p>
      </div>`;
}

function renderArduino(arduino, force = false, ide = {}) {
  if (!arduino) return;
  const nextWorkspacePath = normalizedWindowsPath(arduino.path);
  const currentWorkspacePath = normalizedWindowsPath(state.selectedWorkspacePath);
  const transientWorkspaceLoss = (
    !nextWorkspacePath
    && currentWorkspacePath
    && state.activeFilePath
    && (state.codexBusy || state.codexPreviewStreaming || state.codexPreviewCommitted)
  );
  const workspaceChanged = !transientWorkspaceLoss && nextWorkspacePath !== currentWorkspacePath;
  if (workspaceChanged) {
    if (state.selectedWorkspacePath && state.activeFilePath) {
      state.activeFileByWorkspace[currentWorkspacePath] = state.activeFilePath;
    }
    state.selectedWorkspacePath = arduino.path || "";
    state.lastVerifyResult = null;
    state.lastVerifySignature = "";
    state.lastVerifyOk = false;
    state.lastVerifyContext = null;
    $("#recordEvidenceBtn").disabled = true;
    resetEditor(arduino.valid ? "Select a source file." : "No valid workspace selected.");
  }
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
    <tr class="${state.codexChangedFiles.has(String(file.path).toLowerCase()) ? "codex-changed" : ""}" data-path="${escapeHtml(file.path)}" tabindex="0">
      <td>
        <span class="file-name">${escapeHtml(file.path)}</span>
        <span class="file-meta">${Number(file.lines || 0)} lines | ${Number(file.bytes || 0)} bytes</span>
        ${state.codexChangedFiles.has(String(file.path).toLowerCase()) ? '<span class="file-change-badge">Changed by Codex</span>' : ""}
      </td>
    </tr>
  `).join("");
  $$("#arduinoFiles tr").forEach((row) => {
    const open = () => openWorkspaceFile(row.dataset.path);
    row.addEventListener("click", open);
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        open();
      }
    });
  });
  renderActiveFileRow();
  const rememberedFile = state.activeFileByWorkspace[normalizedWindowsPath(state.selectedWorkspacePath)];
  const rememberedExists = rememberedFile && (arduino.files || []).some((file) => file.path === rememberedFile);
  if (!state.activeFilePath && rememberedExists && !state.editorLoading) {
    window.setTimeout(() => openWorkspaceFile(rememberedFile), 0);
  }
  renderCodexContext();
}

function profileLines(value) {
  return String(value || "").split(/[,\n]/).map((item) => item.trim()).filter(Boolean);
}

function renderEnvironmentProfile(profile = {}) {
  state.environmentProfile = profile && typeof profile === "object" ? profile : {};
  $("#profileSerialPortInput").value = state.environmentProfile.serial_port || "";
  $("#profileBaudRateInput").value = state.environmentProfile.baud_rate || "";
  $("#profileBuildPropertiesInput").value = (state.environmentProfile.build_flags || []).join("\n");
  $("#profileBuildPropertyInput").value = (state.environmentProfile.build_properties || []).join("\n");
  $("#profileLibrariesInput").value = (state.environmentProfile.libraries || []).join("\n");
  $("#saveEnvironmentProfileBtn").disabled = !state.selectedWorkspacePath;
  renderProfileReadiness(state.profileReadiness);
  renderCodexContextPreview();
}

function renderProfileReadiness(readiness = {}) {
  state.profileReadiness = readiness && typeof readiness === "object" ? readiness : {};
  const status = $("#profileReadinessStatus");
  if (!status) return;
  const issues = state.profileReadiness.issues || [];
  const warnings = state.profileReadiness.warnings || [];
  status.classList.toggle("blocked", issues.length > 0);
  status.classList.toggle("warning", !issues.length && warnings.length > 0);
  if (issues.length) {
    status.textContent = `Profile blocked: ${issues[0].message}`;
  } else if (warnings.length) {
    status.textContent = `Profile ready with ${warnings.length} note(s).`;
  } else if (state.profileReadiness.ready) {
    status.textContent = "Profile ready for verify and release evidence.";
  } else {
    status.textContent = "Profile readiness unknown.";
  }
}

async function saveEnvironmentProfile() {
  const path = $("#arduinoPathInput").value;
  if (!path) return;
  const status = $("#environmentProfileStatus");
  status.textContent = "Saving environment profile...";
  const result = await api("/api/arduino_profile", {
    method: "POST",
    body: JSON.stringify({
      path,
      fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value,
      serial_port: $("#profileSerialPortInput").value,
      baud_rate: $("#profileBaudRateInput").value,
      build_flags: profileLines($("#profileBuildPropertiesInput").value),
      build_properties: profileLines($("#profileBuildPropertyInput").value),
      libraries: profileLines($("#profileLibrariesInput").value),
    }),
  });
  renderEnvironmentProfile(result.profile || {});
  status.textContent = "Environment profile saved for this sketch.";
  await refreshAfterWorkspaceMutation();
}

function renderCodexContext() {
  const chips = $$("#codexContext span");
  chips[0]?.classList.toggle("ready", Boolean(state.selectedWorkspacePath));
  chips[1]?.classList.toggle("ready", Boolean(state.workspaceMap.valid));
  chips[0]?.setAttribute("title", state.selectedWorkspacePath || "No workspace selected");
  chips[1]?.setAttribute("title", state.workspaceMap.valid
    ? `${Number(state.workspaceMap.source_tab_count || 0)} source tab(s) | ${state.workspaceMap.main_sketch || "no main sketch"}`
    : "Workspace map unavailable");
  chips[2]?.classList.toggle("ready", Boolean(state.activeFilePath));
  chips[2]?.setAttribute("title", state.activeFilePath || "No active file selected");
  chips[3]?.classList.toggle(
    "ready",
    Boolean(state.lastIssueText || (state.lastVerifyText && !state.lastVerifyText.startsWith("Sandbox compile"))),
  );
  chips[3]?.setAttribute("title", codexVerifySummary());
  renderCodexContextPreview();
}

function codexVerifySummary() {
  const text = String(state.lastIssueText || state.lastVerifyText || "").trim();
  if (!text) return "No verify data";
  const firstLine = text.split(/\r?\n/).find(Boolean) || text;
  return firstLine.length > 120 ? `${firstLine.slice(0, 117)}...` : firstLine;
}

function pathLeaf(path = "") {
  return String(path || "").split(/[\\/]/).filter(Boolean).pop() || "";
}

function setStatusItem(selector, text, title = "") {
  const item = $(selector);
  if (!item) return;
  item.textContent = text;
  item.title = title || text;
}

function renderStatusBar() {
  const workspace = state.selectedWorkspacePath || $("#arduinoPathInput")?.value || "";
  const file = state.activeFilePath || "";
  const board = state.arduinoBoardName || $("#arduinoFqbnInput")?.value || "unknown";
  const verifyState = state.arduinoVerifyRunning
    ? "running"
    : state.lastVerifyResult
      ? (state.lastVerifyOk ? "passed" : "failed")
      : "idle";
  const codexText = $("#codexStatus")?.textContent || (state.codexBusy ? "working" : "ready");
  setStatusItem("#statusWorkspace", `Workspace: ${pathLeaf(workspace) || "none"}`, workspace || "No Arduino workspace selected");
  setStatusItem("#statusFile", `File: ${pathLeaf(file) || "none"}`, file || "No source file selected");
  setStatusItem("#statusBoard", `Board: ${board}`, state.arduinoFqbnFull || board);
  setStatusItem("#statusVerify", `Verify: ${verifyState}`, codexVerifySummary());
  setStatusItem("#statusCodex", `Codex: ${state.codexBusy ? "working" : codexText}`, codexText);
}

function codexPayloadForNextTurn(message = "") {
  return {
    message,
    active_file: state.activeFilePath
      ? { path: state.activeFilePath, content: $("#sourceEditor").value }
      : {},
    verify_context: state.lastIssueText || state.lastVerifyText,
    allow_edits: $("#codexAllowEdits")?.checked !== false,
  };
}

function countEditorLines() {
  const content = $("#sourceEditor")?.value || "";
  return content ? content.split(/\r?\n/).length : 0;
}

function categoryLine(label, items = []) {
  const values = Array.isArray(items) ? items.filter(Boolean) : [];
  if (!values.length) return `${label}: none`;
  const visible = values.slice(0, 6).join(", ");
  const extra = values.length > 6 ? ` (+${values.length - 6})` : "";
  return `${label}: ${visible}${extra}`;
}

function contextCoverageLine(sourceTabs, activeBytes, verifyReady) {
  const activeCoverage = state.activeFilePath
    ? `active file included (${activeBytes} bytes)`
    : "no active file";
  const sourceCoverage = sourceTabs > 24
    ? `${sourceTabs} source file(s), compact map shown`
    : `${sourceTabs} source file(s) mapped`;
  return `Coverage: ${activeCoverage} | ${sourceCoverage} | verify ${verifyReady ? "included" : "not available"}`;
}

function buildCodexContextPreview() {
  const map = state.workspaceMap || {};
  const profile = state.environmentProfile || {};
  const readiness = state.profileReadiness || {};
  const activeFile = state.activeFilePath || "none";
  const sourceTabs = Number(map.source_tab_count || (map.source_tabs || []).length || 0);
  const inventory = map.file_inventory?.categories || {};
  const verifyReady = Boolean(state.lastIssueText || (state.lastVerifyText && !state.lastVerifyText.startsWith("Sandbox compile")));
  const activeBytes = state.activeFilePath ? new Blob([$("#sourceEditor")?.value || ""]).size : 0;
  const profileParts = [
    state.arduinoBoardName || $("#arduinoFqbnInput")?.value || map.board?.name || map.fqbn || "board unknown",
    profile.serial_port ? `port ${profile.serial_port}` : "",
    profile.baud_rate ? `baud ${profile.baud_rate}` : "",
    (profile.build_flags || []).length ? `${profile.build_flags.length} build flag(s)` : "",
  ].filter(Boolean);
  const lines = [
    `Workspace: ${state.selectedWorkspacePath || "none"}`,
    `Workspace map: ${map.valid ? "ready" : "unavailable"} | main ${map.main_sketch || "none"} | ${sourceTabs} source file(s)`,
    categoryLine("Main sketch", inventory.main_sketch),
    categoryLine("Headers", inventory.headers),
    categoryLine("Sources", inventory.sources),
    categoryLine("Docs", inventory.docs),
    `Ignored: ${Number(map.file_inventory?.ignored_count || 0)} file(s)/ignored-dir item(s) excluded`,
    `Active file: ${activeFile}${state.activeFilePath ? ` | ${countEditorLines()} editor line(s)` : ""}`,
    `Profile: ${profileParts.join(" | ") || "none"}`,
    `Profile readiness: ${readiness.ready ? "ready" : "needs review"}${(readiness.blockers || []).length ? ` | blockers: ${(readiness.blockers || []).join(", ")}` : ""}`,
    `Verify: ${codexVerifySummary()}`,
    `Edit permission: ${$("#codexAllowEdits")?.checked ? "Codex may stage changes in Talos only" : "read-only"}`,
    contextCoverageLine(sourceTabs, activeBytes, verifyReady),
    "Scope: selected Arduino sketch folder only",
  ];
  return lines.join("\n");
}

function renderCodexContextPreview() {
  const preview = $("#codexContextPreviewText");
  if (!preview) return;
  const readyParts = [
    state.selectedWorkspacePath ? "workspace" : "",
    state.workspaceMap.valid ? "map" : "",
    state.activeFilePath ? "file" : "",
    state.lastIssueText || (state.lastVerifyText && !state.lastVerifyText.startsWith("Sandbox compile")) ? "verify" : "",
  ].filter(Boolean);
  preview.textContent = buildCodexContextPreview();
  $("#codexContextPreviewStatus").textContent = readyParts.length
    ? `${readyParts.length}/4 ready`
    : "No workspace selected";
}

async function copyCodexContextPackage() {
  const button = $("#copyCodexContextBtn");
  if (button) button.disabled = true;
  try {
    const message = $("#codexInput")?.value?.trim() || "";
    const result = await api("/api/codex_context_package", {
      method: "POST",
      body: JSON.stringify(codexPayloadForNextTurn(message)),
    });
    await copyText(JSON.stringify(result.package || {}, null, 2), "#codexStatus");
    $("#codexStatus").textContent = "Copied exact Codex context package.";
  } catch (error) {
    $("#codexStatus").textContent = `Could not copy Codex context package: ${error.message}`;
  } finally {
    if (button) button.disabled = false;
  }
}

function codexAccountLabel(payload = {}) {
  const account = payload.account || {};
  const connection = payload.connection || {};
  if (!payload.available) return "Codex runtime not found";
  if (payload.initializing) return "Starting local Codex...";
  if (connection.state === "disconnected") return "Disconnected";
  if (connection.state === "reconnecting") return "Reconnecting...";
  if (connection.state === "auth_required") return "Sign-in required";
  if (payload.error && !account.type) return "Sign-in required";
  const plan = account.planType ? ` | ${account.planType}` : "";
  const email = account.email ? `${account.email}${plan}` : `${account.type || "ChatGPT"}${plan}`;
  return payload.connected ? email : "Connecting...";
}

function codexConnectionStatus(payload = {}) {
  const connection = payload.connection || {};
  if (payload.error) {
    const retryIn = Number(connection.next_retry_in || 0);
    if (connection.state === "disconnected" && retryIn > 0) {
      return `${payload.error} Reconnecting in ${retryIn.toFixed(1)}s. The last user turn was not replayed.`;
    }
    return payload.error;
  }
  if (payload.initializing || connection.state === "connecting" || connection.state === "reconnecting") {
    return "Connecting to Codex app-server...";
  }
  return state.codexBusy ? "Codex is working..." : payload.thread_id ? "Thread ready" : "Ready for a new thread";
}

function codexTaskViewModel(payload = {}) {
  const task = payload.task_state || {};
  const connection = payload.connection || {};
  const stateName = String(task.state || "");
  const manualReplay = task.replay_guard === "manual_send_required";
  if (!payload.available) {
    return { kind: "unavailable", title: "Codex runtime unavailable", detail: "Install or enable Codex before starting a task." };
  }
  if (connection.state === "auth_required") {
    return { kind: "blocked", title: "Sign-in required", detail: "Sign in through the Codex extension or CLI, then reconnect." };
  }
  if (connection.state === "disconnected") {
    const retryIn = Number(connection.next_retry_in || 0);
    return {
      kind: "retry",
      title: "Codex disconnected",
      detail: retryIn > 0
        ? `Retry scheduled in ${retryIn.toFixed(1)}s. ${manualReplay ? "The interrupted user turn was not replayed." : ""}`
        : `Use Reconnect when you are ready.${manualReplay ? " Previous user turns are not replayed automatically." : ""}`,
    };
  }
  if (connection.state === "reconnecting") {
    return { kind: "retry", title: "Reconnecting", detail: "Talos is reconnecting without replaying the interrupted turn." };
  }
  if (payload.busy || stateName === "pending_turn") {
    return { kind: "working", title: "Codex is working", detail: task.detail || "A turn is currently running." };
  }
  if (stateName === "cancelled_turn") {
    return { kind: "cancelled", title: "Turn cancelled", detail: task.detail || "The interrupted user turn was not replayed." };
  }
  if (stateName === "failed_turn") {
    return { kind: "failed", title: "Turn failed", detail: task.detail || payload.error || "Review the status and send again when ready." };
  }
  if (stateName === "recovered_review") {
    return { kind: "recovered", title: "Recovered review", detail: task.detail || "Unfinished Codex changes were restored for inspection." };
  }
  if (payload.thread_id) {
    return { kind: "active", title: "Active conversation", detail: task.detail || "Thread ready." };
  }
  return { kind: "new", title: "New conversation", detail: task.detail || "Ready for a new thread." };
}

function codexEmptyState(payload = {}) {
  const model = codexTaskViewModel(payload);
  if (model.kind === "unavailable" || model.kind === "blocked" || model.kind === "retry" || model.kind === "failed") {
    return {
      title: model.title,
      body: model.detail,
      suggestions: [],
    };
  }
  if (!state.selectedWorkspacePath) {
    return {
      title: "Select an Arduino sketch",
      body: "Choose a detected sketch so Codex receives a scoped workspace context.",
      suggestions: [],
    };
  }
  return {
    title: "Work with your Arduino sketch",
    body: "Codex receives the selected workspace, active file, and latest verify result.",
    suggestions: [
      ["Review this sketch", "Review this sketch and identify the most important issues."],
      ["Explain the active file", "Explain the active file and its control flow."],
      ["Optimize the code", "Optimize this sketch while preserving its current behavior."],
    ],
  };
}

function renderCodexTaskBanner(payload = {}) {
  const model = codexTaskViewModel(payload);
  return `
    <section class="codex-task-state ${escapeHtml(model.kind)}">
      <strong>${escapeHtml(model.title)}</strong>
      <span>${escapeHtml(model.detail)}</span>
    </section>
  `;
}

function renderCodexEmptyState(payload = {}) {
  const empty = codexEmptyState(payload);
  const suggestions = empty.suggestions.length
    ? `<div class="codex-suggestions">
        ${empty.suggestions.map(([label, prompt]) => `
          <button type="button" data-codex-prompt="${escapeHtml(prompt)}">${escapeHtml(label)}</button>
        `).join("")}
      </div>`
    : "";
  return `
    <div class="codex-empty">
      <span class="codex-empty-mark">C</span>
      <strong>${escapeHtml(empty.title)}</strong>
      <p>${escapeHtml(empty.body)}</p>
      ${suggestions}
    </div>
  `;
}

function codexChangeStatusLabel(status = "staged") {
  return {
    staged: "Change staged",
    reviewing: "Change under review",
    "applied-to-editor": "Applied to editor",
    saved: "Saved to Arduino workspace",
    rejected: "Change rejected",
    conflict: "Change conflict",
  }[status] || status;
}

function codexPatchFileLabel(file = {}) {
  const hunkCount = Number((file.hunks || []).length || file.hunk_count || 0);
  const hunkText = hunkCount ? `${hunkCount} hunk${hunkCount === 1 ? "" : "s"}` : "no hunks";
  return `${file.kind || "update"} | ${hunkText}`;
}

function renderCodex(payload = {}) {
  state.codexBusy = Boolean(payload.busy);
  previewPendingCodexPatch(payload.pending_patch || {});
  const connection = payload.connection || {};
  $("#codexAccount").textContent = codexAccountLabel(payload);
  $("#sendCodexBtn").disabled = !payload.ok || state.codexBusy;
  $("#sendCodexBtn").hidden = state.codexBusy;
  $("#cancelCodexBtn").hidden = !state.codexBusy;
  $("#cancelCodexBtn").disabled = !state.codexBusy;
  $("#codexInput").disabled = !payload.ok;
  $("#newCodexThreadBtn").disabled = state.codexBusy;
  $("#reconnectCodexBtn").hidden = payload.connected && !payload.error;
  $("#reconnectCodexBtn").disabled = state.codexBusy || payload.initializing || connection.state === "connecting";
  $("#codexStatus").textContent = codexConnectionStatus(payload);
  renderStatusBar();
  const messages = payload.messages || [];
  const patches = payload.patches || [];
  const conversations = payload.conversations || [];
  renderCodexHistory(conversations);
  renderCodexReviewRecovery(payload.review_recovery || {});
  const signature = JSON.stringify([messages, patches, payload.task_state, payload.connection, payload.error, state.selectedWorkspacePath]);
  if (signature !== state.codexMessagesSignature) {
    state.codexMessagesSignature = signature;
    const taskHtml = renderCodexTaskBanner(payload);
    const messageHtml = messages.map((message) => `
          <article class="codex-message ${message.role === "user" ? "user" : "assistant"}">
            <span class="codex-message-role">${message.role === "user" ? "You" : "Codex"}</span>
            <div class="codex-message-body">${escapeHtml(message.text || "")}</div>
          </article>
        `).join("");
    const patchHtml = patches.slice(-5).map((patch) => `
      <section class="codex-patch">
        <div class="codex-patch-head">
          <span>${escapeHtml(codexChangeStatusLabel(patch.review_status || "staged"))}</span>
          <span>${escapeHtml(patch.turn_id ? `turn ${String(patch.turn_id).slice(-6)}` : patch.time || "")}</span>
        </div>
        <div class="codex-patch-list">
          ${(patch.files || []).map((file) => `
            <div class="codex-patch-file">
              <span class="codex-patch-kind">${escapeHtml(file.review_status || "staged")}</span>
              <span class="codex-patch-file-copy">
                <code title="${escapeHtml(file.path || "")}">${escapeHtml(file.path || "")}</code>
                <small>${escapeHtml(codexPatchFileLabel(file))}</small>
              </span>
            </div>
          `).join("")}
        </div>
      </section>
    `).join("");
    $("#codexMessages").innerHTML = (messageHtml || patchHtml)
      ? `${taskHtml}${messageHtml}${patchHtml}`
      : `${taskHtml}${renderCodexEmptyState(payload)}`;
    bindCodexSuggestions();
    $("#codexMessages").scrollTop = $("#codexMessages").scrollHeight;
  }
  const activity = payload.activity || [];
  const visibleActivity = state.codexBusy ? activity.slice(-4) : [];
  $("#codexActivity").hidden = !visibleActivity.length;
  $("#codexActivity").textContent = visibleActivity.join("\n");
  const nextRevision = Number(payload.patch_revision || 0);
  if (nextRevision !== state.codexPatchRevision) {
    const latestPatch = patches.at(-1) || {};
    state.codexPatchRevision = nextRevision;
    state.codexChangedFiles = new Set(
      (latestPatch.files || []).map((file) => String(file.path || "").toLowerCase()),
    );
    renderArduinoFilesAfterCodexPatch();
  }
  refreshCodexReview(patches);
  const nextEventRevision = Number(payload.patch_event_revision || 0);
  if (state.codexPatchEventRevision === null) {
    state.codexPatchEventRevision = nextEventRevision;
  } else if (nextEventRevision !== state.codexPatchEventRevision) {
    state.codexPatchEventRevision = nextEventRevision;
    $("#codexStatus").textContent = "Codex patch is ready for review. Verify the staged change before saving.";
  }
}

function renderCodexHistory(conversations = []) {
  state.codexConversations = conversations;
  const signature = JSON.stringify([conversations, state.codexHistoryExpanded]);
  if (signature === state.codexConversationSignature) return;
  state.codexConversationSignature = signature;
  $("#codexHistoryCount").textContent = conversations.length ? String(conversations.length) : "";
  const visible = state.codexHistoryExpanded ? conversations : conversations.slice(0, 3);
  $("#codexHistoryList").innerHTML = visible.length
    ? `${visible.map((conversation) => `
        <button class="codex-history-item ${conversation.active ? "active" : ""}" type="button" data-conversation-id="${escapeHtml(conversation.id || "")}">
          <span class="codex-history-title">${escapeHtml(conversation.title || "New conversation")}</span>
          <small class="codex-history-context">${escapeHtml(conversation.cwd || conversation.thread_cwd || "No workspace")}</small>
          <span class="codex-history-time">${escapeHtml(relativeTimeLabel(conversation.updated_at || ""))}</span>
        </button>
      `).join("")}${conversations.length > 3 ? `
        <button id="codexHistoryMoreBtn" class="codex-history-more" type="button">
          ${state.codexHistoryExpanded ? "Show recent" : `View all (${conversations.length})`}
        </button>` : ""}`
    : '<div class="codex-history-empty">No saved conversations yet.</div>';
  $$("[data-conversation-id]").forEach((button) => {
    button.addEventListener("click", () => selectCodexConversation(button.dataset.conversationId || ""));
  });
  $("#codexHistoryMoreBtn")?.addEventListener("click", () => {
    state.codexHistoryExpanded = !state.codexHistoryExpanded;
    state.codexConversationSignature = "";
    renderCodexHistory(state.codexConversations);
  });
}

function relativeTimeLabel(value = "") {
  const timestamp = typeof value === "number"
    ? value * 1000
    : Date.parse(String(value).replace(" ", "T"));
  if (!Number.isFinite(timestamp)) return "";
  const seconds = Math.max(0, Math.floor((Date.now() - timestamp) / 1000));
  if (seconds < 60) return "now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d`;
  return `${Math.floor(days / 7)}w`;
}

function bindCodexSuggestions() {
  $$("[data-codex-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#codexInput").value = button.dataset.codexPrompt || "";
      $("#codexInput").focus();
    });
  });
}

function renderArduinoFilesAfterCodexPatch() {
  $$("#arduinoFiles tr").forEach((row) => {
    const changed = state.codexChangedFiles.has(String(row.dataset.path || "").toLowerCase());
    row.classList.toggle("codex-changed", changed);
  });
}

async function refreshCodex() {
  if (state.codexRefreshPromise) return state.codexRefreshPromise;
  state.codexRefreshPromise = api("/api/codex_status")
    .then(renderCodex)
    .catch((error) => {
      renderCodex({ available: true, connected: false, error: error.message });
    })
    .finally(() => {
      state.codexRefreshPromise = null;
      scheduleCodexRefresh();
    });
  return state.codexRefreshPromise;
}

function scheduleCodexRefresh(delay = null) {
  window.clearTimeout(state.codexRefreshTimer);
  const nextDelay = delay ?? (
    document.hidden || activeViewId() !== "workspace" || !codexPanelOpen()
      ? CODEX_HIDDEN_REFRESH_MS
      : state.codexBusy
        ? CODEX_BUSY_REFRESH_MS
        : CODEX_IDLE_REFRESH_MS
  );
  state.codexRefreshTimer = window.setTimeout(refreshCodex, nextDelay);
}

async function sendCodexMessage() {
  const input = $("#codexInput");
  const message = input.value.trim();
  if (!message || state.codexBusy) return;
  renderCodexContextPreview();
  $("#codexStatus").textContent = "Sending context to Codex...";
  $("#codexContextPreview").open = true;
  $("#sendCodexBtn").disabled = true;
  showCodexTasks(false);
  try {
    await api("/api/codex_message", {
      method: "POST",
      body: JSON.stringify(codexPayloadForNextTurn(message)),
    });
    input.value = "";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = error.message;
    $("#sendCodexBtn").disabled = false;
  }
}

async function newCodexThread() {
  try {
    await api("/api/codex_thread", { method: "POST", body: "{}" });
    state.codexMessagesSignature = "";
    showCodexTasks(false);
    await refreshCodex();
    $("#codexInput").focus();
  } catch (error) {
    $("#codexStatus").textContent = error.message;
  }
}

function showCodexTasks(open = true) {
  const history = $("#codexHistory");
  state.codexTasksVisible = Boolean(open);
  history.hidden = !state.codexTasksVisible;
  $("#codexPanel").classList.toggle("history-mode", state.codexTasksVisible);
  $("#codexBackBtn").hidden = state.codexTasksVisible;
  if (state.codexTasksVisible) {
    state.codexHistoryExpanded = false;
    state.codexConversationSignature = "";
    renderCodexHistory(state.codexConversations);
  }
}

async function selectCodexConversation(conversationId) {
  if (!conversationId || state.codexBusy) return;
  try {
    await api("/api/codex_conversation", {
      method: "POST",
      body: JSON.stringify({ id: conversationId }),
    });
    state.codexMessagesSignature = "";
    showCodexTasks(false);
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = error.message;
  }
}

async function cancelCodexTurn() {
  $("#cancelCodexBtn").disabled = true;
  $("#codexStatus").textContent = "Cancelling Codex turn...";
  try {
    await api("/api/codex_cancel", { method: "POST", body: "{}" });
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = error.message;
    $("#cancelCodexBtn").disabled = false;
  }
}

async function reconnectCodex() {
  $("#reconnectCodexBtn").disabled = true;
  $("#codexStatus").textContent = "Reconnecting Codex app-server...";
  try {
    await api("/api/codex_reconnect", { method: "POST", body: "{}" });
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = error.message;
    $("#reconnectCodexBtn").disabled = false;
  }
}

async function restoreCodexReviews() {
  try {
    await api("/api/codex_restore_reviews", { method: "POST", body: "{}" });
    $("#editorStatus").textContent = "Restored unfinished Codex reviews from the previous Talos session.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not restore unfinished reviews: ${error.message}`;
  }
}

async function discardCodexReviews() {
  try {
    await api("/api/codex_discard_reviews", { method: "POST", body: "{}" });
    setCodexReviewMode(null);
    $("#codexReviewRecovery").hidden = true;
    $("#editorStatus").textContent = "Discarded unfinished Codex reviews. The Arduino sketch was not changed.";
    await refreshCodex();
  } catch (error) {
    $("#codexStatus").textContent = `Could not discard unfinished reviews: ${error.message}`;
  }
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
        ${project.valid ? `<div class="project-source-meta">${Number(project.source_count || 0)} source tab(s)</div>` : ""}
        ${project.unsaved ? '<div class="project-path">Save this sketch in Arduino IDE to create a selectable workspace.</div>' : ""}
      </div>
      <button class="button ghost select-project" data-index="${index}" ${project.valid && !state.workspaceSelectionRunning ? "" : "disabled"}>Select</button>
    </div>
  `).join("");
  $$(".select-project").forEach((button) => {
    button.addEventListener("click", async () => {
      if (state.workspaceSelectionRunning) return;
      if (!canDiscardEditorChanges()) return;
      const project = projects[Number(button.dataset.index)];
      if (!project?.path) return;
      state.workspaceSelectionRunning = true;
      $$(".select-project").forEach((item) => {
        item.disabled = true;
      });
      $("#arduinoPathInput").value = project.path;
      if (project.fqbn) setBoardField(project.fqbn, project.board_name || "");
      state.arduinoDirty = true;
      try {
        await saveArduinoWorkspace();
      } finally {
        state.workspaceSelectionRunning = false;
        await refreshAfterWorkspaceMutation();
      }
    });
  });
}

function render(payload) {
  state.lastPayload = payload;
  hydrateAppearance(payload.config || {});
  renderDiagnosticsSettings(payload.config || {});
  hydrateAppIdentity(payload.app || {}, payload.build || {});
  const projects = payload.arduino_projects || [];
  const arduino = payload.arduino || {};
  state.workspaceMap = payload.arduino_workspace_map || {};
  state.arduinoEventRevision = Math.max(state.arduinoEventRevision, Number(payload.arduino_events?.revision || 0));
  const selectedPath = normalizedWindowsPath(arduino.path);
  const selectedProject = projects.find((project) => (
    normalizedWindowsPath(project.path) === selectedPath && project.fqbn === arduino.fqbn
  ))
    || projects.find((project) => normalizedWindowsPath(project.path) === selectedPath)
    || {};
  const versionText = $("#modeLine").dataset.version ? ` | ${$("#modeLine").dataset.version}` : "";
  $("#modeLine").textContent = `${payload.role}${versionText} | ${payload.root}`;
  $("#toolList").textContent = (payload.tools || []).join("\n");
  renderStats(payload);
  renderDashboard(payload);
  renderArduino(arduino, false, selectedProject);
  renderProfileReadiness(payload.arduino_profile_readiness || {});
  renderEnvironmentProfile(payload.arduino_profile || state.workspaceMap.environment_profile || {});
  renderArduinoProjects(projects);
  renderLogs(payload.events || []);
  renderStatusBar();
}

async function refresh() {
  if (state.workspaceMutationRunning) {
    return state.refreshPromise || null;
  }
  if (state.refreshPromise) return state.refreshPromise;
  const mutationVersion = state.workspaceMutationVersion;
  state.refreshPromise = api("/api/state")
    .then((payload) => {
      if (mutationVersion === state.workspaceMutationVersion) {
        render(payload);
      }
      state.lastRefreshAt = Date.now();
      return payload;
    })
    .finally(() => {
      state.refreshPromise = null;
    });
  return state.refreshPromise;
}

async function refreshAfterWorkspaceMutation() {
  if (state.refreshPromise) {
    try {
      await state.refreshPromise;
    } catch (_error) {
      // The fresh request below remains authoritative.
    }
  }
  return refresh();
}

function maybeRefresh() {
  if (document.hidden) return;
  const interval = activeViewId() === "workspace" ? FAST_REFRESH_MS : IDLE_REFRESH_MS;
  if (Date.now() - state.lastRefreshAt >= interval) refresh();
}

async function watchArduinoEvents() {
  if (document.hidden || activeViewId() !== "workspace" || state.arduinoEventPolling) return;
  state.arduinoEventPolling = true;
  try {
    const signal = await api(`/api/arduino_events?since=${state.arduinoEventRevision}`);
    const revision = Number(signal.revision || 0);
    if (revision > state.arduinoEventRevision) {
      state.arduinoEventRevision = revision;
      await refresh();
    }
  } catch (_error) {
    // Normal state polling remains the fallback when event assistance is unavailable.
  } finally {
    state.arduinoEventPolling = false;
  }
}

async function saveArduinoWorkspace() {
  state.workspaceMutationVersion += 1;
  state.workspaceMutationRunning = true;
  try {
    const result = await api("/api/arduino_workspace", {
      method: "POST",
      body: JSON.stringify({
        path: $("#arduinoPathInput").value,
        fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value,
      }),
    });
    state.arduinoDirty = false;
    renderArduino(result.arduino, true);
    return result;
  } finally {
    state.workspaceMutationRunning = false;
  }
}

async function verifyArduinoWorkspace(source = verifySource()) {
  setOutputView("verify");
  const context = currentVerifyContext(source);
  const signature = currentVerifySignature(source);
  const editorOverride = context.editor_override
    ? { path: state.activeFilePath, content: $("#sourceEditor").value }
    : null;
  renderVerifyOutput(null, editorOverride
    ? "Compiling the current Talos editor draft in an isolated Arduino sandbox..."
    : "Copying sketch folder to sandbox and running arduino-cli compile...");
  setArduinoVerifyRunning(true);
  try {
    const result = await api("/api/arduino_verify", {
      method: "POST",
      body: JSON.stringify({
        path: $("#arduinoPathInput").value,
        fqbn: state.arduinoFqbnFull || $("#arduinoFqbnInput").value,
        source,
        active_file: state.activeFilePath,
        editor_override: editorOverride,
      }),
    });
    rememberVerifyResult(result, signature, result.verify_context || context);
    renderProfileReadiness(result.profile_readiness || state.profileReadiness);
    $("#recordEvidenceBtn").disabled = false;
    renderVerifyOutput(result);
    state.arduinoDirty = false;
    await refreshRunHistory();
    await refresh();
    return result;
  } finally {
    setArduinoVerifyRunning(false);
  }
}

async function recordReleaseEvidence() {
  if (!state.lastVerifyResult) {
    $("#editorStatus").textContent = "Run Verify Sandbox before recording release evidence.";
    return;
  }
  const button = $("#recordEvidenceBtn");
  button.disabled = true;
  try {
    const result = await api("/api/release_evidence", {
      method: "POST",
      body: JSON.stringify({ verify_result: state.lastVerifyResult, blocked_cases: [], release: "0.3.0-beta" }),
    });
    $("#editorStatus").textContent = `Recorded release evidence: ${result.evidence?.status || "unknown"}.`;
    await refreshRunHistory();
  } catch (error) {
    $("#editorStatus").textContent = `Could not record release evidence: ${error.message}`;
  } finally {
    button.disabled = !state.lastVerifyResult;
  }
}

function setArduinoVerifyRunning(running) {
  state.arduinoVerifyRunning = Boolean(running);
  $("#verifyArduinoBtn").disabled = state.arduinoVerifyRunning;
  $("#cancelArduinoVerifyBtn").hidden = !state.arduinoVerifyRunning;
  $("#cancelArduinoVerifyBtn").disabled = !state.arduinoVerifyRunning;
  renderStatusBar();
}

async function cancelArduinoVerify() {
  const button = $("#cancelArduinoVerifyBtn");
  button.disabled = true;
  try {
    await api("/api/arduino_verify_cancel", { method: "POST", body: "{}" });
    $("#editorStatus").textContent = "Cancellation requested. Waiting for arduino-cli to stop.";
  } catch (error) {
    $("#editorStatus").textContent = `Could not cancel sandbox verification: ${error.message}`;
  }
}

async function clearVerifyCache() {
  const result = await api("/api/arduino_verify_cache_clear", { method: "POST", body: "{}" });
  state.lastVerifyResult = null;
  state.lastVerifySignature = "";
  state.lastVerifyOk = false;
  state.lastVerifyContext = null;
  $("#editorStatus").textContent = `Cleared ${Number(result.cleared || 0)} cached verification result(s).`;
}

async function saveSettings() {
  const diagnosticsEnabled = Boolean($("#diagnosticsEnabledInput")?.checked);
  const result = await api("/api/settings", {
    method: "POST",
    body: JSON.stringify({
      theme: currentTheme(),
      diagnostics: {
        enabled: diagnosticsEnabled,
        allow_remote_upload: false,
      },
    }),
  });
  renderDiagnosticsSettings(result.config || {});
  $("#settingsStatus").textContent = `Saved ${result.config?.theme || currentTheme()} theme.`;
  return result;
}

async function recordDiagnosticEvent(event, payload = {}) {
  try {
    await api("/api/diagnostics_event", {
      method: "POST",
      body: JSON.stringify({ event, payload }),
    });
  } catch (_) {
    // Diagnostics must never block the user workflow.
  }
}

async function previewDiagnosticsExport(copy = false) {
  const result = await api("/api/diagnostics_export");
  const text = JSON.stringify(result.diagnostics || {}, null, 2);
  $("#diagnosticsPreview").value = text;
  const count = Number(result.diagnostics?.event_count || 0);
  $("#diagnosticsStatus").textContent = `Diagnostics preview ready with ${count} event(s).`;
  if (copy) {
    await copyText(text);
    $("#diagnosticsStatus").textContent = `Copied redacted diagnostics export with ${count} event(s).`;
  }
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
  hideWindowMenu();
}

function hideWindowMenu() {
  $("#windowMenu")?.setAttribute("hidden", "");
}

function showWindowMenu(x = null, y = null) {
  const menu = $("#windowMenu");
  if (!menu) return;
  menu.hidden = false;
  const bounds = menu.getBoundingClientRect();
  const left = x == null ? window.innerWidth - bounds.width - 8 : Math.min(Math.max(4, x), window.innerWidth - bounds.width - 4);
  const top = y == null ? 34 : Math.min(Math.max(4, y), window.innerHeight - bounds.height - 4);
  menu.style.left = `${Math.round(left)}px`;
  menu.style.top = `${Math.round(top)}px`;
  menu.style.right = "auto";
  $("#windowRestoreMenuBtn")?.focus();
}

function resizeBoundsFromEdge(edge, startBounds, deltaX, deltaY) {
  let x = Number(startBounds.x || 0);
  let y = Number(startBounds.y || 0);
  let width = Number(startBounds.width || WINDOW_MIN_WIDTH);
  let height = Number(startBounds.height || WINDOW_MIN_HEIGHT);

  if (edge.includes("e")) width += deltaX;
  if (edge.includes("s")) height += deltaY;
  if (edge.includes("w")) {
    width -= deltaX;
    if (width < WINDOW_MIN_WIDTH) {
      x += Number(startBounds.width || WINDOW_MIN_WIDTH) - WINDOW_MIN_WIDTH;
      width = WINDOW_MIN_WIDTH;
    } else {
      x += deltaX;
    }
  }
  if (edge.includes("n")) {
    height -= deltaY;
    if (height < WINDOW_MIN_HEIGHT) {
      y += Number(startBounds.height || WINDOW_MIN_HEIGHT) - WINDOW_MIN_HEIGHT;
      height = WINDOW_MIN_HEIGHT;
    } else {
      y += deltaY;
    }
  }

  return {
    x: Math.round(x),
    y: Math.round(y),
    width: Math.max(WINDOW_MIN_WIDTH, Math.round(width)),
    height: Math.max(WINDOW_MIN_HEIGHT, Math.round(height)),
  };
}

function bindWindowResizeHandles() {
  $$(".window-resize-handle").forEach((handle) => {
    handle.addEventListener("pointerdown", async (event) => {
      if (event.button !== 0) return;
      const edge = handle.dataset.resizeEdge || "";
      const startBounds = await window.pywebview?.api?.get_window_bounds?.();
      if (!startBounds || startBounds.maximized) return;
      event.preventDefault();
      handle.setPointerCapture(event.pointerId);
      const startX = event.screenX;
      const startY = event.screenY;
      let framePending = false;
      let nextBounds = null;
      const commit = () => {
        framePending = false;
        if (!nextBounds) return;
        window.pywebview?.api?.set_window_bounds?.(nextBounds.x, nextBounds.y, nextBounds.width, nextBounds.height);
      };
      const move = (moveEvent) => {
        nextBounds = resizeBoundsFromEdge(edge, startBounds, moveEvent.screenX - startX, moveEvent.screenY - startY);
        if (!framePending) {
          framePending = true;
          requestAnimationFrame(commit);
        }
      };
      const finish = () => {
        handle.removeEventListener("pointermove", move);
        handle.removeEventListener("pointerup", finish);
        handle.removeEventListener("pointercancel", finish);
        syncWindowState();
      };
      handle.addEventListener("pointermove", move);
      handle.addEventListener("pointerup", finish);
      handle.addEventListener("pointercancel", finish);
    });
  });
}


function bindEvents() {
  restorePaneWidths();
  applyExplorerPanel(explorerPanelOpen());
  applyCodexPanel(codexPanelOpen());
  showCodexTasks(true);
  bindExplorerSplitter("#explorerSplitter");
  bindCodexSplitter("#codexSplitter");
  bindVerifySplitter("#verifySplitter");
  bindWindowResizeHandles();
  $$(".nav").forEach((button) => button.addEventListener("click", () => {
    const viewId = button.dataset.view;
    if (viewId === "workspace" && activeViewId() === "workspace") {
      applyExplorerPanel(!explorerPanelOpen());
      return;
    }
    setView(viewId);
    if (viewId === "workspace") applyExplorerPanel(true);
  }));
  $$("[data-go-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.goView)));
  $("#refreshBtn").addEventListener("click", refresh);
  $("#refreshWorkspaceBtn").addEventListener("click", refresh);
  $("#dashboardSupportBtn")?.addEventListener("click", copySupportBundle);
  $("#logFilter")?.addEventListener("change", () => renderLogs(state.lastPayload?.events || []));
  $("#saveArduinoBtn").addEventListener("click", async () => {
    await saveArduinoWorkspace();
    await refreshAfterWorkspaceMutation();
  });
  $("#saveEnvironmentProfileBtn").addEventListener("click", () => saveEnvironmentProfile().catch((error) => {
    $("#environmentProfileStatus").textContent = error.message;
  }));
  $("#verifyArduinoBtn").addEventListener("click", () => verifyArduinoWorkspace());
  $("#cancelArduinoVerifyBtn").addEventListener("click", cancelArduinoVerify);
  $("#clearVerifyCacheBtn").addEventListener("click", () => clearVerifyCache().catch((error) => {
    $("#editorStatus").textContent = `Could not clear verification cache: ${error.message}`;
  }));
  $("#verifyOutputTab").addEventListener("click", () => setOutputView("verify"));
  $("#runHistoryTab").addEventListener("click", async () => {
    setOutputView("history");
    await refreshRunHistory();
  });
  $("#runHistoryFilter").addEventListener("change", async (event) => {
    state.runHistoryFilter = event.target.value || "all";
    state.runHistorySignature = "";
    await refreshRunHistory();
  });
  $("#runHistorySketchOnly").addEventListener("change", async (event) => {
    state.runHistorySketchOnly = event.target.checked;
    state.runHistorySignature = "";
    await refreshRunHistory();
  });
  $("#copySupportBundleBtn").addEventListener("click", () => copySupportBundle().catch((error) => {
    $("#editorStatus").textContent = `Could not copy support bundle: ${error.message}`;
  }));
  $("#saveSettingsBtn").addEventListener("click", saveSettings);
  $("#copyFilesBtn").addEventListener("click", () => copyText(fileListText(), "#arduinoMeta"));
  $("#copyIssuesBtn").addEventListener("click", () => copyText(state.lastIssueText));
  $("#copyVerifyBtn").addEventListener("click", () => copyText(state.lastVerifyText));
  $("#recordEvidenceBtn").addEventListener("click", recordReleaseEvidence);
  $("#editInTalosBtn").addEventListener("click", () => setLocalEditMode(!state.localEditMode));
  $("#saveFileBtn").addEventListener("click", saveWorkspaceFile);
  $("#saveAndVerifyBtn").addEventListener("click", saveAndVerifyWorkspace);
  $("#rollbackFileBtn").addEventListener("click", rollbackWorkspaceFile);
  $$("[data-menu-button]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleAppMenu(button.dataset.menuButton);
    });
    button.addEventListener("mouseenter", () => {
      if ($(".app-menu.open")) toggleAppMenu(button.dataset.menuButton);
    });
  });
  $$(".app-menu-action[data-command]").forEach((button) => {
    button.addEventListener("click", () => {
      runAppMenuCommand(button.dataset.command);
      closeAppMenus();
    });
  });
  $$(".app-menu-action[id]").forEach((button) => {
    button.addEventListener("click", closeAppMenus);
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".app-menu")) closeAppMenus();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAppMenus();
  });
  $("#commandCenterBtn")?.addEventListener("click", () => showCommandPalette());
  $("#commandPaletteInput")?.addEventListener("input", () => {
    state.commandPaletteIndex = 0;
    renderCommandPalette();
  });
  $("#commandPaletteOverlay")?.addEventListener("mousedown", (event) => {
    if (event.target.id === "commandPaletteOverlay") hideCommandPalette();
  });
  $("#statusWorkspace")?.addEventListener("click", () => {
    setView("workspace");
    applyExplorerPanel(true);
  });
  $("#statusFile")?.addEventListener("click", () => {
    setView("workspace");
    applyExplorerPanel(true);
    $("#sourceEditor")?.focus({ preventScroll: true });
  });
  $("#statusBoard")?.addEventListener("click", () => {
    setView("workspace");
    applyExplorerPanel(true);
    $("#arduinoFqbnInput")?.focus({ preventScroll: true });
  });
  $("#statusVerify")?.addEventListener("click", () => {
    setView("workspace");
    setOutputView("verify");
  });
  $("#statusCodex")?.addEventListener("click", () => {
    setView("workspace");
    applyCodexPanel(true);
  });
  $("#applyCodexPatchBtn").addEventListener("click", () => applyCodexPatch());
  $("#verifyCodexPatchBtn").addEventListener("click", verifyCodexPatch);
  $("#rejectCodexPatchBtn").addEventListener("click", rejectCodexPatch);
  $("#restoreCodexReviewsBtn").addEventListener("click", restoreCodexReviews);
  $("#discardCodexReviewsBtn").addEventListener("click", discardCodexReviews);
  $("#rejectConflictCodexBtn").addEventListener("click", rejectConflictCodex);
  $("#draftConflictMergeBtn").addEventListener("click", draftConflictMerge);
  $("#applyConflictToEditorBtn").addEventListener("click", applyConflictToEditor);
  $("#applyCodexTurnBtn").addEventListener("click", () => resolveCodexTurn("apply"));
  $("#rejectCodexTurnBtn").addEventListener("click", () => resolveCodexTurn("reject"));
  $("#keepExternalConflictBtn").addEventListener("click", keepExternalConflict);
  $("#toggleCodexBtn").addEventListener("click", () => applyCodexPanel(!codexPanelOpen()));
  $("#closeCodexBtn").addEventListener("click", () => applyCodexPanel(false));
  $("#reconnectCodexBtn").addEventListener("click", reconnectCodex);
  $("#newCodexThreadBtn").addEventListener("click", newCodexThread);
  $("#codexBackBtn").addEventListener("click", () => showCodexTasks(true));
  $("#cancelCodexBtn").addEventListener("click", cancelCodexTurn);
  $("#codexComposer").addEventListener("submit", (event) => {
    event.preventDefault();
    sendCodexMessage();
  });
  $("#copyCodexContextBtn").addEventListener("click", (event) => {
    event.preventDefault();
    copyCodexContextPackage();
  });
  $("#codexInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendCodexMessage();
    }
  });
  $("#codexAllowEdits").addEventListener("change", renderCodexContextPreview);
  $("#sourceEditor").addEventListener("input", () => {
    renderEditorLineNumbers();
    setEditorDirty($("#sourceEditor").value !== state.editorOriginalContent);
    $("#editorStatus").textContent = state.editorDirty ? "Unsaved changes." : "No changes.";
    if (!$("#editorFindBar").hidden) runEditorFind(1);
    else renderEditorFindLayer();
    renderCodexContextPreview();
  });
  $("#sourceEditor").addEventListener("keydown", handleEditorShortcut);
  ["click", "keyup", "mouseup", "select", "focus"].forEach((eventName) => {
    $("#sourceEditor").addEventListener(eventName, updateEditorCursorLine);
  });
  $("#editorFindInput").addEventListener("input", () => runEditorFind(1));
  $("#editorFindInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      runEditorFind(event.shiftKey ? -1 : 1);
    }
    if (event.key === "Escape") {
      event.preventDefault();
      hideEditorFind();
    }
  });
  $("#findPreviousBtn").addEventListener("click", () => runEditorFind(-1));
  $("#findNextBtn").addEventListener("click", () => runEditorFind(1));
  $("#closeFindBtn").addEventListener("click", hideEditorFind);
  $("#sourceEditor").addEventListener("scroll", () => {
    $("#editorLineNumbers").scrollTop = $("#sourceEditor").scrollTop;
    syncEditorFindRenderScroll();
    updateEditorCursorLine();
  });
  $("#editorLineNumbers").addEventListener("mousedown", (event) => {
    event.preventDefault();
    selectEditorLine(lineFromGutterEvent(event));
  });
  $("#editorLineNumbers").addEventListener("mousemove", (event) => {
    if (event.buttons === 1) {
      event.preventDefault();
      selectEditorLine(lineFromGutterEvent(event));
    }
  });
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
      applySystemThemePreference(false);
      if (input.checked) applyTheme(input.value);
      $("#settingsStatus").textContent = "Theme changed. Save to keep it for next launch.";
    });
  });
  $("#systemThemeInput").addEventListener("change", (event) => {
    applySystemThemePreference(event.target.checked);
    $("#settingsStatus").textContent = event.target.checked
      ? "System theme sync enabled for this device. Save to keep the current resolved theme for next launch."
      : "System theme sync disabled. Save to keep the selected theme.";
  });
  $("#highContrastInput").addEventListener("change", (event) => {
    localStorage.setItem(HIGH_CONTRAST_KEY, String(Boolean(event.target.checked)));
    applyAppearancePreferences();
    $("#settingsStatus").textContent = "Contrast preference updated on this device.";
  });
  $("#editorFontSizeInput").addEventListener("change", (event) => {
    localStorage.setItem(EDITOR_FONT_SIZE_KEY, event.target.value || "14");
    applyAppearancePreferences();
    $("#settingsStatus").textContent = "Editor font preference updated on this device.";
  });
  $("#editorDensityInput").addEventListener("change", (event) => {
    localStorage.setItem(EDITOR_DENSITY_KEY, event.target.value || "comfortable");
    applyAppearancePreferences();
    $("#settingsStatus").textContent = "Editor density preference updated on this device.";
  });
  $("#diagnosticsEnabledInput").addEventListener("change", () => {
    $("#diagnosticsStatus").textContent = "Diagnostics setting changed. Save to keep it.";
  });
  $("#previewDiagnosticsBtn").addEventListener("click", () => previewDiagnosticsExport(false).catch((error) => {
    $("#diagnosticsStatus").textContent = `Could not preview diagnostics: ${error.message}`;
  }));
  $("#copyDiagnosticsBtn").addEventListener("click", () => previewDiagnosticsExport(true).catch((error) => {
    $("#diagnosticsStatus").textContent = `Could not copy diagnostics: ${error.message}`;
  }));
  $(".app-chrome").addEventListener("dblclick", (event) => {
    if (event.target.closest(".chrome-actions")) return;
    toggleMaximize();
  });
  $(".app-chrome").addEventListener("contextmenu", (event) => {
    if (event.target.closest(".chrome-actions")) return;
    event.preventDefault();
    showWindowMenu(event.clientX, event.clientY);
  });
  document.addEventListener("keydown", (event) => {
    if (commandPaletteOpen()) {
      if (event.key === "Escape") {
        event.preventDefault();
        hideCommandPalette();
      } else if (event.key === "Enter") {
        event.preventDefault();
        runCommandPaletteSelection();
      } else if (event.key === "ArrowDown") {
        event.preventDefault();
        moveCommandPaletteSelection(1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        moveCommandPaletteSelection(-1);
      }
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === "p") {
      event.preventDefault();
      showCommandPalette();
      return;
    }
    if (event.key === "Escape") hideWindowMenu();
    if (event.defaultPrevented) return;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "f" && activeViewId() === "workspace") {
      if (showEditorFind()) event.preventDefault();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === "b" && activeViewId() === "workspace") {
      event.preventDefault();
      verifyArduinoWorkspace();
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s" && activeViewId() === "workspace") {
      event.preventDefault();
      saveWorkspaceFile();
    }
    if (event.altKey && event.code === "Space") {
      event.preventDefault();
      showWindowMenu(12, 34);
    }
  });
  document.addEventListener("pointerdown", (event) => {
    if (!event.target.closest("#windowMenu") && !event.target.closest(".app-chrome")) hideWindowMenu();
  });
  $("#minimizeBtn").addEventListener("click", () => window.pywebview?.api?.minimize?.());
  $("#maximizeBtn").addEventListener("click", toggleMaximize);
  $("#closeBtn").addEventListener("click", () => window.pywebview?.api?.close?.());
  $("#windowRestoreMenuBtn").addEventListener("click", async () => {
    await window.pywebview?.api?.restore?.();
    setMaximizeIcon(false);
    hideWindowMenu();
  });
  $("#windowMinimizeMenuBtn").addEventListener("click", () => {
    hideWindowMenu();
    window.pywebview?.api?.minimize?.();
  });
  $("#windowMaximizeMenuBtn").addEventListener("click", toggleMaximize);
  $("#windowCloseMenuBtn").addEventListener("click", () => window.pywebview?.api?.close?.());
  syncWindowState();
}

bindEvents();
bindCodexSuggestions();
renderEditorLineNumbers();
const requestedView = new URLSearchParams(window.location.search).get("view");
if (["dashboard", "workspace", "logs", "settings"].includes(requestedView)) {
  setView(requestedView);
}
refresh();
setInterval(maybeRefresh, REFRESH_TICK_MS);
setInterval(watchArduinoEvents, ARDUINO_EVENT_POLL_MS);
setInterval(checkActiveFileOnDisk, ACTIVE_FILE_POLL_MS);
refreshCodex();
