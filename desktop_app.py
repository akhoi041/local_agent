from __future__ import annotations

import ast
import json
import math
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any
from urllib.parse import urlparse

if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
TASKS_PATH = ROOT / "tasks.json"

CYBER = {
    "bg": "#050b18",
    "panel": "#071527",
    "panel_2": "#0b1f35",
    "field": "#06101f",
    "rail": "#020713",
    "line": "#12385d",
    "text": "#d8f3ff",
    "muted": "#7fb7d8",
    "cyan": "#00d9ff",
    "blue": "#1677ff",
    "deep_blue": "#0b3d91",
    "green": "#2af5a8",
    "warn": "#ffd166",
    "fail": "#ff5c8a",
}

def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()
        if not self.path.exists():
            self.write([])

    def read(self) -> list[dict[str, Any]]:
        with self.lock:
            return self._read_unlocked()

    def write(self, tasks: list[dict[str, Any]]) -> None:
        with self.lock:
            self._write_unlocked(tasks)

    def create(self, prompt: str) -> int:
        with self.lock:
            tasks = self._read_unlocked()
            task_id = max((task["id"] for task in tasks), default=0) + 1
            stamp = now()
            tasks.append(
                {
                    "id": task_id,
                    "prompt": prompt,
                    "status": "queued",
                    "result": "",
                    "error": "",
                    "created_at": stamp,
                    "updated_at": stamp,
                }
            )
            self._write_unlocked(tasks)
            return task_id

    def claim(self) -> dict[str, Any] | None:
        with self.lock:
            tasks = sorted(self._read_unlocked(), key=lambda item: item["id"])
            for task in tasks:
                if task["status"] == "queued":
                    task["status"] = "running"
                    task["updated_at"] = now()
                    self._write_unlocked(tasks)
                    return task
        return None

    def update(self, task_id: int, **changes: Any) -> None:
        with self.lock:
            tasks = self._read_unlocked()
            for task in tasks:
                if task["id"] == task_id:
                    task.update(changes)
                    task["updated_at"] = now()
                    break
            self._write_unlocked(tasks)

    def clear_done(self) -> None:
        with self.lock:
            tasks = [task for task in self._read_unlocked() if task["status"] != "done"]
            self._write_unlocked(tasks)

    def _read_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _write_unlocked(self, tasks: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")

class ComputerTools:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def handle(self, prompt: str) -> str | None:
        text = prompt.strip()
        lower = text.lower()
        if lower.startswith("open "):
            target = text[5:].strip().strip('"')
            return self.open_target(target)
        if lower.startswith("run "):
            command = text[4:].strip()
            return self.run_allowlisted(command)
        return None

    def open_target(self, target: str) -> str:
        if not target:
            return "No target provided."
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
        return f"Opened: {target}"

    def run_allowlisted(self, command: str) -> str:
        if not self.config.get("allow_shell", False):
            return "Shell is locked. Enable allow_shell in Settings first."
        allowed = self.config.get("allowed_commands", [])
        if command not in allowed:
            return f"Command is not allowlisted: {command}"
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            timeout=60,
            cwd=ROOT,
        )
        output = completed.stdout.strip() or completed.stderr.strip()
        return output or f"Command completed with exit code {completed.returncode}."

