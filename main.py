import shutil
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
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


class DevSuiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trixie DevSuite™")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.interface_density = "Comfortable"

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
        self.add_nav_button(sidebar_layout, "◇   Packages")

        sidebar_layout.addStretch()

        settings_button = self.add_nav_button(
            sidebar_layout, "⚙   Settings"
        )
        settings_button.clicked.connect(self.open_settings)

        version = QLabel("Trixie DevSuite  •  v0.1.2")
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

    def create_new_project(self):
        dialog = NewProjectDialog(self)

        if dialog.exec_() != QDialog.Accepted:
            return

        project_name, project_location = (
            dialog.get_project_details()
        )

        if not project_name:
            QMessageBox.warning(
                self,
                "Project name required",
                "Please enter a name for your project.",
            )
            return

        if not project_location:
            QMessageBox.warning(
                self,
                "Location required",
                "Please choose a location for your project.",
            )
            return

        QMessageBox.information(
            self,
            "Project Details",
            f"Project name: {project_name}\n"
            f"Project location: {project_location}\n\n"
            "Your details have been received. "
            "Project creation will be added next.",
        )


def main():
    app = QApplication(sys.argv)

    window = DevSuiteWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

