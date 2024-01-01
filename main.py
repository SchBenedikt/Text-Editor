from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from docx import Document
from docx.shared import Pt, RGBColor
import os
import re
import webbrowser
import sys
import threading
import requests
from flask import Flask, request, session
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from requests_oauthlib import OAuth2Session
import threading
from auth import app, github
from urllib.parse import quote

from base64 import b64decode


def get_username_from_about_file():
    with open("about.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("Username:"):
                return line.strip().split(":")[1].strip()
    return None


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Editor")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.init_menu()
        self.init_toolbar()
        self.init_tab_bar()
        self.open_new_tab()
        self.text_area = QTextEdit()

        self.set_style_options()

    def init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.open_new_tab)
        file_menu.addAction(new_tab_action)

        search_action = QAction("Search Word", self)
        search_action.triggered.connect(self.show_search_dialog)
        file_menu.addAction(search_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        save_menu = menubar.addMenu("Save")
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        save_menu.addAction(save_action)

        export_docx_action = QAction("Export as DOCX", self)
        export_docx_action.triggered.connect(self.export_as_docx)
        save_menu.addAction(export_docx_action)

        export_txt_action = QAction("Export as TXT", self)
        export_txt_action.triggered.connect(self.export_as_txt)
        save_menu.addAction(export_txt_action)

        login_action = QAction("Login", self)
        login_action.triggered.connect(self.start_webserver)
        file_menu.addAction(login_action)

        projects = self.load_projects()

        # Add projects to the menu
        projects_menu = menubar.addMenu("Projects")
        for project in projects:
            project_action = QAction(project, self)
            project_action.triggered.connect(lambda _, p=project: self.open_project(p))
            projects_menu.addAction(project_action)

    def open_project(self, project):
        username = get_username_from_about_file()
        if username:
            repo_url = f"https://api.github.com/repos/{username}/{project}/contents"
            try:
                response = requests.get(repo_url)
                response.raise_for_status()  # Check if the request was successful

                files = [file_info["name"] for file_info in response.json()]

                # Display the file names in a QMessageBox
                if files:
                    selected_file, ok = QInputDialog.getItem(self, "Select File", "Select a file to open:", files, 0,
                                                             False)
                    if ok and selected_file:
                        # Fetch the content of the selected file
                        file_content_url = f"https://api.github.com/repos/{username}/{project}/contents/{quote(selected_file)}"
                        content_response = requests.get(file_content_url)
                        content_response.raise_for_status()

                        # Decode the base64-encoded content
                        content = b64decode(content_response.json()["content"]).decode("utf-8")

                        # Open the content in a new tab in the text editor
                        self.open_new_tab()
                        current_widget = self.tab_widget.currentWidget()
                        current_widget.setPlainText(content)
                        self.set_tab_title(current_widget, selected_file)
                else:
                    QMessageBox.warning(self, "No Files", f"There are no files in {project}.")
            except requests.RequestException as e:
                QMessageBox.warning(self, "Error", f"Error fetching project files: {str(e)}")
        else:
            # Handle the case when username is not available
            pass

    def load_projects(self):
        projects = []
        with open("projects.txt", "r") as file:
            for line in file:
                project = line.strip()
                if project:
                    projects.append(project)
        return projects

    def start_webserver(self):
        def run_flask_app():
            app.run(host="localhost", port=5000)

        flask_thread = threading.Thread(target=run_flask_app)
        flask_thread.start()

        # Open web browser to localhost:5000
        url = "http://localhost:5000"
        webbrowser.open(url)

    def init_toolbar(self):
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        toolbar.setIconSize(QSize(20, 20))

        bold_action = QAction(QIcon("bold.png"), "Bold", self)
        bold_action.triggered.connect(self.bold_text)
        toolbar.addAction(bold_action)

        italic_action = QAction(QIcon("italic.png"), "Italic", self)
        italic_action.triggered.connect(self.italic_text)
        toolbar.addAction(italic_action)

        underline_action = QAction(QIcon("underline.png"), "Underline", self)
        underline_action.triggered.connect(self.underline_text)
        toolbar.addAction(underline_action)

        increase_font_action = QAction(QIcon("increase_font.png"), "Increase Font Size", self)
        increase_font_action.triggered.connect(self.increase_font_size)
        toolbar.addAction(increase_font_action)

        decrease_font_action = QAction(QIcon("decrease_font.png"), "Decrease Font Size", self)
        decrease_font_action.triggered.connect(self.decrease_font_size)
        toolbar.addAction(decrease_font_action)

        font_combobox = QFontComboBox(self)
        font_combobox.setCurrentFont(QFont("TkDefaultFont"))
        font_combobox.currentFontChanged.connect(self.change_font)
        toolbar.addWidget(font_combobox)

        change_color_action = QAction(QIcon("change_color.png"), "Change Text Color", self)
        change_color_action.triggered.connect(self.change_text_color)
        toolbar.addAction(change_color_action)

        set_text_background_color = QAction(QIcon("change_bg_color.png"), "Change Background Color", self)
        set_text_background_color.triggered.connect(self.set_text_background_color)
        toolbar.addAction(set_text_background_color)

    def init_tab_bar(self):
        add_tab_button = QToolButton(self)
        add_tab_button.setText("+")
        add_tab_button.setStyleSheet("QToolButton { font-size: 20px; }")
        add_tab_button.clicked.connect(self.open_new_tab)
        self.tab_widget.setCornerWidget(add_tab_button)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file:
            encodings = ["utf-8", "latin-1", "cp1252"]
            content = None
            for encoding in encodings:
                try:
                    with open(file, "r", encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if content is not None:
                current_widget = self.tab_widget.currentWidget()
                current_widget.setPlainText(content)
                self.set_tab_title(current_widget, file)
            else:
                QMessageBox.warning(self, "Open File", "Unable to open the file.")

    def save_file(self):
        current_widget = self.tab_widget.currentWidget()
        content = current_widget.toPlainText()
        file, _ = QFileDialog.getSaveFileName(self, "Save File")
        if file:
            try:
                with open(file, "w") as f:
                    f.write(content)
                self.set_tab_title(current_widget, file)  # Set the tab title
                QMessageBox.information(self, "Save File", "File saved successfully.")
            except:
                QMessageBox.warning(self, "Save File", "Unable to save the file.")

    def set_tab_title(self, text_widget, file_path):
        # Set the tab title to the file name
        file_name = QFileInfo(file_path).fileName()
        index = self.tab_widget.indexOf(text_widget)
        self.tab_widget.setTabText(index, file_name)
        # Store the file path in the text_widget for later use
        setattr(text_widget, "file_path", file_path)

    def export_as_docx(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export as DOCX", filter="*.docx")
        if file:
            doc = Document()
            current_widget = self.tab_widget.currentWidget()
            # content = current_widget.toPlainText()
            paragraph = doc.add_paragraph()
            runs = self.get_runs_with_formatting(current_widget)
            for run_text, font_format in runs:
                run = paragraph.add_run(run_text)
                self.apply_formatting(run, font_format)
            doc.save(file)
            QMessageBox.information(self, "Export as DOCX", "File exported successfully.")

    def export_as_txt(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export as TXT", filter="*.txt")
        if file:
            current_widget = self.tab_widget.currentWidget()
            content = current_widget.toPlainText()
            try:
                with open(file, "w") as f:
                    f.write(content)
                QMessageBox.information(self, "Export as TXT", "File exported successfully.")
            except:
                QMessageBox.warning(self, "Export as TXT", "Unable to export the file.")

    def apply_formatting(self, run, font_format):
        font = run.font
        if font_format["bold"]:
            font.bold = True
        if font_format["italic"]:
            font.italic = True
        if font_format["underline"]:
            font.underline = True
        if font_format["color"]:
            rgb_color = QColor(font_format["color"])
            # font.color.rgb = rgb_color.rgb()
            font.color.rgb = RGBColor(rgb_color.red(), rgb_color.green(), rgb_color.blue())
        font.size = Pt(15)

    def get_runs_with_formatting(self, text_widget):
        # cursor = QTextCursor(self.text_area.document())
        cursor = QTextCursor(text_widget.document())
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        selected_text = cursor.selection().toPlainText()

        runs = []
        start = 0
        for char in selected_text:
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            char_format = cursor.charFormat()
            runs.append((char, {
                "bold": char_format.font().bold(),
                "italic": char_format.font().italic(),
                "underline": char_format.font().underline(),
                "color": char_format.foreground().color().name()
            }))
            start += 1
        return runs

    def closeEvent(self, event):
        current_widget = self.tab_widget.currentWidget()
        if self.is_unsaved_changes(current_widget):
            reply = QMessageBox.question(self, "Unsaved Changes",
                                         "There are unsaved changes. Do you want to save before exiting?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def is_unsaved_changes(self, text_widget):
        content = text_widget.toPlainText()
        return content != "" and content != self.get_file_content(text_widget)

    def get_file_content(self, text_widget):
        file_path = getattr(text_widget, "file_path", None)
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    return content
            except FileNotFoundError:
                pass
        return ""

    def bold_text(self):
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setBold(not font.bold())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def italic_text(self):
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setItalic(not font.italic())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def underline_text(self):
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setUnderline(not font.underline())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def increase_font_size(self):
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font_size = font.pointSize()
        font_size += 1
        font.setPointSize(font_size)
        format.setFont(font)
        cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def decrease_font_size(self):
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font_size = font.pointSize()
        font_size -= 1
        font.setPointSize(font_size)
        format.setFont(font)
        cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def change_font(self, font):
        current_widget = self.tab_widget.currentWidget()
        text_cursor = current_widget.textCursor()
        format = text_cursor.charFormat()

        font_name = font.family()
        format.setFontFamily(font_name)
        text_cursor.mergeCharFormat(format)
        current_widget.setFocus()

    def change_text_color(self):
        print("Before opening color dialog")
        color = QColorDialog.getColor(parent=self)
        print("After opening color dialog")

        if color.isValid():
            current_widget = self.tab_widget.currentWidget()
            cursor = current_widget.textCursor()
            format = cursor.charFormat()
            print(f"Cursor: {cursor}")
            print(f"Format: {format}")

            print(f"Color: {color}")
            format.setForeground(color)
            print(f"Foreground color: {format.foreground()}")

            cursor.mergeCharFormat(format)
            current_widget.setFocus()
        elif not color.isValid():
            print("Invalid color")


    def set_text_background_color(self, color):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            current_widget = self.tab_widget.currentWidget()
            cursor = current_widget.textCursor()
            format = cursor.charFormat()
            format.setBackground(color)
            cursor.mergeCharFormat(format)
            current_widget.setFocus()

    def open_new_tab(self):
        text_area = QTextEdit()
        text_area.setFont(QFont("TkDefaultFont"))
        text_area.textChanged.connect(self.update_tab_title)
        self.tab_widget.addTab(text_area, "Untitled")
        self.tab_widget.setCurrentWidget(text_area)

    def close_tab(self, index):
        text_area = self.tab_widget.widget(index)

        if self.is_unsaved_changes(text_area):
            reply = QMessageBox.question(self, "Unsaved Changes",
                                         "There are unsaved changes. Do you want to save before closing the tab?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        self.tab_widget.removeTab(index)

        # Check if it's the last tab being closed
        if self.tab_widget.count() == 0:
            # Close the entire application
            self.close()

    def update_tab_title(self):
        current_widget = self.tab_widget.currentWidget()
        current_index = self.tab_widget.currentIndex()
        if self.is_unsaved_changes(current_widget):
            file_path = getattr(current_widget, "file_path", None)
            if file_path:
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(current_index, file_name + " *")
            else:
                self.tab_widget.setTabText(current_index, "Unsaved *")
        else:
            file_path = getattr(current_widget, "file_path", None)
            if file_path:
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(current_index, file_name)
            else:
                self.tab_widget.setTabText(current_index, "Untitled")

    def search_word(self, word):
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget
        cursor = QTextCursor(text_edit.document())

        if cursor.hasSelection():
            cursor.clearSelection()

        found = False
        while True:
            cursor = text_edit.document().find(word, cursor)

            if cursor.isNull():
                break

            found = True

            cursor.select(QTextCursor.WordUnderCursor)
            text_edit.setTextCursor(cursor)
            text_edit.ensureCursorVisible()

            reply = QMessageBox.question(self, "Word Found",
                                         f"The word '{word}' was found in the document. Do you want to continue searching?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                break

        if not found:
            QMessageBox.information(self, "Word Not Found", f"The word '{word}' was not found in the document.")

    def show_search_dialog(self):
        word, ok = QInputDialog.getText(self, "Search Word", "Enter the word to search:")
        if ok:
            self.search_word(word)

    def set_style_options(self):
        style_sheet = """
QTabWidget::pane {
    background-color: #FFFFFF;
}

QTabWidget::tab-bar {
    alignment: left;
    height: auto;
}

QTabBar::tab {
    background-color: #FFFFFF;
    color: #050000;
    border: 1px solid #C0C0C0;
    padding: 10px 0;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    width: 100px;
    height: 10px;
    text-align: center; 
    transition: background-color 0.3s ease, color 0.3s ease;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom-color: #FFFFFF;
}

QTabBar::tab:!selected {
    margin-top: 2px;
    background-color: #ebfcfc;
}

QTabBar::tab:hover {
    background-color: #a5faf8; 
    color: #303030; 
    cursor: pointer; 
}


        """
        self.setStyleSheet(style_sheet)


if __name__ == "__main__":
    app_thread = threading.Thread(target=app.run, kwargs={"host": "localhost", "port": 5000})
    app_thread.daemon = True
    app_thread.start()

    app_pyqt = QApplication(sys.argv)
    window = TextEditor()
    window.show()

    sys.exit(app_pyqt.exec_())
