from PyQt6.QtWidgets import QTextEdit, QColorDialog, QColorDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextDocument, QPageSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog


class Editor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont())

    def ask_for_text_bg_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            cursor = self.textCursor()
            format = cursor.charFormat()
            format.setBackground(color)
            cursor.mergeCharFormat(format)
            self.setFocus()

    def ask_for_text_color(self):
        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            print("error: Invalid color")
            return

        cursor = self.textCursor()
        char_format = cursor.charFormat()
        char_format.setForeground(color)
        cursor.mergeCharFormat(char_format)
        self.setFocus()

    def change_font(self, font):
        text_cursor = self.textCursor()
        format = text_cursor.charFormat()

        font_name = font.family()
        format.setFontFamily(font_name)
        text_cursor.mergeCharFormat(format)
        self.setFocus()

    def decrease_font_size(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        format = QTextCharFormat()
        font = cursor.charFormat().font()

        new_size = max(1, font.pointSize() - 1)
        font.setPointSize(new_size)

        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.setFocus()

    def bold_text(self):
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setBold(not font.bold())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.setFocus()

    def italic_text(self):
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setItalic(not font.italic())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.setFocus()

    def underline_text(self):
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setUnderline(not font.underline())
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.setFocus()

    def increase_font_size(self):
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font_size = font.pointSize()
        font_size += 1
        font.setPointSize(font_size)
        format.setFont(font)
        cursor.mergeCharFormat(format)
        self.setFocus()

    def get_runs_with_formatting(self):
        cursor = QTextCursor(self.document())
        cursor.setPosition(0)
        cursor.movePosition(
            QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor
        )
        selected_text = cursor.selection().toPlainText()

        runs = []
        start = 0
        for char in selected_text:
            cursor.setPosition(start)
            cursor.movePosition(
                QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor
            )
            char_format = cursor.charFormat()
            runs.append(
                (
                    char,
                    {
                        "bold": char_format.font().bold(),
                        "italic": char_format.font().italic(),
                        "underline": char_format.font().underline(),
                        "color": char_format.foreground().color().name(),
                    },
                )
            )
            start += 1
        return runs

    def open_search(self):
        word, ok = QInputDialog.getText(
            self, "Search Word", "Enter the word to search:"
        )
        if ok:
            self.search_word(word)

    def search_word(self, word: str):
        document = self.document()
        assert isinstance(document, QTextDocument)

        cursor = QTextCursor(document)

        if cursor.hasSelection():
            cursor.clearSelection()

        found: bool = False
        while True:
            cursor = document.find(word, cursor)

            if cursor.isNull():
                break

            found = True

            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()

            reply = QMessageBox.question(
                self,
                "Word Found",
                f"The word '{word}' was found in the document. Do you want to continue searching?",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                break

        if not found:
            QMessageBox.information(
                self,
                "Word Not Found",
                f"The word '{word}' was not found in the document.",
            )

    def print_document(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.print(printer)
