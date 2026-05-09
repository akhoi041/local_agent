# Local Agent Desktop

Native Windows desktop assistant prototype built with Python and Tkinter.

The app runs as a real desktop window, keeps a local task queue, executes lightweight local tasks, and can optionally connect to a local Ollama model.

## Features

- Native desktop UI, no browser required
- Blue cyber theme
- Background worker inside the app process
- Local task queue stored in `tasks.json`
- Gmail-like queue selection:
  - select one task from the checkbox column
  - select all tasks from the toolbar
  - clear selected tasks in one action
- Lightweight local task engine:
  - math: `print the result of 1+2`, `calculate sqrt(16) + 2`
  - date/time: `date`, `time`
  - desktop open: `open notepad`, `open C:\path`
  - allowlisted shell: `run python --version`
- Optional Ollama backend for open-ended language tasks
- PyInstaller build scripts for Windows `.exe`

## Project Files

```text
desktop_app.py        Main desktop app
config.json           Runtime config
tasks.example.json    Empty task queue example
launch_desktop.ps1    Run app from source
build_app.ps1         Build Windows executable
install_app.ps1       Install built app to LocalAppData and create desktop shortcut
install_ollama.ps1    Helper to install Ollama when network allows
setup_model.ps1       Pull the configured Ollama model
requirements.txt      Build dependency list
```

`tasks.json` is runtime state and is intentionally ignored by Git.

## Run From Source

```powershell
python -B desktop_app.py
```

Or:

```powershell
.\launch_desktop.ps1
```

## Build And Install

Install build dependencies:

```powershell
python -m pip install -r requirements.txt
```

Build the app:

```powershell
.\build_app.ps1
```

Install locally and create a desktop shortcut:

```powershell
.\install_app.ps1
```

Installed app path:

```text
%LOCALAPPDATA%\Programs\LocalAgentDesktop\LocalAgentDesktop.exe
```

## Optional Ollama Model

Recommended model for the current target machine:

```text
qwen2.5:7b-instruct-q3_K_L
```

To set up:

```powershell
.\install_ollama.ps1
.\setup_model.ps1
```

If the installer cannot reach GitHub release assets, install Ollama manually:

```text
https://ollama.com/download/windows
```

Then run:

```powershell
.\setup_model.ps1
```

Open the app, go to `Settings`, and press `Test AI Model`.

## Safety Note

Shell execution is disabled by default. The `run ...` command only works when `allow_shell` is enabled and the exact command is present in `allowed_commands` inside `config.json`.
