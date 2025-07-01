from PyQt6.QtWidgets import QApplication
from auth import app
from ui import TextEditor
import sys
import threading


def run_flask_app():
    app.run(host="127.0.0.1", port=5000)


def main():
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Start PyQt app
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
