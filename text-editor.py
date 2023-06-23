from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QMessageBox, QFileDialog, QAction, qApp
from PyQt5.QtGui import QFont, QTextCursor
from docx import Document
from docx.shared import Pt

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Editor")
        self.setGeometry(100, 100, 800, 600)

        self.textarea = QTextEdit(self)
        self.textarea.setFont(QFont("TkDefaultFont", 11))
        self.setCentralWidget(self.textarea)

        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        export_action = QAction("Export as DOCX", self)
        export_action.triggered.connect(self.export_as_docx)
        file_menu.addAction(export_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        format_menu = menubar.addMenu("Format")
        bold_action = QAction("Bold", self)
        bold_action.triggered.connect(self.bold_text)
        format_menu.addAction(bold_action)

        italic_action = QAction("Italic", self)
        italic_action.triggered.connect(self.italic_text)
        format_menu.addAction(italic_action)

        underline_action = QAction("Underline", self)
        underline_action.triggered.connect(self.underline_text)
        format_menu.addAction(underline_action)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file:
            with open(file, "r") as f:
                content = f.read()
                self.textarea.setPlainText(content)

    def save_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save File")
        if file:
            content = self.textarea.toPlainText()
            with open(file, "w") as f:
                f.write(content)
            QMessageBox.information(self, "Save", "File saved successfully.")

    def export_as_docx(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export as DOCX", filter="*.docx")
        if file:
            doc = Document()
            content = self.textarea.toPlainText()
            paragraph = doc.add_paragraph()
            runs = self.get_runs_with_formatting(content)
            for run_text, font_format in runs:
                run = paragraph.add_run(run_text)
                self.apply_formatting(run, font_format)
            doc.save(file)
            QMessageBox.information(self, "Export as DOCX", "File exported successfully.")

    def apply_formatting(self, run, font_format):
        font = run.font
        if font_format["bold"]:
            font.bold = True
        if font_format["italic"]:
            font.italic = True
        if font_format["underline"]:
            font.underline = True
        font.size = Pt(11)

    def get_runs_with_formatting(self, text):
        cursor = QTextCursor(self.textarea.document())
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
                "underline": char_format.font().underline()
            }))
            start += 1
        return runs

    def bold_text(self):
        cursor = self.textarea.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setBold(not font.bold())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.textarea.setFocus()

    def italic_text(self):
        cursor = self.textarea.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setItalic(not font.italic())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.textarea.setFocus()

    def underline_text(self):
        cursor = self.textarea.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setUnderline(not font.underline())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.textarea.setFocus()

if __name__ == "__main__":
    app = QApplication([])
    text_editor = TextEditor()
    text_editor.show()
    app.exec()
