export const THEMES = ["light", "dark", "neutral"];
export const THEME_KEY = "talos-theme";
export const SYSTEM_THEME_KEY = "talos-system-theme";
export const HIGH_CONTRAST_KEY = "talos-high-contrast";
export const EDITOR_FONT_SIZE_KEY = "talos-editor-font-size";
export const EDITOR_DENSITY_KEY = "talos-editor-density";
export const CODEX_PANEL_KEY = "talos-codex-panel-open";
export const EXPLORER_PANEL_KEY = "talos-explorer-panel-open";
export const EXPLORER_WIDTH_KEY = "talos-explorer-pane-width";
export const CODEX_WIDTH_KEY = "talos-codex-pane-width";
export const VERIFY_HEIGHT_KEY = "talos-verify-pane-height";
export const FAST_REFRESH_MS = 1000;
export const IDLE_REFRESH_MS = 5000;
export const REFRESH_TICK_MS = 250;
export const CODEX_BUSY_REFRESH_MS = 400;
export const CODEX_IDLE_REFRESH_MS = 3000;
export const CODEX_HIDDEN_REFRESH_MS = 8000;
export const ACTIVE_FILE_POLL_MS = 700;
export const ARDUINO_EVENT_POLL_MS = 300;
export const TALOS_WRITE_DEBOUNCE_MS = 1500;
export const WINDOW_MIN_WIDTH = 640;
export const WINDOW_MIN_HEIGHT = 460;

export const APP_MENU_COMMANDS = {
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

export const COMMAND_PALETTE_ITEMS = [
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
