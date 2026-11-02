# Trixie DevSuite

Trixie DevSuite is a PyQt5 desktop workspace for creating and managing Python
projects. It provides a dashboard for projects and virtual environments,
guided project creation with `uv`, package recommendations, an in-app manual,
and practical project shortcuts.

## Features

- Create Python application projects with Python 3.12, 3.13, or 3.14.
- Initialize projects with Git, a `pyproject.toml`, and a virtual environment.
- Start projects from Basic Python, CLI, PyQt, FastAPI, or data science templates.
- Choose packages from recommendations based on the project type and idea.
- Install recommended packages individually so one unavailable package does not
  prevent the remaining packages from being installed.
- Report installed and failed packages when setup needs attention.
- Discover projects in configured folders and one level of subfolders.
- Pin favorite projects and keep a list of recent projects.
- Open project folders, terminals, or projects in VS Code.
- Run a project's `main.py` with its managed environment.
- Inspect installed packages in discovered environments.
- Configure interface density, default project location, default Python version,
  automatic refresh, and project search folders from Settings.
- Check the availability of Python, `uv`, Git, VS Code, and PowerShell.
- Browse a searchable offline manual with troubleshooting and project guidance.
- Search the internet from the Help page; unavailable results open in the
  default browser automatically.
- Open official installation and package links for `uv`, PyPI, Git, PowerShell,
  Windows Terminal, and VS Code.
- Visit the owner's Telegram, Instagram, WhatsApp, and GitHub links.

## Requirements

- Python 3.14 or newer
- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- PyQt5-compatible desktop environment

The application currently targets Windows, but terminal integration also
supports common Linux and macOS terminal launchers where available.

## Installation

Clone the repository and enter its directory:

```powershell
git clone https://github.com/Trixiemisheen/trixie-devsuite.git
cd trixie-devsuite
```

Create the environment and install the project dependencies with `uv`:

```powershell
uv sync
```

## Run

Start DevSuite from the repository root:

```powershell
uv run python main.py
```

If you are not using `uv`, run the application with a Python 3.14+
interpreter after installing the dependencies declared in
[`pyproject.toml`](pyproject.toml):

```powershell
python main.py
```

## Creating a project

1. Select **New Project** or **Create a New Python Project**.
2. Enter a project name and choose its location and Python version.
3. Choose a starter template.
4. Select a project type and optionally describe the project idea.
5. Review the package recommendations.
6. Select **Create Project**.

DevSuite uses `uv init`, `uv sync`, and `uv add` during setup. Make sure `uv`
is installed and available on `PATH` before creating a project.
If individual package installation fails, DevSuite continues with the remaining
packages and shows the failed package names after setup.

## Project discovery

By default, DevSuite searches the `Projects` folder in your home directory.
Additional search folders can be configured under **Settings → Project search
folders**. The **My Projects** and **Environments** pages can be refreshed
after changing these locations. Double-click a pinned or recent project on the
dashboard to open its folder.

## Help and online search

Open **Help** from the sidebar or press **Ctrl+H**. The Help page includes:

- A searchable manual for project creation, environments, settings, and
  troubleshooting.
- Official resource links for common missing tools and packages.
- Internet search powered by DuckDuckGo.
- Automatic fallback to a Google search in the default browser when an online
  query fails or returns no usable result.

Online search requires an internet connection. The app remains usable offline
for its built-in manual and project management features.

## Settings

The Settings dialog is compact and scrollable. It supports:

- Comfortable or Compact interface density.
- Default project location and Python version.
- Automatic workspace refresh every 30 seconds.
- Project search folders.
- Tool availability checks.
- Resetting settings to defaults.

## Owner links

- Telegram: <https://t.me/Trixie_Misheen>
- Instagram: <https://instagram.com/trixiemisheen>
- WhatsApp: <https://wa.me/254791915925>
- GitHub: <https://github.com/trixiemisheen/>

## Development

The application entry point is [`main.py`](main.py). To check that the source
compiles without launching the GUI:

```powershell
python -m py_compile main.py
```

## License

No license has been specified for this repository yet
