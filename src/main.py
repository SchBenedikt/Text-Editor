from auth import app
from ui import TextEditor
import sys
import threading
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app_thread = threading.Thread(
        target=app.run, kwargs={"host": "localhost", "port": 5000}
    )
    app_thread.daemon = True
    app_thread.start()

    app_pyqt = QApplication(sys.argv)
    window = TextEditor()
    window.show()

    sys.exit(app_pyqt.exec())
