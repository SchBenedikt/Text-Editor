from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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
        self.init_toolbar()

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

    def init_toolbar(self):
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        bold_button = QToolButton(self)
        bold_button.setText("B")
        bold_button.setCheckable(True)
        bold_button.clicked.connect(self.bold_text)
        bold_button.setStyleSheet("QToolButton { font-size: 20px; }")  # Increase the font size
        toolbar.addWidget(bold_button)

        italic_button = QToolButton(self)
        italic_button.setText("I")
        italic_button.setCheckable(True)
        italic_button.clicked.connect(self.italic_text)
        italic_button.setStyleSheet("QToolButton { font-size: 20px; }")  # Increase the font size
        toolbar.addWidget(italic_button)

        underline_button = QToolButton(self)
        underline_button.setText("U")
        underline_button.setCheckable(True)
        underline_button.clicked.connect(self.underline_text)
        underline_button.setStyleSheet("QToolButton { font-size: 20px; }")  # Increase the font size
        toolbar.addWidget(underline_button)

        color_button = QToolButton(self)
        color_button.setText("A")
        color_button.clicked.connect(self.select_color)
        color_button.setStyleSheet("QToolButton { font-size: 20px; }")  # Increase the font size
        toolbar.addWidget(color_button)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.textarea.setTextColor(color)

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
                self.textarea.setPlainText(content)
            else:
                QMessageBox.warning(self, "Open File", "Unable to open the file with the supported encodings.")

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
        if font_format["color"]:
            color = font_format["color"]
            rgb_color = RGBColor(color.red(), color.green(), color.blue())
            font.color.rgb = rgb_color
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
                "underline": char_format.font().underline(),
                "color": char_format.foreground().color()
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

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.textarea.textCursor()
            format = cursor.charFormat()
            format.setForeground(QBrush(color))
            cursor.mergeCharFormat(format)
            self.textarea.setFocus()

if __name__ == "__main__":
    app = QApplication([])
    text_editor = TextEditor()
    text_editor.show()
    app.exec()
