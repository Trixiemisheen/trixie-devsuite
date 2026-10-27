import re
import shutil
import subprocess
import sys
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
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



class ProjectSetupWorker(QThread):
    """Run project setup off the UI thread and stream command output."""
    progress = pyqtSignal(str)
    log_line = pyqtSignal(str)
    completed = pyqtSignal(object)

    def __init__(self, uv_executable, project_directory, project_name, packages):
        super().__init__()
        self.uv_executable = uv_executable
        self.project_directory = Path(project_directory)
        self.project_name = project_name
        self.packages = list(packages)

    def run_command(self, label, command, timeout_seconds):
        self.progress.emit(label)
        self.log_line.emit(f"\n> {' '.join(str(part) for part in command)}\n")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        try:
            if process.stdout is not None:
                for line in process.stdout:
                    self.log_line.emit(line.rstrip())
            return_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise TimeoutError(f"{label} exceeded the {timeout_seconds}-second time limit.")
        if return_code != 0:
            raise RuntimeError(f"{label} failed with exit code {return_code}.")

    def run(self):
        try:
            self.progress.emit("Preparing project folder…")
            self.project_directory.parent.mkdir(parents=True, exist_ok=True)
            self.run_command(
                "Step 1 of 3: Initializing project and Git repository…",
                [
                    self.uv_executable,
                    "init",
                    "--app",
                    "--python",
                    "3.14",
                    "--vcs",
                    "git",
                    "--no-workspace",
                    "--name",
                    self.project_name,
                    str(self.project_directory),
                ],
                120,
            )
            self.run_command(
                "Step 2 of 3: Creating the virtual environment and syncing dependencies…",
                [self.uv_executable, "sync", "--directory", str(self.project_directory)],
                300,
            )
            if self.packages:
                self.run_command(
                    "Step 3 of 3: Installing recommended packages…",
                    [self.uv_executable, "add", "--directory", str(self.project_directory), *self.packages],
                    600,
                )
            else:
                self.progress.emit("Finalizing your clean Python project…")
            self.completed.emit({"success": True, "packages": self.packages})
        except Exception as error:
            self.log_line.emit(f"\nERROR: {error}")
            self.completed.emit({"success": False, "error": str(error), "packages": self.packages})


