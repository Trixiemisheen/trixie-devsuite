import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
import webbrowser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

import psutil

from PyQt5.QtCore import (
    QDateTime,
    Qt,
    QSettings,
    QThread,
    QTime,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QScrollArea,
    QPlainTextEdit,
    QProgressBar,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

CREATE_CONSOLE = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
APP_ORG = "TrixieMisheen"
APP_NAME = "DevSuite"
SEARCH_ROOTS_KEY = "project_search_roots"

THEME_COLOR_MAPS = {
    "Dev Cyan": {},
    "Neon Sunset": {
        "#151821": "#160F1B",
        "#11141C": "#100B14",
        "#202633": "#25152B",
        "#293548": "#39203E",
        "#303849": "#55304F",
        "#2A3040": "#43253F",
        "#E6EDF3": "#FFF1F8",
        "#8B949E": "#C79BB5",
        "#00E5FF": "#FF4FD8",
        "#00B8D4": "#FF8A3D",
        "#10141C": "#160F1B",
        "#182B3D": "#351B3F",
        "#24506A": "#74345F",
        "#7DEBFF": "#FFB3E8",
        "#F4FBFF": "#FFF8FC",
        "#A9C6D4": "#D9AFCB",
        "#3B5265": "#704361",
        "#111A24": "#1D1022",
        "#2B3C4B": "#4D2850",
        "#AFC1CC": "#D5B3C9",
        "#1D3444": "#4B2550",
        "#0B687E": "#B72E88",
        "#FFFFFF": "#FFFFFF",
        "#1B222E": "#24142A",
        "#DCEAF1": "#F8DDEB",
        "#146A80": "#8C286C",
        "#164653": "#54244F",
        "#697586": "#9B6C8A",
    },
    "Monokai": {
        "#151821": "#272822",
        "#11141C": "#1E1F1C",
        "#202633": "#3E3D32",
        "#293548": "#49483E",
        "#303849": "#75715E",
        "#2A3040": "#49483E",
        "#E6EDF3": "#F8F8F2",
        "#8B949E": "#A6A39A",
        "#00E5FF": "#A6E22E",
        "#00B8D4": "#66D9EF",
        "#10141C": "#272822",
        "#182B3D": "#30302B",
        "#24506A": "#75715E",
        "#7DEBFF": "#E6DB74",
        "#F4FBFF": "#F8F8F2",
        "#A9C6D4": "#C6C5B9",
        "#3B5265": "#75715E",
        "#111A24": "#1E1F1C",
        "#2B3C4B": "#49483E",
        "#AFC1CC": "#C6C5B9",
        "#1D3444": "#49483E",
        "#0B687E": "#F92672",
        "#FFFFFF": "#F8F8F2",
        "#1B222E": "#30302B",
        "#DCEAF1": "#F8F8F2",
        "#146A80": "#F92672",
        "#164653": "#49483E",
        "#697586": "#A6A39A",
    },
    "Nord": {
        "#151821": "#2E3440",
        "#11141C": "#242933",
        "#202633": "#3B4252",
        "#293548": "#434C5E",
        "#303849": "#4C566A",
        "#2A3040": "#4C566A",
        "#E6EDF3": "#ECEFF4",
        "#8B949E": "#D8DEE9",
        "#00E5FF": "#88C0D0",
        "#00B8D4": "#81A1C1",
        "#10141C": "#2E3440",
        "#182B3D": "#3B4252",
        "#24506A": "#5E81AC",
        "#7DEBFF": "#8FBCBB",
        "#F4FBFF": "#ECEFF4",
        "#A9C6D4": "#D8DEE9",
        "#3B5265": "#4C566A",
        "#111A24": "#242933",
        "#2B3C4B": "#4C566A",
        "#AFC1CC": "#D8DEE9",
        "#1D3444": "#434C5E",
        "#0B687E": "#5E81AC",
        "#FFFFFF": "#ECEFF4",
        "#1B222E": "#3B4252",
        "#DCEAF1": "#E5E9F0",
        "#146A80": "#5E81AC",
        "#164653": "#434C5E",
        "#697586": "#A3BE8C",
    },
}


def apply_theme_stylesheet(stylesheet, theme_name):
    replacements = THEME_COLOR_MAPS.get(theme_name, {})
    if not replacements:
        return stylesheet
    pattern = re.compile("|".join(map(re.escape, replacements)))
    return pattern.sub(lambda match: replacements[match.group()], stylesheet)


def read_project_metadata(project_path):
    """Extract dependency names and script entry-points from pyproject.toml."""
    pyproject = Path(project_path) / "pyproject.toml"
    dependencies = []
    scripts = {}
    try:
        with open(pyproject, "rb") as handle:
            data = tomllib.load(handle)
        project_table = data.get("project", {})
        dependencies = list(project_table.get("dependencies") or [])
        scripts = dict(project_table.get("scripts") or {})
    except (OSError, ValueError):
        pass
    return dependencies, scripts


def git_current_branch(project_path):
    """Return the current git branch name, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(project_path), capture_output=True, text=True,
            timeout=5, check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("DevSuite Settings")
        self.setMinimumSize(440, 480)
        self.resize(520, 620)

        self.setStyleSheet("""
            QDialog {
                background-color: #151821;
                color: #E6EDF3;
            }

            QLabel {
                color: #E6EDF3;
                font-size: 13px;
            }

            QComboBox, QLineEdit, QListWidget {
                background-color: #202633;
                color: #E6EDF3;
                border: 1px solid #303849;
                border-radius: 6px;
                padding: 8px;
            }

            QScrollArea {
                background-color: #151821;
                border: 1px solid #303849;
                border-radius: 8px;
            }

            QScrollBar:vertical {
                background-color: #151821;
                width: 10px;
                margin: 4px;
            }

            QScrollBar::handle:vertical {
                background-color: #3B5265;
                border-radius: 5px;
                min-height: 28px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #00B8D4;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QPushButton {
                background-color: #202633;
                color: #E6EDF3;
                border: none;
                border-radius: 6px;
                padding: 9px 14px;
            }

            QPushButton:hover {
                background-color: #293548;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        settings_layout = QVBoxLayout(scroll_content)
        settings_layout.setSpacing(12)
        settings_layout.setContentsMargins(14, 14, 14, 14)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)

        heading = QLabel("Appearance")
        heading.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #00E5FF;"
        )
        settings_layout.addWidget(heading)

        settings_layout.addWidget(QLabel("Interface density"))

        self.density_combo = QComboBox()
        self.density_combo.addItems(["Comfortable", "Compact"])

        if parent:
            self.density_combo.setCurrentText(parent.interface_density)

        settings_layout.addWidget(self.density_combo)

        settings_layout.addWidget(QLabel("Developer color theme"))
        self.color_theme_combo = QComboBox()
        self.color_theme_combo.addItems(list(THEME_COLOR_MAPS))
        if parent:
            self.color_theme_combo.setCurrentText(parent.color_theme)
        settings_layout.addWidget(self.color_theme_combo)

        settings_layout.addWidget(QLabel("Sidebar width"))
        self.sidebar_width_combo = QComboBox()
        self.sidebar_width_combo.addItems(["Narrow", "Standard", "Wide"])
        if parent:
            self.sidebar_width_combo.setCurrentText(parent.sidebar_width)
        settings_layout.addWidget(self.sidebar_width_combo)

        settings_layout.addWidget(QLabel("Startup page"))
        self.startup_page_combo = QComboBox()
        self.startup_page_combo.addItems(
            ["Dashboard", "My Projects", "Environments", "Help"]
        )
        if parent:
            self.startup_page_combo.setCurrentText(parent.startup_page)
        settings_layout.addWidget(self.startup_page_combo)

        project_heading = QLabel("Project defaults")
        project_heading.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #00E5FF;"
        )
        settings_layout.addWidget(project_heading)

        settings_layout.addWidget(QLabel("Default project location"))
        self.project_location_input = QLineEdit()
        self.project_location_input.setText(
            parent.default_project_location if parent else str(Path.home() / "Projects")
        )
        self.project_location_input.setPlaceholderText("e.g. C:\\Users\\You\\Projects")
        settings_layout.addWidget(self.project_location_input)

        settings_layout.addWidget(QLabel("Default Python version"))
        self.python_version_combo = QComboBox()
        self.python_version_combo.addItems(["3.12", "3.13", "3.14"])
        if parent:
            self.python_version_combo.setCurrentText(parent.default_python_version)
        settings_layout.addWidget(self.python_version_combo)

        self.auto_refresh_checkbox = QCheckBox(
            "Refresh projects automatically every 30 seconds"
        )
        self.auto_refresh_checkbox.setChecked(
            parent.auto_refresh_projects if parent else True
        )
        settings_layout.addWidget(self.auto_refresh_checkbox)

        settings_layout.addWidget(QLabel("Automatic refresh interval"))
        self.refresh_interval_combo = QComboBox()
        self.refresh_interval_combo.addItems(
            ["15 seconds", "30 seconds", "60 seconds"]
        )
        if parent:
            self.refresh_interval_combo.setCurrentText(
                f"{parent.refresh_interval} seconds"
            )
        settings_layout.addWidget(self.refresh_interval_combo)

        # ---- Project search folders ----
        folders_heading = QLabel("Project search folders")
        folders_heading.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #00E5FF;"
        )
        folders_heading.setContentsMargins(0, 12, 0, 0)
        settings_layout.addWidget(folders_heading)

        settings_layout.addWidget(QLabel(
            "DevSuite discovers projects inside these folders "
            "(and one level of subfolders)."
        ))

        self.folders_list = QListWidget()
        self.folders_list.setMinimumHeight(120)
        settings_layout.addWidget(self.folders_list)

        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Add a folder to search for projects…")
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_folder)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected_folder)
        folder_row.addWidget(self.folder_input, 1)
        folder_row.addWidget(add_button)
        folder_row.addWidget(remove_button)
        settings_layout.addLayout(folder_row)

        tools_button = QPushButton("Check tool status")
        tools_button.clicked.connect(self.check_tool_status)
        settings_layout.addWidget(tools_button)

        portability_row = QHBoxLayout()
        export_button = QPushButton("Export settings")
        export_button.clicked.connect(self.export_settings)
        import_button = QPushButton("Import settings")
        import_button.clicked.connect(self.import_settings)
        portability_row.addWidget(export_button)
        portability_row.addWidget(import_button)
        settings_layout.addLayout(portability_row)

        reset_button = QPushButton("Reset settings to defaults")
        reset_button.clicked.connect(self.reset_defaults)
        settings_layout.addWidget(reset_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        if parent:
            for folder in parent.project_search_roots:
                self.folders_list.addItem(folder)

    def add_folder(self):
        folder = self.folder_input.text().strip()
        if not folder:
            folder = QFileDialog.getExistingDirectory(
                self, "Choose a project folder"
            )
            folder = folder.strip() if folder else ""
        if not folder:
            return
        path = str(Path(folder).expanduser().resolve())
        existing = {
            self.folders_list.item(i).text()
            for i in range(self.folders_list.count())
        }
        if path not in existing:
            self.folders_list.addItem(path)
        self.folder_input.clear()

    def remove_selected_folder(self):
        for item in self.folders_list.selectedItems():
            self.folders_list.takeItem(self.folders_list.row(item))

    def get_settings(self):
        return (
            self.density_combo.currentText(),
            self.color_theme_combo.currentText(),
            self.sidebar_width_combo.currentText(),
            self.startup_page_combo.currentText(),
            self.project_location_input.text().strip(),
            self.python_version_combo.currentText(),
            self.auto_refresh_checkbox.isChecked(),
            int(self.refresh_interval_combo.currentText().split()[0]),
            [
                self.folders_list.item(i).text()
                for i in range(self.folders_list.count())
            ],
        )

    def export_settings(self):
        path, _filter = QFileDialog.getSaveFileName(
            self,
            "Export DevSuite settings",
            str(Path.home() / "devsuite-settings.json"),
            "JSON files (*.json)",
        )
        if not path:
            return

        (
            density,
            color_theme,
            sidebar_width,
            startup_page,
            location,
            python_version,
            auto_refresh,
            interval,
            roots,
        ) = (
            self.get_settings()
        )
        data = {
            "format": "trixie-devsuite-settings",
            "version": 1,
            "interface_density": density,
            "color_theme": color_theme,
            "sidebar_width": sidebar_width,
            "startup_page": startup_page,
            "default_project_location": location,
            "default_python_version": python_version,
            "auto_refresh_projects": auto_refresh,
            "refresh_interval": interval,
            "project_search_roots": roots,
        }
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
                handle.write("\n")
        except OSError as error:
            QMessageBox.critical(
                self, "Could not export settings", str(error)
            )
            return
        QMessageBox.information(
            self, "Settings exported", f"Settings were saved to:\n{path}"
        )

    def import_settings(self):
        path, _filter = QFileDialog.getOpenFileName(
            self,
            "Import DevSuite settings",
            str(Path.home()),
            "JSON files (*.json)",
        )
        if not path:
            return

        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            QMessageBox.critical(
                self, "Could not import settings",
                f"The selected file is not valid JSON:\n{error}",
            )
            return

        if not isinstance(data, dict) or data.get(
            "format"
        ) != "trixie-devsuite-settings":
            QMessageBox.warning(
                self, "Unsupported settings file",
                "This file is not a DevSuite settings export.",
            )
            return

        density = data.get("interface_density")
        color_theme = data.get("color_theme", "Dev Cyan")
        sidebar_width = data.get("sidebar_width", "Standard")
        startup_page = data.get("startup_page", "Dashboard")
        location = data.get("default_project_location")
        python_version = data.get("default_python_version")
        auto_refresh = data.get("auto_refresh_projects")
        interval = data.get("refresh_interval")
        roots = data.get("project_search_roots")
        valid = (
            density in {"Comfortable", "Compact"}
            and color_theme in THEME_COLOR_MAPS
            and sidebar_width in {"Narrow", "Standard", "Wide"}
            and startup_page in {"Dashboard", "My Projects", "Environments", "Help"}
            and isinstance(location, str) and bool(location.strip())
            and python_version in {"3.12", "3.13", "3.14"}
            and isinstance(auto_refresh, bool)
            and interval in {15, 30, 60}
            and isinstance(roots, list)
            and all(isinstance(root, str) and root.strip() for root in roots)
        )
        if not valid:
            QMessageBox.warning(
                self, "Invalid settings file",
                "The export is missing settings or contains unsupported values.",
            )
            return

        self.density_combo.setCurrentText(density)
        self.color_theme_combo.setCurrentText(color_theme)
        self.sidebar_width_combo.setCurrentText(sidebar_width)
        self.startup_page_combo.setCurrentText(startup_page)
        self.project_location_input.setText(location.strip())
        self.python_version_combo.setCurrentText(python_version)
        self.auto_refresh_checkbox.setChecked(auto_refresh)
        self.refresh_interval_combo.setCurrentText(f"{interval} seconds")
        self.folders_list.clear()
        for root in roots:
            normalized = str(Path(root).expanduser())
            if normalized not in {
                self.folders_list.item(index).text()
                for index in range(self.folders_list.count())
            }:
                self.folders_list.addItem(normalized)
        QMessageBox.information(
            self, "Settings imported",
            "Settings were loaded into this dialog. Select Save to apply them.",
        )

    def reset_defaults(self):
        self.density_combo.setCurrentText("Comfortable")
        self.color_theme_combo.setCurrentText("Dev Cyan")
        self.sidebar_width_combo.setCurrentText("Standard")
        self.startup_page_combo.setCurrentText("Dashboard")
        self.project_location_input.setText(str(Path.home() / "Projects"))
        self.python_version_combo.setCurrentText("3.13")
        self.auto_refresh_checkbox.setChecked(True)
        self.refresh_interval_combo.setCurrentText("30 seconds")
        self.folders_list.clear()
        self.folders_list.addItem(str(Path.home() / "Projects"))

    def check_tool_status(self):
        tools = {
            "Python": sys.executable,
            "uv": shutil.which("uv"),
            "Git": shutil.which("git"),
            "VS Code": shutil.which("code"),
            "PowerShell": shutil.which("pwsh") or shutil.which("powershell"),
        }
        lines = [
            f"{name}: {'Available — ' + path if path else 'Not found on PATH'}"
            for name, path in tools.items()
        ]
        QMessageBox.information(self, "Tool status", "\n".join(lines))


class NewProjectDialog(QDialog):
    """Step 1 of the New Project flow: name, location, Python version."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a New Python Project — Step 1 of 2")
        self.setMinimumWidth(480)

        self.setStyleSheet("""
            QDialog {
                background-color: #151821;
                color: #E6EDF3;
            }

            QLabel {
                color: #E6EDF3;
            }

            QLineEdit, QComboBox {
                background-color: #202633;
                color: #E6EDF3;
                border: 1px solid #303849;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton {
                background-color: #202633;
                color: #E6EDF3;
                border: none;
                border-radius: 6px;
                padding: 9px 14px;
            }

            QPushButton:hover {
                background-color: #293548;
            }
        """)

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText(
            "e.g. trixie's_project"
        )

        self.project_location = QLineEdit()
        default_location = str(Path.home() / "Projects")
        if parent:
            default_location = parent.default_project_location
        self.project_location.setText(default_location)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_location)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.project_location)
        location_layout.addWidget(browse_button)

        self.python_version = QComboBox()
        self.python_version.addItems(["3.12", "3.13", "3.14"])
        self.python_version.setCurrentText(
            parent.default_python_version if parent else "3.13"
        )

        self.template = QComboBox()
        self.template.addItems([
            "Basic Python application",
            "Command-line tool",
            "PyQt desktop application",
            "FastAPI web API",
            "Data science project",
        ])
        self.template_hint = QLabel()
        self.template_hint.setWordWrap(True)
        self.template_hint.setStyleSheet("color: #8B949E; font-size: 12px;")
        self.template.currentTextChanged.connect(self.update_template_hint)
        self.update_template_hint(self.template.currentText())

        form_layout = QFormLayout()
        form_layout.addRow("Project name:", self.project_name)
        form_layout.addRow("Project location:", location_layout)
        form_layout.addRow("Python version:", self.python_version)
        form_layout.addRow("Project template:", self.template)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        buttons.button(QDialogButtonBox.Ok).setText("Next: Choose Packages")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(form_layout)
        layout.addWidget(self.template_hint)
        layout.addWidget(buttons)

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Project Location",
            self.project_location.text(),
        )

        if folder:
            self.project_location.setText(folder)

    def update_template_hint(self, template_name):
        hints = {
            "Basic Python application": "A small application with a starter main.py and test.",
            "Command-line tool": "Includes argparse-based command-line input handling.",
            "PyQt desktop application": "Starts with a minimal PyQt5 window.",
            "FastAPI web API": "Provides a small FastAPI app ready for uvicorn.",
            "Data science project": "Includes a notebook-friendly starter and test.",
        }
        self.template_hint.setText(hints.get(template_name, ""))

    def get_project_details(self):
        return (
            self.project_name.text().strip(),
            self.project_location.text().strip(),
            self.python_version.currentText(),
            self.template.currentText(),
        )

    def set_packages_summary(self, packages):
        summary = QLabel(f"📦 Will install: {', '.join(packages)}")
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #00E5FF; font-size: 12px;")
        self.layout().insertWidget(self.layout().count() - 1, summary)


PACKAGE_CATALOG = {
    "Desktop application": [
        ("PyQt5", "Build desktop interfaces with windows, buttons, dialogs, and layouts.", "Recommended"),
        ("psutil", "Read system and process information, such as CPU and memory usage.", "Optional"),
        ("requests", "Make HTTP requests to web services.", "Optional"),
        ("Pillow", "Open, resize, and process images.", "Optional"),
    ],
    "Web application / API": [
        ("fastapi", "Build modern Python APIs with type hints and automatic documentation.", "Recommended"),
        ("uvicorn", "Run an ASGI application such as FastAPI.", "Required"),
        ("pydantic", "Validate and structure data using Python models.", "Recommended"),
        ("httpx", "Make HTTP requests to other services.", "Optional"),
    ],
    "AI / machine learning": [
        ("scikit-learn", "Train and evaluate classic machine-learning models.", "Recommended"),
        ("numpy", "Work with numerical arrays and mathematical operations.", "Recommended"),
        ("pandas", "Load, clean, and analyze structured datasets.", "Recommended"),
        ("matplotlib", "Create plots and visualizations.", "Optional"),
        ("torch", "Build and train deep-learning models. This is a large dependency.", "Optional"),
    ],
    "Data science": [
        ("pandas", "Clean, transform, and analyze tabular data.", "Recommended"),
        ("numpy", "Perform numerical calculations and array operations.", "Recommended"),
        ("matplotlib", "Create charts and plots.", "Recommended"),
        ("openpyxl", "Read and write Excel .xlsx files.", "Optional"),
        ("jupyterlab", "Explore data interactively in notebooks.", "Optional"),
    ],
    "Web scraping": [
        ("httpx", "Fetch web pages and call HTTP endpoints.", "Recommended"),
        ("beautifulsoup4", "Parse HTML and extract information from pages.", "Recommended"),
        ("lxml", "Provide a fast HTML/XML parser for supported parsing workflows.", "Optional"),
        ("playwright", "Automate a real browser for JavaScript-heavy sites.", "Optional"),
    ],
    "Automation / scripting": [
        ("psutil", "Inspect processes and system resource usage.", "Recommended"),
        ("rich", "Display readable terminal output, tables, and progress bars.", "Recommended"),
        ("schedule", "Run simple jobs on a recurring schedule.", "Optional"),
        ("httpx", "Connect scripts to HTTP APIs.", "Optional"),
    ],
    "Game development": [
        ("pygame", "Create 2D games with input, audio, graphics, and game loops.", "Recommended"),
        ("numpy", "Useful for numerical and array-based game logic.", "Optional"),
    ],
    "Command-line tool": [
        ("typer", "Build command-line interfaces from Python type hints.", "Recommended"),
        ("rich", "Add formatted terminal output, tables, and progress displays.", "Recommended"),
        ("httpx", "Make HTTP requests from your CLI.", "Optional"),
    ],
}

IDEA_KEYWORDS = {
    "video download": ["yt-dlp", "rich"],
    "youtube": ["yt-dlp", "rich"],
    "download": ["httpx", "rich"],
    "excel": ["pandas", "openpyxl"],
    "spreadsheet": ["pandas", "openpyxl"],
    "image": ["Pillow"],
    "api": ["httpx", "pydantic"],
    "website": ["httpx", "beautifulsoup4"],
    "browser": ["playwright"],
    "system monitor": ["psutil", "matplotlib"],
    "machine learning": ["scikit-learn", "pandas"],
    "deep learning": ["torch", "numpy"],
}

EXTRA_PACKAGES = {
    "yt-dlp": ("Download media from supported websites using yt-dlp's command-line library.", "Optional"),
}

PROJECT_TEMPLATES = {
    "Basic Python application": {
        "main.py": 'def main():\n    print("Hello from your new project!")\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/test_main.py": "def test_project_starts():\n    assert True\n",
    },
    "Command-line tool": {
        "main.py": 'import argparse\n\n\ndef main():\n    parser = argparse.ArgumentParser(description="A new command-line tool.")\n    parser.add_argument("name", nargs="?", default="world")\n    args = parser.parse_args()\n    print(f"Hello, {args.name}!")\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/test_main.py": "def test_cli_template():\n    assert True\n",
    },
    "PyQt desktop application": {
        "main.py": 'import sys\n\nfrom PyQt5.QtWidgets import QApplication, QLabel\n\n\ndef main():\n    app = QApplication(sys.argv)\n    window = QLabel("Your PyQt application starts here.")\n    window.setWindowTitle("New PyQt Project")\n    window.resize(420, 120)\n    window.show()\n    sys.exit(app.exec_())\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/test_main.py": "def test_pyqt_template():\n    assert True\n",
    },
    "FastAPI web API": {
        "main.py": 'from fastapi import FastAPI\n\napp = FastAPI(title="New API")\n\n\n@app.get("/")\ndef read_root():\n    return {"message": "Hello from your new API"}\n',
        "tests/test_main.py": "def test_api_template():\n    assert True\n",
    },
    "Data science project": {
        "main.py": 'def main():\n    print("Start your data exploration here.")\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/test_main.py": "def test_data_science_template():\n    assert True\n",
    },
}

HELP_TOPICS = {
    "Welcome": (
        "Trixie DevSuite Help\n\n"
        "DevSuite helps you create and manage Python projects with uv. "
        "Use the sidebar to create a project, browse discovered projects, "
        "inspect environments, or change settings.\n\n"
        "Keyboard shortcut\n"
        "Press Ctrl+H at any time to open this manual."
    ),
    "Create a project": (
        "Create a Python project\n\n"
        "1. Select New Project.\n"
        "2. Enter a project name and choose a parent folder.\n"
        "3. Select the Python version.\n"
        "4. Review the offline package recommendations.\n"
        "5. Confirm the setup.\n\n"
        "DevSuite uses uv to initialize the project, create its virtual "
        "environment, install selected packages, and initialize Git."
    ),
    "My Projects": (
        "My Projects\n\n"
        "Projects are discovered from Settings → Project search folders. "
        "DevSuite checks each configured folder and its immediate subfolders "
        "for pyproject.toml files.\n\n"
        "Select a project to open its folder, launch VS Code, open a terminal, "
        "or run its main.py file."
    ),
    "Environments": (
        "Python Environments\n\n"
        "DevSuite detects .venv and venv folders inside discovered projects. "
        "Use Open Project Terminal to work in that project, or Inspect Packages "
        "to view packages through uv.\n\n"
        "DevSuite never deletes or modifies an existing environment while "
        "refreshing this page."
    ),
    "Settings": (
        "Settings\n\n"
        "Interface density changes dashboard spacing. Project search folders "
        "control where DevSuite looks for projects."
    ),
    "Troubleshooting": (
        "Troubleshooting\n\n"
        "• uv unavailable: install uv and ensure it is on PATH.\n"
        "• Git unavailable: install Git and ensure git is on PATH.\n"
        "• No projects found: add the correct parent folder in Settings.\n"
        "• No environment found: run `uv sync` in the project folder.\n"
        "• Project will not run: make sure the project contains main.py.\n"
        "• Terminal unavailable: install PowerShell or a supported terminal.\n\n"
        "The setup progress window shows command output and failure details."
    ),
    "About & Owner": (
        "About Trixie DevSuite\n\n"
        "Trixie DevSuite is an offline-first Python workspace built with "
        "Python and PyQt5. Package recommendations are rule-based and do not "
        "send your project idea to an online service.\n\n"
        "Created by Trixie Misheen\n"
        "Use the buttons below to visit the official social and project links.\n\n"
        "Version: 1.0.1"
    ),
}

HELP_RESOURCES = {
    "Troubleshooting": [
        ("Install uv", "https://docs.astral.sh/uv/getting-started/installation/"),
        ("Find packages on PyPI", "https://pypi.org/"),
        ("Install Git", "https://git-scm.com/downloads"),
        ("Install PowerShell", "https://learn.microsoft.com/powershell/scripting/install/installing-powershell"),
        ("Install Windows Terminal", "https://learn.microsoft.com/windows/terminal/install"),
        ("Install VS Code", "https://code.visualstudio.com/download"),
    ],
    "About & Owner": [
        ("Telegram", "https://t.me/Trixie_Misheen"),
        ("Instagram", "https://instagram.com/trixiemisheen"),
        ("WhatsApp", "https://wa.me/254791915925"),
        ("GitHub", "https://github.com/trixiemisheen/"),
    ],
}


class SearchResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture = None
        self._snippet_index = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag == "a" and "result__a" in classes:
            self._current = {
                "title": "",
                "url": self.clean_url(attributes.get("href", "")),
                "snippet": "",
            }
            self._capture = "title"
        elif self.results and "result__snippet" in classes:
            self._capture = "snippet"
            self._snippet_index = len(self.results) - 1

    def handle_data(self, data):
        if self._current and self._capture == "title":
            self._current[self._capture] += data
        elif self._capture == "snippet" and self._snippet_index is not None:
            self.results[self._snippet_index]["snippet"] += data

    def handle_endtag(self, tag):
        if self._current and tag == "a" and self._capture == "title":
            self.results.append(self._current)
            self._current = None
            self._capture = None
        elif self._capture == "snippet":
            self._capture = None
            self._snippet_index = None

    @staticmethod
    def clean_url(url):
        parsed = urlparse(url)
        if parsed.path.startswith("/l/"):
            query = parse_qs(parsed.query)
            return unquote(query.get("uddg", [url])[0])
        return url


class WebSearchWorker(QThread):
    completed = pyqtSignal(object)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            url = "https://html.duckduckgo.com/html/?" + urlencode(
                {"q": self.query}
            )
            request = Request(
                url,
                headers={"User-Agent": "TrixieDevSuite/1.0.1"},
            )
            with urlopen(request, timeout=12) as response:
                html = response.read().decode("utf-8", errors="replace")
            parser = SearchResultsParser()
            parser.feed(html)
            self.completed.emit({"success": True, "results": parser.results[:8]})
        except (OSError, ValueError) as error:
            self.completed.emit({"success": False, "error": str(error)})


class ConnectivityWorker(QThread):
    completed = pyqtSignal(object)

    def run(self):
        started = time.perf_counter()
        try:
            request = Request(
                "https://connectivitycheck.gstatic.com/generate_204",
                method="HEAD",
                headers={"User-Agent": "TrixieDevSuite/1.0.1"},
            )
            with urlopen(request, timeout=5):
                pass
        except (OSError, ValueError):
            self.completed.emit({"online": False})
        else:
            self.completed.emit({
                "online": True,
                "latency_ms": round((time.perf_counter() - started) * 1000),
            })


class DiagnosticsWorker(QThread):
    completed = pyqtSignal(object)

    def __init__(self, project=None):
        super().__init__()
        self.project = Path(project) if project else None

    def run(self):
        results = []
        for label, command in (("Python", [sys.executable, "--version"]),
                               ("Git", ["git", "--version"]),
                               ("uv", ["uv", "--version"])):
            executable = shutil.which(command[0])
            if not executable:
                results.append((label, "CRITICAL", "Not found on PATH"))
                continue
            try:
                check = subprocess.run([executable, *command[1:]], capture_output=True,
                                       text=True, timeout=5, check=False)
                detail = (check.stdout or check.stderr).strip()
                results.append((label, "HEALTHY" if check.returncode == 0 else "WARNING",
                                detail or f"Exited with code {check.returncode}"))
            except (OSError, subprocess.TimeoutExpired) as error:
                results.append((label, "WARNING", str(error)))
        if self.project:
            has_main = (self.project / "main.py").is_file()
            results.append(("Workspace · main.py", "HEALTHY" if has_main else "WARNING",
                            str(self.project) if has_main else "No boot file found in workspace"))
            has_environment = (self.project / ".venv").is_dir() or (self.project / "venv").is_dir()
            results.append(("Project environment", "HEALTHY" if has_environment else "WARNING",
                            "Virtual environment found" if has_environment else "No .venv or venv folder"))
        self.completed.emit(results)


class SyncWorker(QThread):
    output = pyqtSignal(str)
    completed = pyqtSignal(int)

    def __init__(self, project):
        super().__init__()
        self.project = Path(project)

    def run(self):
        uv = shutil.which("uv")
        if not uv:
            self.output.emit("ERROR: uv is not available on PATH. Install uv, then rerun diagnostics.")
            self.completed.emit(127)
            return
        try:
            process = subprocess.Popen([uv, "sync"], cwd=str(self.project),
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding="utf-8", errors="replace",
                                       bufsize=1)
            for line in process.stdout:
                self.output.emit(line.rstrip())
            self.completed.emit(process.wait())
        except OSError as error:
            self.output.emit(f"ERROR: {error}")
            self.completed.emit(1)


class PackageAdvisorDialog(QDialog):
    """Step 2 of the New Project flow: rule-based offline package picks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSuite™ Package Advisor — Step 2 of 2")
        self.resize(760, 700)
        self.setMinimumSize(650, 560)
        self.package_checks = {}

        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #151821;
                color: #E6EDF3;
                font-family: Segoe UI;
            }
            QLabel { color: #E6EDF3; }
            QComboBox, QLineEdit, QPlainTextEdit {
                background-color: #202633;
                color: #E6EDF3;
                border: 1px solid #303849;
                border-radius: 6px;
                padding: 8px;
            }
            QCheckBox { color: #E6EDF3; spacing: 8px; }
            QPushButton {
                background-color: #202633;
                color: #E6EDF3;
                border: none;
                border-radius: 6px;
                padding: 10px 14px;
            }
            QPushButton:hover { background-color: #293548; color: #00E5FF; }
            QPushButton#primary {
                background-color: #00B8D4;
                color: #10141C;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        heading = QLabel("🧠  Intelligent Package Advisor")
        heading.setStyleSheet("font-size: 23px; font-weight: bold; color: #00E5FF;")
        layout.addWidget(heading)

        intro = QLabel(
            "Choose a project type and describe your idea. DevSuite™ will suggest "
            "packages using its built-in offline rules. You stay in control."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.project_type = QComboBox()
        self.project_type.addItems(list(PACKAGE_CATALOG.keys()))
        self.idea_input = QLineEdit()
        self.idea_input.setPlaceholderText(
            "e.g. Download videos, show progress, and choose quality"
        )
        form.addRow("What are you building?", self.project_type)
        form.addRow("Describe your idea:", self.idea_input)
        layout.addLayout(form)

        refresh_button = QPushButton("Refresh Recommendations")
        refresh_button.clicked.connect(self.refresh_recommendations)
        layout.addWidget(refresh_button)

        self.recommendation_summary = QLabel()
        self.recommendation_summary.setStyleSheet("color: #00E5FF; font-weight: bold;")
        layout.addWidget(self.recommendation_summary)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #303849; border-radius: 8px; }")
        self.recommendation_container = QWidget()
        self.recommendation_layout = QVBoxLayout(self.recommendation_container)
        self.recommendation_layout.setContentsMargins(12, 12, 12, 12)
        self.recommendation_layout.setSpacing(10)
        self.scroll_area.setWidget(self.recommendation_container)
        layout.addWidget(self.scroll_area, 1)

        note = QLabel(
            "Required = core to the suggested setup. Recommended = useful for most projects "
            "of this type. Optional = only install it if you need that feature."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #8B949E; font-size: 11px;")
        layout.addWidget(note)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.skip_button = buttons.addButton(
            "Skip — No Packages", QDialogButtonBox.ActionRole
        )
        self.continue_button = buttons.addButton(
            "Create Project", QDialogButtonBox.AcceptRole
        )
        self.continue_button.setObjectName("primary")
        buttons.rejected.connect(self.reject)
        self.skip_button.clicked.connect(self.accept)
        self.continue_button.clicked.connect(self.accept)
        layout.addWidget(buttons)

        self.project_type.currentTextChanged.connect(self.refresh_recommendations)
        self.idea_input.returnPressed.connect(self.refresh_recommendations)
        self.refresh_recommendations()

    def refresh_recommendations(self, *_):
        while self.recommendation_layout.count():
            item = self.recommendation_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.package_checks.clear()

        project_type = self.project_type.currentText()
        packages = list(PACKAGE_CATALOG[project_type])
        idea = self.idea_input.text().lower()

        existing = {name.lower() for name, _, _ in packages}
        for keyword, names in IDEA_KEYWORDS.items():
            if keyword in idea:
                for name in names:
                    if name.lower() not in existing:
                        details, level = EXTRA_PACKAGES.get(
                            name, (f"Useful for the '{keyword}' part of your idea.", "Optional")
                        )
                        packages.append((name, details, level))
                        existing.add(name.lower())

        self.recommendation_summary.setText(
            f"{len(packages)} suggestions for {project_type}"
        )

        for name, description, level in packages:
            row = QFrame()
            row.setStyleSheet(
                "QFrame { background-color: #202633; border: 1px solid #303849; "
                "border-radius: 7px; }"
            )
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(12, 9, 12, 9)
            checkbox = QCheckBox(f"{name}   •   {level}")
            checkbox.setStyleSheet("font-weight: bold; border: none;")
            checkbox.setChecked(level in ("Required", "Recommended"))
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet(
                "color: #AAB4C3; font-size: 12px; border: none;"
            )
            row_layout.addWidget(checkbox)
            row_layout.addWidget(description_label)
            self.recommendation_layout.addWidget(row)
            self.package_checks[name] = checkbox

        self.recommendation_layout.addStretch()

    def selected_packages(self):
        return [
            name for name, checkbox in self.package_checks.items()
            if checkbox.isChecked()
        ]


class ProjectSetupWorker(QThread):
    """Run project setup off the UI thread and stream command output."""
    progress = pyqtSignal(str)
    log_line = pyqtSignal(str)
    completed = pyqtSignal(object)

    def __init__(
        self, uv_executable, project_directory, project_name, packages,
        python_version, template_name,
    ):
        super().__init__()
        self.uv_executable = uv_executable
        self.project_directory = Path(project_directory)
        self.project_name = project_name
        self.packages = list(packages)
        self.python_version = python_version
        self.template_name = template_name
        self.installed_packages = []
        self.failed_packages = []
        self._process = None
        self._cancel = False

    def cancel(self):
        """Request cancellation and kill the running subprocess, if any."""
        self._cancel = True
        if self._process and self._process.poll() is None:
            self._process.kill()

    def run_command(self, label, command, timeout_seconds):
        if self._cancel:
            raise RuntimeError("Setup was cancelled by the user.")

        self.progress.emit(label)
        self.log_line.emit(f"\n> {' '.join(str(part) for part in command)}\n")
        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
        try:
            if self._process.stdout is not None:
                for line in self._process.stdout:
                    self.log_line.emit(line.rstrip())
            return_code = self._process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
            raise TimeoutError(f"{label} exceeded the {timeout_seconds}-second time limit.")
        finally:
            self._process = None

        if return_code != 0:
            raise RuntimeError(f"{label} failed with exit code {return_code}.")

    def run(self):
        try:
            self.progress.emit("Preparing project folder…")
            self.project_directory.parent.mkdir(parents=True, exist_ok=True)
            self.run_command(
                "Step 1 of 3: Initializing project and Git repository…",
                [self.uv_executable, "init", "--app", "--python", self.python_version,
                 "--vcs", "git", "--no-workspace", "--name", self.project_name,
                 str(self.project_directory)],
                120,
            )
            self.write_template_files()
            if self._cancel:
                raise RuntimeError("Setup was cancelled by the user.")
            if self.packages:
                for package in self.packages:
                    if self._cancel:
                        raise RuntimeError("Setup was cancelled by the user.")
                    try:
                        self.run_command(
                            f"Step 2 of 3: Adding {package}…",
                            [self.uv_executable, "add", "--directory",
                             str(self.project_directory), package],
                            600,
                        )
                        self.installed_packages.append(package)
                    except (RuntimeError, TimeoutError) as error:
                        self.failed_packages.append(package)
                        self.log_line.emit(
                            f"WARNING: Could not add {package}: {error}"
                        )

            if self._cancel:
                raise RuntimeError("Setup was cancelled by the user.")
            self.run_command(
                "Step 3 of 3: Creating the virtual environment and syncing dependencies…",
                [self.uv_executable, "sync", "--directory", str(self.project_directory)],
                300,
            )
            if self.failed_packages:
                failed = ", ".join(self.failed_packages)
                self.completed.emit({
                    "success": False,
                    "error": f"These packages could not be installed: {failed}",
                    "packages": self.installed_packages,
                    "failed_packages": self.failed_packages,
                })
            else:
                self.completed.emit({
                    "success": True,
                    "packages": self.installed_packages,
                    "failed_packages": [],
                })
        except Exception as error:
            self.log_line.emit(f"\nERROR: {error}")
            self.completed.emit(
                {
                    "success": False,
                    "error": str(error),
                    "packages": self.installed_packages,
                    "failed_packages": self.failed_packages,
                }
            )

    def write_template_files(self):
        template_files = PROJECT_TEMPLATES[self.template_name]
        for relative_path, content in template_files.items():
            path = self.project_directory / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        readme = self.project_directory / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {self.project_name}\n\n"
                f"Created with the {self.template_name} template.\n\n"
                "Run the project with `uv run python main.py`.\n",
                encoding="utf-8",
            )
        self.log_line.emit(f"Template created: {self.template_name}")


class ProjectSetupProgressDialog(QDialog):
    def __init__(self, project_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creating Your Project")
        self.setMinimumSize(560, 390)
        layout = QVBoxLayout(self)
        title = QLabel(f"🚀 Building <b>{project_name}</b>")
        title.setWordWrap(True)
        layout.addWidget(title)
        self.status_label = QLabel("Just wait a bit as we are getting things ready…")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Live setup output"))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("uv output will appear here while your project is being created…")
        layout.addWidget(self.output, 1)

        self.cancel_button = QPushButton("Cancel setup")
        self.cancel_button.clicked.connect(self.request_cancel)
        layout.addWidget(self.cancel_button)

        note = QLabel("Keep this window open while DevSuite™ prepares the project.")
        note.setWordWrap(True)
        layout.addWidget(note)

    def request_cancel(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Cancelling… stopping the running command.")
            self.worker.cancel()

    def closeEvent(self, event):
        if hasattr(self, "worker") and self.worker.isRunning():
            event.ignore()
            self.request_cancel()
            return
        super().closeEvent(event)


class DevSuiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trixie DevSuite™")
        self.setMinimumSize(960, 640)
        self.set_initial_window_geometry()

        self.settings = QSettings(APP_ORG, APP_NAME)
        self.interface_density = self.settings.value(
            "interface_density", "Comfortable", str
        )
        self.color_theme = self.settings.value(
            "color_theme", "Dev Cyan", str
        )
        self.sidebar_width = self.settings.value(
            "sidebar_width", "Standard", str
        )
        self.startup_page = self.settings.value(
            "startup_page", "Dashboard", str
        )
        self.project_search_roots = self.load_search_roots()
        self.recommended_packages = []
        self.favorite_projects = self.load_project_paths("favorite_projects")
        self.recent_projects = self.load_project_paths("recent_projects")
        self.default_project_location = self.settings.value(
            "default_project_location", str(Path.home() / "Projects"), str
        )
        self.default_python_version = self.settings.value(
            "default_python_version", "3.13", str
        )
        self.auto_refresh_projects = self.settings.value(
            "auto_refresh_projects", True, bool
        )
        self.refresh_interval = self.settings.value(
            "refresh_interval", 30, int
        )
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(self.refresh_interval * 1000)
        self.refresh_timer.timeout.connect(self.refresh_workspace_views)
        if self.auto_refresh_projects:
            self.refresh_timer.start()

        self.base_stylesheet = """
            QMainWindow, QWidget {
                background-color: #151821;
                color: #E6EDF3;
                font-family: Segoe UI;
            }

            QLabel#brand {
                color: #00E5FF;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 4px;
                min-width: 0;
            }

            QLabel#section {
                color: #8B949E;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton {
                background-color: #202633;
                color: #E6EDF3;
                border: none;
                border-radius: 7px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #293548;
                color: #00E5FF;
            }

            QFrame#sidebar {
                background-color: #11141C;
                border-right: 1px solid #2A3040;
            }

            QFrame#card {
                background-color: #202633;
                border: 1px solid #303849;
                border-radius: 12px;
            }

            QFrame#dashboard_hero {
                background-color: #182B3D;
                border: 1px solid #24506A;
                border-radius: 14px;
            }

            QLabel#dashboard_kicker {
                color: #7DEBFF;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#dashboard_title {
                color: #F4FBFF;
                font-size: 25px;
                font-weight: bold;
            }

            QLabel#dashboard_body {
                color: #A9C6D4;
                font-size: 13px;
            }

            QLabel#dashboard_section {
                color: #8B949E;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#dashboard_snapshot {
                color: #DCEAF1;
                font-size: 13px;
                padding: 8px;
            }

            QFrame#focus_launchpad {
                background-color: #21152D;
                border: 1px solid #6A3F72;
                border-radius: 12px;
            }

            QLabel#focus_kicker {
                color: #FF9DE6;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#focus_title {
                color: #FFF4FC;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#focus_body {
                color: #D7B5D0;
                font-size: 13px;
            }

            QLabel#card_title {
                color: #8B949E;
                font-size: 13px;
            }

            QLabel#card_value {
                color: #00E5FF;
                font-size: 25px;
                font-weight: bold;
            }

            QLabel#heading {
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #8B949E;
                font-size: 14px;
            }

            QPushButton#primary {
                background-color: #00B8D4;
                color: #10141C;
                font-weight: bold;
                text-align: center;
            }

            QPushButton#primary:hover {
                background-color: #00E5FF;
            }

            QFrame#help_hero {
                background-color: #182B3D;
                border: 1px solid #24506A;
                border-radius: 14px;
            }

            QLabel#help_kicker {
                color: #7DEBFF;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#help_title {
                color: #F4FBFF;
                font-size: 25px;
                font-weight: bold;
            }

            QLabel#help_subtitle {
                color: #A9C6D4;
                font-size: 13px;
            }

            QLineEdit#help_search {
                background-color: #202633;
                border: 1px solid #3B5265;
                border-radius: 9px;
                color: #F4FBFF;
                padding: 11px 14px;
                selection-background-color: #146A80;
            }

            QLineEdit#help_search:focus {
                border: 1px solid #00B8D4;
            }

            QPushButton#help_search_button {
                background-color: #00B8D4;
                border: 1px solid #00E5FF;
                color: #10141C;
                font-weight: bold;
                padding: 10px 16px;
                text-align: center;
            }

            QPushButton#help_search_button:hover {
                background-color: #00E5FF;
            }

            QListWidget#help_topics {
                background-color: #111A24;
                border: 1px solid #2B3C4B;
                border-radius: 10px;
                padding: 8px;
                outline: none;
            }

            QListWidget#help_topics::item {
                color: #AFC1CC;
                border-radius: 7px;
                padding: 11px 12px;
                margin: 2px 0;
            }

            QListWidget#help_topics::item:hover {
                background-color: #1D3444;
                color: #F4FBFF;
            }

            QListWidget#help_topics::item:selected {
                background-color: #0B687E;
                color: #FFFFFF;
                font-weight: bold;
            }

            QPlainTextEdit#help_article {
                background-color: #1B222E;
                border: 1px solid #303849;
                border-radius: 10px;
                color: #DCEAF1;
                font-size: 14px;
                line-height: 150%;
                padding: 18px;
                selection-background-color: #146A80;
            }

            QLabel#help_resources_title {
                color: #8B949E;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton#help_link {
                background-color: #202633;
                border: 1px solid #3B5265;
                color: #7DEBFF;
                padding: 8px 10px;
                text-align: center;
            }

            QPushButton#help_link:hover {
                background-color: #164653;
                border-color: #00B8D4;
                color: #FFFFFF;
            }
        """
        self.setStyleSheet(
            apply_theme_stylesheet(self.base_stylesheet, self.color_theme)
        )

        central = QWidget()
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet(
            apply_theme_stylesheet(
                "QStatusBar { background-color: #11141C; color: #8B949E; "
            "border-top: 1px solid #2A3040; }"
            "QStatusBar::item { border: none; }",
                self.color_theme,
            )
        )
        self.status_page_label = QLabel("Page: Dashboard")
        self.status_project_label = QLabel("Projects: 0")
        self.status_tools_label = QLabel("Tools: checking...")
        self.status_branch_label = QLabel("Branch: none selected")
        self.status_datetime_label = QLabel("Loading date and time...")
        self.status_usage_label = QLabel("CPU: --%  RAM: --%")
        self.status_online_label = QLabel("Network: ▱▱▱▱")
        self.status_refresh_label = QLabel("Last refresh: never")
        for label in (
            self.status_page_label,
            self.status_project_label,
            self.status_tools_label,
            self.status_branch_label,
            self.status_datetime_label,
            self.status_usage_label,
            self.status_online_label,
            self.status_refresh_label,
        ):
            label.setStyleSheet("padding: 0 8px; color: #8B949E;")
            self.statusBar().addPermanentWidget(label)

        self.status_clock_timer = QTimer(self)
        self.status_clock_timer.timeout.connect(self.update_status_clock)
        self.status_clock_timer.start(1000)
        self.status_usage_timer = QTimer(self)
        self.status_usage_timer.timeout.connect(self.update_status_usage)
        self.status_usage_timer.start(2000)
        self.connectivity_timer = QTimer(self)
        self.connectivity_timer.timeout.connect(self.check_connectivity)
        self.connectivity_timer.start(30000)

        self.root_layout = QHBoxLayout(central)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 18, 12, 18)
        sidebar_layout.setSpacing(8)

        brand = QLabel("TRIXIE DEVSUITE™")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)

        section = QLabel("WORKSPACE")
        section.setObjectName("section")
        sidebar_layout.addWidget(section)

        dashboard_nav = self.add_nav_button(sidebar_layout, "⌂   Dashboard")
        dashboard_nav.clicked.connect(self.show_dashboard)

        new_project_nav = self.add_nav_button(sidebar_layout, "+   New Project")
        new_project_nav.clicked.connect(self.create_new_project)

        projects_nav = self.add_nav_button(sidebar_layout, "▣   My Projects")
        projects_nav.clicked.connect(self.show_projects)

        environments_nav = self.add_nav_button(sidebar_layout, "⚙   Environments")
        environments_nav.clicked.connect(self.show_environments)

        help_nav = self.add_nav_button(sidebar_layout, "?   Help")
        help_nav.clicked.connect(self.show_help)

        sidebar_layout.addStretch()

        settings_button = self.add_nav_button(sidebar_layout, "⚙   Settings")
        settings_button.clicked.connect(self.open_settings)

        version = QLabel("Trixie DevSuite • V 1.0.1")
        version.setStyleSheet(
            "color: #697586; font-size: 10px; padding: 8px;"
        )
        sidebar_layout.addWidget(version)

        self.root_layout.addWidget(self.sidebar)

        # Main dashboard
        content = QWidget()

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(32, 28, 32, 28)
        self.content_layout.setSpacing(20)

        hero = QFrame()
        hero.setObjectName("dashboard_hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 18, 22, 18)
        hero_layout.setSpacing(6)

        kicker = QLabel("TRIXIE DEVSUITE  /  WORKSPACE OVERVIEW")
        kicker.setObjectName("dashboard_kicker")
        hero_layout.addWidget(kicker)

        heading = QLabel("Build with less friction.")
        heading.setObjectName("dashboard_title")
        hero_layout.addWidget(heading)

        subtitle = QLabel(
            "Create, inspect, and launch your Python projects from one focused workspace."
        )
        subtitle.setObjectName("dashboard_body")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(subtitle)

        hero_actions = QHBoxLayout()
        hero_actions.setSpacing(10)
        new_project_button = QPushButton("+  New Project")
        new_project_button.setObjectName("primary")
        new_project_button.clicked.connect(self.create_new_project)
        hero_actions.addWidget(new_project_button)
        hero_actions.addStretch()
        hero_layout.addLayout(hero_actions)
        self.content_layout.addWidget(hero)

        stats_heading = QLabel("WORKSPACE SNAPSHOT")
        stats_heading.setObjectName("dashboard_section")
        self.content_layout.addWidget(stats_heading)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.total_projects_card = self.create_card("TOTAL PROJECTS", "0")
        self.environments_card = self.create_card("ENVIRONMENTS", "0")
        self.python_version_card = self.create_card(
            "PYTHON VERSION", sys.version.split()[0]
        )
        self.healthy_projects_card = self.create_card("HEALTHY PROJECTS", "0")
        stats_layout.addWidget(self.total_projects_card)
        stats_layout.addWidget(self.environments_card)
        stats_layout.addWidget(self.python_version_card)
        self.favorites_card = self.create_card("PINNED PROJECTS", "0")
        stats_layout.addWidget(self.favorites_card)
        stats_layout.addWidget(self.healthy_projects_card)

        self.content_layout.addLayout(stats_layout)

        actions_heading = QLabel("QUICK TOOLS")
        actions_heading.setObjectName("dashboard_section")
        self.content_layout.addWidget(actions_heading)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        folder_button = QPushButton("▣  Open Project Root")
        folder_button.clicked.connect(self.open_project_root)
        actions_layout.addWidget(folder_button)
        tools_button = QPushButton("✓  Check Toolchain")
        tools_button.clicked.connect(self.show_toolchain_status)
        actions_layout.addWidget(tools_button)
        terminal_button = QPushButton(">_  Workspace Terminal")
        terminal_button.clicked.connect(self.open_terminal)
        actions_layout.addWidget(terminal_button)
        refresh_button = QPushButton("↻  Scan Workspace")
        refresh_button.clicked.connect(self.refresh_workspace_views)
        actions_layout.addWidget(refresh_button)
        self.content_layout.addLayout(actions_layout)

        snapshot_card = QFrame()
        snapshot_card.setObjectName("card")
        snapshot_layout = QVBoxLayout(snapshot_card)
        snapshot_layout.setContentsMargins(14, 10, 14, 10)
        snapshot_title = QLabel("WORKSPACE NOTE")
        snapshot_title.setObjectName("card_title")
        snapshot_layout.addWidget(snapshot_title)
        self.dashboard_snapshot = QLabel(
            "Refresh the workspace to see the latest project health summary."
        )
        self.dashboard_snapshot.setObjectName("dashboard_snapshot")
        self.dashboard_snapshot.setWordWrap(True)
        snapshot_layout.addWidget(self.dashboard_snapshot)
        self.content_layout.addWidget(snapshot_card)

        project_lists = QHBoxLayout()
        self.favorites_list = self.build_project_shortlist(
            "PINNED PROJECTS", self.favorite_projects
        )
        self.recent_list = self.build_project_shortlist(
            "RECENT PROJECTS", self.recent_projects
        )
        project_lists.addWidget(self.favorites_list)
        project_lists.addWidget(self.recent_list)
        self.content_layout.addLayout(project_lists)

        launchpad = QFrame()
        launchpad.setObjectName("focus_launchpad")
        launchpad_layout = QVBoxLayout(launchpad)
        launchpad_layout.setContentsMargins(16, 13, 16, 13)
        launchpad_layout.setSpacing(6)
        launchpad_kicker = QLabel("FOCUS LAUNCHPAD")
        launchpad_kicker.setObjectName("focus_kicker")
        launchpad_layout.addWidget(launchpad_kicker)
        self.focus_title = QLabel("Ready when you are.")
        self.focus_title.setObjectName("focus_title")
        launchpad_layout.addWidget(self.focus_title)
        self.focus_body = QLabel(
            "Pin or open a project to make it your one-click launch target."
        )
        self.focus_body.setObjectName("focus_body")
        self.focus_body.setWordWrap(True)
        launchpad_layout.addWidget(self.focus_body)
        focus_actions = QHBoxLayout()
        focus_open_button = QPushButton("Open Folder")
        focus_open_button.clicked.connect(self.open_focus_project_folder)
        focus_actions.addWidget(focus_open_button)
        focus_editor_button = QPushButton("Open in VS Code")
        focus_editor_button.clicked.connect(self.open_focus_project_in_editor)
        focus_actions.addWidget(focus_editor_button)
        focus_terminal_button = QPushButton(">_  Terminal")
        focus_terminal_button.clicked.connect(self.open_focus_project_terminal)
        focus_actions.addWidget(focus_terminal_button)
        focus_actions.addStretch()
        launchpad_layout.addLayout(focus_actions)
        self.content_layout.addWidget(launchpad)

        self.content_layout.addStretch()

        footer = QLabel("TRIXIE MISHEEN™  •  BUILT WITH PYTHON & PyQt5")
        footer.setStyleSheet(
            "color: #697586; font-size: 11px; padding: 8px;"
        )
        self.content_layout.addWidget(footer)

        self.pages = QStackedWidget()
        self.dashboard_scroll = QScrollArea()
        self.dashboard_scroll.setWidgetResizable(True)
        self.dashboard_scroll.setFrameShape(QFrame.NoFrame)
        self.dashboard_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dashboard_scroll.setWidget(content)
        self.pages.addWidget(self.dashboard_scroll)
        self.projects_page = self.build_projects_page()
        self.environments_page = self.build_environments_page()
        self.help_page = self.build_help_page()
        self.pages.addWidget(self.projects_page)
        self.pages.addWidget(self.environments_page)
        self.pages.addWidget(self.help_page)
        self.root_layout.addWidget(self.pages, 1)

        self.help_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self.help_shortcut.activated.connect(self.show_help)

        self.refresh_workspace_views()
        self.update_responsive_layout()
        self.apply_startup_page()
        self.update_status_clock()
        self.update_status_usage()
        self.check_connectivity()

    # ---- Settings helpers ----

    def set_initial_window_geometry(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1200, 760)
            return

        available = screen.availableGeometry()
        width = min(1400, max(960, int(available.width() * 0.90)))
        height = min(900, max(640, int(available.height() * 0.88)))
        self.resize(
            min(width, available.width()),
            min(height, available.height()),
        )
        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        self.move(frame.topLeft())

    def load_search_roots(self):
        raw = self.settings.value(SEARCH_ROOTS_KEY)
        if isinstance(raw, str):
            raw = [raw]
        roots = [str(item) for item in (raw or []) if str(item).strip()]
        default_root = str(Path.home() / "Projects")
        if default_root not in roots:
            roots.append(default_root)
        return roots

    def save_search_roots(self):
        self.settings.setValue(SEARCH_ROOTS_KEY, self.project_search_roots)

    def load_project_paths(self, key):
        stored = self.settings.value(key, [])
        if isinstance(stored, str):
            stored = [stored]
        return [
            str(Path(path))
            for path in (stored or [])
            if str(path).strip() and Path(path).is_dir()
        ]

    def save_project_paths(self):
        self.settings.setValue("favorite_projects", self.favorite_projects)
        self.settings.setValue("recent_projects", self.recent_projects)

    def build_project_shortlist(self, title, paths):
        container = QFrame()
        container.setObjectName("card")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 12, 14, 12)
        label = QLabel(title)
        label.setObjectName("card_title")
        layout.addWidget(label)
        project_list = QListWidget()
        project_list.setMaximumHeight(120)
        project_list.setStyleSheet(
            "QListWidget { background-color: #151821; border: none; }"
            "QListWidget::item { padding: 6px; }"
            "QListWidget::item:selected { background-color: #164653; }"
        )
        for path in paths:
            item = QListWidgetItem(Path(path).name)
            item.setData(256, path)
            project_list.addItem(item)
        if not paths:
            empty = QListWidgetItem("No projects yet")
            empty.setFlags(empty.flags() & ~Qt.ItemIsSelectable)
            project_list.addItem(empty)
        project_list.itemDoubleClicked.connect(self.open_shortlist_project)
        layout.addWidget(project_list)
        container.project_list = project_list
        return container

    def refresh_project_shortlists(self):
        for widget, paths in (
            (self.favorites_list, self.favorite_projects),
            (self.recent_list, self.recent_projects),
        ):
            widget.project_list.clear()
            for path in paths:
                item = QListWidgetItem(Path(path).name)
                item.setData(256, path)
                widget.project_list.addItem(item)
            if not paths:
                empty = QListWidgetItem("No projects yet")
                empty.setFlags(empty.flags() & ~Qt.ItemIsSelectable)
                widget.project_list.addItem(empty)
        self.update_focus_launchpad()

    def focus_project(self):
        candidates = self.favorite_projects + self.recent_projects
        for path in candidates:
            project = Path(path)
            if project.is_dir():
                return project
        return None

    def update_focus_launchpad(self):
        project = self.focus_project()
        if project is None:
            self.focus_title.setText("Ready when you are.")
            self.focus_body.setText(
                "Pin or open a project to make it your one-click launch target."
            )
            return
        self.focus_title.setText(f"Continue with {project.name}")
        self.focus_body.setText(
            f"{project}  •  Your fastest route back into the work."
        )

    def open_focus_project_folder(self):
        project = self.focus_project()
        if project is None:
            self.show_projects()
            return
        self.record_recent_project(project)
        self.open_path_in_file_manager(project)

    def open_focus_project_in_editor(self):
        project = self.focus_project()
        if project is None:
            self.show_projects()
            return
        self.record_recent_project(project)
        self.open_project_in_editor(project)

    def open_focus_project_terminal(self):
        project = self.focus_project()
        if project is None:
            self.show_projects()
            return
        self.record_recent_project(project)
        self.open_project_terminal(project)

    def open_shortlist_project(self, item):
        project = Path(item.data(256))
        if project.is_dir():
            self.record_recent_project(project)
            self.open_path_in_file_manager(project)
        else:
            self.refresh_workspace_views()

    def record_recent_project(self, project):
        path = str(Path(project).resolve())
        self.recent_projects = [
            existing for existing in self.recent_projects if existing != path
        ]
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:8]
        self.save_project_paths()
        self.refresh_project_shortlists()

    def toggle_selected_favorite(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        path = str(project.resolve())
        if path in self.favorite_projects:
            self.favorite_projects.remove(path)
        else:
            self.favorite_projects.insert(0, path)
            self.favorite_projects = self.favorite_projects[:8]
        self.save_project_paths()
        self.refresh_project_shortlists()

    def build_projects_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        heading = QLabel("My Projects")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        help_button = QPushButton("?  Help with projects")
        help_button.clicked.connect(lambda: self.show_help("My Projects"))
        layout.addWidget(help_button)

        subtitle = QLabel(
            "Projects discovered in your configured search folders "
            "(Settings → Project search folders)."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        filter_row = QHBoxLayout()
        self.project_filter_input = QLineEdit()
        self.project_filter_input.setPlaceholderText(
            "Search projects by name or path..."
        )
        self.project_filter_input.textChanged.connect(
            self.refresh_workspace_views
        )
        filter_row.addWidget(self.project_filter_input, 1)
        self.project_sort_combo = QComboBox()
        self.project_sort_combo.addItems(
            ["Name (A-Z)", "Name (Z-A)", "Recently used", "Pinned first"]
        )
        self.project_sort_combo.currentTextChanged.connect(
            self.refresh_workspace_views
        )
        filter_row.addWidget(self.project_sort_combo)
        layout.addLayout(filter_row)

        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet(
            "QListWidget { background-color: #202633; border: 1px solid #303849; "
            "border-radius: 8px; padding: 6px; }"
            "QListWidget::item { padding: 10px; border-bottom: 1px solid #303849; }"
            "QListWidget::item:selected { background-color: #164653; color: #FFFFFF; }"
        )
        self.projects_list.currentItemChanged.connect(
            lambda current, _previous: self.update_project_details(current)
        )
        layout.addWidget(self.projects_list, 1)

        self.project_details = QLabel(
            "Select a project to view its health and development details."
        )
        self.project_details.setObjectName("subtitle")
        self.project_details.setWordWrap(True)
        layout.addWidget(self.project_details)

        actions = QHBoxLayout()
        refresh_button = QPushButton("↻  Refresh")
        refresh_button.clicked.connect(self.refresh_workspace_views)
        actions.addWidget(refresh_button)

        open_folder_button = QPushButton("Open Folder")
        open_folder_button.clicked.connect(self.open_selected_project_folder)
        actions.addWidget(open_folder_button)

        open_editor_button = QPushButton("Open in VS Code")
        open_editor_button.clicked.connect(self.open_selected_project_in_editor)
        actions.addWidget(open_editor_button)

        terminal_button = QPushButton(">_  Project Terminal")
        terminal_button.clicked.connect(self.open_selected_project_terminal)
        actions.addWidget(terminal_button)

        run_button = QPushButton("▶  Run main.py")
        run_button.clicked.connect(self.run_selected_project)
        actions.addWidget(run_button)
        test_button = QPushButton("✓  Run Tests")
        test_button.clicked.connect(self.test_selected_project)
        actions.addWidget(test_button)
        lint_button = QPushButton("✓  Run Lint")
        lint_button.clicked.connect(self.lint_selected_project)
        actions.addWidget(lint_button)
        dependencies_button = QPushButton("📦  Dependencies")
        dependencies_button.clicked.connect(self.manage_selected_dependencies)
        actions.addWidget(dependencies_button)
        git_button = QPushButton(" Git  Git Workspace")
        git_button.clicked.connect(self.open_git_workspace)
        actions.addWidget(git_button)
        pin_button = QPushButton("☆  Pin / Unpin")
        pin_button.clicked.connect(self.toggle_selected_favorite)
        actions.addWidget(pin_button)
        layout.addLayout(actions)
        return page

    def build_environments_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        heading = QLabel("Python Environments")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        help_button = QPushButton("?  Help with environments")
        help_button.clicked.connect(lambda: self.show_help("Environments"))
        layout.addWidget(help_button)

        subtitle = QLabel(
            "Virtual environments discovered in the projects DevSuite™ knows about. "
            "DevSuite will inspect them without deleting or modifying them."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.environments_list = QListWidget()
        self.environments_list.setStyleSheet(
            "QListWidget { background-color: #202633; border: 1px solid #303849; "
            "border-radius: 8px; padding: 6px; }"
            "QListWidget::item { padding: 10px; border-bottom: 1px solid #303849; }"
            "QListWidget::item:selected { background-color: #164653; color: #FFFFFF; }"
        )
        layout.addWidget(self.environments_list, 1)

        actions = QHBoxLayout()
        refresh_button = QPushButton("↻  Refresh")
        refresh_button.clicked.connect(self.refresh_workspace_views)
        actions.addWidget(refresh_button)

        terminal_button = QPushButton(">_  Open Project Terminal")
        terminal_button.clicked.connect(self.open_selected_environment_terminal)
        actions.addWidget(terminal_button)

        packages_button = QPushButton("Inspect Packages")
        packages_button.clicked.connect(self.inspect_selected_environment)
        actions.addWidget(packages_button)
        folder_button = QPushButton("Open Project Folder")
        folder_button.clicked.connect(self.open_selected_environment_folder)
        actions.addWidget(folder_button)
        layout.addLayout(actions)
        return page

    def build_help_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("help_hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 16, 20, 16)
        hero_layout.setSpacing(5)

        kicker = QLabel("TRIXIE DEVSUITE  /  KNOWLEDGE BASE")
        kicker.setObjectName("help_kicker")
        hero_layout.addWidget(kicker)

        heading = QLabel("Help & Manual")
        heading.setObjectName("help_title")
        hero_layout.addWidget(heading)

        subtitle = QLabel(
            "Everything you need to create, discover, and run Python projects."
        )
        subtitle.setObjectName("help_subtitle")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(subtitle)
        layout.addWidget(hero)

        search_row = QHBoxLayout()
        search = QLineEdit()
        search.setObjectName("help_search")
        search.setPlaceholderText("Search the manual, e.g. how to activate uv")
        search_button = QPushButton("Search")
        search_button.setObjectName("help_search_button")
        search_row.addWidget(search, 1)
        search_row.addWidget(search_button)
        layout.addLayout(search_row)

        content_layout = QHBoxLayout()
        self.help_topics_list = QListWidget()
        self.help_topics_list.setObjectName("help_topics")
        self.help_topics_list.setMinimumWidth(190)
        self.help_article = QPlainTextEdit()
        self.help_article.setObjectName("help_article")
        self.help_article.setReadOnly(True)
        self.help_article.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        content_layout.addWidget(self.help_topics_list)
        self.help_content_stack = QStackedWidget()
        self.help_content_stack.addWidget(self.help_article)
        diagnostics_page = QWidget()
        diagnostics_layout = QVBoxLayout(diagnostics_page)
        diagnostics_layout.setContentsMargins(12, 8, 4, 4)
        diagnostics_layout.setSpacing(10)
        diagnostics_header = QHBoxLayout()
        self.diagnostics_status = QLabel("Diagnostics have not been run yet")
        self.diagnostics_status.setStyleSheet("font-size: 16px; font-weight: bold;")
        diagnostics_header.addWidget(self.diagnostics_status, 1)
        self.diagnostics_run_button = QPushButton("Run Full Diagnostics")
        self.diagnostics_run_button.clicked.connect(self.run_diagnostics)
        diagnostics_header.addWidget(self.diagnostics_run_button)
        diagnostics_layout.addLayout(diagnostics_header)
        diagnostics_layout.addWidget(QLabel("DEPENDENCY SYSTEM CHECKS"))
        self.diagnostics_results = QPlainTextEdit()
        self.diagnostics_results.setObjectName("help_article")
        self.diagnostics_results.setReadOnly(True)
        self.diagnostics_results.setMaximumHeight(150)
        diagnostics_layout.addWidget(self.diagnostics_results)
        action_row = QHBoxLayout()
        self.diagnostics_project_label = QLabel("Select a project to run setup sync.")
        action_row.addWidget(self.diagnostics_project_label, 1)
        self.diagnostics_sync_button = QPushButton("Setup Sync · uv sync")
        self.diagnostics_sync_button.clicked.connect(self.run_diagnostics_sync)
        action_row.addWidget(self.diagnostics_sync_button)
        diagnostics_layout.addLayout(action_row)
        diagnostics_layout.addWidget(QLabel("LIVE LOG & TERMINAL OUTPUT"))
        self.diagnostics_log = QPlainTextEdit()
        self.diagnostics_log.setObjectName("help_article")
        self.diagnostics_log.setReadOnly(True)
        self.diagnostics_log.setPlaceholderText("Diagnostic and setup output will appear here.")
        diagnostics_layout.addWidget(self.diagnostics_log, 1)
        self.help_content_stack.addWidget(diagnostics_page)
        content_layout.addWidget(self.help_content_stack, 1)
        layout.addLayout(content_layout, 1)

        self.help_resources_title = QLabel("ONLINE RESOURCES")
        self.help_resources_title.setObjectName("help_resources_title")
        layout.addWidget(self.help_resources_title)
        self.help_resources_layout = QHBoxLayout()
        self.help_resources_layout.setSpacing(8)
        layout.addLayout(self.help_resources_layout)

        for topic in HELP_TOPICS:
            self.help_topics_list.addItem(topic)

        def display_topic(item):
            if item is not None:
                topic = item.text()
                troubleshooting = topic == "Troubleshooting"
                self.help_content_stack.setCurrentIndex(1 if troubleshooting else 0)
                if troubleshooting:
                    selected = self.projects_list.currentItem()
                    project = selected.data(256) if selected else None
                    self.diagnostics_project_label.setText(
                        f"Selected project: {project}" if project else "Select a project to run setup sync."
                    )
                    self.run_diagnostics()
                else:
                    self.help_article.setPlainText(HELP_TOPICS[topic])
                self.update_help_resources(topic)

        def filter_topics():
            query = search.text().casefold().strip()
            first_match = None
            for index in range(self.help_topics_list.count()):
                item = self.help_topics_list.item(index)
                topic = item.text()
                matches = (
                    not query
                    or query in topic.casefold()
                    or query in HELP_TOPICS[topic].casefold()
                )
                item.setHidden(not matches)
                if matches and first_match is None:
                    first_match = item
            if first_match is not None:
                self.help_topics_list.setCurrentItem(first_match)
            else:
                self.help_article.setPlainText(
                    f'No help topics matched "{search.text().strip()}".\n\n'
                    "Try searching for uv, Git, projects, environments, "
                    "templates, or settings."
                )
                self.update_help_resources("")

        search_button.clicked.connect(self.search_help_online)
        search.returnPressed.connect(self.search_help_online)
        self.help_search_input = search
        self.help_search_button = search_button
        self.help_topics_list.currentItemChanged.connect(
            lambda current, _previous: display_topic(current)
        )
        self.help_topics_list.setCurrentRow(0)
        self.update_help_resources("Welcome")
        return page

    def update_help_resources(self, topic):
        while self.help_resources_layout.count():
            item = self.help_resources_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        resources = HELP_RESOURCES.get(topic, [])
        self.help_resources_title.setVisible(bool(resources))
        for label, url in resources:
            button = QPushButton(label)
            button.setObjectName("help_link")
            button.clicked.connect(
                lambda _checked=False, target=url: webbrowser.open(target)
            )
            self.help_resources_layout.addWidget(button)
        self.help_resources_layout.addStretch()

    def run_diagnostics(self):
        selected = getattr(self, "projects_list", None)
        item = selected.currentItem() if selected else None
        project = item.data(256) if item else None
        self.diagnostics_run_button.setEnabled(False)
        self.diagnostics_status.setText("Scanning system…")
        self.diagnostics_log.appendPlainText(
            f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] Starting system diagnostics"
        )
        self.diagnostics_worker = DiagnosticsWorker(project)
        def display(results):
            rows = []
            healthy = 0
            for name, status, detail in results:
                icon = {"HEALTHY": "🟢", "WARNING": "🟡", "CRITICAL": "🔴"}[status]
                rows.append(f"{icon}  {name}: {detail}")
                healthy += status == "HEALTHY"
            self.diagnostics_results.setPlainText("\n".join(rows))
            issues = len(results) - healthy
            self.diagnostics_status.setText(
                "All checks healthy" if not issues else f"{issues} issue{'s' if issues != 1 else ''} detected"
            )
            for name, status, detail in results:
                self.diagnostics_log.appendPlainText(
                    f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] {status}: {name} — {detail}"
                )
        self.diagnostics_worker.completed.connect(display)
        self.diagnostics_worker.finished.connect(
            lambda: self.diagnostics_run_button.setEnabled(True)
        )
        self.diagnostics_worker.start()

    def run_diagnostics_sync(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        if not (project / "pyproject.toml").is_file():
            QMessageBox.warning(
                self, "Cannot sync this project",
                "This folder has no pyproject.toml file for uv to sync."
            )
            return
        if not shutil.which("uv"):
            QMessageBox.warning(
                self, "uv unavailable",
                "Install uv from the Troubleshooting online resources, then rerun setup sync."
            )
            return
        self.diagnostics_sync_button.setEnabled(False)
        self.diagnostics_log.appendPlainText(
            f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] Running uv sync in {project}"
        )
        self.diagnostics_sync_worker = SyncWorker(project)
        self.diagnostics_sync_worker.output.connect(self.diagnostics_log.appendPlainText)
        def sync_finished(code):
            state = "completed successfully" if code == 0 else f"failed with exit code {code}"
            self.diagnostics_log.appendPlainText(
                f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] uv sync {state}"
            )
            self.diagnostics_sync_button.setEnabled(True)
            self.run_diagnostics()
        self.diagnostics_sync_worker.completed.connect(sync_finished)
        self.diagnostics_sync_worker.start()

    def search_help_online(self):
        query = self.help_search_input.text().strip()
        if not query:
            self.help_article.setPlainText(
                "Enter a question or topic to search the internet.\n\n"
                "For example: how to activate a Python virtual environment"
            )
            return

        self.help_search_button.setEnabled(False)
        self.help_search_button.setText("Searching...")
        self.help_article.setPlainText(
            f'Searching the internet for "{query}"...\n\n'
            "Please wait while results are fetched."
        )
        self.help_search_worker = WebSearchWorker(query)
        self.help_search_worker.completed.connect(self.display_web_results)
        self.help_search_worker.finished.connect(
            lambda: self.help_search_button.setEnabled(True)
        )
        self.help_search_worker.finished.connect(
            lambda: self.help_search_button.setText("Search")
        )
        self.help_search_worker.start()

    def open_external_help_search(self, query=None):
        query = (query or self.help_search_input.text()).strip()
        if not query:
            return
        url = "https://www.google.com/search?" + urlencode({"q": query})
        webbrowser.open(url)
        self.help_article.setPlainText(
            f'No in-app results were available for "{query}".\n\n'
            "The search was opened in your default browser.\n\n"
            f"Search URL:\n{url}"
        )

    def display_web_results(self, result):
        if not result.get("success"):
            query = self.help_search_input.text().strip()
            self.open_external_help_search(query)
            self.help_article.append(
                "\nIn-app search error:\n"
                f"{result.get('error', 'Unknown network error')}"
            )
            return

        results = result.get("results", [])
        if not results:
            self.open_external_help_search()
            return

        lines = [
            f"Online results for: {self.help_search_input.text().strip()}",
            "Fetched from DuckDuckGo. Double-click a resource button below "
            "for official installation pages.\n",
        ]
        for index, item in enumerate(results, 1):
            lines.extend([
                f"{index}. {item['title'].strip()}",
                item["snippet"].strip() or "No summary available.",
                item["url"],
                "",
            ])
        self.help_article.setPlainText("\n".join(lines))
        self.update_help_resources("")

    def discover_projects(self):
        """Discover projects inside the configured search roots (one level deep)."""
        projects = {}
        for root_text in self.project_search_roots:
            root = Path(root_text).expanduser()
            try:
                if not root.is_dir():
                    continue
                candidates = [root]
                candidates.extend(
                    child for child in root.iterdir()
                    if child.is_dir() and child.name not in {
                        ".git", ".venv", "venv", "__pycache__", "node_modules"
                    }
                )
                for candidate in candidates:
                    try:
                        if (candidate / "pyproject.toml").is_file():
                            projects[str(candidate.resolve()).casefold()] = candidate.resolve()
                    except OSError:
                        continue
            except OSError:
                continue
        return sorted(projects.values(), key=lambda path: path.name.casefold())

    @staticmethod
    def environment_python(project):
        for folder_name in (".venv", "venv"):
            scripts = "Scripts" if os.name == "nt" else "bin"
            executable = "python.exe" if os.name == "nt" else "python"
            candidate = project / folder_name / scripts / executable
            if candidate.is_file():
                return candidate
        return None

    def update_status_clock(self):
        now = QDateTime.currentDateTime()
        self.status_datetime_label.setText(
            now.toString("ddd, dd MMM yyyy  •  HH:mm:ss")
        )

    def update_status_usage(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        self.status_usage_label.setText(
            f"CPU: {cpu_percent:.0f}%  RAM: {memory_percent:.0f}%"
        )
        self.status_usage_label.setToolTip(
            "Current system resource usage. Updated every 2 seconds."
        )

    def check_connectivity(self):
        worker = getattr(self, "connectivity_worker", None)
        if worker is not None and worker.isRunning():
            return
        self.status_online_label.setText("Online: checking...")
        self.connectivity_worker = ConnectivityWorker()
        self.connectivity_worker.completed.connect(
            self.update_connectivity_status
        )
        self.connectivity_worker.finished.connect(self.clear_connectivity_worker)
        self.connectivity_worker.start()

    def clear_connectivity_worker(self):
        worker = self.connectivity_worker
        self.connectivity_worker = None
        if worker is not None:
            worker.deleteLater()

    def update_connectivity_status(self, result):
        if not result.get("online"):
            self.status_online_label.setText("Network: ▱▱▱▱ offline")
            self.status_online_label.setToolTip(
                "No internet response received. The check timed out or failed."
            )
            return

        latency_ms = result["latency_ms"]
        if latency_ms < 100:
            bars = "▰▰▰▰"
            strength = "Excellent"
        elif latency_ms < 250:
            bars = "▰▰▰▱"
            strength = "Good"
        elif latency_ms < 600:
            bars = "▰▰▱▱"
            strength = "Fair"
        else:
            bars = "▰▱▱▱"
            strength = "Weak"
        self.status_online_label.setText(f"Network: {bars}")
        self.status_online_label.setToolTip(
            f"{strength} connection • response time {latency_ms} ms"
        )

    def refresh_workspace_views(self, *_):
        projects = self.discover_projects()
        search_text = self.project_filter_input.text().strip().casefold()
        if search_text:
            projects = [
                project for project in projects
                if search_text in project.name.casefold()
                or search_text in str(project).casefold()
            ]
        sort_mode = self.project_sort_combo.currentText()
        if sort_mode == "Name (Z-A)":
            projects.sort(key=lambda path: path.name.casefold(), reverse=True)
        elif sort_mode == "Recently used":
            recent_order = {
                path: index for index, path in enumerate(self.recent_projects)
            }
            projects.sort(
                key=lambda path: recent_order.get(str(path), len(recent_order))
            )
        elif sort_mode == "Pinned first":
            projects.sort(
                key=lambda path: (
                    str(path) not in self.favorite_projects,
                    path.name.casefold(),
                )
            )
        self.favorite_projects = [
            path for path in self.favorite_projects if Path(path).is_dir()
        ]
        self.recent_projects = [
            path for path in self.recent_projects if Path(path).is_dir()
        ]
        self.save_project_paths()
        self.refresh_project_shortlists()
        self.projects_list.clear()
        self.environments_list.clear()
        self.project_details.setText(
            "Select a project to view its health and development details."
        )
        environment_count = 0

        for project in projects:
            item = QListWidgetItem(f"{project.name}\n{project}")
            item.setData(256, str(project))
            self.projects_list.addItem(item)

            python_executable = self.environment_python(project)
            if python_executable:
                environment_count += 1
                try:
                    result = subprocess.run(
                        [str(python_executable), "--version"],
                        capture_output=True, text=True, timeout=5, check=False,
                    )
                    version = (result.stdout or result.stderr).strip()
                    if result.returncode != 0 or not version:
                        version = "Python version unavailable"
                except (OSError, subprocess.TimeoutExpired):
                    version = "Python version unavailable"

                env_item = QListWidgetItem(
                    f"{project.name}  •  {version}\n{python_executable}"
                )
                env_item.setData(256, str(project))
                self.environments_list.addItem(env_item)

        self.total_projects_card.value_label.setText(str(len(projects)))
        self.environments_card.value_label.setText(str(environment_count))
        self.favorites_card.value_label.setText(str(len(self.favorite_projects)))
        healthy_projects = sum(
            (project / "pyproject.toml").is_file()
            and (project / "main.py").is_file()
            and self.environment_python(project) is not None
            for project in projects
        )
        self.healthy_projects_card.value_label.setText(str(healthy_projects))
        if projects:
            environment_summary = (
                f"{environment_count} of {len(projects)} projects have a virtual environment"
            )
            health_summary = (
                f"{healthy_projects} ready for development"
                if healthy_projects
                else "No projects are fully ready yet"
            )
            pinned_summary = (
                f"{len(self.favorite_projects)} pinned"
                if self.favorite_projects
                else "No pinned projects yet"
            )
            self.dashboard_snapshot.setText(
                f"{health_summary} • {environment_summary} • {pinned_summary}. "
                "Use My Projects to inspect health, run checks, or open a project."
            )
        else:
            self.dashboard_snapshot.setText(
                "No projects discovered yet. Create a project or add a search "
                "folder in Settings to get started."
            )

        if not projects:
            empty = QListWidgetItem(
                "Developer! No projects found yet. Create one with + New Project."
            )
            empty.setFlags(empty.flags() & ~Qt.ItemIsSelectable)
            self.projects_list.addItem(empty)

        if not environment_count:
            empty = QListWidgetItem(
                "No .venv or venv environments found in discovered projects."
            )
            empty.setFlags(empty.flags() & ~Qt.ItemIsSelectable)
            self.environments_list.addItem(empty)
        tool_paths = {
            "uv": shutil.which("uv"),
            "git": shutil.which("git"),
            "VS Code": shutil.which("code"),
            "PowerShell": (
                shutil.which("pwsh") or shutil.which("powershell")
                if os.name == "nt"
                else shutil.which("x-terminal-emulator")
            ),
        }
        tool_count = sum(path is not None for path in tool_paths.values())
        missing_tools = [
            name for name, path in tool_paths.items() if path is None
        ]
        self.status_project_label.setText(f"Projects: {len(projects)}")
        self.status_tools_label.setText(f"Tools: {tool_count}/4")
        self.status_tools_label.setToolTip(
            "All core tools available."
            if not missing_tools
            else "Missing: " + ", ".join(missing_tools)
        )
        self.status_refresh_label.setText(
            f"Last refresh: {QTime.currentTime().toString('HH:mm:ss')}"
        )
        self.status_branch_label.setText("Branch: none selected")
        self.statusBar().showMessage("Workspace refreshed", 3000)

    def show_dashboard(self):
        self.pages.setCurrentIndex(0)
        self.status_page_label.setText("Page: Dashboard")
        self.refresh_workspace_views()

    def show_projects(self):
        self.pages.setCurrentIndex(1)
        self.status_page_label.setText("Page: My Projects")
        self.refresh_workspace_views()

    def show_environments(self):
        self.pages.setCurrentIndex(2)
        self.status_page_label.setText("Page: Environments")
        self.refresh_workspace_views()

    def show_help(self, topic="Welcome"):
        self.pages.setCurrentIndex(3)
        self.status_page_label.setText("Page: Help")
        for index in range(self.help_topics_list.count()):
            item = self.help_topics_list.item(index)
            if item.text() == topic:
                self.help_topics_list.setCurrentItem(item)
                return
        self.help_topics_list.setCurrentRow(0)

    def update_project_details(self, item):
        if item is None or not item.data(256):
            self.project_details.setText(
                "Select a project to view its health and development details."
            )
            self.status_branch_label.setText("Branch: none selected")
            return

        project = Path(item.data(256))
        dependencies, scripts = read_project_metadata(project)
        branch = git_current_branch(project) or "Not a Git repository"
        self.status_branch_label.setText(f"Branch: {branch}")
        self.statusBar().showMessage(
            f"Selected project: {project.name}", 3000
        )
        try:
            git_status = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(project), capture_output=True, text=True,
                timeout=5, check=False,
            )
            changed_files = len(git_status.stdout.splitlines())
        except (OSError, subprocess.TimeoutExpired):
            changed_files = 0

        checks = [
            ("pyproject.toml", (project / "pyproject.toml").is_file()),
            ("main.py", (project / "main.py").is_file()),
            ("virtual environment", self.environment_python(project) is not None),
            ("tests", (project / "tests").is_dir()),
        ]
        health = "  ".join(
            f"{'✓' if available else '!' } {name}"
            for name, available in checks
        )
        script_text = ", ".join(scripts) if scripts else "none"
        self.project_details.setText(
            f"<b>{project.name}</b>  •  branch: {branch}  •  "
            f"changed files: {changed_files}<br>"
            f"{health}<br>"
            f"Dependencies: {len(dependencies)}  •  Scripts: {script_text}"
        )

    def selected_project_path(self, list_widget):
        item = list_widget.currentItem()
        if item is None:
            QMessageBox.information(self, "Select a project", "Please select a project first.")
            return None
        value = item.data(256)
        if not value:
            QMessageBox.information(self, "No project selected", "Select a project from the list.")
            return None
        project = Path(value)
        if not project.is_dir():
            QMessageBox.warning(self, "Project not found", f"This folder no longer exists:\n{project}")
            self.refresh_workspace_views()
            return None
        self.record_recent_project(project)
        return project

    def open_path_in_file_manager(self, path):
        try:
            if os.name == "nt":
                subprocess.Popen(["explorer", str(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError as error:
            QMessageBox.critical(self, "Could not open folder", str(error))

    def open_selected_project_folder(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            self.open_path_in_file_manager(project)

    def open_selected_project_in_editor(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        self.open_project_in_editor(project)

    def open_project_in_editor(self, project):
        editor = shutil.which("code")
        if editor is None:
            QMessageBox.warning(
                self, "VS Code unavailable",
                "The 'code' command was not found on PATH.\n"
                "Install VS Code and enable 'Add to PATH' during setup.",
            )
            return
        try:
            subprocess.Popen([editor, str(project)])
        except OSError as error:
            QMessageBox.critical(self, "Could not open editor", str(error))

    def launch_terminal(self, args, working_directory):
        try:
            subprocess.Popen(
                args,
                cwd=str(working_directory),
                creationflags=CREATE_CONSOLE,
            )
        except OSError as error:
            QMessageBox.critical(self, "Could not open terminal", str(error))

    def open_project_terminal(self, project, activate_environment=False):
        if os.name == "nt":
            terminal = shutil.which("pwsh") or shutil.which("powershell")
            if not terminal:
                QMessageBox.warning(
                    self, "Terminal unavailable",
                    "PowerShell could not be found on PATH."
                )
                return
            command = ""
            python_executable = self.environment_python(project)
            if activate_environment and python_executable:
                activation_script = python_executable.parent / "Activate.ps1"
                command = f'& "{activation_script}"'
            args = (
                [terminal, "-NoExit", "-Command", command]
                if command else [terminal, "-NoExit"]
            )
        else:
            terminal = (
                shutil.which("x-terminal-emulator")
                or shutil.which("gnome-terminal")
                or shutil.which("konsole")
                or shutil.which("xterm")
            )
            if not terminal:
                QMessageBox.warning(
                    self, "Terminal unavailable",
                    "No terminal emulator was found on this system."
                )
                return
            args = [terminal]

        self.launch_terminal(args, project)

    def open_selected_project_terminal(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            self.open_project_terminal(project)

    def open_selected_environment_terminal(self):
        project = self.selected_project_path(self.environments_list)
        if project:
            self.open_project_terminal(project, activate_environment=True)

    def open_selected_environment_folder(self):
        project = self.selected_project_path(self.environments_list)
        if project:
            self.open_path_in_file_manager(project)

    def run_selected_project(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        main_file = project / "main.py"
        if not main_file.is_file():
            QMessageBox.information(
                self, "main.py not found",
                f"No main.py file was found in this project:\n{project}",
            )
            return

        # Prefer uv run — it handles the project context and lockfile correctly.
        uv_path = shutil.which("uv")
        if uv_path and (project / "pyproject.toml").is_file():
            try:
                subprocess.Popen(
                    [uv_path, "run", "python", str(main_file)],
                    cwd=str(project),
                    creationflags=CREATE_CONSOLE,
                )
                return
            except OSError as error:
                QMessageBox.critical(self, "Could not run project", str(error))
                return

        python_executable = self.environment_python(project)
        if python_executable is None:
            QMessageBox.warning(
                self, "Environment not found",
                "This project has no .venv or venv Python environment. Run 'uv sync' "
                "in its folder before launching it.",
            )
            return
        try:
            subprocess.Popen(
                [str(python_executable), str(main_file)],
                cwd=str(project),
                creationflags=CREATE_CONSOLE,
            )
        except OSError as error:
            QMessageBox.critical(self, "Could not run project", str(error))

    def run_project_check(self, project, label, arguments):
        """Run a project command and display its output without hiding failures."""
        uv_path = shutil.which("uv")
        if uv_path and (project / "pyproject.toml").is_file():
            command = [uv_path, "run", *arguments]
        else:
            python_executable = self.environment_python(project)
            if python_executable is None:
                QMessageBox.warning(
                    self, "Environment not found",
                    "This project has no uv project or virtual environment. "
                    "Create one before running project checks.",
                )
                return
            command = [str(python_executable), "-m", *arguments]

        try:
            result = subprocess.run(
                command,
                cwd=str(project),
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired:
            QMessageBox.warning(
                self, f"{label} timed out",
                f"{label} exceeded the five-minute time limit.",
            )
            return
        except OSError as error:
            QMessageBox.critical(self, f"Could not run {label.lower()}", str(error))
            return

        output = (result.stdout or "") + (result.stderr or "")
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{label} • {project.name}")
        dialog.resize(760, 520)
        layout = QVBoxLayout(dialog)
        status = QLabel(
            f"{label} {'passed' if result.returncode == 0 else 'failed'} "
            f"(exit code {result.returncode})"
        )
        layout.addWidget(status)
        output_view = QPlainTextEdit()
        output_view.setReadOnly(True)
        output_view.setPlainText(output.strip() or "No output was produced.")
        layout.addWidget(output_view, 1)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def test_selected_project(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            self.run_project_check(project, "Tests", ["pytest"])

    def lint_selected_project(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            self.run_project_check(project, "Lint", ["ruff", "check", "."])

    def manage_selected_dependencies(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        if not (project / "pyproject.toml").is_file():
            QMessageBox.warning(
                self, "Project metadata not found",
                f"No pyproject.toml was found in:\n{project}",
            )
            return
        if shutil.which("uv") is None:
            QMessageBox.warning(
                self, "uv unavailable",
                "The 'uv' command was not found on PATH. Install uv before "
                "managing project dependencies.",
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Dependencies • {project.name}")
        dialog.resize(760, 560)
        layout = QVBoxLayout(dialog)

        heading = QLabel(
            "Inspect the environment or change this project's dependencies."
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        package_input = QLineEdit()
        package_input.setPlaceholderText("Package name, e.g. requests or rich>=13")
        layout.addWidget(package_input)

        action_row = QHBoxLayout()
        list_button = QPushButton("Refresh Installed")
        add_button = QPushButton("Add Package")
        remove_button = QPushButton("Remove Package")
        upgrade_button = QPushButton("Upgrade Lockfile")
        action_row.addWidget(list_button)
        action_row.addWidget(add_button)
        action_row.addWidget(remove_button)
        action_row.addWidget(upgrade_button)
        layout.addLayout(action_row)

        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlaceholderText("Dependency command output will appear here.")
        layout.addWidget(output, 1)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        uv_path = shutil.which("uv")

        def display_result(label, command):
            try:
                result = subprocess.run(
                    command,
                    cwd=str(project),
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                output.setPlainText(f"{label} timed out after five minutes.")
                return
            except OSError as error:
                output.setPlainText(f"Could not run {label.lower()}:\n{error}")
                return

            command_output = (result.stdout or "") + (result.stderr or "")
            status = "completed successfully" if result.returncode == 0 else (
                f"failed with exit code {result.returncode}"
            )
            output.setPlainText(
                f"{label} {status}.\n\n"
                f"$ {' '.join(command)}\n\n"
                f"{command_output.strip() or 'No output was produced.'}"
            )
            if result.returncode == 0:
                self.refresh_workspace_views()

        def package_name():
            value = package_input.text().strip()
            if not value or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:[<>=!~].+)?", value
            ):
                QMessageBox.warning(
                    dialog, "Invalid package name",
                    "Enter a package name such as requests or rich>=13. "
                    "Do not include spaces.",
                )
                return None
            return value

        def refresh_installed():
            python_executable = self.environment_python(project)
            if python_executable is None:
                output.setPlainText(
                    "Package inspection could not run because this project "
                    "has no .venv or venv environment.\n\n"
                    "Use 'uv sync' from the project folder first, then refresh."
                )
                return
            display_result(
                "Package inspection",
                [uv_path, "pip", "list", "--python", str(python_executable)],
            )

        def add_package():
            package = package_name()
            if package:
                display_result(
                    f"Adding {package}",
                    [uv_path, "add", "--directory", str(project), package],
                )

        def remove_package():
            package = package_name()
            if package:
                display_result(
                    f"Removing {package}",
                    [uv_path, "remove", "--directory", str(project), package],
                )

        list_button.clicked.connect(refresh_installed)
        add_button.clicked.connect(add_package)
        remove_button.clicked.connect(remove_package)
        upgrade_button.clicked.connect(
            lambda: display_result(
                "Lockfile upgrade",
                [uv_path, "lock", "--directory", str(project), "--upgrade"],
            )
        )
        refresh_installed()
        dialog.exec_()

    def open_git_workspace(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        git_path = shutil.which("git")
        if git_path is None:
            QMessageBox.warning(
                self, "Git unavailable",
                "The 'git' command was not found on PATH.",
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Git Workspace • {project.name}")
        dialog.resize(820, 620)
        layout = QVBoxLayout(dialog)

        branch_label = QLabel()
        layout.addWidget(branch_label)

        action_row = QHBoxLayout()
        refresh_button = QPushButton("Refresh Status")
        history_button = QPushButton("View History")
        action_row.addWidget(refresh_button)
        action_row.addWidget(history_button)
        layout.addLayout(action_row)

        output = QPlainTextEdit()
        output.setReadOnly(True)
        layout.addWidget(output, 1)

        commit_message = QLineEdit()
        commit_message.setPlaceholderText("Commit message")
        layout.addWidget(commit_message)
        commit_button = QPushButton("Commit All Changes")
        layout.addWidget(commit_button)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        def run_git(arguments, label):
            try:
                result = subprocess.run(
                    [git_path, *arguments],
                    cwd=str(project),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                output.setPlainText(f"{label} timed out after 30 seconds.")
                return None
            except OSError as error:
                output.setPlainText(f"Could not run Git:\n{error}")
                return None

            command_output = (result.stdout or "") + (result.stderr or "")
            if result.returncode != 0:
                output.setPlainText(
                    f"{label} failed with exit code {result.returncode}.\n\n"
                    f"{command_output.strip() or 'Git returned no details.'}"
                )
                return None
            return command_output.strip()

        def refresh_status():
            branch = run_git(["branch", "--show-current"], "Branch lookup")
            branch_label.setText(
                f"<b>{project.name}</b>  •  branch: {branch or 'detached HEAD'}"
            )
            status = run_git(
                ["status", "--short", "--branch"],
                "Status lookup",
            )
            if status is not None:
                output.setPlainText(status or "Working tree is clean.")

        def show_history():
            history = run_git(
                ["log", "--oneline", "--decorate", "-20"],
                "History lookup",
            )
            if history is not None:
                output.setPlainText(history or "No commits found.")

        def commit_changes():
            message = commit_message.text().strip()
            if not message:
                QMessageBox.warning(
                    dialog, "Commit message required",
                    "Enter a commit message before committing changes.",
                )
                return
            staged = run_git(["add", "--all"], "Staging changes")
            if staged is None:
                return
            commit = run_git(["commit", "-m", message], "Commit")
            if commit is not None:
                output.setPlainText(commit or "Commit created successfully.")
                commit_message.clear()
                self.refresh_workspace_views()

        refresh_button.clicked.connect(refresh_status)
        history_button.clicked.connect(show_history)
        commit_button.clicked.connect(commit_changes)
        refresh_status()
        dialog.exec_()

    def inspect_selected_environment(self):
        project = self.selected_project_path(self.environments_list)
        if not project:
            return
        python_executable = self.environment_python(project)
        if not python_executable:
            QMessageBox.warning(self, "Environment not found",
                                "The environment's Python executable is missing.")
            self.refresh_workspace_views()
            return

        uv_path = shutil.which("uv")
        if uv_path is None:
            QMessageBox.warning(
                self, "uv unavailable",
                "uv was not found on PATH, so packages can't be inspected.\n"
                f"Alternatively inspect manually:\n  {python_executable} -m pip list"
            )
            return

        try:
            result = subprocess.run(
                [uv_path, "pip", "list", "--python", str(python_executable)],
                cwd=str(project), capture_output=True, text=True,
                timeout=60, check=False,
            )
            output = (result.stdout or "").strip()
            if result.returncode != 0:
                output = (result.stderr or "Could not inspect packages.").strip()
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Installed Packages • {project.name}")
            dialog.resize(700, 500)
            layout = QVBoxLayout(dialog)
            text_view = QPlainTextEdit()
            text_view.setReadOnly(True)
            text_view.setPlainText(output or "No package information returned.")
            layout.addWidget(text_view)
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            dialog.exec_()
        except (OSError, subprocess.TimeoutExpired) as error:
            QMessageBox.warning(self, "Package inspection failed", str(error))

    @staticmethod
    def add_nav_button(layout, text):
        button = QPushButton(text)
        button.setMinimumHeight(42)
        layout.addWidget(button)
        return button

    @staticmethod
    def create_card(title, value):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(110)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)

        title_label = QLabel(title)
        title_label.setObjectName("card_title")

        value_label = QLabel(value)
        value_label.setObjectName("card_value")
        card.value_label = value_label

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return card

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layout()

    def closeEvent(self, event):
        self.refresh_timer.stop()
        self.status_clock_timer.stop()
        self.status_usage_timer.stop()
        self.connectivity_timer.stop()

        setup_workers = self.findChildren(ProjectSetupWorker)
        for worker in setup_workers:
            if worker.isRunning():
                worker.cancel()

        workers = [
            worker for worker in (
                getattr(self, "connectivity_worker", None),
                getattr(self, "help_search_worker", None),
                *setup_workers,
            )
            if worker is not None and worker.isRunning()
        ]
        for worker in workers:
            worker.wait(13000)

        super().closeEvent(event)

    def update_responsive_layout(self):
        width = self.width()

        if self.interface_density == "Compact":
            horizontal_padding = 18 if width < 1200 else 24
            vertical_padding = 16
            spacing = 12
        else:
            horizontal_padding = 22 if width < 1200 else 32
            vertical_padding = 20 if width < 1200 else 28
            spacing = 14 if width < 1200 else 20

        self.content_layout.setContentsMargins(
            horizontal_padding, vertical_padding,
            horizontal_padding, vertical_padding,
        )
        self.content_layout.setSpacing(spacing)

        sidebar_widths = {"Narrow": 200, "Standard": 230, "Wide": 280}
        self.sidebar.setFixedWidth(
            sidebar_widths.get(self.sidebar_width, 230)
        )

    def apply_startup_page(self):
        page_actions = {
            "Dashboard": self.show_dashboard,
            "My Projects": self.show_projects,
            "Environments": self.show_environments,
            "Help": self.show_help,
        }
        page_actions.get(self.startup_page, self.show_dashboard)()

    def open_terminal(self):
        working_directory = Path(__file__).resolve().parent

        if os.name == "nt":
            terminal = shutil.which("pwsh") or shutil.which("powershell")
            if terminal is None:
                QMessageBox.warning(
                    self, "Terminal unavailable",
                    "PowerShell could not be found on this system. Install it "
                    "via Choco or winget, or download it from the browser and "
                    "get it installed on your pc to use this feature.",
                )
                return
            args = [terminal, "-NoExit"]
        else:
            terminal = (
                shutil.which("x-terminal-emulator")
                or shutil.which("gnome-terminal")
                or shutil.which("konsole")
                or shutil.which("xterm")
            )
            if terminal is None:
                QMessageBox.warning(
                    self, "Terminal unavailable",
                    "No terminal emulator was found on this system.",
                )
                return
            args = [terminal]

        self.launch_terminal(args, working_directory)

    def open_project_root(self):
        project_root = Path(self.default_project_location).expanduser()
        if not project_root.is_dir():
            QMessageBox.information(
                self,
                "Project root not found",
                f"The configured project location does not exist yet:\n{project_root}\n\n"
                "Create a project first or update the default location in Settings.",
            )
            return
        self.open_path_in_file_manager(project_root)

    def show_toolchain_status(self):
        tools = {
            "Python": sys.executable,
            "uv": shutil.which("uv"),
            "Git": shutil.which("git"),
            "VS Code": shutil.which("code"),
            "PowerShell": shutil.which("pwsh") or shutil.which("powershell"),
        }
        lines = [
            f"{name}: {'Available — ' + path if path else 'Not found on PATH'}"
            for name, path in tools.items()
        ]
        available = sum(path is not None for path in tools.values())
        dialog = QDialog(self)
        dialog.setWindowTitle("Developer Toolchain")
        dialog.resize(620, 320)
        layout = QVBoxLayout(dialog)
        heading = QLabel(f"{available}/{len(tools)} developer tools available")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText("\n".join(lines))
        layout.addWidget(output, 1)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def open_settings(self):
        dialog = SettingsDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            (
                self.interface_density,
                self.color_theme,
                self.sidebar_width,
                self.startup_page,
                self.default_project_location,
                self.default_python_version,
                self.auto_refresh_projects,
                self.refresh_interval,
                self.project_search_roots,
            ) = (
                dialog.get_settings()
            )
            self.settings.setValue("interface_density", self.interface_density)
            self.settings.setValue("color_theme", self.color_theme)
            self.settings.setValue("sidebar_width", self.sidebar_width)
            self.settings.setValue("startup_page", self.startup_page)
            self.settings.setValue(
                "default_project_location", self.default_project_location
            )
            self.settings.setValue(
                "default_python_version", self.default_python_version
            )
            self.settings.setValue(
                "auto_refresh_projects", self.auto_refresh_projects
            )
            self.settings.setValue("refresh_interval", self.refresh_interval)
            self.refresh_timer.setInterval(self.refresh_interval * 1000)
            if self.auto_refresh_projects:
                self.refresh_timer.start()
            else:
                self.refresh_timer.stop()
            self.save_search_roots()
            self.setStyleSheet(
                apply_theme_stylesheet(self.base_stylesheet, self.color_theme)
            )
            self.statusBar().setStyleSheet(
                apply_theme_stylesheet(
                    "QStatusBar { background-color: #11141C; color: #8B949E; "
                    "border-top: 1px solid #2A3040; }"
                    "QStatusBar::item { border: none; }",
                    self.color_theme,
                )
            )
            self.update_responsive_layout()
            self.refresh_workspace_views()

    def create_new_project(self, *_):
        """Two-step wizard: details → package advisor → confirm → create."""
        # ---- Step 1: project details ----
        dialog = NewProjectDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        project_name, project_location, python_version, template_name = (
            dialog.get_project_details()
        )

        if not project_name:
            QMessageBox.warning(
                self, "Project name required",
                "Please enter a name for your project.",
            )
            return

        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", project_name):
            QMessageBox.warning(
                self, "Invalid project name",
                "Use letters, numbers, underscores, or hyphens. "
                "The name must begin with a letter or number.\n\n"
                "Example: Trixie's_work",
            )
            return

        if not project_location:
            QMessageBox.warning(
                self, "Location required",
                "Please choose a location for your project.",
            )
            return

        parent_directory = Path(project_location).expanduser()
        project_directory = parent_directory / project_name

        uv_executable = shutil.which("uv")
        git_executable = shutil.which("git")

        if uv_executable is None:
            QMessageBox.critical(
                self, "uv unavailable",
                "Could not find uv on PATH.\n"
                "Please install uv or correct your PATH.",
            )
            return

        if git_executable is None:
            QMessageBox.critical(
                self, "Git unavailable",
                "Could not find Git on PATH.\n"
                "Please install Git before creating a project.",
            )
            return

        if project_directory.exists():
            QMessageBox.warning(
                self, "Project already exists",
                f"This location already exists:\n\n"
                f"{project_directory}\n\n"
                "Choose another project name or location.",
            )
            return

        # ---- Step 2: package advisor (skippable) ----
        advisor = PackageAdvisorDialog(self)
        if advisor.exec_() == QDialog.Accepted:
            self.recommended_packages = advisor.selected_packages()
        else:
            # Cancelled the wizard outright — stop without creating anything.
            return

        selected_packages = list(self.recommended_packages)

        # ---- Step 3: confirm and create ----
        confirmation = QMessageBox.question(
            self, "Create Python Project",
            f"Create project '{project_name}'?\n\n"
            f"Location:\n{project_directory}\n\n"
            f"Python: {python_version}\n\n"
            f"Template: {template_name}\n\n"
            "DevSuite will:\n"
            "• Initialize a Python application with uv\n"
            "• Create a Git repository\n"
            "• Create a virtual environment\n"
            "• Generate the initial project files"
            + (
                f"\n• Install: {', '.join(selected_packages)}"
                if selected_packages else ""
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if confirmation != QMessageBox.Yes:
            return

        progress_dialog = ProjectSetupProgressDialog(project_name, self)
        worker = ProjectSetupWorker(
            uv_executable, project_directory, project_name,
            selected_packages, python_version, template_name,
        )
        progress_dialog.worker = worker
        worker.progress.connect(progress_dialog.status_label.setText)
        worker.log_line.connect(progress_dialog.output.appendPlainText)

        def setup_finished(result):
            progress_dialog.progress_bar.setRange(0, 1)
            progress_dialog.progress_bar.setValue(1)
            progress_dialog.accept()
            self.recommended_packages = []
            self.refresh_workspace_views()

            if result.get("success"):
                installed_packages = result.get("packages", [])
                deps_line = (
                    "✓ Dependencies: " + ", ".join(installed_packages) + "\n\n"
                    if installed_packages else "✓ Dependencies: none\n\n"
                )
                QMessageBox.information(
                    self, "Project created successfully! 🎉",
                    f"Your Python project is ready!\n\n"
                    f"Name: {project_name}\n\n"
                    f"Location:\n{project_directory}\n\n"
                    "Created:\n"
                    "✓ Python application structure\n"
                    "✓ pyproject.toml\n"
                    "✓ Git repository\n"
                    "✓ Virtual environment\n"
                    "✓ uv.lock\n"
                    + deps_line
                    + "Completed successfully! "
                    "Happy coding, buddy! 🐍",
                )
            else:
                installed_packages = result.get("packages", [])
                failed_packages = result.get("failed_packages", [])
                package_summary = (
                    f"Installed: {', '.join(installed_packages)}\n"
                    if installed_packages else "Installed: none\n"
                )
                if failed_packages:
                    package_summary += (
                        f"Failed: {', '.join(failed_packages)}\n"
                    )
                QMessageBox.warning(
                    self, "Project setup needs attention",
                    "DevSuite™ could not finish every setup step. The project may "
                    "have been partially created.\n\n"
                    f"Details: {result.get('error', 'Unknown setup error')}\n\n"
                    f"{package_summary}\n"
                    f"Project location:\n{project_directory}\n\n"
                    "Open the project folder and inspect the files before retrying. "
                    "You can usually finish dependency setup by running `uv sync` there.",
                )

        worker.setup_result = None
        worker.completed.connect(lambda result: setattr(worker, "setup_result", result))
        worker.finished.connect(
            lambda: setup_finished(
                worker.setup_result
                or {"success": False, "error": "Setup worker stopped unexpectedly."}
            )
        )
        worker.start()
        progress_dialog.exec_()


def main():
    app = QApplication(sys.argv)

    window = DevSuiteWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
