import re
import shutil
import subprocess
import sys
from pathlib import Path
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
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("DevSuite Settings")
        self.setMinimumWidth(360)

        self.setStyleSheet("""
            QDialog {
                background-color: #151821;
                color: #E6EDF3;
            }

            QLabel {
                color: #E6EDF3;
                font-size: 13px;
            }

            QComboBox {
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

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        heading = QLabel("Appearance")
        heading.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #00E5FF;"
        )
        layout.addWidget(heading)

        layout.addWidget(QLabel("Interface density"))

        self.density_combo = QComboBox()
        self.density_combo.addItems(["Comfortable", "Compact"])

        if parent:
            self.density_combo.setCurrentText(
                parent.interface_density
            )

        layout.addWidget(self.density_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a New Python Project")
        self.setMinimumWidth(480)

        self.setStyleSheet("""
            QDialog {
                background-color: #151821;
                color: #E6EDF3;
            }

            QLabel {
                color: #E6EDF3;
            }

            QLineEdit {
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
            "e.g. my_awesome_project"
        )

        self.project_location = QLineEdit()
        self.project_location.setText(
            str(Path.home() / "Projects")
        )

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_location)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.project_location)
        location_layout.addWidget(browse_button)

        form_layout = QFormLayout()
        form_layout.addRow("Project name:", self.project_name)
        form_layout.addRow("Project location:", location_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        buttons.button(QDialogButtonBox.Ok).setText("Create Project")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Project Location",
            self.project_location.text(),
        )

        if folder:
            self.project_location.setText(folder)

    def get_project_details(self):
        return (
            self.project_name.text().strip(),
            self.project_location.text().strip(),
        )




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