class ProjectSetupProgressDialog(QDialog):
    def __init__(self, project_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creating Your Project")
        self.setMinimumSize(560, 390)
        layout = QVBoxLayout(self)
        title = QLabel(f"🚀 Building <b>{project_name}</b>")
        title.setWordWrap(True)
        layout.addWidget(title)
        self.status_label = QLabel("Getting things ready…")
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
        note = QLabel("Keep this window open while DevSuite prepares the project.")
        note.setWordWrap(True)
        layout.addWidget(note)

    def closeEvent(self, event):
        if hasattr(self, "worker") and self.worker.isRunning():
            event.ignore()
            return
        super().closeEvent(event)


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

        dashboard_nav = self.add_nav_button(sidebar_layout, "⌂   Dashboard")
        dashboard_nav.clicked.connect(self.show_dashboard)

        new_project_nav = self.add_nav_button(
            sidebar_layout, "+   New Project"
        )
        new_project_nav.clicked.connect(self.create_new_project)

        projects_nav = self.add_nav_button(sidebar_layout, "▣   My Projects")
        projects_nav.clicked.connect(self.show_projects)
        environments_nav = self.add_nav_button(sidebar_layout, "⚙   Environments")
        environments_nav.clicked.connect(self.show_environments)
        packages_nav = self.add_nav_button(sidebar_layout, "◇   Package Advisor")
        packages_nav.clicked.connect(self.open_package_advisor)

        sidebar_layout.addStretch()

        settings_button = self.add_nav_button(
            sidebar_layout, "⚙   Settings"
        )
        settings_button.clicked.connect(self.open_settings)

        version = QLabel("Trixie DevSuite  •  v0.5.0")
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

        self.total_projects_card = self.create_card("TOTAL PROJECTS", "0")
        self.environments_card = self.create_card("ENVIRONMENTS", "0")
        self.python_version_card = self.create_card(
            "PYTHON VERSION", sys.version.split()[0]
        )
        stats_layout.addWidget(self.total_projects_card)
        stats_layout.addWidget(self.environments_card)
        stats_layout.addWidget(self.python_version_card)

        self.content_layout.addLayout(stats_layout)

        actions_heading = QLabel("QUICK ACTIONS")
        actions_heading.setObjectName("section")
        self.content_layout.addWidget(actions_heading)

        new_project_button = QPushButton(
            "+   Create a New Python Project")


    def build_projects_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        heading = QLabel("My Projects")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        subtitle = QLabel(
            "Projects discovered in your DevSuite folder, its parent workspace, "
            "and your personal Projects folder."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Search projects by name or folder path.
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText(
            "🔍  Search projects by name or location..."
        )
        self.project_search.setClearButtonEnabled(True)
        self.project_search.textChanged.connect(self.filter_projects)
        layout.addWidget(self.project_search)

        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet(
            "QListWidget { background-color: #202633; border: 1px solid #303849; "
            "border-radius: 8px; padding: 6px; }"
            "QListWidget::item { padding: 10px; border-bottom: 1px solid #303849; }"
            "QListWidget::item:selected { background-color: #164653; color: #FFFFFF; }"
        )
        layout.addWidget(self.projects_list, 1)

        actions = QHBoxLayout()

        refresh_button = QPushButton("↻  Refresh")
        refresh_button.clicked.connect(self.refresh_workspace_views)
        actions.addWidget(refresh_button)

        open_folder_button = QPushButton("Open Folder")
        open_folder_button.clicked.connect(self.open_selected_project_folder)
        actions.addWidget(open_folder_button)

        terminal_button = QPushButton(">_  Project Terminal")
        terminal_button.clicked.connect(self.open_selected_project_terminal)
        actions.addWidget(terminal_button)

        run_button = QPushButton("▶  Run main.py")
        run_button.clicked.connect(self.run_selected_project)
        actions.addWidget(run_button)

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

        subtitle = QLabel(
            "Virtual environments discovered in the projects DevSuite knows about. "
            "DevSuite will inspect them without deleting or modifying them."
        )
        
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Search projects by name or folder path.
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText(
            "🔍  Search projects by name or location..."
        )
        self.project_search.setClearButtonEnabled(True)
        self.project_search.textChanged.connect(
            self.filter_projects
        )
        layout.addWidget(self.project_search)

        self.projects_list = QListWidget()



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
        layout.addLayout(actions)
        return page

    def discover_projects(self):
        """Discover projects in a small set of predictable workspace folders."""
        app_directory = Path(__file__).resolve().parent
        roots = [
            app_directory,
            app_directory.parent,
            Path.home() / "Projects",
        ]
        projects = {}
        for root in roots:
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
            candidate = project / folder_name / "Scripts" / "python.exe"
            if candidate.is_file():
                return candidate
        return None

    def refresh_workspace_views(self, *_):
        projects = self.discover_projects()
        self.projects_list.clear()
        self.environments_list.clear()
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

        if not projects:
            empty = QListWidgetItem(
                "No projects found yet. Create one with + New Project."
            )
            empty.setFlags(empty.flags() & ~empty.ItemIsSelectable)
            self.projects_list.addItem(empty)

        if not environment_count:
            empty = QListWidgetItem(
                "No .venv or venv environments found in discovered projects."
            )
            empty.setFlags(empty.flags() & ~empty.ItemIsSelectable)
            self.environments_list.addItem(empty)

    def show_dashboard(self):
        self.pages.setCurrentIndex(0)
        self.refresh_workspace_views()

    def show_projects(self):
        self.pages.setCurrentIndex(1)
        self.refresh_workspace_views()

    def show_environments(self):
        self.pages.setCurrentIndex(2)
        self.refresh_workspace_views()

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
            QMessageBox.warning(self, "Project not found", f"This folder no longer exists:\\n{project}")
            self.refresh_workspace_views()
            return None
        return project

    def open_selected_project_folder(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            try:
                subprocess.Popen(["explorer", str(project)])
            except OSError as error:
                QMessageBox.critical(self, "Could not open folder", str(error))

    def open_project_terminal(self, project, activate_environment=False):
        terminal = shutil.which("pwsh") or shutil.which("powershell")
        if not terminal:
            QMessageBox.warning(self, "Terminal unavailable", "PowerShell could not be found on PATH.")
            return
        command = ""
        python_executable = self.environment_python(project)
        if activate_environment and python_executable:
            activation_script = python_executable.parent / "Activate.ps1"
            command = f'& "{activation_script}"'
        try:
            subprocess.Popen(
                [terminal, "-NoExit", "-Command", command] if command else [terminal, "-NoExit"],
                cwd=str(project),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except OSError as error:
            QMessageBox.critical(self, "Could not open terminal", str(error))

    def open_selected_project_terminal(self):
        project = self.selected_project_path(self.projects_list)
        if project:
            self.open_project_terminal(project)

    def open_selected_environment_terminal(self):
        project = self.selected_project_path(self.environments_list)
        if project:
            self.open_project_terminal(project, activate_environment=True)

    def run_selected_project(self):
        project = self.selected_project_path(self.projects_list)
        if not project:
            return
        main_file = project / "main.py"
        if not main_file.is_file():
            QMessageBox.information(
                self, "main.py not found",
                f"No main.py file was found in this project:\\n{project}",
            )
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
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except OSError as error:
            QMessageBox.critical(self, "Could not run project", str(error))

    def inspect_selected_environment(self):
        project = self.selected_project_path(self.environments_list)
        if not project:
            return
        python_executable = self.environment_python(project)
        if not python_executable:
            QMessageBox.warning(self, "Environment not found", "The environment's Python executable is missing.")
            self.refresh_workspace_views()
            return
        try:
            result = subprocess.run(
                [shutil.which("uv") or "uv", "pip", "list", "--python", str(python_executable)],
                cwd=str(project), capture_output=True, text=True, timeout=60, check=False,
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

        selected_packages = list(self.recommended_packages)
        progress_dialog = ProjectSetupProgressDialog(project_name, self)
        worker = ProjectSetupWorker(
            uv_executable,
            project_directory,
            project_name,
            selected_packages,
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
                        "✓ Dependencies: "
                        + ", ".join(selected_packages)
                        + "\n\n"
                        if selected_packages
                        else "\n"
                    )
                    + "Happy coding, buddy! 🐍",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Project setup needs attention",
                    "DevSuite could not finish every setup step. The project may have been partially created.\n\n"
                    f"Details: {result.get('error', 'Unknown setup error')}\n\n"
                    f"Project location:\n{project_directory}\n\n"
                    "Open the project folder and inspect the files before retrying. "
                    "You can usually finish dependency setup by running `uv sync` there.",
                )

        worker.setup_result = None
        worker.completed.connect(lambda result: setattr(worker, "setup_result", result))
        worker.finished.connect(
            lambda: setup_finished(
                worker.setup_result or {"success": False, "error": "Setup worker stopped unexpectedly."}
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
