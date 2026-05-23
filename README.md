# Talos

Native Windows desktop assistant prototype.

The app runs as a real desktop window, keeps a local task queue, executes lightweight local tasks, and can optionally connect to a local Ollama model. After packaging, normal use does not require launching Python manually.

## Features

- Native desktop UI, no browser required
- Cyber neon purple/violet theme
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
- Language setting for responses:
  - Auto detect command language, fallback English
  - Vietnamese
  - English
  - French
  - Japanese
  - Chinese
- PyInstaller build scripts for a one-file Windows `.exe`

## Project Files

```text
desktop_app.py        Main desktop app
config.json           Runtime config
tasks.example.json    Empty task queue example
launch_desktop.ps1    Open installed app, fallback to source mode
build_app.ps1         Build one-file Windows executable
install_app.ps1       Install built app to LocalAppData and create desktop shortcut
install_ollama.ps1    Helper to install Ollama when network allows
setup_model.ps1       Pull the configured Ollama model
requirements.txt      Build dependency list
```

`tasks.json` is runtime state and is intentionally ignored by Git.

## Normal Use

After install, open the Desktop shortcut:

```text
Talos
```

Installed app path:

```text
%LOCALAPPDATA%\Programs\Talos\Talos.exe
```

Python is not needed for normal installed usage.

## Run From Source

```powershell
python -B desktop_app.py
```

Or:

```powershell
.\launch_desktop.ps1
```

## Build And Install

Python is only required for development/building the `.exe`.

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
