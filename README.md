<div align="center">

# Trixie DevSuite

### A focused Python workspace for creating, discovering, and managing projects

<p>
  <img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.14 or newer">
  <img src="https://img.shields.io/badge/PySide6-desktop%20UI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/uv-powered-DE5FE9?style=for-the-badge" alt="uv powered">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
</p>

<p>
  <a href="#quick-start">Quick start</a> ·
  <a href="#features">Features</a> ·
  <a href="#creating-a-project">Create a project</a> ·
  <a href="#development">Development</a>
</p>

</div>

> **Trixie DevSuite** is an offline-first PySide6 desktop workspace for Python
> developers. It brings project creation, environment discovery, package
> management, Git shortcuts, diagnostics, support tools, and an in-app manual
> together in one dashboard.

## Features

### Create and discover projects

- Create Basic Python, command-line, PySide6, FastAPI, and data-science projects.
- Choose the Python version, project location, and starter template.
- Receive rule-based package recommendations from the project type and idea.
- Initialize Git, `pyproject.toml`, the virtual environment, and `uv.lock`.
- Discover projects and environments in configurable folders and immediate
  subfolders.
- Pin favorite projects and reopen recent projects from the dashboard.

### Work inside projects

- Open a project folder, terminal, or VS Code.
- Run the project's `main.py` with its managed environment.
- Run `pytest` and `ruff` without freezing the GUI.
- View project metadata, Python version, environment health, Git branch, and
  changed-file count.
- Inspect installed packages, add or remove dependencies, and upgrade
  `uv.lock`.
- Review Git status and recent history, then stage and commit changes.

### Monitor and troubleshoot

- View CPU and RAM percentages in the status bar and live dashboard chart.
- Track project count, selected branch, tool availability, refresh time, clock,
  and network status.
- Run system diagnostics and `uv sync` from the Troubleshooting page.
- Stream background command output and cancel long-running project operations.
- Use notifications and the activity log to follow important app actions.
- Use Panic Mode to run a safe diagnostics and workspace-refresh sequence.

### Settings, help, and support

- Choose Comfortable or Compact density and the Dev Cyan, Hacker Red, or
  Neon Sunset theme.
- Configure sidebar width, startup page, default project location and Python
  version, refresh behavior, and project search folders.
- Export and import portable JSON settings, including Developer Mode.
- Browse the searchable offline manual and open official online resources.
- Export a support report that excludes source code and credentials.
- Enable Developer Mode for runtime snapshots and advanced support tools.

## Requirements

- Python **3.14 or newer**
- [`uv`](https://docs.astral.sh/uv/) available on `PATH`
- A PySide6-compatible desktop environment

DevSuite currently targets Windows. Terminal integration also supports common
Linux and macOS terminal launchers where available.

## Quick start

### 1. Clone the repository

```powershell
git clone https://github.com/Trixiemisheen/trixie-devsuite.git
cd trixie-devsuite
```

### 2. Install dependencies

```powershell
uv sync
```

### 3. Launch DevSuite

```powershell
uv run python main.py
```

If a virtual environment is already activated and `uv` reports that
`VIRTUAL_ENV` does not match the project environment, use:

```powershell
uv run --active python main.py
```

Alternatively, run `deactivate` first and let `uv` select the project
environment automatically.

<details>
<summary>Run without uv</summary>

Install the dependencies declared in [`pyproject.toml`](pyproject.toml), then
run:

```powershell
python main.py
```

</details>

## Creating a project

1. Select **New Project**.
2. Enter a name and choose a parent location.
3. Select a Python version and starter template.
4. Choose a project type and optionally describe the idea.
5. Review the recommended packages.
6. Select **Create Project**.

DevSuite uses `uv init`, `uv add`, and `uv sync` during setup. Keep `uv`
available on `PATH` before starting the wizard.

If an individual package fails, setup continues with the remaining packages and
reports the failed package names afterward.

## Project discovery

By default, DevSuite searches the `Projects` folder in the user's home
directory. Add more locations under **Settings → Project search folders**, then
refresh **My Projects** or **Environments**.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+N` | New project |
| `Ctrl+1` | Dashboard |
| `Ctrl+2` | My Projects |
| `Ctrl+3` | Environments |
| `Ctrl+4` | Help |
| `Ctrl+5` | Troubleshooting |
| `Ctrl+6` | Support |
| `Ctrl+,` | Settings |
| `Ctrl+B` | Collapse or expand the sidebar |
| `Ctrl+Shift+M` | Notification center |
| `Ctrl+H` | Help and manual |

## Support-report privacy

Support reports do not include project source code or credentials. They may
include local executable paths, selected project paths, diagnostics, and recent
activity. Review the exported JSON before sharing it.

## Development

The current application entry point is [`main.py`](main.py).

Compile-check the source without launching the GUI:

```powershell
uv run python -m py_compile main.py
```

The application is currently organized as a single entry-point module. The
worker, dialog, page, and service boundaries are gradually being separated as
the feature set grows.

## Owner links

- [Telegram](https://t.me/Trixie_Misheen)
- [Instagram](https://instagram.com/trixiemisheen)
- [WhatsApp](https://wa.me/254791915925)
- [GitHub](https://github.com/trixiemisheen/)

## License

No license has been specified for this repository yet.
