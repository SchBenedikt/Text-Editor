import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.ui import TextEditor
from auth import login_to_github, github

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    
    # Handle GitHub login
    if github is None:
        login_to_github()
    
    sys.exit(app.exec())
