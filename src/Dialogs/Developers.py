import requests
from PyQt6.QtWidgets import (
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
    QWidget,
)
from PyQt6.QtCore import Qt


class Developers(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developers")
        self.developers = self.get_developers()
        self.setup_ui()

    def get_developers(self):
        repo_owner = "SchBenedikt"
        repo_name = "Text-Editor"
        repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
        response = requests.get(repo_url)
        if response.status_code == 200:
            contributors = response.json()
            return [contributor.get("login", "Unknown") for contributor in contributors]
        else:
            print("Failed to fetch contributors.")
            return []

    def setup_ui(self):
        table = QTableWidget()
        table.setRowCount(len(self.developers))
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Username"])

        for row, username in enumerate(self.developers):
            table.setItem(row, 0, QTableWidgetItem(username))

        layout = QVBoxLayout(self)
        layout.addWidget(table)

        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_rect = parent_widget.geometry()
            self.move(parent_rect.center() - self.rect().center())

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
