import requests
from PyQt6.QtWidgets import QDialog, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices


class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_version: str = "v2025.02.02"
        repo_owner = "SchBenedikt"
        repo_name = "Text-Editor"

        self.release_url = (
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        )

        self.setWindowTitle("About")
        self.setup_ui()

    def get_latest_version(self):
        response = requests.get(self.release_url)
        if response.status_code == 200:
            latest_version = response.json().get("tag_name", "vYYYY.MM.DD")
        else:
            latest_version = "vYYYY.MM.DD"

        return latest_version

    def setup_ui(self):
        latest_version: str = self.get_latest_version()

        if latest_version != self.current_version:
            label_version = QLabel(
                f"Current Version: {self.current_version}\n\nNew Version: {latest_version}",
                self,
            )
            button_open_release = QPushButton("New release available", self)
            button_open_release.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(self.release_url))
            )
        else:
            label_version = QLabel(f"{self.current_version}", self)
            button_open_release = None

        layout = QVBoxLayout(self)
        layout.addWidget(label_version)
        if button_open_release:
            layout.addWidget(button_open_release)

        self.adjustSize()
        self.setFixedSize(self.width() + 10, self.height() + 10)

        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_rect = parent_widget.geometry()
            self.move(parent_rect.center() - self.rect().center())
