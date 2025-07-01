import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTextEdit, QStatusBar, QLabel, 
    QMessageBox, QInputDialog, QFileDialog, QToolBar, QMenuBar, QMenu, QProgressDialog
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QTextCharFormat, QContextMenuEvent
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt, QProcess
from typing import cast

from ai import get_ollama_response, PROMPTS

# --- AI Worker Thread ---
class AIWorker(QObject):
    finished = pyqtSignal(str)
    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        result = get_ollama_response(self.prompt)
        self.finished.emit(result)

# --- Main Application Window ---
class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Text Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Core widgets
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Initialize UI components
        self.init_menu()
        self.init_ai_toolbar()

        # Start with a clean slate
        self.open_empty_tab()
    
    # --- UI Initialization ---
    def init_menu(self):
        menubar = cast(QMenuBar, self.menuBar())
        file_menu = cast(QMenu, menubar.addMenu("File"))
        
        new_action = QAction("New File", self)
        new_action.triggered.connect(self.open_empty_tab)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

    def init_ai_toolbar(self):
        ai_toolbar = cast(QToolBar, self.addToolBar("AI Tools"))
        
        self.ai_toggle_action = QAction("Enable AI", self)
        self.ai_toggle_action.setCheckable(True)
        ai_toolbar.addAction(self.ai_toggle_action)

        ai_toolbar.addSeparator()

        autocorrect_action = QAction("Autocorrect Selection", self)
        autocorrect_action.triggered.connect(lambda: self._run_ai_action("autocorrect"))
        ai_toolbar.addAction(autocorrect_action)

        translate_action = QAction("Translate Selection", self)
        translate_action.triggered.connect(self.run_translate_action)
        ai_toolbar.addAction(translate_action)
        
    # --- Context Menu ---
    def contextMenuEvent(self, event: QContextMenuEvent):
        editor = self._get_current_editor()
        if not editor or not self.ai_toggle_action.isChecked() or not editor.textCursor().hasSelection():
            return
            
        menu = cast(QMenu, editor.createStandardContextMenu())
        menu.addSeparator()
        
        ai_submenu = cast(QMenu, menu.addMenu("AI Actions"))
        
        improve_action = cast(QAction, ai_submenu.addAction("Improve Writing"))
        improve_action.triggered.connect(lambda: self._run_ai_action("improve"))
        
        summarize_action = cast(QAction, ai_submenu.addAction("Summarize Text"))
        summarize_action.triggered.connect(lambda: self._run_ai_action("summarize"))

        custom_action = cast(QAction, ai_submenu.addAction("Custom Prompt..."))
        custom_action.triggered.connect(self.run_custom_prompt_action)

        menu.exec(event.globalPos())

    # --- AI Action Handlers ---
    def _get_current_editor(self) -> QTextEdit | None:
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return cast(QTextEdit, widget)
        return None

    def _run_ai_action(self, action_type: str):
        editor = self._get_current_editor()
        if not editor or not editor.textCursor().hasSelection():
            self.status_bar.showMessage("No text selected for AI action.", 3000)
            return

        selected_text = editor.textCursor().selectedText()
        prompt = f"{PROMPTS[action_type]}\n\n--- TEXT ---\n{selected_text}"
        self._execute_ai_for_editor(prompt)
        
    def run_translate_action(self):
        editor = self._get_current_editor()
        if not editor or not editor.textCursor().hasSelection():
            self.status_bar.showMessage("Select text to translate.", 3000)
            return
            
        language, ok = QInputDialog.getText(self, "Translate", "Enter target language (e.g., 'Spanish'):")
        if ok and language:
            selected_text = editor.textCursor().selectedText()
            prompt = PROMPTS["translate"].format(language=language)
            full_prompt = f"{prompt}\n\n--- TEXT ---\n{selected_text}"
            self._execute_ai_for_editor(full_prompt)

    def run_custom_prompt_action(self):
        editor = self._get_current_editor()
        if not editor or not editor.textCursor().hasSelection():
            self.status_bar.showMessage("Select text for your custom prompt.", 3000)
            return

        instruction, ok = QInputDialog.getText(self, "Custom AI Prompt", "Your instruction for the selected text:")
        if ok and instruction:
            selected_text = editor.textCursor().selectedText()
            prompt = f"{instruction}\n\n--- TEXT ---\n{selected_text}"
            self._execute_ai_for_editor(prompt)

    def _execute_ai_for_editor(self, prompt: str):
        self.status_bar.showMessage("🤖 Asking AI...")
        
        self.ai_thread = QThread()
        self.ai_worker = AIWorker(prompt)
        self.ai_worker.moveToThread(self.ai_thread)

        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_worker.finished.connect(self.on_ai_editor_finished)
        self.ai_worker.finished.connect(self.ai_thread.quit)
        self.ai_worker.finished.connect(self.ai_worker.deleteLater)
        self.ai_thread.finished.connect(self.ai_thread.deleteLater)

        self.ai_thread.start()

    def on_ai_editor_finished(self, result: str):
        editor = self._get_current_editor()
        if result.startswith("Error:"):
            self.status_bar.showMessage(f"❌ {result}", 10000)
            QMessageBox.warning(self, "Ollama Error", result)
        elif editor:
            self.status_bar.showMessage("✅ AI response received.", 5000)
            editor.textCursor().insertText(result)

    # --- Tab and File Management ---
    def open_empty_tab(self):
        text_area = QTextEdit()
        # The context menu is now global, so we don't need to set it per-widget
        self.tab_widget.addTab(text_area, "Untitled")
        self.tab_widget.setCurrentWidget(text_area)
        
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.status_bar.showMessage("Cannot close the last tab.", 3000)
            
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.open_empty_tab()
                editor = self._get_current_editor()
                if editor:
                    editor.setPlainText(text)
                    self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        editor = self._get_current_editor()
        if not editor: return
        
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(path))
                self.status_bar.showMessage(f"Saved to {path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def download_model(self):
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QProcess, Qt

        model = os.getenv("OLLAMA_MODEL", "llama3")
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

        # Progress Dialog
        progress = QProgressDialog(f"Downloading {model}...", "Cancel", 0, 0, self)
        progress.setWindowTitle("Download Model")
        progress.setWindowModality(Qt.WindowModal)  # type: ignore[attr-defined]
        progress.show()

        # Start external process: ollama pull
        process = QProcess(self)
        process.setProgram("ollama")
        process.setArguments(["pull", model])
        # Pass Ollama host via env
        env = process.processEnvironment()
        env.insert("OLLAMA_HOST", host)
        process.setProcessEnvironment(env)

        # Update progress label with CLI output
        process.readyReadStandardOutput.connect(
            lambda: progress.setLabelText(process.readAllStandardOutput().data().decode(errors="ignore").strip())
        )
        process.readyReadStandardError.connect(
            lambda: progress.setLabelText(process.readAllStandardError().data().decode(errors="ignore").strip())
        )

        # Cancel button kills the process
        progress.canceled.connect(process.kill)

        # On finish, close dialog and notify
        def on_finished(exitCode, exitStatus):
            progress.close()
            if exitCode == 0:
                QMessageBox.information(self, "Download Model", f"Model {model} downloaded successfully.")
            else:
                QMessageBox.warning(self, "Download Model", f"Model download failed (exit code {exitCode}).")

        process.finished.connect(on_finished)
        process.start() 