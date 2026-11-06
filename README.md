<div align="center">

# Trixie DevSuite

### A focused Python workspace for creating, discovering, and managing projects

<p>
  <img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.14 or newer">
  <img src="https://img.shields.io/badge/PyQt5-desktop%20UI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/uv-powered-DE5FE9?style=for-the-badge" alt="uv powered">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
</p>

<p>
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-it-does">Features</a> ·
  <a href="#creating-a-project">Create a project</a> ·
  <a href="#development">Development</a>
</p>

</div>

> **Trixie DevSuite** is an offline-first PyQt5 desktop workspace for Python
> developers. It combines project creation, environment discovery, package
> recommendations, Git shortcuts, health checks, and an in-app manual in one
> focused dashboard.

## At a glance

| Workspace | Capabilities |
| --- | --- |
| **Create** | Start Basic Python, CLI, PyQt, FastAPI, or data science projects |
| **Discover** | Find projects and virtual environments in configured folders |
| **Develop** | Run projects, tests, lint checks, terminals, and VS Code |
| **Manage** | Inspect packages, update dependencies, and upgrade `uv.lock` |
| **Collaborate** | Review Git status and history, switch branches, and commit changes |
| **Monitor** | Track project health, CPU, RAM, time, tools, Git branch, and network strength |
| **Dashboard** | View workspace metrics, health summaries, recent projects, and developer tools |

## What it does

### Project creation

- Initialize projects with Git, `pyproject.toml`, and a virtual environment.
- Select a Python version and starter template.
- Get package recommendations based on project type and idea.
- Install recommendations individually so one unavailable package does not
  block the rest.
- See installed and failed packages when setup needs attention.

### Project workspace

- Discover projects in configured folders and one level of subfolders.
- Pin favorites and keep a list of recent projects.
- Open folders, terminals, or projects in VS Code.
- Run a project's `main.py` with its managed environment.
- View Git branch, changed files, metadata, environment, and test-folder health.
- Run `pytest` and `ruff` with command output shown inside DevSuite.
- Inspect installed packages, add or remove dependencies, and upgrade `uv.lock`.

### Git and environments

- Inspect Git status and recent history from Git Workspace.
- Review the current branch and commit project changes.
- Inspect installed packages in discovered environments.
- Open a project terminal with its virtual environment activated.

### Settings and status

- Configure interface density, neon developer themes (including Neon Sunset),
  sidebar width, and startup page.
- Set the default project location and Python version.
- Configure automatic refresh and project search folders.
- Export and import portable JSON settings.
- See current day and time, CPU and RAM usage, available tools, selected branch,
  project count, refresh time, and a response-time-based network strength meter
  in the status bar.
- Use the dashboard Focus Launchpad to jump back into the most relevant pinned
  or recently used project with one click.

### Help

- Browse a searchable offline manual.
- Read troubleshooting and project guidance.
- Search the internet from Help using DuckDuckGo.
- Fall back to a Google search in the default browser when needed.
- Open official links for `uv`, PyPI, Git, PowerShell, Windows Terminal, and
  VS Code.

## Requirements

- Python **3.14 or newer**
- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- A PyQt5-compatible desktop environment

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

Alternatively, run `deactivate` first and let `uv` select the project's
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

1. Select **New Project** or **Create a New Python Project**.
2. Enter a project name, location, and Python version.
3. Choose a starter template.
4. Select a project type and optionally describe the project idea.
5. Review the package recommendations.
6. Select **Create Project**.

DevSuite uses `uv init`, `uv sync`, and `uv add` during setup. Make sure `uv`
is installed and available on `PATH` before creating a project.

> If an individual package fails to install, setup continues with the remaining
> packages and reports the failed package names afterward.

## Project discovery

By default, DevSuite searches the `Projects` folder in your home directory.
Configure additional locations under **Settings → Project search folders**.
Refresh **My Projects** or **Environments** after changing these locations.

Double-click a pinned or recent project on the dashboard to open its folder.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+H` | Open Help |

## Settings

The scrollable Settings dialog supports:

- Comfortable or Compact interface density
- Developer color themes: Dev Cyan, Monokai, and Nord
- Narrow, Standard, or Wide sidebar width
- Dashboard, My Projects, Environments, or Help as the startup page
- Default project location and Python version
- Automatic refresh and refresh interval
- Project search folders
- Tool availability checks
- JSON settings export and import
- Resetting settings to defaults

## Development

The application entry point is [`main.py`](main.py). Compile-check the source
without launching the GUI:

```powershell
python -m py_compile main.py
```

## Owner links

- [Telegram](https://t.me/Trixie_Misheen)
- [Instagram](https://instagram.com/trixiemisheen)
- [WhatsApp](https://wa.me/254791915925)
- [GitHub](https://github.com/trixiemisheen/)

## License

No license has been specified for this repository yet.
