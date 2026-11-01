# Trixie DevSuite

Trixie DevSuite is a desktop workspace for creating and managing Python
projects. It provides a dashboard for projects and virtual environments,
guided project creation with `uv`, and an offline package recommendation
assistant.

## Features

- Create Python application projects with Python 3.12, 3.13, or 3.14.
- Initialize projects with Git, a `pyproject.toml`, and a virtual environment.
- Choose packages from recommendations based on the project type and idea.
- Discover projects in configured folders and one level of subfolders.
- Open project folders, terminals, or projects in VS Code.
- Run a project's `main.py` with its managed environment.
- Inspect installed packages in discovered environments.
- Adjust interface density and project search folders from Settings.

## Requirements

- Python 3.14 or newer
- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- PyQt5-compatible desktop environment

The application currently targets Windows, but the terminal integration also
supports common Linux terminal emulators.

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
3. Select a project type and optionally describe the project idea.
4. Review the package recommendations.
5. Select **Create Project**.

DevSuite uses `uv init`, `uv sync`, and `uv add` during setup. Make sure `uv`
is installed and available on `PATH` before creating a project.

## Project discovery

By default, DevSuite searches the `Projects` folder in your home directory.
Additional search folders can be configured under **Settings → Project search
folders**. The **My Projects** and **Environments** pages can be refreshed
after changing these locations.

## Development

The application entry point is [`main.py`](main.py). To check that the source
compiles without launching the GUI:

```powershell
python -m py_compile main.py
```

## License

No license has been specified for this repository yet.