class PackageAdvisorDialog(QDialog):
    """Rule-based, offline package recommendations for a new project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSuite Package Advisor")
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
            "Choose a project type and describe your idea. DevSuite will suggest "
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
        self.continue_button = buttons.addButton(
            "Continue to Create Project", QDialogButtonBox.AcceptRole
        )
        self.continue_button.setObjectName("primary")
        buttons.rejected.connect(self.reject)
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

        # Add idea-specific suggestions, without duplicating existing packages.
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



class DevSuiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trixie DevSuite™")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.interface_density = "Comfortable"
        self.recommended_packages = []

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #151821;
                color: #E6EDF3;
                font-family: Segoe UI;
            }

            QLabel#brand {
                color: #00E5FF;
                font-size: 23px;
                font-weight: bold;
                padding: 12px;
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
        """)

        # Main layout
        central = QWidget()
        self.setCentralWidget(central)

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

        self.add_nav_button(sidebar_layout, "⌂   Dashboard")

        new_project_nav = self.add_nav_button(
            sidebar_layout, "+   New Project"
        )
        new_project_nav.clicked.connect(self.create_new_project)

        self.add_nav_button(sidebar_layout, "▣   My Projects")
        self.add_nav_button(sidebar_layout, "⚙   Environments")
        packages_nav = self.add_nav_button(sidebar_layout, "◇   Package Advisor")
        packages_nav.clicked.connect(self.open_package_advisor)

        sidebar_layout.addStretch()

        settings_button = self.add_nav_button(
            sidebar_layout, "⚙   Settings"
        )
        settings_button.clicked.connect(self.open_settings)

        version = QLabel("Trixie DevSuite  •  v0.4.0")
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

        heading = QLabel("Developer Dashboard")
        heading.setObjectName("heading")
        self.content_layout.addWidget(heading)

        subtitle = QLabel(
            "Your Python projects, environments, and tools in one place."
        )
        subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(subtitle)

        welcome = QLabel("Welcome back, Developer! 🐍")
        welcome.setStyleSheet(
            "font-size: 19px; font-weight: bold; padding-top: 12px;"
        )
        self.content_layout.addWidget(welcome)

        description = QLabel(
            "Build something brilliant. "
            "Let DevSuite™ handle the setup."
        )
        description.setObjectName("subtitle")
        self.content_layout.addWidget(description)

        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        stats_layout.addWidget(
            self.create_card("TOTAL PROJECTS", "0")
        )
        stats_layout.addWidget(
            self.create_card("ENVIRONMENTS", "0")
        )
        stats_layout.addWidget(
            self.create_card("PYTHON VERSION", "3.14")
        )

        self.content_layout.addLayout(stats_layout)

        actions_heading = QLabel("QUICK ACTIONS")
        actions_heading.setObjectName("section")
        self.content_layout.addWidget(actions_heading)

        new_project_button = QPushButton(
            "+   Create a New Python Project"
        )
        new_project_button.setObjectName("primary")
        new_project_button.setMinimumHeight(48)
        new_project_button.clicked.connect(self.create_new_project)

        self.content_layout.addWidget(new_project_button)

        advisor_button = QPushButton("🧠   Recommend Packages for My Idea")
        advisor_button.setMinimumHeight(45)
        advisor_button.clicked.connect(self.open_package_advisor)
        self.content_layout.addWidget(advisor_button)

        terminal_button = QPushButton(">_   Open Terminal")
        terminal_button.setMinimumHeight(45)
        terminal_button.clicked.connect(self.open_terminal)

        self.content_layout.addWidget(terminal_button)

        self.content_layout.addStretch()

        footer = QLabel(
            "TRIXIE MISHEEN™  •  BUILT WITH PYTHON & PyQt5"
        )
        footer.setStyleSheet(
            "color: #697586; font-size: 11px; padding: 8px;"
        )
        self.content_layout.addWidget(footer)

        self.root_layout.addWidget(content, 1)

        self.update_responsive_layout()

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

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return card

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layout()

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
            horizontal_padding,
            vertical_padding,
            horizontal_padding,
            vertical_padding,
        )
        self.content_layout.setSpacing(spacing)

        self.sidebar.setFixedWidth(
            max(200, min(250, int(width * 0.21)))
        )

    def open_terminal(self):
        project_directory = Path(__file__).resolve().parent

        # Prefer PowerShell 7, falling back to Windows PowerShell.
        terminal = shutil.which("pwsh") or shutil.which("powershell")

        if terminal is None:
            QMessageBox.warning(
                self,
                "Terminal unavailable",
                "PowerShell could not be found on this system.",
            )
            return

        try:
            subprocess.Popen(
                [terminal, "-NoExit"],
                cwd=str(project_directory),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Could not open terminal",
                f"PowerShell could not be started:\n{error}",
            )

    def open_settings(self):
        dialog = SettingsDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            self.interface_density = (
                dialog.density_combo.currentText()
            )
            self.update_responsive_layout()

    def open_package_advisor(self):
        dialog = PackageAdvisorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.recommended_packages = dialog.selected_packages()
            if not self.recommended_packages:
                QMessageBox.information(
                    self,
                    "No packages selected",
                    "No dependencies were selected. You can still create a clean Python project.",
                )
            self.create_new_project()

    def create_new_project(self):
        dialog = NewProjectDialog(self)

        if dialog.exec_() != QDialog.Accepted:
            return

        project_name, project_location = (
            dialog.get_project_details()
        )

        # Validate the project name.
        if not project_name:
            QMessageBox.warning(
                self,
                "Project name required",
                "Please enter a name for your project.",
            )
            return

        if not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_-]*",
            project_name,
        ):
            QMessageBox.warning(
                self,
                "Invalid project name",
                "Use letters, numbers, underscores, or hyphens. "
                "The name must begin with a letter or number.\n\n"
                "Example: my_awesome_project",
            )
            return

        # Validate the destination.
        if not project_location:
            QMessageBox.warning(
                self,
                "Location required",
                "Please choose a location for your project.",
            )
            return

        parent_directory = Path(project_location).expanduser()
        project_directory = parent_directory / project_name

        # Check the required tools.
        uv_executable = shutil.which("uv")
        git_executable = shutil.which("git")

        if uv_executable is None:
            QMessageBox.critical(
                self,
                "uv unavailable",
                "Could not find uv on PATH.\n"
                "Please install uv or correct your PATH.",
            )
            return

        if git_executable is None:
            QMessageBox.critical(
                self,
                "Git unavailable",
                "Could not find Git on PATH.\n"
                "Please install Git before creating a project.",
            )
            return

        # Never overwrite an existing project.
        if project_directory.exists():
            QMessageBox.warning(
                self,
                "Project already exists",
                f"This location already exists:\n\n"
                f"{project_directory}\n\n"
                "Choose another project name or location.",
            )
            return

        # Confirm the operation before creating files.
        confirmation = QMessageBox.question(
            self,
            "Create Python Project",
            f"Create project '{project_name}'?\n\n"
            f"Location:\n{project_directory}\n\n"
            "DevSuite will:\n"
            "• Initialize a Python application with uv\n"
            "• Create a Git repository\n"
            "• Create a virtual environment\n"
            "• Generate the initial project files",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if confirmation != QMessageBox.Yes:
            return

        try:
            # Create the selected parent directory if necessary.
            parent_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Initialize a standalone Python application.
            init_result = subprocess.run(
                [
                    uv_executable,
                    "init",
                    "--app",
                    "--python",
                    "3.14",
                    "--vcs",
                    "git",
                    "--no-workspace",
                    "--name",
                    project_name,
                    str(project_directory),
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            if init_result.returncode != 0:
                details = (
                    init_result.stderr.strip()
                    or init_result.stdout.strip()
                    or "uv returned an unknown error."
                )

                QMessageBox.critical(
                    self,
                    "Project initialization failed",
                    f"uv could not initialize the project.\n\n"
                    f"{details}\n\n"
                    f"Check the destination:\n{project_directory}",
                )
                return

            # Create the virtual environment and synchronize dependencies.
            sync_result = subprocess.run(
                [
                    uv_executable,
                    "sync",
                    "--directory",
                    str(project_directory),
                ],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            if sync_result.returncode != 0:
                details = (
                    sync_result.stderr.strip()
                    or sync_result.stdout.strip()
                    or "uv sync returned an unknown error."
                )

                QMessageBox.warning(
                    self,
                    "Project created with a setup issue",
                    "The project and Git repository were initialized, "
                    "but environment setup did not complete successfully.\n\n"
                    f"{details}\n\n"
                    f"Project location:\n{project_directory}\n\n"
                    "You can finish setup by running:\n"
                    "uv sync",
                )
                return

            selected_packages = list(self.recommended_packages)
            if selected_packages:
                add_result = subprocess.run(
                    [
                        uv_executable,
                        "add",
                        "--directory",
                        str(project_directory),
                        *selected_packages,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    check=False,
                )
                if add_result.returncode != 0:
                    details = (
                        add_result.stderr.strip()
                        or add_result.stdout.strip()
                        or "uv add returned an unknown error."
                    )
                    QMessageBox.warning(
                        self,
                        "Project created; dependency installation needs attention",
                        "The project was created, but some selected packages could not "
                        "be installed. You can retry from the project directory with "
                        "'uv add package-name'.\n\n"
                        f"{details}\n\nProject location:\n{project_directory}",
                    )
                    self.recommended_packages = []
                    return

            QMessageBox.information(
                self,
                "Project created successfully! 🎉",
                f"Your Python project is ready!\n\n"
                f"Name: {project_name}\n\n"
                f"Location:\n{project_directory}\n\n"
                "Created:\n"
                "✓ Python application structure\n"
                "✓ pyproject.toml\n"
                "✓ Git repository\n"
                "✓ Virtual environment\n"
                "✓ uv.lock\n"
                + (
                    "✓ Dependencies: " + ", ".join(selected_packages) + "\n\n"
                    if selected_packages else "\n"
                )
                + "Happy coding, buddy! 🐍",
            )
            self.recommended_packages = []

        except subprocess.TimeoutExpired:
            QMessageBox.warning(
                self,
                "Setup timed out",
                "Project setup took too long and was stopped.\n\n"
                f"Check the project directory:\n{project_directory}\n\n"
                "If the project was partially created, inspect it "
                "before trying again.",
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "Project creation error",
                f"An operating-system error occurred:\n\n{error}",
            )

def main():
    app = QApplication(sys.argv)

    window = DevSuiteWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