class LocalTaskEngine:
    ALLOWED_BINOPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a**b,
    }
    ALLOWED_UNARY = {
        ast.UAdd: lambda value: value,
        ast.USub: lambda value: -value,
    }
    ALLOWED_FUNCS = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
    }
    ALLOWED_NAMES = {
        "pi": math.pi,
        "e": math.e,
    }

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.tools = ComputerTools(config)

    def handle(self, prompt: str) -> str | None:
        text = prompt.strip()
        if not text:
            return "No task content."

        tool_result = self.tools.handle(text)
        if tool_result is not None:
            return tool_result

        time_result = self.handle_time(text)
        if time_result is not None:
            return time_result

        math_result = self.handle_math(text)
        if math_result is not None:
            return math_result

        return None

    def handle_time(self, prompt: str) -> str | None:
        lower = prompt.lower()
        if lower in {"time", "what time is it", "current time", "now", "gio hien tai", "mấy giờ rồi"}:
            return datetime.now().strftime("Current local time: %H:%M:%S")
        if lower in {"date", "today", "current date", "ngay hom nay", "hôm nay"}:
            return datetime.now().strftime("Current local date: %Y-%m-%d")
        return None

    def handle_math(self, prompt: str) -> str | None:
        expression = self.extract_expression(prompt)
        if expression is None:
            return None
        value = self.safe_eval(expression)
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return f"{expression} = {value}"

    def extract_expression(self, prompt: str) -> str | None:
        lower = prompt.lower().strip()
        prefixes = [
            "print the result of",
            "calculate",
            "compute",
            "solve",
            "what is",
            "result of",
            "tinh",
            "tính",
        ]
        for prefix in prefixes:
            if lower.startswith(prefix):
                expression = prompt[len(prefix) :].strip(" :?=")
                return expression if self.looks_like_math(expression) else None
        return prompt if self.looks_like_math(prompt) else None

    def looks_like_math(self, expression: str) -> bool:
        if not expression or len(expression) > 160:
            return False
        if not re.search(r"\d", expression):
            return False
        return re.fullmatch(r"[0-9a-zA-Z_+\-*/%.(),\s]+", expression) is not None

    def safe_eval(self, expression: str) -> int | float:
        tree = ast.parse(expression, mode="eval")
        return self.eval_node(tree.body)

    def eval_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_BINOPS:
                raise ValueError("Unsupported operator.")
            return self.ALLOWED_BINOPS[op_type](self.eval_node(node.left), self.eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_UNARY:
                raise ValueError("Unsupported unary operator.")
            return self.ALLOWED_UNARY[op_type](self.eval_node(node.operand))
        if isinstance(node, ast.Name):
            if node.id not in self.ALLOWED_NAMES:
                raise ValueError(f"Unknown name: {node.id}")
            return self.ALLOWED_NAMES[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in self.ALLOWED_FUNCS:
                raise ValueError(f"Unsupported function: {node.func.id}")
            args = [self.eval_node(arg) for arg in node.args]
            return self.ALLOWED_FUNCS[node.func.id](*args)
        raise ValueError("Expression is not supported.")

def call_model(prompt: str, config: dict[str, Any]) -> str:
    if not config.get("model_enabled", False):
        return (
            "Prototype mode\n\n"
            "The desktop app worker received this task. Model calls are disabled.\n\n"
            f"Task:\n{prompt}"
        )
    body = {
        "model": config["model"],
        "messages": [
            {
                "role": "system",
                "content": "You are a local desktop assistant. Answer in Vietnamese. Be concise and practical.",
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": config.get("temperature", 0.4),
            "num_ctx": config.get("num_ctx", 4096),
        },
    }
    request = urllib.request.Request(
        config["ollama_url"],
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload.get("message", {}).get("content", "").strip()
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama backend is not reachable.\n\n"
            "Install Ollama, then run:\n"
            f"ollama pull {config.get('model', 'qwen2.5:7b-instruct-q3_K_L')}\n\n"
            f"Configured endpoint: {config.get('ollama_url')}\n"
            f"Details: {exc}"
        ) from exc

def ollama_base_url(config: dict[str, Any]) -> str:
    parsed = urlparse(config.get("ollama_url", "http://127.0.0.1:11434/api/chat"))
    return f"{parsed.scheme}://{parsed.netloc}"

def check_ollama(config: dict[str, Any], timeout: float = 2.0) -> tuple[bool, str]:
    base_url = ollama_base_url(config)
    tags_url = f"{base_url}/api/tags"
    try:
        with urllib.request.urlopen(tags_url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return False, (
            "Ollama is not reachable.\n"
            "Install/start Ollama, then pull the configured model.\n"
            f"Endpoint: {tags_url}\n"
            f"Details: {exc}"
        )

    model = config.get("model", "")
    models = [item.get("name", "") for item in payload.get("models", [])]
    if any(name == model or name.startswith(f"{model}:") for name in models):
        return True, f"Ollama is ready. Model found: {model}"
    available = ", ".join(models[:8]) if models else "none"
    return False, (
        f"Ollama is running, but the configured model is missing: {model}\n"
        f"Run: ollama pull {model}\n"
        f"Available models: {available}"
    )

class LocalAgentDesktop(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Local Agent Desktop")
        self.geometry("1120x720")
        self.minsize(920, 620)
        self.configure(bg=CYBER["bg"])

        self.config_data = load_config()
        self.store = TaskStore(TASKS_PATH)
        self.events: queue.Queue[str] = queue.Queue()
        self.stop_event = threading.Event()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure_style()
        self.build_ui()
        self.refresh_all()

        self.worker = threading.Thread(target=self.worker_loop, daemon=True)
        self.worker.start()
        self.after(1000, self.tick)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_style(self) -> None:
        self.style.configure("TFrame", background=CYBER["bg"])
        self.style.configure("Rail.TFrame", background=CYBER["rail"])
        self.style.configure("Panel.TFrame", background=CYBER["panel"], relief="flat")
        self.style.configure("TLabel", background=CYBER["bg"], foreground=CYBER["text"])
        self.style.configure("Muted.TLabel", background=CYBER["panel"], foreground=CYBER["muted"])
        self.style.configure("Panel.TLabel", background=CYBER["panel"], foreground=CYBER["text"])
        self.style.configure("TButton", padding=8, background=CYBER["panel_2"], foreground=CYBER["text"])
        self.style.configure("Accent.TButton", padding=8, background=CYBER["cyan"], foreground=CYBER["bg"])
        self.style.map("TButton", background=[("active", CYBER["deep_blue"])], foreground=[("active", CYBER["text"])])
        self.style.map("Accent.TButton", background=[("active", CYBER["blue"])], foreground=[("active", CYBER["text"])])
        self.style.configure("TNotebook", background=CYBER["bg"], bordercolor=CYBER["line"])
        self.style.configure("TNotebook.Tab", padding=(12, 7), background=CYBER["panel_2"], foreground=CYBER["muted"])
        self.style.map("TNotebook.Tab", background=[("selected", CYBER["deep_blue"])], foreground=[("selected", CYBER["text"])])
        self.style.configure(
            "Treeview",
            rowheight=28,
            background=CYBER["field"],
            fieldbackground=CYBER["field"],
            foreground=CYBER["text"],
        )
        self.style.configure("Treeview.Heading", background=CYBER["panel_2"], foreground=CYBER["cyan"])
        self.style.map("Treeview", background=[("selected", CYBER["deep_blue"])], foreground=[("selected", CYBER["text"])])

    def build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        rail = ttk.Frame(self, width=84, style="Rail.TFrame")
        rail.grid(row=0, column=0, sticky="ns")
        rail.grid_propagate(False)

        mark = tk.Label(rail, text="LA", bg=CYBER["blue"], fg=CYBER["text"], font=("Segoe UI", 14, "bold"), width=4, height=2)
        mark.pack(pady=(18, 20))
        for label, command in [
            ("Dash", self.show_dashboard),
            ("Queue", self.show_queue),
            ("Logs", self.show_logs),
            ("Set", self.show_settings),
        ]:
            ttk.Button(rail, text=label, command=command).pack(fill="x", padx=10, pady=5)

        self.content = ttk.Frame(self, padding=18, style="TFrame")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        header = ttk.Frame(self.content, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Local Agent Desktop", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        self.mode_label = ttk.Label(header, text="", foreground=CYBER["muted"])
        self.mode_label.grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="Refresh", command=self.refresh_all).grid(row=0, column=1, rowspan=2, padx=(10, 0))

        self.notebook = ttk.Notebook(self.content)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        self.dashboard_tab = ttk.Frame(self.notebook, padding=14, style="Panel.TFrame")
        self.queue_tab = ttk.Frame(self.notebook, padding=14, style="Panel.TFrame")
        self.logs_tab = ttk.Frame(self.notebook, padding=14, style="Panel.TFrame")
        self.settings_tab = ttk.Frame(self.notebook, padding=14, style="Panel.TFrame")
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.queue_tab, text="Queue")
        self.notebook.add(self.logs_tab, text="Logs")
        self.notebook.add(self.settings_tab, text="Settings")

        self.build_dashboard()
        self.build_queue()
        self.build_logs()
        self.build_settings()

    def build_dashboard(self) -> None:
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(2, weight=1)
        self.stats_label = ttk.Label(self.dashboard_tab, text="", style="Panel.TLabel", font=("Segoe UI", 12, "bold"))
        self.stats_label.grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(self.dashboard_tab, text="Command Deck", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).grid(row=1, column=0, sticky="w")
        self.prompt_text = tk.Text(
            self.dashboard_tab,
            height=7,
            bg=CYBER["field"],
            fg=CYBER["text"],
            insertbackground=CYBER["cyan"],
            selectbackground=CYBER["deep_blue"],
            relief="flat",
            wrap="word",
        )
        self.prompt_text.grid(row=2, column=0, sticky="nsew", pady=8)
        actions = ttk.Frame(self.dashboard_tab, style="Panel.TFrame")
        actions.grid(row=3, column=0, sticky="ew")
        ttk.Button(actions, text="Queue Task", style="Accent.TButton", command=self.queue_prompt).pack(side="right")
        ttk.Label(actions, text="Use: open notepad | open C:\\path | run python --version", style="Muted.TLabel").pack(side="left")

    def build_queue(self) -> None:
        self.queue_tab.columnconfigure(0, weight=1)
        self.queue_tab.rowconfigure(0, weight=1)
        self.task_tree = ttk.Treeview(self.queue_tab, columns=("status", "created", "prompt"), show="headings")
        self.task_tree.heading("status", text="Status")
        self.task_tree.heading("created", text="Created")
        self.task_tree.heading("prompt", text="Prompt")
        self.task_tree.column("status", width=90, stretch=False)
        self.task_tree.column("created", width=150, stretch=False)
        self.task_tree.column("prompt", width=620)
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        self.task_tree.bind("<<TreeviewSelect>>", self.show_selected_task)

        side = ttk.Frame(self.queue_tab, style="Panel.TFrame")
        side.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        ttk.Button(side, text="Clear Done", command=self.clear_done).pack(fill="x", pady=(0, 8))
        ttk.Button(side, text="Refresh", command=self.refresh_all).pack(fill="x")
        self.task_detail = tk.Text(
            self.queue_tab,
            height=9,
            bg=CYBER["field"],
            fg=CYBER["text"],
            insertbackground=CYBER["cyan"],
            selectbackground=CYBER["deep_blue"],
            relief="flat",
            wrap="word",
        )
        self.task_detail.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def build_logs(self) -> None:
        self.logs_tab.columnconfigure(0, weight=1)
        self.logs_tab.rowconfigure(0, weight=1)
        self.log_text = tk.Text(
            self.logs_tab,
            bg=CYBER["field"],
            fg=CYBER["text"],
            insertbackground=CYBER["cyan"],
            selectbackground=CYBER["deep_blue"],
            relief="flat",
            wrap="word",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def build_settings(self) -> None:
        self.settings_tab.columnconfigure(1, weight=1)
        self.model_var = tk.StringVar(value=self.config_data.get("model", ""))
        self.url_var = tk.StringVar(value=self.config_data.get("ollama_url", ""))
        self.ctx_var = tk.StringVar(value=str(self.config_data.get("num_ctx", 4096)))
        self.temp_var = tk.StringVar(value=str(self.config_data.get("temperature", 0.4)))
        self.model_enabled_var = tk.BooleanVar(value=bool(self.config_data.get("model_enabled", False)))
        self.shell_var = tk.BooleanVar(value=bool(self.config_data.get("allow_shell", False)))
        self.model_status_var = tk.StringVar(value="Model status has not been checked.")

        rows = [
            ("Model", self.model_var),
            ("Ollama URL", self.url_var),
            ("Context", self.ctx_var),
            ("Temperature", self.temp_var),
        ]
        for row, (label, var) in enumerate(rows):
            ttk.Label(self.settings_tab, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=6)
            ttk.Entry(self.settings_tab, textvariable=var).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Checkbutton(self.settings_tab, text="Enable model calls", variable=self.model_enabled_var).grid(row=4, column=1, sticky="w", pady=6)
        ttk.Checkbutton(self.settings_tab, text="Allow shell commands from allowlist", variable=self.shell_var).grid(row=5, column=1, sticky="w", pady=6)
        ttk.Label(self.settings_tab, textvariable=self.model_status_var, style="Muted.TLabel", wraplength=720).grid(row=6, column=1, sticky="ew", pady=8)
        action_row = ttk.Frame(self.settings_tab, style="Panel.TFrame")
        action_row.grid(row=7, column=1, sticky="e", pady=12)
        ttk.Button(action_row, text="Test AI Model", command=self.test_model_status).pack(side="left", padx=(0, 8))
        ttk.Button(action_row, text="Save Settings", style="Accent.TButton", command=self.save_settings).pack(side="left")

    def queue_prompt(self) -> None:
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            return
        task_id = self.store.create(prompt)
        self.prompt_text.delete("1.0", "end")
        self.events.put(f"{now()} queued task #{task_id}")
        self.refresh_all()

    def worker_loop(self) -> None:
        while not self.stop_event.is_set():
            task = self.store.claim()
            if not task:
                self.stop_event.wait(1.0)
                continue
            self.events.put(f"{now()} running task #{task['id']}")
            try:
                config = load_config()
                local_engine = LocalTaskEngine(config)
                local_result = local_engine.handle(task["prompt"])
                result = local_result if local_result is not None else call_model(task["prompt"], config)
                self.store.update(task["id"], status="done", result=result, error="")
                self.events.put(f"{now()} completed task #{task['id']}")
            except Exception as exc:
                self.store.update(task["id"], status="failed", error=str(exc))
                self.events.put(f"{now()} failed task #{task['id']}: {exc}")

    def refresh_all(self) -> None:
        self.config_data = load_config()
        mode = "Prototype mode" if not self.config_data.get("model_enabled", False) else self.config_data.get("model", "")
        shell = "shell allowlist" if self.config_data.get("allow_shell", False) else "shell locked"
        self.mode_label.configure(text=f"{mode} | {shell} | {ROOT}")

        tasks = sorted(self.store.read(), key=lambda item: item["id"], reverse=True)
        counts = {"queued": 0, "running": 0, "done": 0, "failed": 0}
        for task in tasks:
            counts[task["status"]] = counts.get(task["status"], 0) + 1
        self.stats_label.configure(
            text=f"Queued {counts['queued']}    Running {counts['running']}    Done {counts['done']}    Failed {counts['failed']}"
        )

        selected = self.task_tree.selection()
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task in tasks:
            prompt = task["prompt"]
            if len(prompt) > 120:
                prompt = prompt[:117] + "..."
            self.task_tree.insert("", "end", iid=str(task["id"]), values=(task["status"], task["created_at"], prompt))
        if selected:
            for item in selected:
                if self.task_tree.exists(item):
                    self.task_tree.selection_set(item)
                    break

    def show_selected_task(self, _event: object | None = None) -> None:
        selected = self.task_tree.selection()
        if not selected:
            return
        task = next((item for item in self.store.read() if str(item["id"]) == selected[0]), None)
        if not task:
            return
        text = (
            f"Task #{task['id']} [{task['status']}]\n"
            f"Created: {task['created_at']}\nUpdated: {task['updated_at']}\n\n"
            f"Prompt:\n{task['prompt']}\n\n"
            f"Result:\n{task.get('result', '')}\n\n"
            f"Error:\n{task.get('error', '')}"
        )
        self.task_detail.delete("1.0", "end")
        self.task_detail.insert("1.0", text)

    def show_dashboard(self) -> None:
        self.notebook.select(self.dashboard_tab)

    def show_queue(self) -> None:
        self.notebook.select(self.queue_tab)

    def show_logs(self) -> None:
        self.notebook.select(self.logs_tab)

    def show_settings(self) -> None:
        self.notebook.select(self.settings_tab)

    def save_settings(self) -> None:
        config = load_config()
        config["model"] = self.model_var.get().strip()
        config["ollama_url"] = self.url_var.get().strip()
        config["num_ctx"] = int(self.ctx_var.get())
        config["temperature"] = float(self.temp_var.get())
        config["model_enabled"] = bool(self.model_enabled_var.get())
        config["allow_shell"] = bool(self.shell_var.get())
        save_config(config)
        self.events.put(f"{now()} saved settings")
        self.refresh_all()

    def test_model_status(self) -> None:
        self.save_settings()
        self.model_status_var.set("Checking Ollama...")

        def run_check() -> None:
            ok, message = check_ollama(load_config())
            prefix = "Ready" if ok else "Not ready"
            self.events.put(f"{now()} model check: {prefix}")
            self.after(0, lambda: self.model_status_var.set(message))

        threading.Thread(target=run_check, daemon=True).start()

    def clear_done(self) -> None:
        self.store.clear_done()
        self.events.put(f"{now()} cleared completed tasks")
        self.refresh_all()

    def tick(self) -> None:
        updated = False
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            self.log_text.insert("end", event + "\n")
            self.log_text.see("end")
            updated = True
        if updated:
            self.refresh_all()
        self.after(1000, self.tick)

    def on_close(self) -> None:
        self.stop_event.set()
        self.destroy()

if __name__ == "__main__":
    try:
        app = LocalAgentDesktop()
        app.mainloop()
    except Exception as exc:
        messagebox.showerror("Local Agent Desktop", str(exc))
